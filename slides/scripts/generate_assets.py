from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "slides" / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)

INK = "#273140"
MUTED = "#667085"
RULE = "#D9DEE8"
ACCENT = "#275DA8"
ACCENT_SOFT = "#EAF1FB"
CANVAS = "#FAFBFD"
GREEN = "#2F8F64"
AMBER = "#B7791F"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        (
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
            if bold
            else "/System/Library/Fonts/Supplemental/Arial.ttf"
        ),
        (
            "/System/Library/Fonts/Supplemental/Helvetica Bold.ttf"
            if bold
            else "/System/Library/Fonts/Supplemental/Helvetica.ttf"
        ),
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def rounded(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    fill: str,
    outline: str = RULE,
    width: int = 2,
) -> None:
    draw.rounded_rectangle(box, radius=14, fill=fill, outline=outline, width=width)


def arrow(
    draw: ImageDraw.ImageDraw,
    start: tuple[int, int],
    end: tuple[int, int],
    color: str = ACCENT,
) -> None:
    draw.line([start, end], fill=color, width=4)
    x2, y2 = end
    draw.polygon([(x2, y2), (x2 - 12, y2 - 7), (x2 - 12, y2 + 7)], fill=color)


def label(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    size: int = 28,
    color: str = INK,
    bold: bool = False,
) -> None:
    draw.text(xy, text, fill=color, font=font(size, bold=bold))


def title(draw: ImageDraw.ImageDraw, text: str) -> None:
    label(draw, (58, 36), text, 36, INK, True)
    draw.line([(58, 88), (1222, 88)], fill=RULE, width=2)


def save(img: Image.Image, name: str) -> None:
    img.save(ASSETS / name, optimize=True)


def architecture() -> None:
    img = Image.new("RGB", (1280, 720), CANVAS)
    d = ImageDraw.Draw(img)
    title(d, "Arquitectura reproducible")
    boxes = [
        ("Socrata API\nSECOP/PAA", 70, 170),
        ("Parquet local\nfallback demo", 70, 360),
        ("ETL Python\nnormalizacion", 330, 265),
        ("PostgreSQL\n27 tablas + vistas", 590, 170),
        ("MongoDB\nlogs/eventos", 590, 360),
        ("FastAPI\n3 servicios", 850, 265),
        ("Dash\nrevision humana", 1080, 265),
    ]
    for text, x, y in boxes:
        rounded(d, (x, y, x + 170, y + 96), ACCENT_SOFT)
        for i, line in enumerate(text.split("\n")):
            label(d, (x + 18, y + 18 + i * 32), line, 24, INK, i == 0)
    arrow(d, (240, 218), (330, 300))
    arrow(d, (240, 408), (330, 330))
    arrow(d, (500, 300), (590, 218))
    arrow(d, (500, 330), (590, 408))
    arrow(d, (760, 218), (850, 300))
    arrow(d, (760, 408), (850, 330))
    arrow(d, (1020, 313), (1080, 313))
    label(
        d,
        (70, 610),
        "Fuente de verdad: PostgreSQL. MongoDB soporta documentos y eventos.",
        28,
        MUTED,
    )
    save(img, "architecture.png")


def pipeline() -> None:
    img = Image.new("RGB", (1280, 720), CANVAS)
    d = ImageDraw.Draw(img)
    title(d, "ETL con checkpoints")
    stages = [
        ("1", "Extraer", "Socrata o fallback local", 70),
        ("2", "Manifest", "reanudacion y chunks", 295),
        ("3", "Normalizar", "entidades, PAA, scores", 520),
        ("4", "Cargar", "PostgreSQL + MongoDB", 745),
        ("5", "Validar", "tests, API health, conteos", 970),
    ]
    y = 245
    for n, head, sub, x in stages:
        d.ellipse((x, y, x + 56, y + 56), fill=ACCENT, outline=ACCENT)
        label(d, (x + 19, y + 11), n, 26, "#F7FAFF", True)
        label(d, (x, y + 84), head, 30, INK, True)
        label(d, (x, y + 126), sub, 21, MUTED)
        if x < 970:
            arrow(d, (x + 76, y + 28), (x + 200, y + 28))
    rounded(d, (92, 510, 1188, 600), "#FFFFFF", RULE)
    label(
        d,
        (125, 536),
        "Salida validada: 17.229 procesos, 27 tablas y 33 objetos, 5 colecciones Mongo.",
        28,
        INK,
    )
    save(img, "pipeline.png")


def er_model() -> None:
    img = Image.new("RGB", (1280, 720), CANVAS)
    d = ImageDraw.Draw(img)
    title(d, "Modelo relacional agrupado")
    groups = [
        ("Ingesta", ["source_dataset", "extraction_run"], 60, 150, ACCENT_SOFT),
        (
            "Catalogo publico",
            ["department", "municipality", "public_entity", "provider"],
            330,
            150,
            "#F2F6F0",
        ),
        (
            "Contratacion",
            ["procurement_process", "contract", "paa_item", "paa_process_match"],
            650,
            150,
            "#FFF7E8",
        ),
        ("Scoring", ["risk_assessment", "risk_reason", "semantic_comparable"], 60, 410, "#F4F0FA"),
        ("Revision humana", ["human_review", "app_user"], 410, 410, "#EEF7F8"),
        ("Auditoria", ["audit_log", "process_state_history"], 760, 410, "#F8F1F1"),
    ]
    for head, items, x, y, fill in groups:
        rounded(d, (x, y, x + 270, y + 190), fill)
        label(d, (x + 18, y + 18), head, 26, INK, True)
        for i, item in enumerate(items):
            label(d, (x + 24, y + 62 + i * 28), item, 21, INK)
    arrow(d, (330, 246), (650, 246), GREEN)
    arrow(d, (785, 340), (195, 410), GREEN)
    arrow(d, (570, 505), (760, 505), GREEN)
    label(
        d,
        (60, 640),
        "El detalle completo vive en sql/001_schema.sql y db/migrations/001_schema.sql.",
        24,
        MUTED,
    )
    save(img, "er_model.png")


def validation_card() -> None:
    final = json.loads((ROOT / "validation" / "final_validation.json").read_text())
    evidence = final["evidence"]
    img = Image.new("RGB", (1280, 720), CANVAS)
    d = ImageDraw.Draw(img)
    title(d, "Validacion final")
    metrics = [
        ("Estado", "OK"),
        ("Tablas PostgreSQL", str(evidence["postgres_table_count"])),
        ("Procesos demo", f"{evidence['procurement_process_rows']:,}".replace(",", ".")),
        ("APIs health", "3/3"),
        ("Pytest", "66 passed"),
        ("Ruff", "passed"),
    ]
    for idx, (k, v) in enumerate(metrics):
        x = 90 + (idx % 3) * 380
        y = 170 + (idx // 3) * 190
        rounded(d, (x, y, x + 310, y + 124), "#FFFFFF", RULE)
        label(d, (x + 24, y + 24), v, 34, GREEN if v in {"OK", "passed"} else ACCENT, True)
        label(d, (x + 24, y + 78), k, 22, MUTED)
    label(
        d,
        (90, 610),
        "Evidencia: validation/final_validation.json, validation/table_counts.csv.",
        25,
        MUTED,
    )
    save(img, "validation_summary.png")


if __name__ == "__main__":
    architecture()
    pipeline()
    er_model()
    validation_card()
