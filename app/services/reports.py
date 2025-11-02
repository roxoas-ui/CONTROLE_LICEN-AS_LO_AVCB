from datetime import date
from pathlib import Path
from typing import Iterable

from fpdf import FPDF

from app.config import get_settings


class PDFReportService:
    def __init__(self) -> None:
        self.base_dir = Path(get_settings().file_storage_dir) / "reports"
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def generate_license_expiry_report(self, entries: Iterable[dict]) -> Path:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=14)
        pdf.cell(200, 10, txt="Relatório de Licenças", ln=True, align="C")
        pdf.ln(10)
        pdf.set_font("Arial", size=11)
        for entry in entries:
            pdf.multi_cell(
                0,
                8,
                txt=(
                    f"Licença: {entry['name']}\n"
                    f"Órgão emissor: {entry['issuing_agency']}\n"
                    f"Validade: {entry['expiry_date']}\n"
                    f"Status: {entry['status']}\n"
                ),
                border=1,
            )
            pdf.ln(2)
        output_path = self.base_dir / f"licenses_{date.today().isoformat()}.pdf"
        pdf.output(str(output_path))
        return output_path


pdf_report_service = PDFReportService()
