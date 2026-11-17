"""Retrieval: búsqueda híbrida en Vector Search + reranker con LLM + diversidad por artículo + chunks de introducción."""

import time
import warnings

import mlflow
from mlflow.entities import Document

from rag_lab.clients import get_llm, get_spark
from rag_lab.config import (CHUNKS_TABLE, INTRO_CHUNKS, LLM_ENDPOINT, MAX_PER_SOURCE, N_CANDIDATES,
                            RERANK_BATCH, TOP_K)
from rag_lab.index import index
from rag_lab.utils import add_intro_chunks, parse_scores, select_top, short_id, strip_title

# Reranker: el LLM puntúa 0-10 cada pasaje de un lote. Plantilla con {question}, {listing} y {n}.
RERANK_PROMPT = (
    "Question: {question}\n\nPassages:\n{listing}\n\n"
    "For EACH passage, score 0-10 how likely it contains the exact answer (specific numbers/facts). "
    "Each passage starts with 'Paper: <title>'. If the question refers to a specific study and the "
    "passage belongs to a different paper, score it 0. "
    "Reply with ONLY a JSON list of {n} integers in passage order, e.g. [0, 7, 2, 0, 9]."
)

# Contadores de diagnóstico del reranker (lotes procesados y lotes cuya respuesta no fue JSON válido).
RERANK_STATS = {"batches": 0, "parse_failures": 0}


def call_llm(messages, max_tokens=60, retries=5):
    """Llamada al LLM con reintentos ante el límite de QPS (429)."""
    from openai import RateLimitError
    llm = get_llm()
    for a in range(retries):
        try:
            return llm.chat.completions.create(model=LLM_ENDPOINT, messages=messages,
                                               max_tokens=max_tokens, temperature=0).choices[0].message.content
        except RateLimitError:
            time.sleep(2 ** a)   # 1, 2, 4, 8, 16 s
    raise RuntimeError("Rate limit persistente en el endpoint del LLM")


def search(question, k=N_CANDIDATES, query_type="HYBRID", filters=None):
    """Búsqueda en Vector Search. Devuelve dicts con chunk_id, source, content y score."""
    kw = dict(query_text=question, columns=["chunk_id", "source", "content"],
              num_results=k, query_type=query_type, disable_notice=True)
    if filters:
        kw["filters"] = filters
    res = index().similarity_search(**kw)
    return [{"chunk_id": r[0], "source": r[1], "content": r[2], "score": r[-1]}
            for r in res["result"]["data_array"]]


def score_batch(question, batch):
    """Puntúa 0-10 un lote de pasajes según qué tan probable es que contengan la respuesta exacta.
    El reranker ve 'Paper: <título>' y da 0 a los pasajes de otro artículo."""
    listing = "\n\n".join(f"<{i}>\n{d['content'][:1100]}" for i, d in enumerate(batch))
    prompt = RERANK_PROMPT.format(question=question, listing=listing, n=len(batch))
    txt = call_llm([{"role": "user", "content": prompt}])
    RERANK_STATS["batches"] += 1
    s = parse_scores(txt, len(batch))
    if s is None:
        RERANK_STATS["parse_failures"] += 1
        warnings.warn("El reranker no devolvió JSON válido para este lote; se asignan ceros a sus pasajes.")
        return [0] * len(batch)
    return s


@mlflow.trace(span_type="RERANKER")
def llm_rerank(question, docs, top_n=TOP_K, bs=RERANK_BATCH):
    """Reordena candidatos con el LLM. Devuelve [(score, doc)] de los top_n."""
    scores = []
    for i in range(0, len(docs), bs):
        scores += score_batch(question, docs[i:i + bs])
    ranked = sorted(range(len(docs)), key=lambda i: (-scores[i], i))   # empate: orden original
    return [(scores[i], docs[i]) for i in ranked[:top_n]]


# --- Caché de chunks (para los chunks de introducción) ---
_by_id = None


def chunk_cache():
    """dict chunk_id -> {"chunk_id", "source", "content"}, cargado perezosamente desde la tabla de chunks."""
    global _by_id
    if _by_id is None:
        rows = get_spark().table(CHUNKS_TABLE).select("chunk_id", "source", "content").collect()
        _by_id = {r.chunk_id: {"chunk_id": r.chunk_id, "source": r.source, "content": r.content} for r in rows}
    return _by_id


def refresh_chunk_cache():
    """Invalida la caché (llamar tras re-ingerir)."""
    global _by_id
    _by_id = None


@mlflow.trace(span_type="RETRIEVER")
def retrieve(question, k=TOP_K, n_candidates=N_CANDIDATES, rerank=True, query_type="HYBRID",
             max_per_source=MAX_PER_SOURCE, intro_chunks=INTRO_CHUNKS, rerank_bs=RERANK_BATCH):
    """Retriever completo: máximo `max_per_source` chunks por artículo + chunks _0 y _1 (título/abstract)
    del artículo principal. Devuelve Documents para que los jueces de MLflow lean los chunks del trace."""
    cands = search(question, k=n_candidates, query_type=query_type)
    ranked = [d for _, d in llm_rerank(question, cands, top_n=len(cands), bs=rerank_bs)] if rerank else cands
    top = select_top(ranked, k, max_per_source)
    if intro_chunks and top:
        top = add_intro_chunks(top, chunk_cache(), intro_chunks)
    return [Document(page_content=d["content"], metadata={"doc_uri": d["source"], "chunk_id": d["chunk_id"]})
            for d in top]


def retrieval_probe(question, needle, n_candidates=N_CANDIDATES, query_type="HYBRID"):
    """¿Dónde quedan los chunks que contienen `needle`? (entre candidatos y tras el reranker)"""
    cands = search(question, k=n_candidates, query_type=query_type)
    print("en candidatos:", [(i + 1, short_id(c["chunk_id"])) for i, c in enumerate(cands) if needle in c["content"]])
    print("top rerank   :", [(s, short_id(d["chunk_id"]), needle in d["content"]) for s, d in llm_rerank(question, cands)])


def show_context(question, chars=900, **kw):
    for d in retrieve(question, **kw):
        print(f"--- {d.metadata['chunk_id']}\n{strip_title(d.page_content)[:chars]}\n")
