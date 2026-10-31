"""Orquestación acotada de Analista, Formulador y Verificador.

La entrada tiene exactamente id, title y problem. Las herramientas se ejecutan
solo a petición de un agente. Cada llamada se registra antes de devolver el
control al agente, incluidas las que terminan en un fallo de formato.
"""

from __future__ import annotations

import inspect
import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping, Optional
from uuid import uuid4

from pydantic import Field

from agents.analista import AgentFormatError, LLM, analizar, load_prompt, render
from agents.formulador import formular, limpiar_candidate
from agents.verificador import verificar
from schemas import AuditReport, ContractModel, RunResult, TraceEvent, Variant
from tools.audit_model import audit_model
from tools.extract_data_spans import extract_data_spans

ROOT = Path(__file__).resolve().parent


class Budgets(ContractModel):
    clarifications: int = Field(default=1, ge=0)
    revisions: int = Field(default=1, ge=0)
    format_retries: int = Field(default=1, ge=0)
    rereads: int = Field(default=1, ge=0)
    audits_per_candidate: int = Field(default=1, ge=0, le=1)
    model_calls: int = Field(default=20, ge=1)


class Adapters(ContractModel):
    analista: bool = False
    formulador_plan: bool = False
    formulador_candidate: bool = True
    verificador: bool = True


class TokenLimits(ContractModel):
    analista: int = Field(default=1200, ge=1)
    formulador_plan: int = Field(default=1200, ge=1)
    formulador_candidate: int = Field(default=1200, ge=1)
    verificador: int = Field(default=1200, ge=1)


class PromptPaths(ContractModel):
    analista: Path = ROOT / "prompts/analista_v3.md"
    analista_no_evidence: Path = ROOT / "prompts/analista_v3_noevidence.md"
    formulador: Path = ROOT / "prompts/formulador_v2.md"
    formulador_no_plan: Path = ROOT / "prompts/formulador_v1_noplan.md"
    verificador: Path = ROOT / "prompts/verificador_v2.md"
    control: Path = ROOT / "prompts/orquestador_v1.md"


class OrchestratorConfig(ContractModel):
    budgets: Budgets = Field(default_factory=Budgets)
    adapters: Adapters = Field(default_factory=Adapters)
    token_limits: TokenLimits = Field(default_factory=TokenLimits)
    prompts: PromptPaths = Field(default_factory=PromptPaths)

    @classmethod
    def from_mapping(cls, config: Mapping[str, Any]) -> OrchestratorConfig:
        """Consume la configuración ya leída por run.py, sin abrir datasets."""
        model = config.get("model", {})
        if model.get("id", "Qwen/Qwen2.5-1.5B-Instruct") != "Qwen/Qwen2.5-1.5B-Instruct":
            raise ValueError("el sistema solo admite Qwen2.5-1.5B-Instruct")
        generation = config.get("generation", {})
        if generation.get("do_sample", False) is not False:
            raise ValueError("la decodificación debe ser determinista")
        adapters = dict(model.get("adapter_enabled", {}))
        legacy = adapters.pop("formulador", None)
        if legacy is not None:
            adapters.setdefault("formulador_plan", legacy)
            adapters.setdefault("formulador_candidate", legacy)
        prompts = {key: (Path(value) if Path(value).is_absolute() else ROOT / value)
                   for key, value in config.get("prompts", {}).items()}
        limits = dict(generation.get("max_new_tokens", {}))
        if "max_new_tokens_candidate" in generation:
            limits.setdefault("formulador_candidate", generation["max_new_tokens_candidate"])
        return cls(budgets=config.get("budgets", {}), adapters=adapters,
                   token_limits=limits, prompts=prompts)


class _BudgetExhausted(Exception):
    pass


class _Stopped(Exception):
    pass


