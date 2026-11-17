# Experimentos: de v2 a v6

Todas las cifras salen de las métricas registradas en el notebook original (MLflow). Donde no quedó métrica registrada,
se dice así. Los jueces son LLM, así que hay ruido entre corridas: con 23 preguntas, cada una mueve la correctness 0.043.

## Línea de tiempo

| Fecha (2026) | Qué se corrió | Set |
|---|---|---|
| 4-nov | prompts v2 y v3 | 23 del dominio + 5 fuera de tema |
| 12-nov | v5-rr2 y v6 | 23 del dominio + 5 fuera de tema (set corregido) |
| 12-13-nov | v6 x3 y c20b10 x2 | 44 del dominio + 10 fuera de tema |

## v2 y v3 (4-nov)

Se compararon con el índice limpio sobre las 23 preguntas originales y 5 fuera de tema.

| Prompt | correctness | retrieval_relevance | retrieval_groundedness | relevance_to_query | ood_correctness |
|---|---|---|---|---|---|
| v2 | 0.87 | 0.652 | 0.913 | 0.957 | 1.0 |
| v3 | 0.826 | 0.641 | 0.913 | 0.957 | 1.0 |

- **v2**: responder solo con el contexto, 1-3 frases, usar solo el paper de la pregunta, citar chunk_ids y negarse con `I don't know`.
- **v3**: añade el manejo de preguntas ambiguas (dar cada respuesta con el título de su paper), ignorar trabajo relacionado y copiar nombres y números exactos.
- Con v3 la correctness bajó respecto a v2 (0.87 a 0.826). Después se usaron `show_failures` y `retrieval_probe` para diagnosticar los fallos.
- Nota: un comentario del notebook decía que v2 "dio correctness 0.83"; las métricas registradas dicen 0.87 para v2 y 0.826 (redondeado, 0.83) para v3. Aquí se usan las registradas.

## v4

Cambios de prompt respecto a v3: permitir combinar chunks del mismo paper; responder la parte contestable y decir qué falta;
escribir `pp` (no `%`) para diferencias en puntos porcentuales; reservar `I don't know` para cuando el contexto no contiene nada
que responda. Además se añadió el parámetro `max_per_source` al retriever (máximo de chunks por artículo).

Se corrieron `v3` (línea base con el caso SACL ya corregido), `v4` (solo cambia el prompt) y `v4-div2` (prompt v4 y `max_per_source=2`).
**Las métricas de estas tres corridas no quedaron registradas.**

## v5-rr2 y v6 (12-nov)

- **Prompt v5** = v4 + no poner reparos cuando el título del paper ya identifica el estudio (por ejemplo, objetar que una región o un nombre de dataset no aparece en el contexto).
- **Reranker que ve el título**: el prompt del reranker incluye `Paper: <título>`, trunca cada pasaje a 1100 caracteres y puntúa 0 los pasajes de un artículo distinto al de la pregunta.
- **Chunks de introducción**: se añaden `_0` y `_1` del artículo principal; tamaño de lote del reranker configurable (`rerank_bs`).

Resultados registrados en el notebook (23 del dominio + 5 fuera de tema, set corregido):

| Configuración | correctness | groundedness | relevance | retrieval_relevance | OOD |
|---|---|---|---|---|---|
| v5-rr2 | 0.870 | 0.913 | 0.957 | 0.527 | 1.0 |
| v6 | 0.957 | 1.000 | 1.000 | 0.422 | 1.0 |

`v5-rr2` se cita tal cual aparece en el comentario del notebook. Su configuración exacta no quedó documentada y no se reproduce: se conserva solo como referencia histórica, y la configuración vigente es v6.
`retrieval_relevance` baja en v6 porque el juez cuenta los chunks del abstract como no relevantes.

## Set final: v6 x3 y variante barata (12-13-nov)

El set se amplió a 44 preguntas del dominio (23 originales + 21 nuevas, revisadas a mano a partir de borradores del LLM) y 10 fuera de tema.
Las 3 corridas de v6 tardaron 45 min 56 s; las 2 de la variante barata, 19 min 1 s.

| Corrida | correctness | relevance_to_query | retrieval_groundedness | retrieval_relevance | ood_correctness |
|---|---|---|---|---|---|
| v6-r1 | 0.909 | 1.000 | 0.977 | 0.407 | 1.0 |
| v6-r2 | 0.909 | 1.000 | 1.000 | 0.407 | 1.0 |
| v6-r3 | 0.909 | 1.000 | 0.977 | 0.416 | 1.0 |
| c20b10-r1 | 0.818 | 0.955 | 0.909 | 0.426 | 1.0 |
| c20b10-r2 | 0.841 | 0.977 | 0.932 | 0.422 | 0.9 |

