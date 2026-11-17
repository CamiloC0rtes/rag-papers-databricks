"""Evaluación con mlflow.genai.evaluate: casos desde eval/cases.json, métricas por tipo y latencia."""

import json
from pathlib import Path

import mlflow
import pandas as pd

from rag_lab.clients import get_spark
from rag_lab.config import CHUNKS_TABLE, REFUSAL
from rag_lab.utils import question_kind

CASES_PATH = Path(__file__).resolve().parents[1] / "eval" / "cases.json"


def load_cases(path=None):
    """Lee eval/cases.json y devuelve (in_domain, out_of_domain)."""
    with open(path or CASES_PATH, encoding="utf-8") as f:
        d = json.load(f)
    return d["in_domain"], d["out_of_domain"]


def _resolve(in_domain, out_of_domain):
    if in_domain is None or out_of_domain is None:
        din, dood = load_cases()
        in_domain = din if in_domain is None else in_domain
        out_of_domain = dood if out_of_domain is None else out_of_domain
    return in_domain, out_of_domain


def verify_cases(cases=None):
    """Comprueba que cada 'key' exista en los chunks del artículo esperado."""
    if cases is None:
        cases = load_cases()[0]
    rows = get_spark().table(CHUNKS_TABLE).select("source", "content").collect()
    problems = []
    for c in cases:
        txt = " ".join(r.content for r in rows if c["src"] is None or c["src"] in r.source)
        missing = [k for k in c["keys"] if k not in txt]
        if not txt:
            problems.append((c["q"][:60], f"sin chunks para {c['src']}"))
        elif missing:
            problems.append((c["q"][:60], missing))
    print("OK: todas las respuestas esperadas existen en los chunks" if not problems else problems)
    return problems


def eval_rows(in_domain=None, out_of_domain=None):
    in_domain, out_of_domain = _resolve(in_domain, out_of_domain)
    rin = [{"inputs": {"question": c["q"]}, "expectations": {"expected_facts": c["facts"]}} for c in in_domain]
    rood = [{"inputs": {"question": q}, "expectations": {"expected_response": REFUSAL}} for q in out_of_domain]
    return rin, rood


def run_eval(rag_fn, label, in_domain=None, out_of_domain=None):
    """Evalúa por separado preguntas del dominio (4 jueces) y fuera de dominio (solo Correctness)."""
    from mlflow.genai.scorers import RetrievalGroundedness, RelevanceToQuery, Correctness, RetrievalRelevance
    rin, rood = eval_rows(in_domain, out_of_domain)
    with mlflow.start_run(run_name=f"{label}-in"):
        r_in = mlflow.genai.evaluate(data=rin, predict_fn=rag_fn,
                                     scorers=[RetrievalGroundedness(), RelevanceToQuery(), Correctness(), RetrievalRelevance()])
    with mlflow.start_run(run_name=f"{label}-ood"):
        r_ood = mlflow.genai.evaluate(data=rood, predict_fn=rag_fn, scorers=[Correctness()])
    m = {k.replace("/mean", ""): round(float(v), 3) for k, v in r_in.metrics.items() if "precision" not in k}
    m["ood_correctness"] = round(float(r_ood.metrics["correctness/mean"]), 3)
    print(label, m)
    return {"in": r_in, "ood": r_ood, "metrics": m}


def compare(results):
    """Tabla comparativa de varias corridas de run_eval: {label: resultado}."""
    return pd.DataFrame({label: r["metrics"] for label, r in results.items()})


def _q(t):
    """Pregunta de un trace (el 'request' puede ser dict, JSON en texto o texto)."""
    r = t["request"]
    if isinstance(r, str):
        try:
            r = json.loads(r)
        except Exception:
            return r
    return r.get("question", str(r)) if isinstance(r, dict) else str(r)


def show_failures(run_id, judges=("correctness", "retrieval_groundedness"), width=300):
    """Imprime solo las preguntas que fallaron algún juez, con la explicación del juez."""
    tr = mlflow.search_traces(run_id=run_id)
    for _, t in tr.iterrows():
        A = [a if isinstance(a, dict) else a.to_dictionary() for a in t["assessments"]]
        val = lambda n: [a.get("feedback", {}).get("value") for a in A if a["assessment_name"] == n]
        bad = [n for n in judges if "no" in val(n)]
        if not bad:
            continue
        print("=" * 90, f"\nFALLA: {bad} | precisión retrieval: {val('retrieval_relevance/precision')}")
        print("Q:", _q(t))
        print("A:", str(t["response"])[:500])
        for a in A:
            if a["assessment_name"] in bad:
                print(f"  [{a['assessment_name']}] {a.get('rationale', '')[:width]}")


def per_question(results, judge="correctness"):
    out = {}
    for label, r in results.items():
        for _, t in mlflow.search_traces(run_id=r["in"].run_id).iterrows():
            A = [a if isinstance(a, dict) else a.to_dictionary() for a in t["assessments"]]
            v = [a.get("feedback", {}).get("value") for a in A if a["assessment_name"] == judge]
            out.setdefault(_q(t)[:80], {})[label] = v[0] if v else None
    df = pd.DataFrame(out).T
    return df[(df != "yes").any(axis=1)]   # solo preguntas que fallaron en alguna versión


def summarize(res, label, in_domain=None):
    """Una fila por pregunta: tipo, correctness (1/0) y latencia del RAG en segundos."""
    in_domain, _ = _resolve(in_domain, [])
    kind = {c["q"]: question_kind(c) for c in in_domain}
    rows = []
    for part in ("in", "ood"):
        for _, t in mlflow.search_traces(run_id=res[part].run_id).iterrows():
            A = [a if isinstance(a, dict) else a.to_dictionary() for a in t["assessments"]]
            v = [a.get("feedback", {}).get("value") for a in A if a["assessment_name"] == "correctness"]
            q = _q(t)
            rows.append({"run": label, "tipo": kind.get(q, "?") if part == "in" else "fuera de tema",
                         "ok": float(v[0] == "yes") if v else None, "seg": t["execution_duration"] / 1000, "q": q})
    return pd.DataFrame(rows)


def report(stats):
    by_type = stats.pivot_table(index="tipo", columns="run", values="ok", aggfunc="mean").round(3)
    lat = stats.groupby("run")["seg"].describe(percentiles=[.5, .95])[["50%", "95%", "max"]].round(1)
    return by_type, lat
