"""Calibración reproducible, sin LLM, con controles de los ocho dev_cases."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from eval.audit_dev_fixtures import development_artifacts
from tools.audit_model import audit_model


def calibrate():
    cases = {}
    for case_id, args in development_artifacts().items():
        report = audit_model(*args)
        cases[case_id] = {
            "findings": [f.model_dump(exclude_none=True) for f in report.findings],
            "errors": sum(f.level == "error" for f in report.findings),
            "warnings": sum(f.level == "aviso" for f in report.findings),
            "unverified": sum(f.status == "no_verificado" for f in report.findings),
        }
    return {"scope": "eight manually written development controls; no LLM or official benchmark",
            "syntax_level": "aviso", "cases": cases}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    options = parser.parse_args()
    result = calibrate()
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if options.output:
        options.output.write_text(rendered + "\n", encoding="utf-8")
    print(json.dumps({k: {m: v[m] for m in ("errors", "warnings", "unverified")}
                      for k, v in result["cases"].items()}, indent=2))