@dataclass
class _State:
    run_id: str
    case: dict[str, str]
    variant: Variant
    stream: Any
    events: list[TraceEvent] = field(default_factory=list)
    revisions: int = 0
    clarifications: int = 0
    retries: int = 0
    rereads: int = 0
    calls: int = 0
    tools: int = 0
    tokens: int = 0
    latency: float = 0.0
    final_text: str = ""

    def emit(self, actor, event, **details):
        record = TraceEvent(run_id=self.run_id, problem_id=self.case["id"],
                            variant=self.variant, step=len(self.events), round=self.revisions,
                            actor=actor, event=event, **details)
        self.events.append(record)
        self.stream.write(record.model_dump_json(exclude_none=True) + "\n")
        self.stream.flush()


class _RecordingLLM:
    """Captura métricas inmediatamente, antes de que otra llamada las reemplace."""

    def __init__(self, llm, state, config, actor, version, feedback):
        self.llm, self.state, self.config = llm, state, config
        self.actor, self.version, self.feedback = actor, version, feedback
        self.position = 0

    def generate(self, prompt: str, adapter_on: bool) -> str:
        state = self.state
        if state.calls >= self.config.budgets.model_calls:
            raise _BudgetExhausted("model_calls")
        stage = ("formulador_plan" if self.position == 0 else "formulador_candidate") if self.actor == "formulador" else self.actor
        self.position += 1
        limit = getattr(self.config.token_limits, stage)
        actual_prompt = prompt + ("\n\n" + self.feedback if self.feedback else "")
        state.calls += 1
        state.emit(self.actor, "llamada", prompt_version=self.version, adapter_on=adapter_on,
                   input={"prompt": actual_prompt, "stage": stage, "max_new_tokens": limit})
        started = time.perf_counter()
        try:
            kwargs = {"max_new_tokens": limit} if "max_new_tokens" in inspect.signature(self.llm.generate).parameters else {}
            raw = self.llm.generate(actual_prompt, adapter_on, **kwargs)
            if not isinstance(raw, str):
                raise TypeError("generate debe devolver texto")
        except Exception as error:
            elapsed = (time.perf_counter() - started) * 1000
            state.latency += elapsed
            state.emit(self.actor, "respuesta", prompt_version=self.version,
                       adapter_on=adapter_on, output={"error": str(error), "stage": stage}, latency_ms=elapsed)
            raise _Stopped(f"fallo del modelo: {error}") from error
        if stage == "formulador_candidate" and raw.strip():
            state.final_text = limpiar_candidate(raw)
        stats = getattr(self.llm, "last_stats", None)

        def metric(name, fallback=None):
            return stats.get(name, fallback) if isinstance(stats, dict) else getattr(stats, name, fallback)

        elapsed = metric("latency_ms", (time.perf_counter() - started) * 1000)
        tokens_in, tokens_out = metric("tokens_in"), metric("tokens_out")
        state.tokens += (tokens_in or 0) + (tokens_out or 0)
        state.latency += elapsed
        state.emit(self.actor, "respuesta", prompt_version=self.version, adapter_on=adapter_on,
                   output={"raw": raw, "stage": stage, "reached_limit": metric("reached_limit")},
                   tokens_in=tokens_in, tokens_out=tokens_out, latency_ms=elapsed)
        return raw


