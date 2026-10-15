"""Командний рядок: межа між користувачем і модулями пакета."""

import argparse
import sys
from pathlib import Path

from kzp_lab06.analysis import make_summary
from kzp_lab06.errors import DataError
from kzp_lab06.loader import load_records
from kzp_lab06.reporting import format_report, write_report

EXIT_OK = 0
EXIT_DATA_ERROR = 1
EXIT_FILE_ERROR = 3


def build_parser() -> argparse.ArgumentParser:
    """Створює розбір аргументів командного рядка."""
    parser = argparse.ArgumentParser(
        prog="kzp-lab06",
        description="Звіт за розкладом занять із CSV-файла.",
    )
    parser.add_argument("input", type=Path, help="вхідний CSV-файл")
    parser.add_argument("output", type=Path, help="вихідний текстовий звіт")
    parser.add_argument("--day", default="Понеділок", help="день для відбору")
    return parser


def _use_utf8_streams() -> None:
    """Задає UTF-8 для stdout і stderr, бо консоль ОС може мати інше кодування."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    """Запускає програму й повертає код завершення (0, 1 — дані, 3 — файл)."""
    args = build_parser().parse_args(argv)
    _use_utf8_streams()
    try:
        if args.input.resolve() == args.output.resolve():
            raise DataError("Вихідний файл не може збігатися з вхідним")
        records = load_records(args.input)
        text = format_report(make_summary(records, args.day))
        write_report(args.output, text)
    except DataError as error:
        print(f"Помилка даних: {error}", file=sys.stderr)
        return EXIT_DATA_ERROR
    except OSError as error:
        print(f"Помилка файлу: {error}", file=sys.stderr)
        return EXIT_FILE_ERROR
    print(text, end="")
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
