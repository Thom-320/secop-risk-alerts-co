# ContratIA Abierta — Punto de entrada para el jurado

> **Concurso Datos al Ecosistema 2026 — IA para Colombia**
> Categoría: Gobernanza y Transparencia · Región demo: Meta y Casanare
> Universidad del Rosario · Ingeniería de Datos

---

## En una frase

IA explicable que **prioriza revisión humana** de la contratación pública colombiana. Convierte miles de procesos SECOP en una cola priorizada y auditable. **No emite juicios de corrupción**; ordena qué revisar primero, con evidencia trazable.

---

## Qué mirar primero (orden recomendado, 10 minutos)

1. **Demo pública** — *URL pendiente de deploy. Para ejecutar localmente, ver "Quickstart" abajo.*
2. **Diapositivas** — [slides/contratia_abierta_deck_v3.pdf](slides/contratia_abierta_deck_v3.pdf) (13 slides, ES).
3. **Tesis ética** — [docs/ethics-note.md](docs/ethics-note.md) (1 página).
4. **Score y límites** — [docs/model-card.md](docs/model-card.md).
5. **Evidencia técnica** — [docs/testing_evidence.md](docs/testing_evidence.md) — 71 tests pasan, 17.229 procesos cargados.

---

## Quickstart (5 minutos en una máquina limpia)

```bash
# Requiere: Python 3.11, uv, Docker (opcional para ruta full-stack)
git clone https://github.com/Thom-320/secop-risk-alerts-co.git
cd secop-risk-alerts-co
uv sync --python 3.11 --extra dev

# Ruta lean — sin base de datos, datos versionados de muestra
make product-pipeline      # ETL + scoring (≈30s con fixtures)
make validate-product      # validador automático
make product-api &         # API en :8000
make dashboard             # Dash UI en :8050
```

Visita:
- API health: http://localhost:8000/health
- Dashboard: http://localhost:8050

### Ruta full-stack (evidencia académica de ingeniería)

```bash
make demo-full             # Docker Compose: Postgres + Mongo + 3 servicios + Dash
make validate-final        # exige PG + Mongo + healthchecks vivos
```

---

## Cómo cumple los criterios del concurso

| Criterio | Evidencia |
|---|---|
| **Uso de datos abiertos** | 4 datasets oficiales SECOP/PAA/AGR vía Socrata. Ver [docs/data-cards/](docs/data-cards/). |
| **IA aplicada** | Score híbrido: reglas + desviación contra pares + IsolationForest + confianza. Matching semántico TF-IDF (embeddings activables). [docs/model-card.md](docs/model-card.md). |
| **Rigor técnico** | PostgreSQL 33 objetos, MongoDB 5 colecciones, 71 tests, 3 servicios FastAPI, validación reproducible. |
| **Impacto y escalabilidad** | Demo Meta+Casanare; pipeline horizontal escalable por departamento. Costo marginal mínimo. |
| **Ética y trazabilidad** | Disclaimers persistentes, model card, contexto fiscal no entra al modelo, exports auditable. |
| **Reproducibilidad** | `make product-pipeline && make validate-product` desde clone limpio. |
| **Comunicación** | Diapositivas, README, model card, data cards, ethics note. |

---

## Despliegue público con un click

```bash
# Render Blueprint listo. Tras git push:
# 1) https://dashboard.render.com/select-repo?type=blueprint
# 2) Conecta este repo. Render lee render.yaml automáticamente.
# 3) Apply. Free tier.
```

Resultado: `https://contratia-api.onrender.com/health` + `https://contratia-dashboard.onrender.com`.

---

## Repo: navegación rápida

```
.
├── CONTEST_SUBMISSION.md           ← este archivo
├── README.md                       ← README técnico completo
├── Dockerfile                      ← imagen production-ready
├── render.yaml                     ← deploy Render con 1 click
├── Makefile                        ← orquestación reproducible
├── pyproject.toml                  ← deps gestionadas con uv
│
├── src/                            ← ruta lean del producto
│   ├── extract/secop_api.py        ← Socrata SODA + fallback Parquet
│   ├── transform/build_process_master.py
│   ├── scoring/score_processes.py  ← score + matching + comparables
│   ├── features/process_features.py
│   ├── api/main.py                 ← FastAPI lean read-only
│   └── app/streamlit_app.py        ← UI alterna (fallback)
│
├── services/                       ← ruta full-stack académica
│   ├── contracts_service/main.py   ← :8001
│   ├── risk_service/main.py        ← :8002
│   └── analytics_service/main.py   ← :8003
│
├── dashboard/dash_app.py           ← UI oficial Dash
├── db/migrations/                  ← schema PostgreSQL completo
├── sql/                            ← vistas analíticas, window functions, CTE
├── etl/                            ← pipeline full-stack
│
├── tests/                          ← 71 tests pytest
│
├── docs/
│   ├── arquitectura.md
│   ├── model-card.md
│   ├── ethics-note.md
│   ├── testing_evidence.md
│   ├── data-cards/                 ← una ficha por dataset
│   ├── claude_design_slides_brief.md
│   └── claude_design_prompt.md
│
└── slides/
    ├── contratia_abierta_deck_v3.pdf   ← entregable del concurso
    └── contratia_abierta_deck_v3.pptx
```

---

## Estado y honestidad

**Listo:**
- ✓ 71 tests pasan, lint estable
- ✓ ETL reproducible con fixtures versionables
- ✓ 17.229 procesos cargados en demo (Meta + Casanare)
- ✓ Schema PostgreSQL con triggers, CTE, window functions, vistas
- ✓ 3 microservicios FastAPI con `/health` 200
- ✓ UI Dash oficial + API lean
- ✓ Documentación: model card, data cards, ethics note, validación
- ✓ Dockerfile + render.yaml para deploy público

**Pendiente (parte del roadmap, no oculto):**
- ○ Validación humana de 100 casos con dos revisores (protocolo definido)
- ○ Benchmark embeddings vs TF-IDF en goldset manual (backend ya activable)
- ○ Despliegue público read-only (Blueprint listo, falta `git push` + apply)
- ○ Sesiones de usabilidad con 5 usuarios reales

Esto es honesto a propósito: la rúbrica del concurso premia más una validación pendiente declarada que una validación inventada.

---

## Contacto

- Repo: `github.com/Thom-320/secop-risk-alerts-co`
- Estudiante: Thomas Chisica · `chisicathomas@gmail.com`
- Director del proyecto: Ingeniería de Datos, Universidad del Rosario
- Licencia código: MIT · Licencias datos: heredan CC_40_BY_SA de cada dataset SECOP
