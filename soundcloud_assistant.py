
import csv
from pathlib import Path
from urllib.parse import quote_plus

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

BASE_DIR = Path(__file__).resolve().parent
TRACKS_FILE = BASE_DIR / "tracks.txt"
PROGRESS_FILE = BASE_DIR / "soundcloud_progress.csv"

CDP_URL = "http://127.0.0.1:9222"


def load_tracks():
    lines = TRACKS_FILE.read_text(encoding="utf-8-sig").splitlines()
    nonempty = [line.strip() for line in lines if line.strip()]

    # Первые три строки — название плейлиста и метаданные.
    tracks = nonempty[3:]

    if len(tracks) != 3034:
        raise ValueError(
            f"Ожидалось 3034 трека, найдено: {len(tracks)}"
        )

    return tracks


def load_progress():
    if not PROGRESS_FILE.exists():
        with PROGRESS_FILE.open(
            "w", encoding="utf-8-sig", newline=""
        ) as f:
            writer = csv.writer(f)
            writer.writerow(["number", "track", "status"])
        return {}

    with PROGRESS_FILE.open(
        "r", encoding="utf-8-sig", newline=""
    ) as f:
        return {
            int(row["number"]): row["status"]
            for row in csv.DictReader(f)
        }


def save_progress(number, track, status):
    with PROGRESS_FILE.open(
       "a", encoding="utf-8", newline=""
    ) as f:
        writer = csv.writer(f)
        writer.writerow([number, track, status])


def main():
    tracks = load_tracks()
    progress = load_progress()

    print(f"Всего треков: {len(tracks)}")
    print(f"Уже обработано: {len(progress)}")
    print("Подключаемся к открытому Яндекс Браузеру...")

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(CDP_URL)

        pages = [
            page
            for context in browser.contexts
            for page in context.pages
            if "soundcloud.com" in page.url
        ]

        if not pages:
            raise RuntimeError(
                "Не найдена открытая вкладка SoundCloud."
            )

        page = pages[0]

        print("Подключение успешно.")
        print("Работаем в одной вкладке.")
        print("")

        for index, track in enumerate(tracks, start=1):

            if index in progress:
                continue

            print("=" * 55)
            print(f"ТРЕК {index}/{len(tracks)}")
            print(track)

            search_url = (
                "https://soundcloud.com/search?q="
                + quote_plus(track)
            )

            try:
                page.goto(
                    search_url,
                    wait_until="domcontentloaded",
                    timeout=30000
                )
                page.wait_for_timeout(2500)

            except PlaywrightTimeoutError:
                print("Поиск загружается слишком долго.")
                print("Проверь браузер и попробуй снова.")
                break

            print("")
            print("Добавь найденный трек в свой плейлист.")
            print("")
            print("[Enter] — добавил")
            print("[S]     — пропустить")
            print("[Q]     — остановить")

            answer = input("Твой выбор: ").strip().lower()

            if answer == "q":
                print("Останавливаемся. Прогресс сохранён.")
                break

            elif answer == "s":
                save_progress(index, track, "skipped")
                progress[index] = "skipped"
                print("Пропущено.")

            elif answer == "":
                save_progress(index, track, "added")
                progress[index] = "added"
                print("Добавление подтверждено.")

            else:
                print("Неизвестная команда. Этот трек не записан.")

        added = sum(v == "added" for v in progress.values())
        skipped = sum(v == "skipped" for v in progress.values())

        print("")
        print("=" * 55)
        print("СЕАНС ЗАВЕРШЁН")
        print(f"Добавлено: {added}")
        print(f"Пропущено: {skipped}")
        print(f"Всего обработано: {len(progress)}")
        print(f"Осталось: {len(tracks) - len(progress)}")

        # Не закрываем браузер — он остаётся открытым.


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nОстановлено пользователем.")
    except Exception as error:
        print(f"\nОшибка: {error}")
