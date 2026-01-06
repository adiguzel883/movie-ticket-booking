import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Optional


def _ensure_parent(path: str) -> None:
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)


def load_movies(path: str) -> List[Dict]:
    """Load movies from JSON file. Returns empty list if file is missing."""
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else []


def save_movies(path: str, movies: List[Dict]) -> None:
    """Persist movie list to disk."""
    _ensure_parent(path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(movies, f, indent=2, ensure_ascii=False)


def add_movie(movies: List[Dict], movie_data: Dict) -> Dict:
    """Add a movie to catalog and return the created record."""
    movie = {
        "id": movie_data.get("id") or str(uuid.uuid4())[:8],
        "title": movie_data.get("title", "Untitled"),
        "genre": movie_data.get("genre", "Unknown"),
        "duration_min": movie_data.get("duration_min", 90),
        "rating": movie_data.get("rating", "NR"),
        "description": movie_data.get("description", ""),
        "created_at": movie_data.get("created_at")
        or datetime.utcnow().isoformat(timespec="seconds"),
    }
    movies.append(movie)
    return movie


def schedule_showtime(showtimes: List[Dict], showtime_data: Dict) -> Dict:
    """Create a new showtime entry."""
    showtime = {
        "id": showtime_data.get("id") or str(uuid.uuid4())[:10],
        "movie_id": showtime_data["movie_id"],
        "screen": showtime_data.get("screen", "Screen 1"),
        "datetime": showtime_data.get("datetime")
        or datetime.utcnow().isoformat(timespec="minutes"),
        "language": showtime_data.get("language", "OV"),
        "pricing": showtime_data.get("pricing")
        or {"standard": 10.0, "premium": 14.0},
        "screen_config": showtime_data.get("screen_config")
        or {"rows": list("ABCDEFGH"), "seats_per_row": 12, "premium_rows": ["A", "B"]},
    }
    showtimes.append(showtime)
    return showtime


def list_showtimes(
    showtimes: List[Dict],
    movie_id: Optional[str] = None,
    date: Optional[str] = None,
    screen: Optional[str] = None,
) -> List[Dict]:
    """Filter showtimes by movie, date (YYYY-MM-DD), or screen."""
    results = []
    for st in showtimes:
        if movie_id and st.get("movie_id") != movie_id:
            continue
        if date and not st.get("datetime", "").startswith(date):
            continue
        if screen and st.get("screen") != screen:
            continue
        results.append(st)
    return results


def update_showtime(showtimes: List[Dict], showtime_id: str, updates: Dict) -> Optional[Dict]:
    """Update a showtime by id; returns the updated record or None if not found."""
    for st in showtimes:
        if st.get("id") == showtime_id:
            for key, value in updates.items():
                if key == "id":
                    continue
                st[key] = value
            st["updated_at"] = datetime.utcnow().isoformat(timespec="seconds")
            return st
    return None


