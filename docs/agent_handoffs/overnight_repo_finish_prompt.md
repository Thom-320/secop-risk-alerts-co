# Overnight Orchestrator Prompt: ContratIA Abierta / Transparencia360

`/goal` Work for up to 8 hours as an autonomous orchestrator to finish, audit, and harden the repository `secop-risk-alerts-co` for Universidad del Rosario Data Engineering delivery, public GitHub portfolio quality, and a possible contest/product pitch. Use subagents or specialist lanes where available. Return a concise final report with exact commands, files changed, validation evidence, blockers, and next human-only tasks.

## Repository

- Local path: `/Users/thom/Desktop/IA colombia/secop-risk-alerts-co`
- GitHub: `https://github.com/Thom-320/secop-risk-alerts-co`
- Current branch: `main`
- Current pushed commit before this overnight pass: `0423fdc` (`Finalize reproducible delivery flow`)

## Product

Primary product name:

**ContratIA Abierta**

Portfolio/academic umbrella:

**Transparencia360 / ContratIA Abierta: Sistema Políglota de Priorización de Revisión Contractual en Colombia**

Core thesis:

> ContratIA Abierta ayuda a oficinas de control interno, veedurías y periodistas de datos a decidir qué procesos SECOP revisar primero, reduciendo miles de procesos a una cola priorizada, explicable y auditable.

Non-negotiable ethical boundary:

- The system does **not** detect corruption.
- The system does **not** accuse fraud.
- The system does **not** prove wrongdoing or individual responsibility.
- Use the language: `priorización de revisión humana`, `score de prioridad`, `explicación auditable`, `trazabilidad de datos`, `alerta para revisión`.
- Avoid public claims like `detectar corrupción`, `fraude probado`, `proveedor corrupto`, `riesgo de corrupción confirmado`, or equivalents.

## Current state to verify, not blindly trust

The latest Codex pass pushed commit `0423fdc` and reported:

- `make lint`: passed.
- `make test`: 46 tests passed, 2 Dash deprecation warnings.
- `make validate-final`: passed with `ok=true` in a host-port fallback run.
- PostgreSQL public objects: 33.
- `procurement_process` rows: 17,229.
- MongoDB collections with documents: 5/5.
- API `/health`: 200 for contracts, risk, analytics.
- Large data, `.venv`, caches and `validation/*.json|*.csv` are ignored.

Important caveat:

- OrbStack/Docker had unresponsive port forwards during the previous validation, so `docs/testing_evidence.md` documents a host-port fallback using:

```bash
DATABASE_URL=postgresql://contratia@127.0.0.1:15532/contratia \
MONGO_URL=mongodb://127.0.0.1:17018/contratia \
CONTRACTS_SERVICE_URL=http://127.0.0.1:18001 \
RISK_SERVICE_URL=http://127.0.0.1:18002 \
ANALYTICS_SERVICE_URL=http://127.0.0.1:18003 \
make validate-final
```

The official route should remain:

```bash
uv sync --python 3.11 --extra dev
cp .env.example .env
make demo-full
make validate-final
```

## Source reports and prior audits

Read these local files if available:

- `/Users/thom/Downloads/deep-research-report(18).md`
- `/Users/thom/Downloads/deep-research-report(19).md`

They include:

- Product/contest critique.
- The distinction between academic final project and contest-winning product.
- Gaps around deploy, human validation, data cards, model card, fairness, narrative, and demo casebook.
- Caution that the repo should not grow more architecture unless it directly improves product evidence.

## Hard academic requirements

The repository should remain a complete Data Engineering final project:

1. Real open data from Colombian public procurement datasets.
2. Demo load with at least 10,000 records.
3. Relational database with at least 15 real tables, preferably 20+.
4. PostgreSQL as main relational store.
5. MongoDB as NoSQL support store.
6. FastAPI microservices.
7. Plotly Dash as official dashboard.
8. Python ETL.
9. SQL DDL, DML, constraints, indexes, triggers, views, CTEs, window functions, transactions.
10. Tests and evidence.
11. Full documentation and final report.
12. Ethical language: priorización, not accusation.

## Required datasets

Official open datasets:

- `p6dx-8zbt`: SECOP II Procesos de Contratación.
- `rpmr-utcd`: SECOP Integrado.
- `9sue-ezhx`: SECOP II Plan Anual de Adquisiciones Detalle.
- `wasc-xi4h`: Resultado de ejecución del plan de vigilancia/control fiscal.

Do not fabricate production data. Small fixtures are allowed only for CI/unit tests and must be clearly sample/fixture data.

## Overnight mission

Act as an orchestrator, not just a coder. Use subagents/specialists if your runtime supports them. Work for as long as useful, up to 8 hours. If you cannot continue due to missing credentials, Docker, network, Socrata, or permissions, leave a precise blocker report and the smallest useful patch.

Prioritize in this order:

### 1. Reproducibility and validation

- Start by running:

```bash
git status --short --branch
git log --oneline -5
make lint
make test
```

- Then try the official route:

```bash
make db-up
make db-reset
make etl-demo
make mongo-load
make services-up
make validate-final
```

- If OrbStack/Docker fails, document the exact command and error in `docs/testing_evidence.md`; do not claim Docker success unless it actually worked.
- Verify `validation/final_validation.json` if generated locally, but do not commit generated `validation/*.json` or `validation/*.csv`.
- Ensure CI can run from a clean clone without ignored Parquet files.

### 2. Product focus and public narrative

