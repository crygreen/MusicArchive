
import csv
import json
import time
import urllib.parse
import urllib.request
from difflib import SequenceMatcher
from pathlib import Path

API = "https://api.audius.co/v1/tracks/search"
INPUT = Path("tracks.txt")
OUTPUT = Path("audius_test_results.csv")

def similarity(a, b):
    return SequenceMatcher(
        None, a.lower().strip(), b.lower().strip()
    ).ratio() * 100

def parse_track(line):
    for separator in (" — ", " – ", " - "):
        if separator in line:
            artist, title = line.split(separator, 1)
            return artist.strip(), title.strip()
    return None, None

def search_track(artist, title):
    query = f"{artist} {title}"
    params = urllib.parse.urlencode({
        "query": query,
        "limit": 10
    })
    url = f"{API}?{params}"

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "MusicArchive/1.0"}
    )

    with urllib.request.urlopen(request, timeout=25) as response:
        data = json.loads(response.read().decode("utf-8"))

    return data.get("data", [])

with INPUT.open("r", encoding="utf-8-sig") as file:
    lines = file.readlines()

tracks = []

for line in lines:
    artist, title = parse_track(line.strip())
    if artist and title:
        tracks.append((artist, title))

results = []

for index, (artist, title) in enumerate(tracks[:20], 1):
    print(f"\n[{index}/20] {artist} — {title}")

    try:
        candidates = search_track(artist, title)

        ranked = []

        for item in candidates:
            found_title = item.get("title", "")
            user = item.get("user") or {}
            found_artist = user.get("name", "")

            title_score = similarity(title, found_title)
            artist_score = similarity(artist, found_artist)
            total_score = title_score * 0.65 + artist_score * 0.35

            ranked.append({
                "original_artist": artist,
                "original_title": title,
                "found_artist": found_artist,
                "found_title": found_title,
                "title_score": round(title_score),
                "artist_score": round(artist_score),
                "total_score": round(total_score),
                "downloadable": item.get("is_downloadable", False),
                "streamable": item.get("is_streamable", False),
                "url": item.get("permalink", ""),
                "track_id": item.get("id", "")
            })

        ranked.sort(key=lambda x: x["total_score"], reverse=True)

        if not ranked:
            print("Совпадений нет")

        for candidate in ranked[:3]:
            results.append(candidate)
            print(
                f"{candidate['total_score']}% | "
                f"{candidate['found_artist']} — "
                f"{candidate['found_title']} | "
                f"Скачивание: {candidate['downloadable']}"
            )

    except Exception as error:
        print(f"Ошибка: {error}")

    time.sleep(1)

if results:
    with OUTPUT.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=results[0].keys()
        )
        writer.writeheader()
        writer.writerows(results)

print(f"\nГотово. Найдено вариантов: {len(results)}")
print(f"Результат: {OUTPUT}")
