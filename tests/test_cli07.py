"""Тести CLI (пакет kzp_lab07)."""

import importlib
from pathlib import Path

import pytest

from conftest import HEADER, write_csv
from kzp_lab07 import cli

SAMPLE = (
    HEADER
    + "Програмування,Олексів М. В.,Понеділок,1,101\n"
    + "Бази даних,Коваленко О. П.,Середа,2,98\n"
    + "Алгоритми,Олексів М. В.,Понеділок,3,215\n"
)


def test_success_writes_report_and_returns_zero(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Успішний запуск: код 0, файл звіту й вивід у консоль."""
    source = write_csv(tmp_path / "in.csv", SAMPLE)
    output = tmp_path / "out" / "summary.txt"

    code = cli.main([str(source), str(output)])

    text = output.read_text(encoding="utf-8")
    assert code == 0
    assert "Олексів М. В.: 2" in text
    assert "215: 1 зан., 2 год" in text
    assert capsys.readouterr().out == text


def test_day_option_changes_selection(tmp_path: Path) -> None:
    """Опція --day змінює відбір."""
    source = write_csv(tmp_path / "in.csv", SAMPLE)
    output = tmp_path / "summary.txt"

    code = cli.main([str(source), str(output), "--day", "Середа"])

    assert code == 0
    assert "Коваленко О. П.: 1" in output.read_text(encoding="utf-8")


def test_corrupt_csv_returns_one_with_row_in_stderr(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Пошкоджений CSV: ненульовий код і повідомлення в stderr."""
    source = write_csv(tmp_path / "in.csv", HEADER + "А,Б,В,abc,10\n")
    output = tmp_path / "summary.txt"

    code = cli.main([str(source), str(output)])

    captured = capsys.readouterr()
    assert code == 1
    assert "Рядок 2" in captured.err
    assert captured.out == ""
    assert not output.exists()


def test_missing_input_returns_three(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Відсутній вхідний файл: код 3."""
    code = cli.main([str(tmp_path / "немає.csv"), str(tmp_path / "out.txt")])

    assert code == 3
    assert "Помилка файлу" in capsys.readouterr().err


def test_output_cannot_equal_input(tmp_path: Path) -> None:
    """Вихідний файл не може збігатися з вхідним."""
    source = write_csv(tmp_path / "in.csv", SAMPLE)
    before = source.read_bytes()

    code = cli.main([str(source), str(source)])

    assert code == 1
    assert source.read_bytes() == before


def test_empty_data_gives_report_with_no_data(tmp_path: Path) -> None:
    """Файл із заголовком без записів дає коректний звіт."""
    source = write_csv(tmp_path / "in.csv", HEADER)
    output = tmp_path / "summary.txt"

    code = cli.main([str(source), str(output)])

    assert code == 0
    assert "Перша пара: немає даних" in output.read_text(encoding="utf-8")


def test_missing_arguments_exit_with_usage_error() -> None:
    """Без аргументів argparse завершує роботу з кодом 2."""
    with pytest.raises(SystemExit) as info:
        cli.main([])

    assert info.value.code == 2


def test_import_does_not_run_cli() -> None:
    """Імпорт модуля не запускає програму."""
    module = importlib.reload(cli)

    assert callable(module.main)
