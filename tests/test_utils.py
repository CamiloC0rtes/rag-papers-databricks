import copy

from rag_lab.utils import (add_intro_chunks, chunk_num, parse_scores, question_kind, select_top,
                           short_id, strip_title)


# --- strip_title / short_id / chunk_num ---
def test_strip_title_quita_prefijo():
    assert strip_title("Paper: Mi titulo\n\nTexto del chunk") == "Texto del chunk"


def test_strip_title_sin_separador_devuelve_igual():
    assert strip_title("sin prefijo") == "sin prefijo"


def test_strip_title_conserva_parrafos_posteriores():
    assert strip_title("Paper: T\n\nA\n\nB") == "A\n\nB"


def test_short_id():
    assert short_id("archivo.pdf_136") == "_136"


def test_short_id_extension_mayuscula():
    assert short_id("archivo.PDF_7") == "_7"


def test_short_id_nombre_con_guiones_bajos():
    assert short_id("mi_archivo_v2.pdf_12") == "_12"


def test_chunk_num():
    assert chunk_num("archivo.pdf_136") == 136
    assert chunk_num("a_b.pdf_0") == 0


# --- parse_scores ---
def test_parse_scores_lista_valida():
    assert parse_scores("[0, 7, 2, 0, 9]", 5) == [0, 7, 2, 0, 9]


def test_parse_scores_lista_corta_rellena_con_ceros():
    assert parse_scores("[3, 4]", 5) == [3, 4, 0, 0, 0]


def test_parse_scores_lista_larga_recorta():
    assert parse_scores("[1, 2, 3, 4, 5, 6]", 3) == [1, 2, 3]


def test_parse_scores_texto_alrededor():
    assert parse_scores("Claro, aqui va: [1, 8, 3]\nEspero que sirva.", 3) == [1, 8, 3]


def test_parse_scores_sin_lista():
    assert parse_scores("no hay nada", 3) is None


def test_parse_scores_json_invalido():
    assert parse_scores("[1, 2,, 3]", 3) is None


def test_parse_scores_elementos_no_numericos():
    assert parse_scores('["a", 2]', 2) is None
    assert parse_scores("[null, 2]", 2) is None


def test_parse_scores_bool_no_cuenta_como_numero():
    assert parse_scores("[true, 2]", 2) is None


def test_parse_scores_acepta_floats():
    assert parse_scores("[0.5, 7]", 2) == [0.5, 7]


# --- select_top ---
def _d(cid, src):
    return {"chunk_id": cid, "source": src, "content": "c"}


def test_select_top_limite_por_articulo():
    ranked = [_d("a_0", "a"), _d("a_1", "a"), _d("a_2", "a"), _d("b_0", "b"), _d("a_3", "a"), _d("c_0", "c")]
    top = select_top(ranked, k=4, max_per_source=2)
    assert [d["chunk_id"] for d in top] == ["a_0", "a_1", "b_0", "c_0"]


def test_select_top_sin_limite():
    ranked = [_d("a_0", "a"), _d("a_1", "a"), _d("a_2", "a")]
    assert len(select_top(ranked, k=3, max_per_source=None)) == 3
    assert len(select_top(ranked, k=3, max_per_source=0)) == 3


def test_select_top_corta_en_k():
    ranked = [_d(f"s{i}_0", f"s{i}") for i in range(10)]
    assert len(select_top(ranked, k=4, max_per_source=2)) == 4


def test_select_top_preserva_orden():
    ranked = [_d("z_0", "z"), _d("a_0", "a"), _d("m_0", "m")]
    assert [d["chunk_id"] for d in select_top(ranked, k=3, max_per_source=2)] == ["z_0", "a_0", "m_0"]


def test_select_top_menos_candidatos_que_k():
    assert len(select_top([_d("a_0", "a")], k=4, max_per_source=2)) == 1


# --- add_intro_chunks ---
BY_ID = {f"p.pdf_{n}": {"chunk_id": f"p.pdf_{n}", "source": "p.pdf", "content": f"intro {n}"} for n in range(5)}
BY_ID.update({"q.pdf_0": {"chunk_id": "q.pdf_0", "source": "q.pdf", "content": "otro"}})


def test_add_intro_chunks_anade_0_y_1_del_primer_articulo():
    top = [_d("p.pdf_30", "p.pdf"), _d("q.pdf_5", "q.pdf")]
    out = add_intro_chunks(top, BY_ID, 2)
    assert [d["chunk_id"] for d in out] == ["p.pdf_30", "q.pdf_5", "p.pdf_0", "p.pdf_1"]
    assert out[2]["content"] == "intro 0"


def test_add_intro_chunks_no_duplica():
    top = [_d("p.pdf_1", "p.pdf"), _d("p.pdf_9", "p.pdf")]
    out = add_intro_chunks(top, BY_ID, 2)
    assert [d["chunk_id"] for d in out] == ["p.pdf_1", "p.pdf_9", "p.pdf_0"]


def test_add_intro_chunks_no_muta_la_entrada():
    top = [_d("p.pdf_30", "p.pdf")]
    copia = copy.deepcopy(top)
    out = add_intro_chunks(top, BY_ID, 2)
    assert top == copia
    assert out is not top


def test_add_intro_chunks_cero_no_anade():
    top = [_d("p.pdf_30", "p.pdf")]
    assert add_intro_chunks(top, BY_ID, 0) == top


def test_add_intro_chunks_lista_vacia():
    assert add_intro_chunks([], BY_ID, 2) == []


def test_add_intro_chunks_ignora_los_que_no_existen():
    top = [_d("zzz.pdf_4", "zzz.pdf")]
    assert add_intro_chunks(top, BY_ID, 2) == top


# --- question_kind ---
def test_question_kind():
    assert question_kind({"q": "x", "src": "a"}) == "específica"
    assert question_kind({"q": "x", "src": None}) == "global"
    assert question_kind({"q": "x", "src": None, "kind": "ambigua"}) == "ambigua"
