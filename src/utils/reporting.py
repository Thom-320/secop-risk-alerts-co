from __future__ import annotations

from collections.abc import Sequence
from html import escape


def _fmt_currency(value: float | int | None) -> str:
    if value is None:
        return "No disponible"
    return "$" + f"{float(value):,.0f}".replace(",", ".")


def _fmt_percent(value: float | None) -> str:
    if value is None:
        return "No disponible"
    return f"{value:.1%}"


def _present(value: object, default: str = "No disponible") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _to_float(value: object) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _first_present(*values: object) -> object:
    for value in values:
        if value is not None and str(value).strip():
            return value
    return None


def _recommended_action(priority_score: float | None, confidence_score: float | None) -> str:
    if priority_score is None:
        return "No escalar sin revisar primero la calidad de datos y la fuente primaria."
    if priority_score >= 70 and (confidence_score is None or confidence_score >= 60):
        return "Abrir revision prioritaria y contrastar el proceso con fuente primaria."
    if priority_score >= 70:
        return "Validar datos de soporte antes de escalar la alerta a revision prioritaria."
    if priority_score >= 40:
        return "Mantener en cola de observacion y revisar si coincide con una prioridad humana."
    return "No requiere revision prioritaria salvo que exista contexto externo relevante."


def build_process_report_html(
    process: dict[str, object],
    comparables: Sequence[dict[str, object]],
) -> str:
    comparable_rows = "".join(
        """
        <tr>
          <td>{reference}</td>
          <td>{entity}</td>
          <td>{price}</td>
          <td>{score}</td>
        </tr>
        """.format(
            reference=escape(
                str(
                    item.get("process_reference")
                    or item.get("comparable_label")
                    or item.get("comparable_process_key")
                    or ""
                )
            ),
            entity=escape(str(item.get("entity_name") or item.get("department") or "")),
            price=escape(
                _fmt_currency(
                    item.get("base_price")
                    if item.get("base_price") is not None
                    else item.get("comparable_value")
                )
            ),
            score=escape(
                _present(_first_present(item.get("priority_score"), item.get("similarity")), "")
            ),
        )
        for item in comparables
    )

    if not comparable_rows:
        comparable_rows = "<tr><td colspan='4'>Sin comparables disponibles</td></tr>"

    process_reference = escape(
        _present(_first_present(process.get("process_reference"), process.get("process_key")), "")
    )
    entity_name = escape(_present(process.get("entity_name"), ""))
    priority_value = _to_float(process.get("priority_score"))
    confidence_value = _to_float(process.get("confidence_score"))
    priority_score = escape(_present(process.get("priority_score"), ""))
    confidence_score = escape(_present(process.get("confidence_score"), ""))
    base_price = escape(_fmt_currency(process.get("base_price")))
    paa_status = escape(_present(process.get("paa_match_status"), ""))
    reasons_text = escape(
        _present(process.get("reasons_text") or process.get("reasons"), "Sin razones disponibles")
    )
    action = escape(_recommended_action(priority_value, confidence_value))
    limitations = escape(
        "El score ordena revision humana; no determina corrupcion, fraude, "
        "responsabilidad fiscal ni responsabilidad juridica. La decision exige "
        "contrastar documentos SECOP, PAA, comparables y contexto institucional."
    )

    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
      <meta charset="utf-8" />
      <title>Reporte ContratIA Abierta</title>
      <style>
        body {{ font-family: Arial, sans-serif; margin: 32px; color: #18212b; }}
        h1, h2 {{ margin-bottom: 8px; }}
        .grid {{
          display: grid;
          grid-template-columns: repeat(2, minmax(240px, 1fr));
          gap: 12px;
          margin: 20px 0;
        }}
        .card {{
          border: 1px solid #d9e1ea;
          border-radius: 8px;
          padding: 12px;
          background: #f8fafc;
        }}
        .label {{ font-size: 12px; text-transform: uppercase; color: #5a6b7b; }}
        .value {{ font-size: 18px; font-weight: bold; margin-top: 4px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 12px; }}
        th, td {{ border: 1px solid #d9e1ea; padding: 8px; text-align: left; }}
        th {{ background: #edf2f7; }}
        .small {{ font-size: 12px; color: #5a6b7b; }}
        .callout {{
          border-left: 4px solid #2f6f73;
          background: #eef7f6;
          padding: 12px 14px;
          margin: 16px 0;
        }}
        .disclaimer {{ margin-top: 24px; font-size: 12px; color: #6b7280; }}
      </style>
    </head>
    <body>
      <h1>ContratIA Abierta</h1>
      <p class="small">Reporte individual de prioridad de revision contractual.</p>
      <div class="callout">
        <strong>Accion recomendada:</strong> {action}
      </div>
      <div class="disclaimer">
        Priorizacion, no acusacion. Este reporte no determina corrupcion, fraude,
        responsabilidad fiscal ni responsabilidad juridica; requiere revision humana
        y contraste con fuente primaria.
      </div>
      <div class="grid">
        <div class="card">
          <div class="label">Proceso</div>
          <div class="value">{process_reference}</div>
        </div>
        <div class="card">
          <div class="label">Entidad</div>
          <div class="value">{entity_name}</div>
        </div>
        <div class="card">
          <div class="label">Score de prioridad</div>
          <div class="value">{priority_score}</div>
        </div>
        <div class="card">
          <div class="label">Confianza</div>
          <div class="value">{confidence_score}</div>
        </div>
        <div class="card">
          <div class="label">Valor base</div>
          <div class="value">{base_price}</div>
        </div>
        <div class="card">
          <div class="label">Match PAA</div>
          <div class="value">{paa_status}</div>
        </div>
      </div>

      <h2>Razones principales</h2>
      <p>{reasons_text}</p>

      <h2>Que revisar manualmente</h2>
      <ul>
        <li>Documentos y estado del proceso en la fuente SECOP.</li>
        <li>Coherencia entre objeto, valor, modalidad y comparables.</li>
        <li>Contexto PAA y trazabilidad de la entidad contratante.</li>
      </ul>

      <h2>Comparables</h2>
      <table>
        <thead>
          <tr>
            <th>Referencia</th>
            <th>Entidad</th>
            <th>Valor base</th>
            <th>Score</th>
          </tr>
        </thead>
        <tbody>
          {comparable_rows}
        </tbody>
      </table>

      <h2>Limitaciones</h2>
      <p>{limitations}</p>

      <div class="disclaimer">
        Este reporte prioriza revision humana.
        No prueba corrupcion, fraude ni responsabilidad individual.
      </div>
    </body>
    </html>
    """
