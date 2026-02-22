import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def render_dummy_pdf(run_id: int, verdict: str, fitness_result: dict | None = None) -> str:
    out_path = f"/tmp/run_{run_id}.pdf"

    c = canvas.Canvas(out_path, pagesize=A4)
    c.setFont("Helvetica", 16)
    c.drawString(72, 800, "KeelShift v1 Report")
    c.setFont("Helvetica", 12)
    c.drawString(72, 770, f"Run ID: {run_id}")
    c.drawString(72, 750, f"Verdict: {verdict}")
    y = 700
    if fitness_result:
        c.setFont("Helvetica", 12)
        m = fitness_result.get("metrics", {})
        c.drawString(72, y, f"Users: {m.get('n_users')} | Events: {m.get('n_rows')} | Span days: {m.get('span_days')}")
        y -= 25

        c.setFont("Helvetica", 11)
        c.drawString(72, y, "Checks:")
        y -= 18

        for chk in fitness_result.get("checks", []):
            line = f"- [{chk['status']}] {chk['name']}: {chk['detail']}"
            c.drawString(72, y, line[:110])  # keep it simple, avoid wrapping today
            y -= 16
            if y < 72:
                c.showPage()
                y = 800
                c.setFont("Helvetica", 11)
    c.drawString(72, 720, "Placeholder PDF. Correlation only.")
    c.showPage()
    c.save()

    return out_path
