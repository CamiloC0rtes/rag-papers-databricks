import json
from collections import Counter
from pathlib import Path

import pytest

CASES = Path(__file__).resolve().parents[1] / "eval" / "cases.json"


@pytest.fixture(scope="module")
def data():
    return json.loads(CASES.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def by_q(data):
    return {c["q"]: c for c in data["in_domain"]}


def test_cantidades(data):
    assert len(data["in_domain"]) == 44
    assert len(data["out_of_domain"]) == 10
    assert data["refusal"] == "I don't know"


def test_conteo_por_kind(data):
    assert Counter(c["kind"] for c in data["in_domain"]) == {"específica": 40, "ambigua": 3, "global": 1}


def test_sin_preguntas_duplicadas(data):
    qs = [c["q"] for c in data["in_domain"]] + data["out_of_domain"]
    assert len(qs) == len(set(qs)) == 54


def test_campos_no_vacios(data):
    for c in data["in_domain"]:
        assert c["q"].strip()
        assert c["facts"] and all(f.strip() for f in c["facts"]), c["q"]
        assert c["keys"] and all(k.strip() for k in c["keys"]), c["q"]


def test_src_nulo_equivale_a_ambigua_o_global(data):
    for c in data["in_domain"]:
        assert (c["src"] is None) == (c["kind"] in {"ambigua", "global"}), c["q"]


# --- los 7 parches del paso 5 ---
def test_parche_1_sacl(by_q):
    c = by_q["What improvements over baseline did Scale-Adaptive Curriculum Learning (SACL) achieve at 10%, 20% and 50% of the training data?"]
    assert c["facts"] == ["SACL improved over the baseline by about 4.6%, 3.5% and 2.0% at 10%, 20% and 50% of the training data"]
    assert c["keys"] == ["4.6%", "3.5%"]


def test_parche_2_land_cover(by_q):
    c = by_q["Which architectures were used with transfer learning in the land-cover classification study with high-resolution remote-sensing imagery?"]
    assert c["facts"] == ["Inception-v3 was used with transfer learning", "DenseNet121 was used with transfer learning"]


def test_parche_3_inceptionv3_ambigua(by_q):
    assert by_q["What test accuracy did InceptionV3 obtain?"]["kind"] == "ambigua"


def test_parche_4_yolo_capsnet_facts(by_q):
    c = by_q["In the YOLO and Capsule Network hybrid study for lung nodule detection, what overall accuracy did the proposed hybrid model achieve?"]
    assert c["facts"] == ["The three-stage YOLO-CapsNet-YOLO pipeline achieved an overall detection accuracy of 89.98%"]


def test_parche_5_keys_dataset_yolo(by_q):
    c = by_q["Which public dataset was used to train and evaluate the YOLO models in the YOLO comparison study for lung cancer detection?"]
    assert c["keys"] == ["Lung-PET-CT-"]


def test_parche_6_resnet50_tercer_fact(by_q):
    c = by_q["What test accuracy did ResNet50 obtain?"]
    assert len(c["facts"]) == 3
    assert c["facts"][2] == "ResNet-50 obtained 93% testing accuracy in the land-cover classification study with remote-sensing imagery"


def test_parche_7_keys_estudios_lung_pet_ct(by_q):
    assert by_q["Which studies used the Lung-PET-CT-Dx dataset?"]["keys"] == ["Lung-PET-CT-"]


def test_orden_original_y_nuevos(data):
    qs = [c["q"] for c in data["in_domain"]]
    assert qs[0].startswith("Which architecture was identified as the best for lung cancer detection")
    assert qs[22] == "What test accuracy did InceptionV3 obtain?"
    assert qs[23].startswith("In the YOLO and Capsule Network hybrid study")
    assert qs[-1] == "Which studies used the Lung-PET-CT-Dx dataset?"
    assert data["out_of_domain"][0] == "What is the capital of France?"
    assert data["out_of_domain"][5] == "What is the recommended chemotherapy regimen for lung adenocarcinoma?"
