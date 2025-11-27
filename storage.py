import json
import os
from datetime import datetime
from typing import Tuple, List, Dict, Any

from movies import load_movies, save_movies
from seating import initialize_seat_map


DATA_FILES = {
    "movies": "data/movies.json",
    "showtimes": "data/showtimes.json",
    "bookings": "data/bookings.json",
}


def load_state(base_dir: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Dict[str, str]], List[Dict[str, Any]]]:
    movies_path = os.path.join(base_dir, DATA_FILES["movies"])
    showtimes_path = os.path.join(base_dir, DATA_FILES["showtimes"])
    bookings_path = os.path.join(base_dir, DATA_FILES["bookings"])

    movies = load_movies(movies_path)
    try:
        with open(showtimes_path, "r", encoding="utf-8") as f:
            showtimes = json.load(f)
    except FileNotFoundError:
        showtimes = []

    seat_maps: Dict[str, Dict[str, str]] = {}
    for showtime in showtimes:
        seat_map = showtime.get("seat_map")
        if not seat_map:
            seat_map = initialize_seat_map(showtime.get("screen_config", {"rows": 5, "cols": 8}))
        seat_maps[showtime["id"]] = seat_map
        showtime["seat_map"] = seat_map

    try:
        with open(bookings_path, "r", encoding="utf-8") as f:
            bookings = json.load(f)
    except FileNotFoundError:
        bookings = []

    return movies, showtimes, seat_maps, bookings


def save_state(
    base_dir: str, showtimes: List[Dict[str, Any]], seat_maps: Dict[str, Dict[str, str]], bookings: List[Dict[str, Any]]
) -> None:
    movies_path = os.path.join(base_dir, DATA_FILES["movies"])
    showtimes_path = os.path.join(base_dir, DATA_FILES["showtimes"])
    bookings_path = os.path.join(base_dir, DATA_FILES["bookings"])

    current_movies = load_movies(movies_path)
    save_movies(movies_path, current_movies)

    for showtime in showtimes:
        showtime["seat_map"] = seat_maps.get(showtime["id"], showtime.get("seat_map", {}))
    os.makedirs(os.path.dirname(showtimes_path), exist_ok=True)
    with open(showtimes_path, "w", encoding="utf-8") as f:
        json.dump(showtimes, f, indent=2, ensure_ascii=False)

    with open(bookings_path, "w", encoding="utf-8") as f:
        json.dump(bookings, f, indent=2, ensure_ascii=False)


def backup_state(base_dir: str, backup_dir: str) -> str:
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    target_dir = os.path.join(backup_dir, f"backup_{timestamp}")
    os.makedirs(target_dir, exist_ok=True)
    for key, rel_path in DATA_FILES.items():
        src = os.path.join(base_dir, rel_path)
        dest = os.path.join(target_dir, os.path.basename(rel_path))
        if os.path.exists(src):
            with open(src, "r", encoding="utf-8") as f_src:
                data = json.load(f_src)
            with open(dest, "w", encoding="utf-8") as f_dest:
                json.dump(data, f_dest, indent=2, ensure_ascii=False)
    return target_dir


def validate_showtime(showtime: Dict[str, Any]) -> bool:
    required_fields = ["id", "movie_id", "start_time", "screen"]
    return all(field in showtime for field in required_fields)