`c20b10` = 20 candidatos en lotes de 10 (`make_rag(n_candidates=20, rerank_bs=10)`): 2 llamadas al reranker por pregunta en vez de 8.

Correctness por tipo de pregunta:

| Tipo | v6-r1 | v6-r2 | v6-r3 | c20b10-r1 | c20b10-r2 |
|---|---|---|---|---|---|
| ambigua | 0.333 | 0.333 | 0.000 | 0.000 | 0.000 |
| específica | 0.950 | 0.950 | 0.975 | 0.875 | 0.900 |
| fuera de tema | 1.000 | 1.000 | 1.000 | 1.000 | 0.900 |
| global | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |

Latencia del RAG por pregunta, en segundos (endpoint gratuito, 1 worker):

| Corrida | p50 | p95 | max |
|---|---|---|---|
| v6-r1 | 11.0 | 17.1 | 23.2 |
| v6-r2 | 12.4 | 23.0 | 29.4 |
| v6-r3 | 17.3 | 38.2 | 44.1 |
| c20b10-r1 | 9.1 | 15.6 | 18.9 |
| c20b10-r2 | 8.9 | 15.9 | 20.7 |

La variante barata baja el p50 a ~9 s, pero pierde 7-9 puntos de correctness frente a v6 (0.909).

## Preguntas que fallan de forma recurrente

Número de corridas (de 5) en que falló correctness:

| Fallos | Corridas | Pregunta |
|---|---|---|
| 5 | todas | What test accuracy did ResNet50 obtain? |
| 5 | todas | Which studies used the Lung-PET-CT-Dx dataset? |
| 4 | v6-r1, v6-r2, c20b10-r1, c20b10-r2 | In the YOLO and Capsule Network hybrid study for lung nodule detection, what overall accuracy did the proposed hybrid model achieve? |
| 4 | v6-r1, v6-r2, v6-r3, c20b10-r2 | What performance overhead do the authenticated prompts and authenticated context defenses introduce? |
| 3 | v6-r3, c20b10-r1, c20b10-r2 | What test accuracy did InceptionV3 obtain? |
| 2 | c20b10-r1, c20b10-r2 | In the study assessing VGG16 and CNN architectures for CT scan classification, what test accuracy did InceptionV3 obtain? |
| 1 | c20b10-r1 | In the YOLO-CapsNet hybrid study, what F1-score did the Cropped Image CapsNet obtain? |
| 1 | c20b10-r2 | What dice coefficient did MultiResUNet achieve on the BraTS brain tumor dataset? (fuera de tema) |
| 1 | c20b10-r1 | What limitation do 2D images have compared to 3D CNNs for CT analysis? |
| 1 | c20b10-r2 | What percentage of the Gilgit-Baltistan area was classified as barren land by the random forest map? |
| 1 | c20b10-r1 | Which public dataset was used to train and evaluate the YOLO models in the YOLO comparison study for lung cancer detection? |

## Correcciones al set de evaluación

Se aplicaron sobre los casos originales y los nuevos; `verify_cases` comprueba que las respuestas esperadas existen en los chunks:

| Caso | Corrección | Motivo |
|---|---|---|
| SACL (mejoras sobre el baseline) | `facts` y `keys` pasan a la forma relativa: "about 4.6%, 3.5% and 2.0%" y claves `4.6%`, `3.5%` | El abstract reporta la forma relativa. |
| Land-cover (arquitecturas con transfer learning) | Dos hechos separados: Inception-v3 y DenseNet121 | El paper también propone ResNet-50 (sección 2.5), así que se piden los dos modelos del abstract como hechos separados. |
| "What test accuracy did InceptionV3 obtain?" | `kind` = ambigua | Dos artículos responden (88.79% y 76.9%). |
| Nuevo 0: accuracy global del híbrido YOLO-CapsNet | `facts` pasa a "The three-stage YOLO-CapsNet-YOLO pipeline achieved an overall detection accuracy of 89.98%" | El hecho se reformula para describir la cifra como lo hace el paper: es la accuracy de detección del pipeline completo de tres etapas, no la de un modelo aislado. Esta pregunta sigue entre las que más fallan. |
| Nuevo 18 (dataset del estudio de comparación YOLO) y nuevo 20 (estudios que usaron Lung-PET-CT-Dx) | `keys` = `Lung-PET-CT-` | El PDF parte el nombre: 'Lung-PET-CT- Dx'. |
| Nuevo 19 (ResNet50, ambigua) | Se añade un tercer hecho: ResNet-50 con 93% de accuracy en el estudio de land-cover | La pregunta es ambigua a propósito y el paper de land-cover también reporta ResNet-50 (sección 2.5), así que una respuesta completa debe incluirlo. |
