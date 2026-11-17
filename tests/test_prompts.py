from rag_lab.prompts import DEFAULT_PROMPT, PROMPTS

# `replace` literales del notebook original (celdas 30 y 34), aplicados sobre v3.
V4_OLD = "- If the context does not contain the answer, reply exactly: I don't know"
V4_NEW = (
    "- You may combine information from several chunks of the SAME paper.\n"
    "- If the context answers only part of the question, answer that part and say what is missing.\n"
    "- When the paper reports differences in percentage points, write 'pp', not '%'.\n"
    "- Reply exactly 'I don't know' only if the context contains nothing that answers the question.")
V5_OLD = "- Reply exactly 'I don't know'"
V5_NEW = (
    "- The 'Paper:' title and the chunks identify the study. If they match the study in the question, answer directly; "
    "do not remark that some detail of the question (a region, a dataset name) is not mentioned in the context.\n"
    "- Reply exactly 'I don't know'")


def test_los_replace_cambian_el_texto():
    assert V4_OLD in PROMPTS["v3"]
    v4 = PROMPTS["v3"].replace(V4_OLD, V4_NEW)
    assert v4 != PROMPTS["v3"]
    assert V5_OLD in v4
    assert v4.replace(V5_OLD, V5_NEW) != v4


def test_v4_igual_a_replace_sobre_v3():
    assert PROMPTS["v4"] == PROMPTS["v3"].replace(V4_OLD, V4_NEW)


def test_v5_igual_a_replace_sobre_v4():
    esperado = PROMPTS["v3"].replace(V4_OLD, V4_NEW).replace(V5_OLD, V5_NEW)
    assert PROMPTS["v5"] == esperado


def test_todos_contienen_la_negativa():
    for nombre, texto in PROMPTS.items():
        assert "I don't know" in texto, nombre


def test_versiones_y_default():
    assert list(PROMPTS) == ["v2", "v3", "v4", "v5"]
    assert DEFAULT_PROMPT == "v5"
    assert len(set(PROMPTS.values())) == 4
