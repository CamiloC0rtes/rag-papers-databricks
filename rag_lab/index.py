"""Índice vectorial (Vector Search Delta Sync). El endpoint de Vector Search NO se crea por código:
créalo a mano en la UI del workspace (ver README)."""

import time

from rag_lab.clients import get_spark, get_vsc
from rag_lab.config import CHUNKS_TABLE, EMBEDDING_MODEL, INDEX_NAME, VS_ENDPOINT

_idx = None


def index():
    """Devuelve el índice (cacheado)."""
    global _idx
    if _idx is None:
        _idx = get_vsc().get_index(endpoint_name=VS_ENDPOINT, index_name=INDEX_NAME)
    return _idx


def index_status():
    st = index().describe().get("status", {})
    out = {"ready": st.get("ready"), "indexed": st.get("indexed_row_count"),
           "table": get_spark().table(CHUNKS_TABLE).count()}
    out["in_sync"] = bool(out["ready"]) and out["indexed"] == out["table"]
    return out


def wait_for_index(timeout_min=20, every=30):
    """Espera hasta que el índice esté listo y con el mismo número de filas que la tabla."""
    t0 = time.time()
    while time.time() - t0 < timeout_min * 60:
        s = index_status()
        print(f"ready={s['ready']} indexed={s['indexed']} table={s['table']}")
        if s["in_sync"]:
            return s
        time.sleep(every)
    print("⚠️ Timeout. Si 'indexed' no coincide con 'table', usa recreate_index().")
    return index_status()


def sync_index():
    """Sincroniza el índice (pipeline TRIGGERED) y espera a que termine."""
    index().sync()
    return wait_for_index()


def create_index():
    """Crea el índice Delta Sync sobre la tabla de chunks (pipeline TRIGGERED, embeddings gestionados)."""
    global _idx
    get_vsc().create_delta_sync_index(
        endpoint_name=VS_ENDPOINT, index_name=INDEX_NAME, source_table_name=CHUNKS_TABLE,
        pipeline_type="TRIGGERED", primary_key="chunk_id",
        embedding_source_column="content", embedding_model_endpoint_name=EMBEDDING_MODEL)
    _idx = None


def index_exists():
    """True si el índice existe (get_index no lanza excepción)."""
    try:
        get_vsc().get_index(endpoint_name=VS_ENDPOINT, index_name=INDEX_NAME)
        return True
    except Exception:
        return False


def ensure_index():
    """Camino para montar desde cero: crea el índice si no existe y espera a su primera sincronización.
    Si ya existe no espera: tras re-ingerir, la tabla y el índice difieren hasta que se llame sync_index()."""
    if index_exists():
        return index_status()
    create_index()
    return wait_for_index()


def recreate_index(delete_timeout_min=10):
    """Borra y vuelve a crear el índice desde cero. Úsalo si quedan filas viejas (indexed > table)."""
    global _idx
    vsc = get_vsc()
    vsc.delete_index(endpoint_name=VS_ENDPOINT, index_name=INDEX_NAME)
    t0 = time.time()
    while True:   # esperar a que el borrado termine
        try:
            vsc.get_index(endpoint_name=VS_ENDPOINT, index_name=INDEX_NAME)
        except Exception:
            break
        if time.time() - t0 > delete_timeout_min * 60:
            raise TimeoutError(
                f"El índice {INDEX_NAME} sigue existiendo tras {delete_timeout_min} min de espera del borrado. "
                "Revisa su estado en el workspace y vuelve a intentarlo.")
        time.sleep(15)
    create_index()
    _idx = None
    return wait_for_index()
