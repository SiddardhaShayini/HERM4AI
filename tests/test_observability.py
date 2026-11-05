"""
Tests: tests/test_observability.py
Verifies dashboard generation and observability rendering functions.
"""

from pathlib import Path
from src.herm4ai.dashboard import generate_html_dashboard


def test_html_dashboard_generation(tmp_path):
    mock_results = [
        {
            "id": "test_case_01",
            "category": "TR",
            "predicted_status": "ACTIVE",
            "predicted_val": "Tokyo",
            "expected_val": "Tokyo",
            "is_correct": True,
            "provenance_count": 2
        },
        {
            "id": "test_case_02",
            "category": "CA",
            "predicted_status": "CONFLICTED",
            "predicted_val": "CONFLICTED",
            "expected_val": "CONFLICTED",
            "is_correct": True,
            "provenance_count": 2
        }
    ]

    out_file = tmp_path / "dashboard.html"
    generate_html_dashboard(mock_results, str(out_file))

    assert out_file.exists()
    content = out_file.read_text(encoding="utf-8")
    assert "HERM4AI — Memory Observability Dashboard" in content
    assert "test_case_01" in content
    assert "test_case_02" in content
    assert "Scientific Observability Notice" in content
