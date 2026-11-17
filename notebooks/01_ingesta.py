# Databricks notebook source
# MAGIC %md
# MAGIC # 01 - Ingesta: PDFs -> tabla de chunks -> índice vectorial
# MAGIC
# MAGIC Pipeline: PDFs en el Volume -> chunks con `Paper: <título>` -> tabla Delta (MERGE) -> índice Vector Search (Delta Sync, HYBRID).
# MAGIC
# MAGIC Requisito manual: el **endpoint de Vector Search** (por defecto `genai_lab_vs`) se crea desde la UI del workspace; este repo no lo crea por código.

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
# MAGIC ## 1. Schema y Volume

# COMMAND ----------

from rag_lab.ingest import ensure_schema_and_volume
ensure_schema_and_volume()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Subir los PDFs al Volume
# MAGIC
# MAGIC Sube los PDFs a `/Volumes/<catálogo>/<schema>/<volumen>/` (por defecto `/Volumes/test/genai_lab/raw_docs/`), por ejemplo desde la UI de Catalog Explorer.
# MAGIC Los PDFs no se incluyen en este repo: ver `data/README.md` para la lista de los 12 papers usados.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Chunks -> tabla Delta
# MAGIC
# MAGIC Cada chunk lleva el título del artículo al inicio (`Paper: <título>`). La escritura usa MERGE (no overwrite): los chunks que desaparecen se borran también del índice y solo se re-embeben los que cambian.

# COMMAND ----------

from rag_lab.ingest import build_chunks, upsert_chunks
upsert_chunks(build_chunks())

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Índice vectorial
# MAGIC
# MAGIC `ensure_index()` crea el índice si no existe y espera a que quede en sincronía con la tabla.

# COMMAND ----------

from rag_lab.index import ensure_index, sync_index
ensure_index()

# COMMAND ----------

s = sync_index()
if not s["in_sync"]:
    print("⚠️ El índice no coincide con la tabla. Ejecuta recreate_index().")

# COMMAND ----------

# Solo si el índice no queda en sincronía (por ejemplo, filas viejas: indexed > table):
# from rag_lab.index import recreate_index
# recreate_index()

# COMMAND ----------

from rag_lab.retrieval import refresh_chunk_cache
refresh_chunk_cache()   # invalida la caché de chunks tras re-ingerir

# COMMAND ----------

from rag_lab.index import index_status
index_status()
# Ejemplo de salida con el corpus original: {'ready': True, 'indexed': 1112, 'table': 1112, 'in_sync': True}
