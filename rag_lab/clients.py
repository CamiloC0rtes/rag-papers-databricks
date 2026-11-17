"""Clientes de Databricks. Se crean de forma perezosa (nunca al importar) y se cachean en el módulo."""

import os

_spark = None
_llm = None
_vsc = None


def get_spark():
    """SparkSession (en un notebook de Databricks devuelve la sesión existente)."""
    global _spark
    if _spark is None:
        from pyspark.sql import SparkSession
        _spark = SparkSession.builder.getOrCreate()
    return _spark


def get_llm():
    """Cliente compatible con OpenAI del endpoint de Foundation Models.
    Nota: get_open_ai_client() está deprecado (ver "Trabajo futuro" en el README); se mantiene porque es lo que se probó."""
    global _llm
    if _llm is None:
        from databricks.sdk import WorkspaceClient
        _llm = WorkspaceClient().serving_endpoints.get_open_ai_client()
    return _llm


def get_vsc():
    """Cliente de Vector Search (databricks-vectorsearch, deprecado pero probado)."""
    global _vsc
    if _vsc is None:
        from databricks.vector_search.client import VectorSearchClient
        _vsc = VectorSearchClient(disable_notice=True)
    return _vsc


def setup_mlflow():
    """Configura MLflow: evaluación de a una pregunta y autolog de OpenAI."""
    # El endpoint gratuito tiene un QPS muy bajo: evaluate de a una pregunta
    os.environ.setdefault("MLFLOW_GENAI_EVAL_MAX_WORKERS", "1")
    import mlflow
    mlflow.openai.autolog()
