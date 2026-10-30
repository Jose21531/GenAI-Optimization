"""Controles paramétricos escritos a partir de los ocho enunciados de desarrollo.

Solo evaluación local de la herramienta. No son entradas de los agentes ni
salidas atribuidas a Qwen. No se calculan soluciones de las instancias.
"""

from schemas import CoverageMap, DraftModel, ProblemSpec


def development_artifacts():
    # índices, parámetros, variables (dominio), objetivo y restricciones.
    cases = [
        ({"i": "I"}, "c_i p_i g_i Q P L U t A", ["x_i >= 0"],
         "min sum_{i in I} c_i x_i",
         ["sum_{i in I} x_i = Q", "sum_{i in I} p_i x_i >= P",
          "sum_{i in I} g_i x_i >= L", "sum_{i in I} g_i x_i <= U", "x_4 <= t Q", "x_2 <= A"]),
        ({"k": "K"}, "d_k t_k e_k f_k H c B E", ["x_k >= 0", "z_k >= 0", "h >= 0"],
         "min c h + sum_{k in K} f_k z_k",
         ["x_k + z_k >= d_k forall k in K", "sum_{k in K} t_k x_k <= H + h",
          "sum_{k in K} e_k x_k <= E", "h <= B"]),
        ({"r": "R", "a": "A"}, "s_ra k m v_ra", [r"x_ra \in {0,1}"],
         "max sum_{r in R} sum_{a in A} s_ra x_ra",
         ["sum_{r in R} x_ra = k forall a in A", "sum_{a in A} x_ra <= m forall r in R",
          "x_ra <= v_ra forall r in R, a in A"]),
        ({"p": "P"}, "b_p c_p h_p B H n", [r"y_p \in {0,1}"],
         "max sum_{p in P} b_p y_p",
         ["sum_{p in P} c_p y_p <= B", "sum_{p in P} h_p y_p <= H",
          "y_4 <= y_1", "y_2 + y_5 <= 1", "sum_{p in P} y_p >= n"]),
        ({"i": "I", "j": "J"}, "s_i d_j c_ij Q V", ["q_ij >= 0", r"n_ij \in \mathbb{Z}_{\ge 0}"],
         "min sum_{i in I} sum_{j in J} c_ij n_ij",
         ["sum_{j in J} q_ij <= s_i forall i in I", "sum_{i in I} q_ij >= d_j forall j in J",
          "q_ij <= Q n_ij forall i in I, j in J", "n_ij <= V forall i in I, j in J"]),
        ({"p": "P", "l": "L"}, "f_l c_pl a_pl H m d_p", ["x_pl >= 0", r"y_l \in {0,1}"],
         "min sum_{l in L} f_l y_l + sum_{p in P} sum_{l in L} c_pl x_pl",
         ["sum_{l in L} x_pl >= d_p forall p in P", "sum_{p in P} a_pl x_pl <= H y_l forall l in L",
          "sum_{p in P} x_pl >= m y_l forall l in L"]),
        ({"i": "I", "k": "K"}, "w_i C f", [r"x_ik \in {0,1}", r"y_k \in {0,1}"],
         "min sum_{k in K} f y_k",
         ["sum_{k in K} x_ik = 1 forall i in I", "sum_{i in I} w_i x_ik <= C y_k forall k in K",
          "x_2k + x_5k <= 1 forall k in K"]),
        ({"t": "T"}, "d_t p_t S h I F U", ["q_t >= 0", "v_t >= 0"],
         "min sum_{t in T} (p_t q_t + h v_t)",
         ["v_{t-1} + q_t - d_t = v_t forall t in T", "v_t <= S forall t in T",
          "q_t <= U forall t in T", "v_0 = I", "v_4 >= F"]),
    ]
    result = {}
    for number, (bindings, parameters, variables, objective, constraints) in enumerate(cases, 1):
        case_id = f"dev{number:02}"
        params = parameters.split()

        def declaration(symbol):
            name, _, sub = symbol.partition("_")
            suffix = ", ".join(f"{i} \\in {bindings[i]}" for i in sub)
            return f"{symbol}: dato {name}" + (f", {suffix}" if suffix else "")

        text = ("Conjuntos:\n" + "\n".join(f"{s}: conjunto" for s in dict.fromkeys(bindings.values()))
                + "\nParámetros:\n" + "\n".join(map(declaration, params))
                + "\nVariables de decisión:\n" + "\n".join(v + ": decisión" for v in variables)
                + "\nFunción objetivo:\n" + objective
                + "\nRestricciones:\n" + "\n".join(constraints))
        elements = [("objective", objective)] + [("constraint", c) for c in constraints]
        elements += [("domain", v) for v in variables]
        requirements = [{"id": f"U{i}", "kind": kind, "text": excerpt}
                        for i, (kind, excerpt) in enumerate(elements, 1)]
        spec = ProblemSpec.model_validate({
            "case_id": case_id, "sets": [{"name": s, "description": "conjunto"} for s in dict.fromkeys(bindings.values())],
            "data": [{"name": p.partition("_")[0], "description": "dato paramétrico",
                      "indexed_by": [bindings[i] for i in p.partition("_")[2]]} for p in params],
            "objective": {"sense": objective.split()[0], "description": "objetivo de desarrollo"},
            "requirements": requirements,
        })
        draft = DraftModel(candidate_id=case_id + "-control", raw_text=text)
        coverage = CoverageMap.model_validate({"candidate_id": draft.candidate_id,
            "elements": [{"id": f"E{i}", "kind": kind, "excerpt": excerpt}
                         for i, (kind, excerpt) in enumerate(elements, 1)],
            "links": [{"requirement_id": f"U{i}", "element_id": f"E{i}"}
                      for i in range(1, len(elements) + 1)]})
        result[case_id] = (spec, draft, coverage)
    return result
