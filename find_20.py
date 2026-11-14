
import json
import csv
import urllib.parse
import urllib.request
import time
from difflib import SequenceMatcher

API = "https://archive.org/advancedsearch.php"

with open("tracks.txt", encoding="utf-8-sig") as file:
    tracks = []

    for line in file:
        line = line.strip()

        if not line or line.startswith(
            ("Плейлист:", "Владелец:", "Треков:")
        ):
            continue

        if " - " not in line:
            continue

        artist, title = line.rsplit(" - ", 1)

        if title.strip() and artist.strip():
            tracks.append((artist.strip(), title.strip()))

tracks = tracks[:20]


def search_archive(query):
    params = {
        "q": query,
        "fl[]": [
            "identifier",
            "title",
            "creator",
            "licenseurl",
            "rights"
        ],
        "rows": 10,
        "output": "json"
    }

    url = API + "?" + urllib.parse.urlencode(params, doseq=True)

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "MusicArchiveResearch/1.0"}
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.loads(response.read().decode("utf-8"))

    return data["response"]["docs"]


def similarity(a, b):
    a = (a or "").lower().strip()
    b = (b or "").lower().strip()
    return round(SequenceMatcher(None, a, b).ratio() * 100)


results = []

for number, (artist, title) in enumerate(tracks, 1):
    print(f"\n[{number}/20] {artist} — {title}")

    candidates = []
    seen = set()

    # Сначала ищем по названию и исполнителю
    queries = [
        f'mediatype:audio AND title:"{title}" AND creator:"{artist}"',
        f'mediatype:audio AND title:"{title}"'
    ]

    for query_number, query in enumerate(queries, 1):
        try:
            found = search_archive(query)

            for item in found:
                identifier = item.get("identifier", "")

                if not identifier or identifier in seen:
                    continue

                seen.add(identifier)

                found_title = item.get("title", "")
                found_artist = item.get("creator", "")

                title_score = similarity(title, found_title)
                artist_score = similarity(artist, found_artist)

                total_score = round(
                    title_score * 0.7 + artist_score * 0.3
                )

                candidates.append({
                    "original_track": f"{artist} - {title}",
                    "found_title": found_title,
                    "found_artist": found_artist,
                    "title_score": title_score,
                    "artist_score": artist_score,
                    "total_score": total_score,
                    "search_type": (
                        "artist+title" if query_number == 1
                        else "title only"
                    ),
                    "identifier": identifier,
                    "license": item.get("licenseurl", ""),
                    "rights": item.get("rights", ""),
                    "archive_url": (
                        f"https://archive.org/details/{identifier}"
                    )
                })

        except Exception as error:
            print("Ошибка поиска:", error)

        time.sleep(1)

    candidates.sort(
        key=lambda x: x["total_score"],
        reverse=True
    )

    if not candidates:
        print("Кандидатов нет")
    else:
        for item in candidates[:5]:
            results.append(item)

            print(
                f"  {item['total_score']}% | "
                f"{item['found_artist']} — {item['found_title']}"
            )

            print("  Лицензия:", item["license"] or "не указана")

    time.sleep(1)


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
    "archive_url"
]

with open(
    "search_results_improved.csv",
    "w",
    newline="",
    encoding="utf-8-sig"
) as file:
    writer = csv.DictWriter(file, fieldnames=fields)
    writer.writeheader()
    writer.writerows(results)

print("\nПоиск завершён.")
print("Кандидатов:", len(results))
print("Файл: search_results_improved.csv")
