from __future__ import annotations

import re
import unicodedata
from datetime import datetime


def strip_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return normalized.encode("ascii", "ignore").decode("ascii")


def normalize_text(value: str | None) -> str:
    if value is None:
        return ""
    cleaned = strip_accents(str(value)).upper().strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


def normalize_reference(value: str | None) -> str:
    if value is None:
        return ""
    cleaned = normalize_text(value)
    cleaned = re.sub(r"[^A-Z0-9]+", "", cleaned)
    return cleaned


def only_digits(value: str | None) -> str:
    if value is None:
        return ""
    return re.sub(r"\D", "", str(value))


def safe_float(value: object) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if not text or text.lower() in {"none", "nan", "no definido"}:
        return None
    digits = re.sub(r"[^0-9,\.\-]", "", text)
    if not digits:
        return None
    if digits.count(",") > 0 and digits.count(".") > 0:
        if digits.rfind(",") > digits.rfind("."):
            digits = digits.replace(".", "").replace(",", ".")
        else:
            digits = digits.replace(",", "")
    else:
        digits = digits.replace(",", "")
    try:
        return float(digits)
    except ValueError:
        return None


def parse_date(value: str | None) -> datetime | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in {"none", "nan", "no definido"}:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def normalize_duration_to_days(value: object, unit: str | None) -> float | None:
    amount = safe_float(value)
    if amount is None:
        return None
    normalized_unit = normalize_text(unit)
    if normalized_unit.startswith("DIA"):
        factor = 1.0
    elif normalized_unit.startswith("SEMANA"):
        factor = 7.0
    elif normalized_unit.startswith("MES"):
        factor = 30.0
    elif normalized_unit.startswith("ANO"):
        factor = 365.0
    elif normalized_unit.startswith("HORA"):
        factor = 1.0 / 24.0
    else:
        return None
    return amount * factor


def text_is_sufficient(value: str | None, min_chars: int = 40, min_words: int = 6) -> bool:
    normalized = normalize_text(value)
    if len(normalized) < min_chars:
        return False
    words = [token for token in normalized.split(" ") if token]
    return len(words) >= min_words
