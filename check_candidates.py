
import csv
import re
from pathlib import Path
from difflib import SequenceMatcher

INPUT = "search_results_improved.csv"
OUTPUT = "checked_candidates.csv"


def normalize(text):
    text = (text or "").lower()
    text = re.sub(r"\[[^\]]*\]", " ", text)
    text = re.sub(r"[^a-zа-яё0-9]", " ", text)
    return " ".join(text.split())


def similarity(a, b):
    return SequenceMatcher(
        None, normalize(a), normalize(b)
    ).ratio() * 100


def clean_creator(value):
    if isinstance(value, list):
        return " ".join(str(x) for x in value)
    return str(value or "")


if not Path(INPUT).exists():
    print("Не найден файл:", INPUT)
    raise SystemExit

accepted = []
rejected = []

with open(INPUT, encoding="utf-8-sig", newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
        original = row.get("original_track", "")
        found_title = row.get("found_title", "")
        found_artist = clean_creator(row.get("found_artist", ""))

        if " - " in original:
            artist, title = original.rsplit(" - ", 1)
        else:
            artist, title = "", original

        title_score = similarity(title, found_title)
        artist_score = similarity(artist, found_artist)

        # Сильное совпадение названия и исполнителя
        if title_score >= 85 and artist_score >= 65:
            status = "Проверить: вероятное совпадение"

        # Название совпадает, но исполнитель неизвестен
        elif title_score >= 90 and not found_artist.strip():
            status = "Проверить вручную: исполнитель неизвестен"

        # Остальные результаты не считаем совпадениями
        else:
            status = "Слабое совпадение"

        row["checked_title_score"] = round(title_score)
        row["checked_artist_score"] = round(artist_score)
        row["status"] = status

        if status != "Слабое совпадение":
            accepted.append(row)
        else:
            rejected.append(row)

fields = [
    "original_track",
    "found_title",
    "found_artist",
    "title_score",
    "artist_score",
    "total_score",
    "search_type",
    "identifier",
    "license",
    "rights",
    "archive_url",
    "checked_title_score",
    "checked_artist_score",
    "status"
]

with open(OUTPUT, "w", encoding="utf-8-sig", newline="") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=fields,
        extrasaction="ignore"
    )
    writer.writeheader()
    writer.writerows(accepted)

print("Проверка завершена.")
print("Кандидатов для ручной проверки:", len(accepted))
print("Отсеяно:", len(rejected))
print("Результат:", OUTPUT)
print("\nКандидаты:")

for row in accepted:
    print(
        row["original_track"],
        "->",
        row["found_artist"],
        "—",
        row["found_title"],
        "|",
        row["status"]
    )
