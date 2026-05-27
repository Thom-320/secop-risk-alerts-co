from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_PATTERNS = [
    "fraude probado",
    "proveedor corrupto",
    "riesgo de corrupcion confirmado",
    "responsable de corrupcion",
]


def test_public_docs_do_not_make_accusatory_claims() -> None:
    paths = [
        ROOT / "README.md",
        ROOT / "dashboard" / "dash_app.py",
        ROOT / "docs" / "project_report.md",
        ROOT / "docs" / "scoring.md",
        ROOT / "docs" / "ethics-note.md",
    ]
    combined = "\n".join(path.read_text().lower() for path in paths if path.exists())
    for pattern in FORBIDDEN_PATTERNS:
        assert pattern not in combined
