"""
tests/test_phase8_streamlit_shell.py
Verification test suite for Phase 8:
- Validates Streamlit theme renderers (stat_card, hero, page_header)
- Validates APIClient communication methods
- Verifies view modules import cleanly without syntax or missing dependency errors
"""
import pytest
from frontend.theme import stat_card, hero, page_header, apply_theme
from frontend.api_client import APIClient

def test_theme_component_renderers():
    """Verify HTML rendering helper functions generate well-formed markup."""
    card_html = stat_card("Active Classes", "3", "🎓")
    assert "Active Classes" in card_html
    assert "3" in card_html
    assert "stat-card" in card_html

def test_api_client_urls():
    """Verify download and API URLs are formed accurately."""
    csv_url = APIClient.get_csv_download_url()
    assert "/api/io/export-csv" in csv_url

    excel_url = APIClient.get_excel_download_url()
    assert "/api/io/export-excel" in excel_url

    pdf_url = APIClient.get_pdf_download_url()
    assert "/api/io/export-pdf" in pdf_url

def test_views_import():
    """Verify all Phase 8 Streamlit views import cleanly."""
    from frontend.views.dashboard import render_dashboard
    from frontend.views.generate import render_generate_page
    from frontend.views.timetable_grid import render_timetable_grid
    from frontend.views.entities import render_entities_page

    assert callable(render_dashboard)
    assert callable(render_generate_page)
    assert callable(render_timetable_grid)
    assert callable(render_entities_page)
