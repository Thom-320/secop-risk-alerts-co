from __future__ import annotations

import subprocess
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_PATTERNS = [
    "detecta corrupcion",
    "detectar corrupcion",
    "prueba fraude",
    "culpable",
    "irregularidad confirmada",
    "fraude probado",
    "proveedor corrupto",
    "riesgo de corrupcion confirmado",
    "responsable de corrupcion",
    "corrupcion confirmada",
]

PUBLIC_SCAN_DIRS = [
    "README.md",
    "PRODUCT.md",
    "SECURITY.md",
    "dashboard",
    "docs",
    "presentation",
    "services",
    "slides",
    "src",
]

PUBLIC_SCAN_EXCLUDES = (
    "docs/agent_handoffs/",
    "docs/legacy/raw_metadata/",
)


def normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text.lower())
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def tracked_public_text_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", *PUBLIC_SCAN_DIRS],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    files: list[Path] = []
    for line in result.stdout.splitlines():
        if line.endswith((".png", ".pdf", ".pptx", ".jpg", ".jpeg")):
            continue
        if line.startswith(PUBLIC_SCAN_EXCLUDES):
            continue
        path = ROOT / line
        if path.is_file():
            files.append(path)
    return files


def test_public_docs_do_not_make_accusatory_claims() -> None:
    combined = "\n".join(
        normalize(path.read_text(errors="ignore")) for path in tracked_public_text_files()
    )
    for pattern in FORBIDDEN_PATTERNS:
        assert normalize(pattern) not in combined
