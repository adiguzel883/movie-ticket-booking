import json
from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, List, Any


def occupancy_report(showtimes: List[Dict[str, Any]], seat_maps: Dict[str, Dict[str, str]], bookings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    report = []
    for showtime in showtimes:
        seat_map = seat_maps.get(showtime["id"], {})
        total_seats = len(seat_map)
        reserved = sum(1 for status in seat_map.values() if status != "available")
        occupancy = round((reserved / total_seats) * 100, 2) if total_seats else 0
        report.append(
            {
                "showtime_id": showtime["id"],
                "movie_id": showtime["movie_id"],
                "screen": showtime.get("screen"),
                "start_time": showtime.get("start_time"),
                "reserved": reserved,
                "total_seats": total_seats,
                "occupancy_pct": occupancy,
            }
        )
    return report


def revenue_summary(bookings: List[Dict[str, Any]], period: str) -> Dict[str, float]:
    summary: Dict[str, float] = defaultdict(float)
    for booking in bookings:
        if booking.get("status") != "active":
            continue
        date_str = booking.get("created_at", "")
        if not date_str:
            continue
        created = datetime.fromisoformat(date_str)
        if period == "daily":
            key = created.strftime("%Y-%m-%d")
        elif period == "weekly":
            key = f"{created.isocalendar().year}-W{created.isocalendar().week:02d}"
        elif period == "monthly":
            key = created.strftime("%Y-%m")
        else:
            key = "all_time"
        summary[key] += float(booking.get("total", 0))
    return dict(summary)


def top_movies(bookings: List[Dict[str, Any]], showtimes: List[Dict[str, Any]], limit: int = 5) -> List[Dict[str, Any]]:
    movie_counts: Counter[str] = Counter()
    showtime_lookup = {s["id"]: s for s in showtimes}
    for booking in bookings:
        if booking.get("status") != "active":
            continue
        showtime_id = booking.get("showtime_id")
        movie_id = showtime_lookup.get(showtime_id, {}).get("movie_id")
        if movie_id:
            movie_counts[movie_id] += len(booking.get("seats", []))
    top = movie_counts.most_common(limit)
    return [{"movie_id": movie_id, "seats_sold": count} for movie_id, count in top]


def export_report(report: Any, filename: str) -> str:
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    return filename
