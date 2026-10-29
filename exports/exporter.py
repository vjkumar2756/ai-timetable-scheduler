"""
Comprehensive Export Engine for SchedulAI.
Provides CSV, Multi-Sheet Styled Excel, Print-Ready Colored PDF, and All-in-One ZIP package.
"""
import io
import zipfile
import json
from backend.app.database.store import db_store
from backend.app.services.io_service import IOService

class TimetableExporter:
    """
    Central exporter generating CSV, Excel (.xlsx), PDF, and ZIP archives.
    """
    @staticmethod
    def get_csv() -> str:
        return IOService.export_timetable_csv()

    @staticmethod
    def get_excel() -> bytes:
        return IOService.export_timetable_excel()

    @staticmethod
    def get_pdf() -> bytes:
        return IOService.export_timetable_pdf()

    @staticmethod
    def get_all_zip() -> bytes:
        """Packages CSV, Excel, PDF, and active dataset JSON into a single ZIP archive"""
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            # 1. CSV
            csv_str = TimetableExporter.get_csv()
            zip_file.writestr("schedulai_timetable.csv", csv_str)

            # 2. Excel
            excel_bytes = TimetableExporter.get_excel()
            zip_file.writestr("schedulai_timetable.xlsx", excel_bytes)

            # 3. PDF
            pdf_bytes = TimetableExporter.get_pdf()
            zip_file.writestr("schedulai_timetable.pdf", pdf_bytes)

            # 4. JSON Dataset
            dataset_dict = db_store.export_to_dict()
            zip_file.writestr("dataset_active.json", json.dumps(dataset_dict, indent=2))

        return zip_buffer.getvalue()
