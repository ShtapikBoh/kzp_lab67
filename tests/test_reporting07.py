"""Тести звіту (пакет kzp_lab07)."""

from pathlib import Path

from kzp_lab07.analysis import make_summary
from kzp_lab07.models import Lecture, Practice
from kzp_lab07.reporting import format_report, write_report


def test_format_report_is_deterministic() -> None:
    """Звіт має стабільний порядок і формат, включно з блоком завантаження."""
    lessons = [
        Practice("Б", "Ю", "Понеділок", 2, 110),
        Practice("А", "Е", "Понеділок", 1, 101),
        Lecture("В", "Е", "Понеділок", 3, 215),
    ]

    assert format_report(make_summary(lessons, "Понеділок")) == (
        "Записів у файлі: 3\n"
        "День: Понеділок\n"
        "Занять у цей день: 3\n"
        "Заняття за викладачами:\n"
        "  Е: 2\n"
        "  Ю: 1\n"
        "Аудиторії: 101, 110, 215\n"
        "Перша пара: 1\n"
        "Остання пара: 3\n"
        "Завантаження аудиторій:\n"
        "  101: 1 зан., 1 год\n"
        "  110: 1 зан., 1 год\n"
        "  215: 1 зан., 2 год\n"
    )


def test_format_report_for_empty_selection() -> None:
    """Порожній відбір позначається «немає даних»."""
    text = format_report(make_summary([], "Середа"))

    assert "  немає даних" in text
    assert "Аудиторії: немає даних" in text
    assert "Перша пара: немає даних" in text
    assert text.endswith("Завантаження аудиторій:\n  немає даних\n")


def test_write_report_utf8_and_newlines(tmp_path: Path) -> None:
    """Звіт у UTF-8 з роздільником \\n."""
    output = tmp_path / "report.txt"

    write_report(output, "Готово, Ї є\nдругий\n")

    assert output.read_bytes() == "Готово, Ї є\nдругий\n".encode()


def test_write_report_creates_missing_directory(tmp_path: Path) -> None:
    """Відсутній каталог створюється."""
    output = tmp_path / "нова" / "тека" / "report.txt"

    write_report(output, "x\n")

    assert output.exists()


def test_write_report_replaces_old_content(tmp_path: Path) -> None:
    """Старий вміст не залишається після коротшого запису."""
    output = tmp_path / "report.txt"
    write_report(output, "довгий текст\n")

    write_report(output, "ко\n")

    assert output.read_text(encoding="utf-8") == "ко\n"