class Orchestrator:
    """Una corrida por enunciado; todos los presupuestos se reinician en run()."""

    def __init__(self, llm: LLM, config: Optional[OrchestratorConfig] = None,
                 *, audit_fn: Callable = audit_model, span_fn: Callable = extract_data_spans):
        self.llm = llm
        self.config = config or OrchestratorConfig()
        self.audit_fn, self.span_fn = audit_fn, span_fn
        self.last_events: list[TraceEvent] = []

    def run(self, case: Mapping[str, str], *, variant: Variant = "full",
            run_id: Optional[str] = None, trace_path: Optional[Path] = None) -> RunResult:
        if set(case) != {"id", "title", "problem"} or any(not isinstance(v, str) or not v.strip() for v in case.values()):
            raise ValueError("la entrada debe contener solo id, title y problem no vacíos")
        if variant not in ("full", "no_evidence", "no_plan", "no_audit", "no_review"):
            raise ValueError("variante no reconocida")
        run_id = run_id or uuid4().hex
        if not re.fullmatch(r"[A-Za-z0-9_-]+", run_id):
            raise ValueError("run_id debe ser un identificador simple")
        path = Path(trace_path) if trace_path is not None else ROOT / "traces" / f"{run_id}.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        control_version, controls = load_prompt(self.config.prompts.control)
        # No sobrescribir una traza anterior con el mismo identificador.
        with path.open("x", encoding="utf-8") as stream:
            state = _State(run_id, dict(case), variant, stream)
            self.last_events = state.events
            state.emit("orquestador", "llamada", prompt_version=control_version,
                       input={"case": dict(case), "config": self.config.model_dump(mode="json")})
            try:
                status = self._pipeline(state, controls)
            except _BudgetExhausted as error:
                state.emit("orquestador", "presupuesto_agotado", output={"budget": str(error)})
                status = "presupuesto_agotado"
            except AgentFormatError as error:
                state.emit("orquestador", "presupuesto_agotado", output={"budget": "format_retries", "error": str(error)})
                status = "fallo_formato"
            except _Stopped as error:
                state.emit("orquestador", "decision", decision="stop", output={"reason": str(error)})
                status = "detenido"
            result = RunResult(problem_id=case["id"], variant=variant, final_text=state.final_text,
                               status=status, rounds=state.revisions, clarifications=state.clarifications,
                               tool_calls=state.tools, tokens_total=state.tokens, latency_ms_total=state.latency)
            state.emit("orquestador", "fin", output=result.model_dump(mode="json"))
            return result

    def _invoke(self, state, controls, actor, path, function, validate=None):
        feedback = ""
        while True:
            llm = _RecordingLLM(self.llm, state, self.config, actor, path.stem, feedback)
            try:
                step = function(llm)
                if validate is not None:
                    try:
                        validate(step.output)
                    except ValueError as error:
                        raise AgentFormatError(str(error), raw=step.calls[-1].raw,
                                               prompt_version=path.stem, calls=step.calls,
                                               warnings=step.warnings) from None
            except AgentFormatError as error:
                state.emit(actor, "fallo_formato", prompt_version=path.stem,
                           output={"error": str(error), "raw": error.raw, "warnings": error.warnings})
                if state.retries >= self.config.budgets.format_retries:
                    raise
                state.retries += 1
                feedback = render(controls["format_retry"], feedback=str(error))
                state.emit("orquestador", "reintento", input={"actor": actor}, output={"feedback": feedback})
                continue
            state.emit(actor, "decision", prompt_version=path.stem,
                       output={"artifact": step.output.model_dump(mode="json"), "warnings": step.warnings},
                       decision=step.output.action)
            return step.output

    def _tool(self, state, actor, arguments, call):
        state.tools += 1
        started = time.perf_counter()
        try:
            output = call()
            if actor == "audit_model" and not isinstance(output, AuditReport):
                raise TypeError("audit_model debe devolver AuditReport")
            value = [v.model_dump(mode="json") for v in output] if isinstance(output, list) else output.model_dump(mode="json")
        except Exception as error:
            elapsed = (time.perf_counter() - started) * 1000
            state.latency += elapsed
            state.emit(actor, "herramienta", input=arguments, output={"error": str(error)}, latency_ms=elapsed)
            raise _Stopped(f"fallo de herramienta {actor}: {error}") from error
        elapsed = (time.perf_counter() - started) * 1000
        state.latency += elapsed
        state.emit(actor, "herramienta", input=arguments, output=value, latency_ms=elapsed)
        return output

    def _pipeline(self, state, controls):
        config = self.config
        analyst_path = config.prompts.analista_no_evidence if state.variant == "no_evidence" else config.prompts.analista
        formulator_path = config.prompts.formulador_no_plan if state.variant == "no_plan" else config.prompts.formulador
        verifier_path = config.prompts.verificador
        problem = state.case["problem"]
        spans = None

        def validate_spec(output):
            if output.action != "deliver" or state.variant == "no_evidence":
                return
            for requirement in output.spec.requirements:
                evidence = requirement.evidence
                if evidence is None or evidence.text not in problem:
                    raise ValueError(f"{requirement.id}: falta una cita literal comprobable")
                if evidence.start is not None and problem[evidence.start:evidence.end] != evidence.text:
                    raise ValueError(f"{requirement.id}: offsets de evidencia incorrectos")

        def analysis(question=None, previous_spec=None):
            nonlocal spans
            while True:
                output = self._invoke(state, controls, "analista", analyst_path,
                    lambda llm: analizar(llm, state.case["id"], problem,
                                         adapter_on=config.adapters.analista, prompt_path=analyst_path,
                                         spans=spans, question=question, previous_spec=previous_spec), validate_spec)
                if output.action == "deliver":
                    return output.spec
                if state.rereads >= config.budgets.rereads:
                    raise _BudgetExhausted("rereads")
                state.rereads += 1
                spans = self._tool(state, "extract_data_spans", {"problem": problem}, lambda: self.span_fn(problem))

        def validate_draft(output):
            if output.action == "formulate":
                state.final_text = output.draft.raw_text
                if not output.draft.parse_ok:
                    raise ValueError("; ".join(output.draft.parse_errors))

        spec = analysis()
        draft = None
        observations = []
        while True:
            current_observations = list(observations)
            if state.clarifications >= config.budgets.clarifications:
                current_observations.append(render(controls["no_clarification"]))
            output = self._invoke(state, controls, "formulador", formulator_path,
                lambda llm: formular(llm, problem, spec, candidate_id=f"{state.run_id}-r{state.revisions}",
                    adapter_plan=config.adapters.formulador_plan, adapter_candidate=config.adapters.formulador_candidate,
                    prompt_path=formulator_path, observations=current_observations,
                    previous_draft=draft.raw_text if draft is not None else None), validate_draft)
            if output.action == "clarify":
                if state.clarifications >= config.budgets.clarifications:
                    raise _BudgetExhausted("clarifications")
                state.clarifications += 1
                spec = analysis(question=output.question, previous_spec=spec)
                continue
            draft = output.draft
            can_audit = state.variant != "no_audit" and config.budgets.audits_per_candidate > 0
            review = self._invoke(state, controls, "verificador", verifier_path,
                lambda llm: verificar(llm, problem, spec, draft, adapter_on=config.adapters.verificador,
                                      prompt_path=verifier_path, audit_allowed=can_audit))
            if review.action == "audit":
                report = self._tool(state, "audit_model",
                    {"spec": spec.model_dump(mode="json"), "draft": draft.model_dump(mode="json"),
                     "coverage": review.coverage.model_dump(mode="json")},
                    lambda: self.audit_fn(spec, draft, review.coverage))
                if report.candidate_id != draft.candidate_id:
                    raise _Stopped("informe de auditoría de otro borrador")
                coverage = review.coverage
                review = self._invoke(state, controls, "verificador", verifier_path,
                    lambda llm: verificar(llm, problem, spec, draft, adapter_on=config.adapters.verificador,
                        prompt_path=verifier_path, coverage=coverage, audit_report=report))
            decision = review.decision
            if decision.action == "accept":
                return "aceptado"
            if decision.action == "stop":
                return "detenido"
            if state.variant == "no_review":
                raise _BudgetExhausted("no_review")
            if state.revisions >= config.budgets.revisions:
                raise _BudgetExhausted("revisions")
            state.revisions += 1
            observations = decision.issues
