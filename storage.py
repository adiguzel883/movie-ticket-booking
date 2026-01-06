import json
import os
import shutil
from datetime import datetime
from typing import List, Dict, Tuple


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def load_state(base_dir: str) -> Tuple[List, Dict, List]:
    """Load showtimes, seat_maps, and bookings."""
    showtimes_path = os.path.join(base_dir, "showtimes.json")
    bookings_path = os.path.join(base_dir, "bookings.json")

    showtimes: List[Dict] = []
    seat_maps: Dict = {}
    bookings: List[Dict] = []

    if os.path.exists(showtimes_path):
        with open(showtimes_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                showtimes = data.get("showtimes", [])
                seat_maps = data.get("seat_maps", {})
            elif isinstance(data, list):
                showtimes = data

    if os.path.exists(bookings_path):
        with open(bookings_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            bookings = data if isinstance(data, list) else []

    return showtimes, seat_maps, bookings


def save_state(base_dir: str, showtimes: List, seat_maps: Dict, bookings: List) -> None:
    """Persist showtimes, seat maps, and bookings to disk."""
    _ensure_dir(base_dir)
    with open(os.path.join(base_dir, "showtimes.json"), "w", encoding="utf-8") as f:
        json.dump({"showtimes": showtimes, "seat_maps": seat_maps}, f, indent=2, ensure_ascii=False)
    with open(os.path.join(base_dir, "bookings.json"), "w", encoding="utf-8") as f:
        json.dump(bookings, f, indent=2, ensure_ascii=False)


def backup_state(base_dir: str, showtimes: List, seat_maps: Dict, bookings: List, backup_dir: str) -> List[str]:
    """Create timestamped backup files; returns backup file paths."""
    _ensure_dir(backup_dir)
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    showtime_file = os.path.join(backup_dir, f"showtimes-{timestamp}.json")
    booking_file = os.path.join(backup_dir, f"bookings-{timestamp}.json")
    seatmap_file = os.path.join(backup_dir, f"seatmaps-{timestamp}.json")

    with open(showtime_file, "w", encoding="utf-8") as f:
        json.dump(showtimes, f, indent=2, ensure_ascii=False)
    with open(booking_file, "w", encoding="utf-8") as f:
        json.dump(bookings, f, indent=2, ensure_ascii=False)
    with open(seatmap_file, "w", encoding="utf-8") as f:
        json.dump(seat_maps, f, indent=2, ensure_ascii=False)

    # copy movies file if exists to keep aligned
    movies_src = os.path.join(base_dir, "movies.json")
    if os.path.exists(movies_src):
        shutil.copy(movies_src, os.path.join(backup_dir, f"movies-{timestamp}.json"))

    return [showtime_file, booking_file, seatmap_file]


def validate_showtime(showtime: Dict) -> bool:
    """Light validation to prevent incomplete records."""
    required = ["id", "movie_id", "screen", "datetime", "pricing"]
    return all(key in showtime for key in required)


