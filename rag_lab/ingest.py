"""Ingesta: PDFs del Volume -> chunks con título -> tabla Delta (MERGE)."""

import os

from rag_lab.clients import get_spark
from rag_lab.config import (CATALOG, CHUNK_OVERLAP, CHUNK_SIZE, CHUNKS_TABLE, SCHEMA, SKIP_PAGES,
                            TITLE_OVERRIDES, VOLUME_NAME, VOLUME_PATH)


def ensure_schema_and_volume():
    """Crea el schema y el Volume si no existen."""
    spark = get_spark()
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA}")
    spark.sql(f"CREATE VOLUME IF NOT EXISTS {CATALOG}.{SCHEMA}.{VOLUME_NAME}")


def get_title(reader, fname):
    """Título del artículo: override manual > metadatos del PDF > primera línea larga de la página 1."""
    if fname in TITLE_OVERRIDES:
        return TITLE_OVERRIDES[fname]
    t = (reader.metadata.title if reader.metadata else None) or ""
    if len(t.strip()) < 15:
        first = (reader.pages[0].extract_text() or "").strip().split("\n")
        t = next((l for l in first if len(l.strip()) > 25), fname)
    return t.strip()[:200]


def extract_text(reader, fname):
    pages = reader.pages[SKIP_PAGES.get(fname, 0):]
    return "\n".join(p.extract_text() or "" for p in pages)


def build_chunks(path=VOLUME_PATH, verbose=True):
    """Lee todos los PDFs del Volume y devuelve filas (chunk_id, source, title, content)."""
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from pypdf import PdfReader

    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    rows = []
    for f in sorted(os.listdir(path)):
        if not f.lower().endswith(".pdf"):
            continue
        reader = PdfReader(path + f)
        title = get_title(reader, f)
        chunks = splitter.split_text(extract_text(reader, f))
        rows += [(f"{f}_{i}", f, title, f"Paper: {title}\n\n{c}") for i, c in enumerate(chunks)]
        if verbose:
            print(f"{len(chunks):4d} chunks | {f[:40]:40} -> {title[:70]}")
    return rows


def upsert_chunks(rows):
    """Escribe los chunks con MERGE (inserta, actualiza y borra los que ya no existen)."""
    spark = get_spark()
    df = spark.createDataFrame(rows, "chunk_id string, source string, title string, content string")
    if not spark.catalog.tableExists(CHUNKS_TABLE):
        df.write.saveAsTable(CHUNKS_TABLE)
        spark.sql(f"""ALTER TABLE {CHUNKS_TABLE} SET TBLPROPERTIES (
            delta.enableChangeDataFeed = true,
            'delta.deletedFileRetentionDuration' = 'interval 30 days')""")
    else:
        df.createOrReplaceTempView("new_chunks")
        spark.sql(f"""
            MERGE INTO {CHUNKS_TABLE} t USING new_chunks s ON t.chunk_id = s.chunk_id
            WHEN MATCHED AND (t.content <> s.content OR t.title <> s.title OR t.source <> s.source)
              THEN UPDATE SET *
            WHEN NOT MATCHED THEN INSERT *
            WHEN NOT MATCHED BY SOURCE THEN DELETE""")
    n = spark.table(CHUNKS_TABLE).count()
    print(f"Tabla {CHUNKS_TABLE}: {n} chunks")
    return n
