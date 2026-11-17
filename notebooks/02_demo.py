# Databricks notebook source
# MAGIC %md
# MAGIC # 02 - Demo del RAG
# MAGIC
# MAGIC Una pregunta de ejemplo y las herramientas de diagnóstico del retriever. `make_rag()` por defecto es la configuración "v6" (prompt v5 + reranker con título + máx. 2 chunks por artículo + 2 chunks de introducción).

# COMMAND ----------

# MAGIC %pip install -q -r ../requirements.txt
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

import os, sys
sys.path.append(os.path.abspath(".."))

from rag_lab.clients import setup_mlflow
setup_mlflow()

# COMMAND ----------

from rag_lab.generation import make_rag

rag = make_rag()
print(rag("In the study assessing VGG16 and CNN architectures for CT scan classification, what test accuracy did InceptionV3 obtain?"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Diagnóstico del retriever
# MAGIC
# MAGIC `retrieval_probe` muestra en qué posición quedan los chunks que contienen un texto (`needle`), entre los candidatos y tras el reranker.

# COMMAND ----------

from rag_lab.retrieval import retrieval_probe, show_context

retrieval_probe("In the study assessing VGG16 and CNN architectures for CT scan classification, "
                "what test accuracy did InceptionV3 obtain?", needle="88.79")

# COMMAND ----------

show_context("In the study assessing VGG16 and CNN architectures for CT scan classification, "
             "what test accuracy did InceptionV3 obtain?")
