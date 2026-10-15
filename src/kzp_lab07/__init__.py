"""Об'єктна обробка CSV розкладу занять: моделі, завантаження, аналіз, звіт."""

from kzp_lab07.analysis import make_summary
from kzp_lab07.errors import DataError
from kzp_lab07.loader import load_lessons
from kzp_lab07.models import Lecture, Lesson, Practice, RoomLoad, ScheduleSummary
from kzp_lab07.reporting import format_report, write_report

__all__ = [
    "DataError",
    "Lecture",
    "Lesson",
    "Practice",
    "RoomLoad",
    "ScheduleSummary",
    "format_report",
    "load_lessons",
    "make_summary",
    "write_report",
]
