"""Funciones puras (solo biblioteca estándar): no importa mlflow, pyspark, openai ni databricks."""

import json
import re


def strip_title(content):
    """Quita el prefijo 'Paper: <título>' de un chunk."""
    return content.split("\n\n", 1)[-1]


def short_id(chunk_id):
    """'archivo.pdf_136' -> '_136'"""
    return "_" + chunk_id.rsplit("_", 1)[-1]


def chunk_num(chunk_id):
    """'archivo.pdf_136' -> 136 (número de chunk dentro del artículo)."""
    return int(re.search(r"_(\d+)$", chunk_id).group(1))


def parse_scores(txt, n):
    """Extrae la primera lista JSON de `txt` y la ajusta a `n` elementos (relleno con ceros o recorte).
    Devuelve None si no hay lista, el JSON es inválido o algún elemento no es número (bool no cuenta)."""
    m = re.search(r"\[.*?\]", txt, re.S)
    if not m:
        return None
    try:
        s = json.loads(m.group())
    except Exception:
        return None
    if not isinstance(s, list):
        return None
    if any(isinstance(x, bool) or not isinstance(x, (int, float)) for x in s):
        return None
    return (s + [0] * n)[:n]


def select_top(ranked, k, max_per_source):
    """Toma los primeros `k` de `ranked` (dicts con 'source') con un máximo de `max_per_source` por artículo
    (None o 0 = sin límite). Conserva el orden de `ranked`."""
    top, per = [], {}
    for d in ranked:
        if max_per_source and per.get(d["source"], 0) >= max_per_source:
            continue
        top.append(d)
        per[d["source"]] = per.get(d["source"], 0) + 1
        if len(top) == k:
            break
    return top


def add_intro_chunks(top, by_id, intro_chunks):
    """Añade al final los chunks _0 … _{n-1} del artículo del primer resultado si no están ya.
    `by_id`: dict chunk_id -> {"chunk_id", "source", "content"}. No modifica `top`."""
    top = list(top)
    if intro_chunks and top:
        src, have = top[0]["source"], {d["chunk_id"] for d in top}
        for n in range(intro_chunks):
            r = by_id.get(f"{src}_{n}")
            if r and r["chunk_id"] not in have:
                top.append({"chunk_id": r["chunk_id"], "source": r["source"], "content": r["content"]})
    return top


def question_kind(case):
    """Tipo de pregunta: el 'kind' explícito o, si no hay, 'específica' (con src) / 'global' (sin src)."""
    return case.get("kind") or ("específica" if case["src"] else "global")
