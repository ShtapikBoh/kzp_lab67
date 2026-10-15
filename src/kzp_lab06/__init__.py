"""Обробка CSV розкладу занять: завантаження, аналіз і звіт."""

from kzp_lab06.analysis import make_summary
from kzp_lab06.errors import DataError
from kzp_lab06.loader import load_records
from kzp_lab06.reporting import format_report, write_report

__all__ = [
    "DataError",
    "format_report",
    "load_records",
    "make_summary",
    "write_report",
]
