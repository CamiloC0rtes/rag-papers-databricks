# Databricks notebook source
# MAGIC %md
# MAGIC # 04 - Generar casos de evaluación nuevos
# MAGIC
# MAGIC El LLM propone **borradores** de preguntas por artículo y el código verifica automáticamente que la evidencia y las claves existan en los chunks.
# MAGIC Los borradores **se revisan a mano** antes de añadirlos a `eval/cases.json`; este notebook no modifica ese archivo.

# COMMAND ----------

# MAGIC %pip install -q -r ../requirements.txt
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

import os, sys
sys.path.append(os.path.abspath(".."))

from rag_lab.clients import setup_mlflow
setup_mlflow()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Borradores generados por el LLM + verificación automática de evidencia

# COMMAND ----------

import json, random, re
import pandas as pd

from rag_lab.clients import get_spark
from rag_lab.config import CHUNKS_TABLE
from rag_lab.evaluation import load_cases
from rag_lab.retrieval import call_llm
from rag_lab.utils import chunk_num, short_id, strip_title

IN_DOMAIN, OUT_OF_DOMAIN = load_cases()   # casos existentes, para no repetir preguntas

_chunks = get_spark().table(CHUNKS_TABLE).select("chunk_id", "source", "title", "content").collect()
by_src = {}
for r in _chunks:
    by_src.setdefault(r.source, []).append(r)

GEN_PROMPT = """You write evaluation questions for a RAG system over a collection of scientific papers.
Paper title: {title}
Existing questions about this paper (do not repeat them):
{existing}

Excerpts:
{text}

Write 3 NEW factual questions answerable ONLY from the excerpts, about what THIS paper itself did or found (never cited related work).
Rules:
- Each question must name the study explicitly (e.g. "In the study on <short topic>, ...") so it is unambiguous among many papers.
- Prefer specific numbers, datasets, methods or named findings.
- "evidence": an EXACT substring copied from the excerpts (5-15 words) that contains the answer.
- "keys": 1-2 short EXACT substrings from the evidence (e.g. a number as written).
Reply with ONLY a JSON list: [{{"q": "...", "fact": "...", "evidence": "...", "keys": ["..."]}}]"""

drafts = []
for src, rows in sorted(by_src.items()):
    rows = sorted(rows, key=lambda r: chunk_num(r.chunk_id))
    res = [r for r in rows[4:] if re.search(r"\d+\.\d+ ?%|accuracy|F1|AUC|kappa|dice", r.content, re.I)]
    pick = rows[:4] + random.Random(0).sample(res, min(3, len(res)))
    text = "\n\n".join(strip_title(r.content) for r in pick)[:7000]
    existing = "\n".join(c["q"] for c in IN_DOMAIN if c["src"] and c["src"] in src) or "(none)"
    out = call_llm([{"role": "user", "content": GEN_PROMPT.format(title=rows[0].title, existing=existing, text=text)}],
                   max_tokens=900)
    try:
        items = json.loads(re.search(r"\[.*\]", out, re.S).group())
    except Exception:
        print("JSON inválido:", src)
        continue
    full = " ".join(r.content for r in rows)
    for it in items:
        ok = it.get("evidence", "") in full and all(k in full for k in it.get("keys", []))
        drafts.append(dict(src=src, ok=ok, q=it.get("q"), fact=it.get("fact"), keys=it.get("keys", [])))

draft_df = pd.DataFrame(drafts)
print(draft_df.ok.value_counts().to_dict())
for i, d in draft_df.iterrows():
    print(i, "OK" if d.ok else "XX", "|", d.src[:22], "|", d.q, "|", d.fact, "|", d["keys"])

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Revisión manual
# MAGIC
# MAGIC Elige a mano los borradores que sirvan y pégalos en `NEW_CASES` con el formato de `eval/cases.json`
# MAGIC (`q`, `facts`, `src`, `keys` y, si varios artículos responden, `"kind": "ambigua"`). La celda imprime una ventana de texto
# MAGIC alrededor de la primera clave de cada caso para comprobar la evidencia. Después, añade los casos revisados a `eval/cases.json` por tu cuenta.

# COMMAND ----------

NEW_CASES = [
    # dict(q="...", facts=["..."], src="...", keys=["..."]),
]

for i, c in enumerate(NEW_CASES):
    hits = [r for r in _chunks if (c["src"] is None or c["src"] in r.source) and c["keys"][0] in r.content]
    if not hits:
        print(i, "SIN EVIDENCIA |", c["q"][:60]); continue
    b = strip_title(hits[0].content); j = b.find(c["keys"][0])
    print(i, "|", short_id(hits[0].chunk_id), "|", b[max(0, j - 160): j + 90].replace(chr(10), " "))
