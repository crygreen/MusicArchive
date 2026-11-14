
import csv
import json
import urllib.request
import time

INPUT = "checked_candidates.csv"
OUTPUT = "archive_full_metadata.csv"

def value_to_text(value):
    if isinstance(value, list):
        return "; ".join(str(x) for x in value)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)
    return str(value or "")

def get_metadata(identifier):
    url = f"https://archive.org/metadata/{identifier}"

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "MusicArchiveResearch/1.0"}
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))

with open(INPUT, encoding="utf-8-sig", newline="") as file:
    candidates = list(csv.DictReader(file))

results = []
checked = set()

for candidate in candidates:
    identifier = candidate.get("identifier", "").strip()

    if not identifier or identifier in checked:
        continue

    checked.add(identifier)

    print("\nПроверяю:", identifier)

    try:
        data = get_metadata(identifier)
        meta = data.get("metadata", {})

        fields_to_check = [
            "title",
            "creator",
            "uploader",
            "date",
            "publicdate",
            "addeddate",
            "description",
            "rights",
            "license",
            "licenseurl",
            "source",
            "mediatype",
            "collection",
            "identifier"
        ]

        row = {
            "original_track": candidate.get("original_track", ""),
            "archive_page": f"https://archive.org/details/{identifier}"
        }

        for field in fields_to_check:
            row[field] = value_to_text(meta.get(field, ""))

        results.append(row)

        print("Название:", row["title"])
        print("Автор:", row["creator"] or "не указан")
        print("Загрузчик:", row["uploader"] or "не указан")
        print("Дата:", row["date"] or "не указана")
        print("Лицензия:", row["licenseurl"] or row["license"] or "не указана")
        print("Права:", row["rights"] or "не указаны")
        print("Описание:", row["description"][:250] or "нет")

    except Exception as error:
        print("Ошибка:", error)

    time.sleep(1)

fields = [
    "original_track",
    "title",
    "creator",
    "uploader",
    "date",
    "publicdate",
    "addeddate",
    "description",
    "rights",
    "license",
    "licenseurl",
    "source",
    "mediatype",
    "collection",
    "identifier",
    "archive_page"
]

with open(OUTPUT, "w", encoding="utf-8-sig", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=fields)
    writer.writeheader()
    writer.writerows(results)

print("\nПроверка завершена.")
print("Записей проверено:", len(results))
print("Файл:", OUTPUT)
