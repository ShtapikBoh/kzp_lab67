"""Тести формування й запису звіту."""

from pathlib import Path

from kzp_lab06.analysis import make_summary
from kzp_lab06.reporting import format_report, write_report


def test_format_report_is_deterministic() -> None:
    """Звіт має стабільний порядок і формат."""
    records = [
        {"subject": "Б", "teacher": "Ю", "day": "Понеділок", "period": 2, "room": 110},
        {"subject": "А", "teacher": "Е", "day": "Понеділок", "period": 1, "room": 101},
        {"subject": "В", "teacher": "Е", "day": "Понеділок", "period": 3, "room": 101},
    ]

    assert format_report(make_summary(records, "Понеділок")) == (
        "Записів у файлі: 3\n"
        "День: Понеділок\n"
        "Занять у цей день: 3\n"
        "Заняття за викладачами:\n"
        "  Е: 2\n"
        "  Ю: 1\n"
        "Аудиторії: 101, 110\n"
        "Перша пара: 1\n"
        "Остання пара: 3\n"
    )


def test_format_report_for_empty_selection() -> None:
    """Порожній відбір позначається «немає даних»."""
    text = format_report(make_summary([], "Середа"))

    assert "  немає даних" in text
    assert "Аудиторії: немає даних" in text
    assert "Перша пара: немає даних" in text
    assert "Остання пара: немає даних" in text


def test_write_report_utf8(tmp_path: Path) -> None:
    """Звіт записується в UTF-8 і читається назад."""
    output = tmp_path / "report.txt"

    write_report(output, "Готово, Ї є\n")

    assert output.read_text(encoding="utf-8") == "Готово, Ї є\n"


def test_write_report_uses_unix_newlines(tmp_path: Path) -> None:
    """Роздільник рядків — \\n на будь-якій ОС."""
    output = tmp_path / "report.txt"

    write_report(output, "а\nб\n")

    assert output.read_bytes() == "а\nб\n".encode()


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
