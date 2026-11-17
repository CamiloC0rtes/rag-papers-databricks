# Corpus

Los PDFs **no se incluyen en el repo** (`*.pdf` está en `.gitignore`). Se suben manualmente al Volume de Unity Catalog
(por defecto `/Volumes/test/genai_lab/raw_docs/`). El corpus original tiene 12 papers y genera 1112 chunks.

La columna "Fragmento" es el texto del nombre de archivo que usan los casos de evaluación (`src` en `eval/cases.json`)
para identificar el artículo. Los títulos en inglés son los de `TITLE_OVERRIDES` en `rag_lab/config.py`; para el resto,
la fuente solo documenta el tema (en español).

| Fragmento del archivo | Tema / título | Enlace |
|---|---|---|
| `AI-Powered` | VGG16 vs arquitecturas CNN para cáncer de pulmón en TC | TODO(Juan) |
| `1-s2.0-S1877050925029461-main.pdf` | A Capsule Network-Based Hybrid Model for Lung Nodule Detection | TODO(Juan) |
| `2510.26923v1.pdf` | Scale-Aware Curriculum Learning for Data-Efficient Lung Nodule Detection with YOLOv11 | https://arxiv.org/abs/2510.26923 |
| `2602.10481` | Prompts y contexto autenticados en aplicaciones LLM | https://arxiv.org/abs/2602.10481 |
| `Assessment of Machine` | Clasificación de cobertura del suelo en Gilgit-Baltistan | TODO(Juan) |
| `NSCLC` | Subtipos de NSCLC a partir del microbioma pulmonar | TODO(Juan) |
| `Deep learning-based approach` | Diagnóstico de cáncer de pulmón con imágenes de TC (Enhanced CNN) | TODO(Juan) |
| `Land-Cover Classification Using` | Cobertura del suelo con imágenes de alta resolución (Inception-v3, DenseNet121) | TODO(Juan) |
| `LungPaper.pdf` | Revisiting Segmentation of Lung Tumors from CT Images (dataset LOTUS) | TODO(Juan) |
| `fmed` | Comparación de versiones de YOLO para cáncer de pulmón (Lung-PET-CT-Dx) | TODO(Juan) |
| `Gelephu` | LULC y NDVI en Gelephu, Bután | TODO(Juan) |
| `2404.03936` | Revisión de deep learning para series temporales de imágenes satelitales | https://arxiv.org/abs/2404.03936 |
