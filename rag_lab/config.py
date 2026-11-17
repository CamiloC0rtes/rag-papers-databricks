"""Configuración del RAG. Los valores por defecto son los del notebook original; los seis primeros
se pueden sobreescribir con variables de entorno (ver README). No importa nada de Databricks."""

import os

# --- Datos ---
CATALOG = os.environ.get("RAG_CATALOG", "test")
SCHEMA = os.environ.get("RAG_SCHEMA", "genai_lab")
VOLUME_NAME = os.environ.get("RAG_VOLUME", "raw_docs")
VOLUME_PATH = f"/Volumes/{CATALOG}/{SCHEMA}/{VOLUME_NAME}/"
CHUNKS_TABLE = f"{CATALOG}.{SCHEMA}.doc_chunks"

# --- Vector Search ---
VS_ENDPOINT = os.environ.get("RAG_VS_ENDPOINT", "genai_lab_vs")
INDEX_NAME = f"{CATALOG}.{SCHEMA}.doc_chunks_index"
EMBEDDING_MODEL = os.environ.get("RAG_EMBEDDING_MODEL", "databricks-qwen3-embedding-0-6b")

# --- LLM ---
LLM_ENDPOINT = os.environ.get("RAG_LLM_ENDPOINT", "databricks-meta-llama-3-3-70b-instruct")

# --- Chunking / retrieval ---
CHUNK_SIZE, CHUNK_OVERLAP = 1000, 150
N_CANDIDATES = 40     # candidatos que trae Vector Search antes del reranker
TOP_K = 4             # chunks que llegan al LLM
RERANK_BATCH = 5      # pasajes por llamada al reranker (lotes pequeños = mejor juicio)
MAX_PER_SOURCE = 2    # máximo de chunks por artículo entre los TOP_K
INTRO_CHUNKS = 2      # chunks _0 y _1 (título/abstract) del artículo principal que se añaden al contexto

REFUSAL = "I don't know"

# --- Correcciones de ingesta ---
TITLE_OVERRIDES = {
    "1-s2.0-S1877050925029461-main.pdf": "A Capsule Network-Based Hybrid Model for Lung Nodule Detection",
    "LungPaper.pdf": "Revisiting Segmentation of Lung Tumors from CT Images",
    "2510.26923v1.pdf": "Scale-Aware Curriculum Learning for Data-Efficient Lung Nodule Detection with YOLOv11",
}
SKIP_PAGES = {"LungPaper.pdf": 1}   # páginas iniciales a saltar (portada de ResearchGate)
