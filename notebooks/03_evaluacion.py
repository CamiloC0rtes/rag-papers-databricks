# Databricks notebook source
# MAGIC %md
# MAGIC # 03 - Evaluación (configuración v6)
# MAGIC
# MAGIC Evalúa por separado las preguntas del dominio (4 jueces) y las de fuera de tema (solo Correctness), con los casos de `eval/cases.json` (44 + 10).
# MAGIC
# MAGIC Tiempo aproximado con el endpoint gratuito (1 worker): ~15 min por corrida del set de 44 + 10.

# COMMAND ----------

# MAGIC %pip install -q -r ../requirements.txt
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

import os, sys
sys.path.append(os.path.abspath(".."))

from rag_lab.clients import setup_mlflow
setup_mlflow()

# COMMAND ----------

from rag_lab.evaluation import load_cases, verify_cases

in_domain, out_of_domain = load_cases()
print(len(in_domain), "del dominio |", len(out_of_domain), "fuera de tema")
verify_cases(in_domain)   # comprueba que las respuestas esperadas existen en los chunks

# COMMAND ----------

from rag_lab.evaluation import run_eval
from rag_lab.generation import make_rag

results = {"v6": run_eval(make_rag(), "v6", in_domain, out_of_domain)}

# COMMAND ----------

from rag_lab.evaluation import compare, report, summarize

stats = summarize(results["v6"], "v6", in_domain)
by_type, lat = report(stats)
display(compare(results)); display(by_type); display(lat)

# COMMAND ----------

from rag_lab.evaluation import show_failures

show_failures(results["v6"]["in"].run_id)
show_failures(results["v6"]["ood"].run_id, judges=("correctness",))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Opcional: repetir 3 corridas para medir el ruido entre corridas
# MAGIC
# MAGIC Descomenta para ejecutar (~46 min con el endpoint gratuito).

# COMMAND ----------

# runs = {}
# for i in range(1, 4):
#     runs[f"v6-r{i}"] = run_eval(make_rag(), f"v6-r{i}", in_domain, out_of_domain)
# import pandas as pd
# stats = pd.concat([summarize(r, l, in_domain) for l, r in runs.items()])
# by_type, lat = report(stats)
# display(compare(runs)); display(by_type); display(lat)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Opcional: variante barata (20 candidatos en lotes de 10)
# MAGIC
# MAGIC 2 llamadas al reranker por pregunta en vez de 8. En las corridas registradas bajó la latencia p50 a ~9 s, pero también la correctness. Descomenta para ejecutar (~19 min para 2 corridas).

# COMMAND ----------

# cheap = {}
# for i in range(1, 3):
#     cheap[f"c20b10-r{i}"] = run_eval(make_rag(n_candidates=20, rerank_bs=10), f"c20b10-r{i}", in_domain, out_of_domain)
# display(compare(cheap))
