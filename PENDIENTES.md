# Pendientes

Cosas que solo se pueden hacer o decidir en el workspace de Databricks, o que la fuente no documenta.

- [x] **Ejecutar los notebooks 01 a 03 de punta a punta en Databricks** (16-nov-2026). La celda `%pip install` + `restartPython()` funciona. Se corrigió `ensure_index()`, que bloqueaba el notebook 01 tras re-ingerir.
- [x] **Confirmar que el refactor conserva el comportamiento medido**: una corrida de v6 dio correctness 0.909 (set de 44 + 10), igual que el notebook original.
- [ ] **Fijar versiones**: `pip freeze` en el cluster y copiar las versiones a `requirements.txt` (hoy no tienen versión, salvo `mlflow>=3`). La re-ingesta del 16-nov dio 1111 chunks frente a 1112 del original, probablemente por esto. TODO(Juan)
- [ ] **Completar enlaces y DOI** de los papers en `data/README.md` (solo los tres de arXiv están enlazados). TODO(Juan)
- [ ] **Migrar dependencias deprecadas** (avisos del notebook): `databricks-vectorsearch` -> `databricks-ai-search`, y `get_open_ai_client()` -> paquete `databricks-openai` (`DatabricksOpenAI`). Se mantuvieron las actuales porque son las probadas.
- [ ] **Crear el endpoint de Vector Search** a mano en la UI (el repo no lo crea por código).
- [ ] **Si se sube el notebook original, limpiar sus outputs antes**: contienen texto de los papers, IDs de trazas y rutas con el correo.
- [ ] **Métricas que no quedaron registradas**: v4 y v4-div2 (y v3 con el caso SACL corregido). Si interesan, volver a correrlas.
- [ ] **Configuración exacta de `v5-rr2`**: el notebook solo la cita en un comentario; no quedó documentada. TODO(Juan)
- [ ] **Discrepancia de un comentario**: el notebook decía que v2 "dio correctness 0.83", pero las métricas registradas dicen 0.87 (v2) y 0.826 (v3). `docs/experimentos.md` usa las registradas.
- [ ] **Motivo de dos correcciones al set** (nuevo 0 y tercer hecho de ResNet-50): el notebook registra el cambio sin explicarlo; confirmar o corregir la explicación de `docs/experimentos.md`. TODO(Juan)

## Ideas de mejora

- Manejo de preguntas ambiguas (hoy 0 a 0.33 de correctness).
- Reducir las llamadas del reranker (hoy 8 por pregunta).
- Ampliar el set de evaluación (con 44 preguntas, cada una mueve la correctness 0.023).
