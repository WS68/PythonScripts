"""Generate random Russian surnames and gender-consistent full names."""

from __future__ import annotations

import argparse
import random
import sys
from typing import Final


def configure_console() -> None:
    """Make standard streams use UTF-8 when the interpreter supports it."""
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8")


CONSONANTS: Final[str] = "бвгджзклмнпрстфхцчшщ"
VOWELS: Final[str] = "аеиоуэюя"

FIRST_PATTERNS: Final[tuple[str, ...]] = ("СГ", "ССГ", "СГСГ", "СГСГСГ", "ССГСГ")
PENULTIMATE_PATTERNS: Final[tuple[str, ...]] = ("ССГС", "СГС")

MALE_NAMES: Final[tuple[str, ...]] = (
    "Александр", "Алексей", "Андрей", "Антон", "Арсений", "Борис",
    "Вадим", "Валерий", "Василий", "Виктор", "Владимир", "Владислав",
    "Георгий", "Глеб", "Даниил", "Денис", "Дмитрий", "Евгений",
    "Иван", "Игорь", "Илья", "Кирилл", "Константин", "Максим",
    "Михаил", "Никита", "Николай", "Олег", "Павел", "Роман",
    "Сергей", "Степан", "Федор", "Юрий", "Ярослав",
)
FEMALE_NAMES: Final[tuple[str, ...]] = (
    "Александра", "Алина", "Алёна", "Анастасия", "Анна", "Валентина",
    "Варвара", "Вера", "Вероника", "Виктория", "Галина", "Дарья",
    "Диана", "Евгения", "Екатерина", "Елена", "Ирина", "Кира",
    "Кристина", "Людмила", "Маргарита", "Марина", "Мария", "Надежда",
    "Наталья", "Оксана", "Ольга", "Полина", "Светлана", "София",
    "Татьяна", "Ульяна", "Юлия", "Яна",
)

MALE_PATRONYMICS: Final[tuple[str, ...]] = (
    "Александрович", "Алексеевич", "Андреевич", "Антонович", "Борисович",
    "Вадимович", "Васильевич", "Викторович", "Владимирович", "Георгиевич",
    "Дмитриевич", "Евгеньевич", "Иванович", "Игоревич", "Ильич",
    "Кириллович", "Константинович", "Максимович", "Михайлович", "Николаевич",
    "Олегович", "Павлович", "Романович", "Сергеевич", "Степанович",
    "Федорович", "Юрьевич", "Ярославович",
)
FEMALE_PATRONYMICS: Final[tuple[str, ...]] = (
    "Александровна", "Алексеевна", "Андреевна", "Антоновна", "Борисовна",
    "Вадимовна", "Васильевна", "Викторовна", "Владимировна", "Георгиевна",
    "Дмитриевна", "Евгеньевна", "Ивановна", "Игоревна", "Ильинична",
    "Кирилловна", "Константиновна", "Максимовна", "Михайловна", "Николаевна",
    "Олеговна", "Павловна", "Романовна", "Сергеевна", "Степановна",
    "Федоровна", "Юрьевна", "Ярославовна",
)


def random_syllable(pattern: str) -> str:
    """Build one syllable, drawing a random letter for every placeholder."""
    letters = []
    for symbol in pattern:
        if symbol == "С":
            letters.append(random.choice(CONSONANTS))
        elif symbol == "Г":
            letters.append(random.choice(VOWELS))
    return "".join(letters)


def generate_surname(female: bool) -> str:
    """Generate a surname from the specified syllable scheme."""
    first_pattern = random.choice(FIRST_PATTERNS)
    penultimate_pattern = random.choice(PENULTIMATE_PATTERNS)
    first_part = random_syllable(first_pattern)
    penultimate_part = random_syllable(penultimate_pattern)
    ending = random.choice(("ина", "ова") if female else ("ин", "ов"))
    return first_part + penultimate_part + ending


def generate_person() -> dict[str, str]:
    """Generate all parts of one gender-consistent name."""
    female = random.choice((False, True))
    if female:
        name = random.choice(FEMALE_NAMES)
        patronymic = random.choice(FEMALE_PATRONYMICS)
    else:
        name = random.choice(MALE_NAMES)
        patronymic = random.choice(MALE_PATRONYMICS)
    return {"F": generate_surname(female), "I": name, "O": patronymic}


def parse_format(value: str) -> str:
    normalized = value.upper()
    if not normalized or any(letter not in "FIO" for letter in normalized):
        raise argparse.ArgumentTypeError("format must contain only F, I, and O")
    if len(set(normalized)) != len(normalized):
        raise argparse.ArgumentTypeError("format must not repeat F, I, or O")
    return normalized


def positive_count(value: str) -> int:
    try:
        count = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("N must be an integer") from error
    if count <= 0:
        raise argparse.ArgumentTypeError("N must be greater than zero")
    return count


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate random Russian names.")
    parser.add_argument("N", nargs="?", type=positive_count, default=10,
                        help="number of names to generate (default: 10)")
    parser.add_argument("--format", default="FIO", type=parse_format,
                        help="name part order using F, I, and O (default: FIO)")
    parser.add_argument("--output", default="names.txt",
                        help="UTF-8 output file (default: names.txt)")
    return parser


def main() -> int:
    configure_console()
    args = build_parser().parse_args()
    lines = [" ".join(generate_person()[part] for part in args.format)
             for _ in range(args.N)]
    try:
        with open(args.output, "w", encoding="utf-8", newline="\n") as output:
            output.write("\n".join(lines) + "\n")
    except OSError as error:
        print(f"Error: cannot write output file: {error}", file=sys.stderr)
        return 1
    print(f"Generated {args.N} name(s) in {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