- Ensure README opens with a clear single product story:
  - Official demo route: Dash + PostgreSQL + FastAPI microservices.
  - Streamlit/Parquet is legacy/offline fallback only.
  - No two “official” products.
- If the naming still feels split, make the hierarchy explicit:
  - `ContratIA Abierta` = product.
  - `Transparencia360` = academic/portfolio system umbrella.
- Add or refine:
  - `docs/demo-guide.md`: 2-minute demo flow.
  - `docs/demo-casebook.md`: five curated demo cases.
  - `validation/demo_cases_sample.csv` or similar small versionable sample if allowed.
- Do not commit generated large validation outputs.

### 3. Evidence and validation without fabrication

Create useful artifacts that do not pretend to be real human results:

- `docs/human_validation_protocol.md`: manual validation plan for 40-100 cases.
- `docs/human_validation_results.md`: clearly marked pending unless real labels exist.
- `validation/manual_review_sample.csv`: template/sample rows clearly labeled `SAMPLE`, not real.
- `docs/validation-summary.md`: explain what has been validated automatically and what remains human-only.

Do not fabricate real UX survey results or human review labels.

### 4. Model card, data cards, fairness

Strengthen governance docs:

- Expand `docs/model-card.md` if it exists, or create a bridge doc if naming differs.
- Create `docs/data-cards/` with:
  - `secop-ii-procesos.md`
  - `secop-integrado.md`
  - `paa-detalle.md`
  - `control-fiscal.md`
- Create or refine `docs/fairness_territorial.md`:
  - regional coverage,
  - high-priority share by department,
  - confidence by department,
  - PAA match coverage,
  - limitations and risk of bias.

If metrics cannot be computed without local data, write the exact command that computes them and mark results pending.

### 5. Dashboard and executive demo

Inspect `dashboard/dash_app.py`.

The first viewport should communicate:

- Qué revisar primero.
- Por qué está priorizado.
- Qué acción humana sigue.
- Visible disclaimer: `Esta herramienta prioriza revisión humana. No prueba corrupción ni reemplaza auditoría jurídica o fiscal.`

Keep the UI clean and Dash official. Avoid decorative AI visuals.

If changing UI, run/import-test it and, if practical, capture screenshots. Do not break tests.

### 6. Report HTML as executive review brief

Inspect `src/utils/reporting.py`.

If missing, add:

- recommended human action,
- top 3 reasons,
- score components,
- confidence,
- comparables,
- PAA context,
- limitations,
- “qué revisar manualmente”.

Again: no accusation language.

### 7. Slides

Slides must be Spanish, professional, evidence-based, not generic AI visuals.

Check:

- `presentation/slides.md`
- `presentation/speaker_notes.md`
- `slides/contratia_abierta_deck.md`
- `slides/html/contratia_abierta_interactive.html`
- `slides/latex/contratia_abierta_beamer.tex`

Improve only if necessary:

- align claims with actual metrics,
- avoid “33 tables” imprecision unless phrased as `27 tablas relacionales y 33 objetos públicos entre tablas y vistas`,
- include ethics disclaimer,
- include a 2-minute demo story.

Do not spend the whole night redesigning slides if repo reproducibility or evidence is weaker.

### 8. Deployment readiness, but no risky deployment

Do not deploy using private credentials unless explicitly available and safe.

Instead, prepare deployment docs:

- `docs/deployment.md` or `docs/deployment_render.md`
- explain Render/Railway/Fly/HF Spaces options,
- specify required env vars,
- read-only mode for public demo,
- disable/protect mutable endpoints in public environments.

If you add `Dockerfile` or `render.yaml`, make it minimal and validate with `docker compose config` or local build only if Docker works.

### 9. Tests

Strengthen tests where cheap:

- language guardrail,
- sample fixtures clean-clone,
- risk recompute no placeholders,
- dashboard import with service-down fallback,
- docs existence,
- no absolute `/Users/thom/...` in public scripts,
- no generated junk in git.

Keep `make lint` and `make test` passing.

## Operating rules

- Do not rewrite the project from scratch.
- Do not delete useful existing work.
- Do not commit `.venv`, caches, Parquet, generated PDFs, or `validation/*.json|*.csv`.
- If you commit, use a clear branch or document the commit. Prefer not to push `main` unless explicitly instructed and fully validated.
- If working in parallel, use a separate branch/worktree to avoid colliding with other agents.
- Leave a final artifact in the repo, preferably:
  - `docs/agent_handoffs/<agent-name>-overnight-report.md`
  - include commands run, failures, patches, and next actions.
- If using ChatGPT web/browser and the user’s history is available, you may search previous conversations for `secop-risk-alerts-co`, `ContratIA Abierta`, `Transparencia360`, and `Datos al Ecosistema`; treat that context as supplementary, not source of truth.

## Acceptance criteria for your overnight run

At the end, return:

1. Whether you edited files.
2. Exact commands executed.
3. `make lint` result.
4. `make test` result.
5. `make validate-final` result, or exact blocker.
6. Files changed.
7. What is still human-only:
   - real UX survey with 5 users,
   - real manual validation labels,
   - optional public deployment credentials,
   - final professor/team metadata if not known.
8. Top 5 remaining improvements ranked by impact.

## Final reminder

The repository already meets a strong academic baseline. The overnight goal is not to add complexity. The goal is to make it more reproducible, more coherent as a product, better documented as a portfolio artifact, and more convincing for a jury.

