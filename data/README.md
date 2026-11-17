# Corpus

Los PDFs **no se incluyen en el repo** (`*.pdf` está en `.gitignore`). Se descargan de los enlaces de abajo y se suben
manualmente al Volume de Unity Catalog (por defecto `/Volumes/test/genai_lab/raw_docs/`). Con las versiones de
`requirements.txt`, los 12 papers generan 1111 chunks.

La columna "Fragmento" es el texto del nombre de archivo que usan los casos de evaluación (`src` en `eval/cases.json`)
para identificar el artículo, así que los PDFs deben conservar un nombre que lo contenga.

| Fragmento del archivo | Paper | Publicación | Enlace |
|---|---|---|---|
| `AI-Powered` | AI-Powered Lung Cancer Detection: Assessing VGG16 and CNN Architectures for CT Scan Image Classification | Informatics 12, 18 (2025) | https://doi.org/10.3390/informatics12010018 |
| `1-s2.0-S1877050925029461-main.pdf` | A Capsule Network-Based Hybrid Model for Lung Nodule Detection | Procedia Computer Science (2025) | https://www.sciencedirect.com/science/article/pii/S1877050925029461 |
| `2510.26923v1.pdf` | Scale-Aware Curriculum Learning for Data-Efficient Lung Nodule Detection with YOLOv11 | arXiv (2025) | https://arxiv.org/abs/2510.26923 |
| `2602.10481` | Protecting Context and Prompts: Deterministic Security for Non-Deterministic AI | arXiv (2026) | https://arxiv.org/abs/2602.10481 |
| `Assessment of Machine` | Assessment of Machine Learning Algorithms for Land Cover Classification in a Complex Mountainous Landscape | J. Geovisualization and Spatial Analysis 8, 34 (2024) | https://doi.org/10.1007/s41651-024-00195-z |
| `NSCLC` | Classification of NSCLC subtypes using lung microbiome from resected tissue based on machine learning methods | npj Systems Biology and Applications 11 (2025) | https://doi.org/10.1038/s41540-025-00491-4 |
| `Deep learning-based approach` | Deep learning-based approach to diagnose lung cancer using CT-scan images | Intelligence-Based Medicine 11, 100188 (2025) | https://doi.org/10.1016/j.ibmed.2024.100188 |
| `Land-Cover Classification Using` | Land-Cover Classification Using Deep Learning with High-Resolution Remote-Sensing Imagery | Applied Sciences 14(5), 1844 (2024) | https://doi.org/10.3390/app14051844 |
| `LungPaper.pdf` | Revisiting Segmentation of Lung Tumors from CT Images | Computers in Biology and Medicine 144, 105385 (2022) | https://doi.org/10.1016/j.compbiomed.2022.105385 |
| `fmed` | Deep learning object detection-based early detection of lung cancer | Frontiers in Medicine 12, 1567119 (2025) | https://doi.org/10.3389/fmed.2025.1567119 |
| `Gelephu` | Utilizing Sentinel-2 Satellite Imagery for LULC and NDVI Change Dynamics for Gelephu, Bhutan | Applied Sciences 14(4), 1578 (2024) | https://doi.org/10.3390/app14041578 |
| `2404.03936` | Deep Learning for Satellite Image Time Series (revisión) | arXiv (2024) | https://arxiv.org/abs/2404.03936 |

El enlace del paper de Procedia Computer Science usa el identificador PII que aparece en el nombre del archivo.
