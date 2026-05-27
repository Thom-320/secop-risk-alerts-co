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
            score=escape(str(item.get("priority_score") or item.get("similarity") or "")),
        )
        for item in comparables
    )

    if not comparable_rows:
        comparable_rows = "<tr><td colspan='4'>Sin comparables disponibles</td></tr>"

    process_reference = escape(
        str(process.get("process_reference") or process.get("process_key") or "")
    )
    entity_name = escape(str(process.get("entity_name") or ""))
    priority_score = escape(str(process.get("priority_score") or ""))
    confidence_score = escape(str(process.get("confidence_score") or ""))
    base_price = escape(_fmt_currency(process.get("base_price")))
    paa_status = escape(str(process.get("paa_match_status") or ""))
    reasons_text = escape(
        str(
            process.get("reasons_text")
            or process.get("reasons")
            or "Sin razones disponibles"
        )
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
        .disclaimer {{ margin-top: 24px; font-size: 12px; color: #6b7280; }}
      </style>
    </head>
    <body>
      <h1>ContratIA Abierta</h1>
      <p class="small">Reporte individual de prioridad de revision contractual.</p>
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

      <div class="disclaimer">
        Este reporte prioriza revision humana.
        No prueba corrupcion, fraude ni responsabilidad individual.
      </div>
    </body>
    </html>
    """
