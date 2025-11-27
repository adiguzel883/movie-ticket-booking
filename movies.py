import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any


def load_movies(path: str) -> List[Dict[str, Any]]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_movies(path: str, movies: List[Dict[str, Any]]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(movies, f, indent=2, ensure_ascii=False)


def add_movie(movies: List[Dict[str, Any]], movie_data: Dict[str, Any]) -> Dict[str, Any]:
    movie = {
        "id": movie_data.get("id") or str(uuid.uuid4()),
        "title": movie_data["title"],
        "duration": movie_data.get("duration", 120),
        "rating": movie_data.get("rating", "PG"),
    }
    movies.append(movie)
    return movie


def schedule_showtime(showtimes: List[Dict[str, Any]], showtime_data: Dict[str, Any]) -> Dict[str, Any]:
    showtime = {
        "id": showtime_data.get("id") or str(uuid.uuid4()),
        "movie_id": showtime_data["movie_id"],
        "start_time": showtime_data["start_time"],
        "screen": showtime_data.get("screen", "Screen 1"),
        "pricing": showtime_data.get("pricing", {"standard": 10.0}),
        "screen_config": showtime_data.get(
            "screen_config", {"rows": 5, "cols": 8, "aisles": []}
        ),
        "seat_map": showtime_data.get("seat_map"),
    }
    showtimes.append(showtime)
    return showtime


def list_showtimes(
    showtimes: List[Dict[str, Any]], movie_id: Optional[str] = None, date: Optional[str] = None
) -> List[Dict[str, Any]]:
    results = []
    for showtime in showtimes:
        if movie_id and showtime.get("movie_id") != movie_id:
            continue
        if date:
            show_date = showtime.get("start_time", "")[:10]
            if show_date != date:
                continue
        results.append(showtime)
    return results


def update_showtime(
    showtimes: List[Dict[str, Any]], showtime_id: str, updates: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    for showtime in showtimes:
        if showtime.get("id") == showtime_id:
            showtime.update(updates)
            showtime["updated_at"] = datetime.utcnow().isoformat()
            return showtime
    return None
