# OpenClaw Overnight Report - 2026-05-27

## Summary

Edited files. The pass focused on product coherence, governance documentation,
clean-clone safety, dashboard/report decision clarity, and validation evidence.
No files were committed or pushed.

The repository now has stronger evidence docs for human validation, data cards,
territorial fairness, deployment readiness, demo cases, report disclaimers, and
tests that guard against stale generated artifacts, local absolute paths in
public scripts, and weak source-volume validation.

## Commands executed

Core requested gates:

```bash
git status --short --branch
git log --oneline -5
make lint
make test
make db-up
make validate-final
```

Docker and environment probes:

```bash
ps -axo pid,ppid,stat,command | rg 'docker compose up -d postgres mongo|make db-up|docker-compose|com.docker|OrbStack'
kill 30718 30734 30737 || true
lsof -nP -iTCP:15532 -iTCP:17018 -iTCP:18001 -iTCP:18002 -iTCP:18003 -sTCP:LISTEN || true
lsof -nP -iTCP:55432 -iTCP:27018 -iTCP:8001 -iTCP:8002 -iTCP:8003 -iTCP:8050 -sTCP:LISTEN || true
python3 - <<'PY'
import subprocess
subprocess.run(['docker','compose','ps'], cwd='.', text=True, capture_output=True, timeout=12)
PY
python3 - <<'PY'
import subprocess
subprocess.run(['docker','compose','config'], cwd='.', text=True, capture_output=True, timeout=20)
PY
```

Hygiene and inspection:

```bash
git diff --check
git ls-files -ci --exclude-standard
git ls-files | xargs rg -n "/Users/thom" || true
git ls-files | xargs rg -n "fraude probado|proveedor corrupto|riesgo de corrupci[oó]n confirmado|responsable de corrupci[oó]n|proveedor corrupt|corrupci[oó]n confirmada" -S || true
```

## Validation evidence

- `make lint`: passed, `All checks passed!`.
- `make test`: passed, `51 passed, 2 warnings in 48.78s`.
- `docker compose config`: passed.
- `git diff --check`: passed.
- `git ls-files -ci --exclude-standard`: empty.
- `make validate-final`: failed correctly because the local Docker/OrbStack
  services were not responsive.

`make db-up` reached `docker compose up -d postgres mongo` and then hung without
output. It was interrupted after waiting. Follow-up probes showed OrbStack
listening on the default ports, but PostgreSQL, MongoDB, and API endpoints timed
out or reset connections.

`make validate-final` blocker:

```text
No se pudo validar PostgreSQL en postgresql://contratia:contratia@localhost:55432/contratia
No se pudo validar MongoDB en mongodb://localhost:27018/contratia
Endpoints API no disponibles: contracts=unavailable: timed out, risk=unavailable: timed out, analytics=unavailable: timed out
```

## Files changed

- `.gitignore`
- `README.md`
- `dashboard/dash_app.py`
- `dashboard/assets/styles.css`
- `docs/crisp_ml.md`
- `docs/demo-guide.md`
- `docs/demo-casebook.md`
- `docs/deployment.md`
- `docs/fairness_territorial.md`
- `docs/human_validation_protocol.md`
- `docs/human_validation_results.md`
- `docs/model-card.md`
- `docs/testing_evidence.md`
- `docs/validation-summary.md`
- `docs/data-cards/secop-ii-procesos.md`
- `docs/data-cards/secop-integrado.md`
- `docs/data-cards/paa-detalle.md`
- `docs/data-cards/control-fiscal.md`
- `etl/common.py`
- `etl/validate_final.py`
- `etl/validate_sources.py`
- `scripts/launch_overnight_agents.sh`
- `src/utils/reporting.py`
- `tests/test_final_project_static.py`
- `tests/test_language_guardrails.py`
- `tests/test_reproducibility_closure.py`
- `tests/test_scoring.py`
- `tests/test_services_and_dashboard.py`
- `validation/README.md`
- `validation/demo_cases_sample.csv`
- `validation/manual_review_sample.csv`
- `docs/agent_handoffs/openclaw-overnight-report-2026-05-27.md`

Note: `.gitignore` already had a pre-existing dirty change for `.worktrees/`
before this pass. This pass added versionable exceptions for the two small
`SAMPLE` CSV files under `validation/`.

## What changed

- Made README naming explicit: ContratIA Abierta is the product;
  Transparencia360 is the academic/portfolio umbrella.
- Added a Dash first-viewport decision strip: what to review first, why it is
  prioritized, and the next human action.
- Repeated the ethical disclaimer near score-heavy dashboard surfaces.
- Strengthened HTML reports with recommended action, manual review checklist,
  limitations, and a top disclaimer.
- Added model card details, data cards, deployment guidance, fairness
  territorial guidance, validation summary, demo casebook, and human validation
  protocol/results placeholder.
- Added versionable sample CSVs marked `SAMPLE`, not real labels.
- Made source validation fail clearly when the available demo source has fewer
  than 10,000 processes.
- Ensured requested download mode is checked before tiny sample fixtures.
- Removed a hard-coded `/Users/thom/...` path from the public overnight launcher
  script.
- Expanded static tests for required governance docs, human-validation honesty,
  language guardrails, path portability, generated-artifact hygiene, and report
  content.

## Human-only tasks

- Real UX survey with 5 users.
- Real manual validation labels for 40-100 cases.
- Optional public deployment credentials and hosting decision.
- Final professor/team metadata if it differs from placeholders.
- Human review of generated slide/PPTX freshness before submission.

## Top 5 remaining improvements

1. Restore or restart OrbStack/Docker and rerun:
   `make db-up && make db-reset && make etl-demo && make mongo-load && make services-up && make validate-final`.
2. Capture fresh dashboard screenshots after the decision strip change and
   regenerate slide/PPTX exports if those binaries will be submitted.
3. Run the human validation protocol on 40-100 real cases and update
   `docs/human_validation_results.md`.
4. Add a public read-only deployment only after endpoints are protected and
   credentials are provider-managed.
5. Add CI steps for `docker compose config` and generated-artifact hygiene.
