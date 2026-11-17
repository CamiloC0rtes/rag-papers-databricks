"""Generación: cadena RAG con prompt versionado."""

import mlflow

from rag_lab.prompts import DEFAULT_PROMPT, PROMPTS
from rag_lab.retrieval import call_llm, retrieve


def make_rag(prompt_version=DEFAULT_PROMPT, **retrieve_kwargs):
    """make_rag() = v6. Variantes: make_rag("v4"), make_rag(intro_chunks=0), make_rag(max_per_source=None), make_rag(n_candidates=20, rerank_bs=10)."""
    system_prompt = PROMPTS[prompt_version]

    @mlflow.trace(span_type="CHAIN", name=f"rag_{prompt_version}")
    def rag(question):
        docs = retrieve(question, **retrieve_kwargs)
        context = "\n\n".join(f"[{d.metadata['chunk_id']}]\n{d.page_content}" for d in docs)
        return call_llm([{"role": "system", "content": system_prompt},
                         {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}],
                        max_tokens=400)
    return rag
