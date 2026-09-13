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
CONSONANT_WEIGHTS: Final[tuple[float, ...]] = (
    1.59, 4.54, 1.70, 2.98, 0.94, 1.65, 3.49, 4.40, 3.21,
    6.70, 2.81, 4.73, 5.47, 6.26, 0.26, 0.97, 0.48, 1.44,
    0.73, 0.36,
)
VOWEL_WEIGHTS: Final[tuple[float, ...]] = (
    8.01, 8.45, 7.35, 10.97, 2.62, 0.32, 0.64, 2.01,
)
# Ordered consonant pairs that are too unnatural for generated Russian names.
RARE_CONSONANT_PAIRS: Final[frozenset[str]] = frozenset({
    "бж", "гж", "гз", "гц", "гш", "гщ", "жз", "жп", "жф",
    "жх", "жц", "жщ", "кг", "кж", "кщ", "нж", "пж", "пщ", "фж",
    "фщ", "хж", "хщ", "цж", "цщ", "чж", "чщ", "шж", "шщ", "щж",
    "щш", "щц", "мп", "лн",
})

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


def random_syllable(pattern: str, previous_letter: str = "") -> str:
    """Build a syllable while avoiding disallowed adjacent consonant pairs."""
    letters = []
    previous = previous_letter
    for symbol in pattern:
        if symbol == "С":
            available = tuple(
                (letter, weight)
                for letter, weight in zip(CONSONANTS, CONSONANT_WEIGHTS)
                if letter != previous
                and previous + letter not in RARE_CONSONANT_PAIRS
            )
            consonants, weights = zip(*available)
            letter = random.choices(consonants, weights=weights, k=1)[0]
            letters.append(letter)
            previous = letter
        elif symbol == "Г":
            letter = random.choices(VOWELS, weights=VOWEL_WEIGHTS, k=1)[0]
            letters.append(letter)
            previous = letter
    return "".join(letters)


def generate_surname(female: bool) -> str:
    """Generate a surname from the specified syllable scheme."""
    first_pattern = random.choice(FIRST_PATTERNS)
    penultimate_pattern = random.choice(PENULTIMATE_PATTERNS)
    first_part = random_syllable(first_pattern)
    penultimate_part = random_syllable(penultimate_pattern, first_part[-1:])
    ending = random.choice(("ина", "ова") if female else ("ин", "ов"))
    return (first_part + penultimate_part + ending).capitalize()


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
    lines = []
    for _ in range(args.N):
        person = generate_person()
        lines.append(" ".join(person[part] for part in args.format))
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
