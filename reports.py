import json
import os
from datetime import datetime
from typing import List, Dict, Tuple


def occupancy_report(showtimes: List[Dict], seat_maps: Dict, bookings: List[Dict]) -> Dict:
    """Return occupancy metrics per showtime."""
    report = {}
    booking_by_showtime = {}
    for b in bookings:
        if b.get("status") != "active":
            continue
        sid = b.get("showtime_id")
        booking_by_showtime.setdefault(sid, 0)
        booking_by_showtime[sid] += 1

    for st in showtimes:
        sid = st.get("id")
        seat_map = seat_maps.get(sid, {})
        total_seats = len(seat_map)
        reserved = sum(1 for seat in seat_map.values() if seat.get("status") == "reserved")
        occupancy = (reserved / total_seats) if total_seats else 0
        report[sid] = {
            "screen": st.get("screen"),
            "datetime": st.get("datetime"),
            "total_seats": total_seats,
            "reserved": reserved,
            "occupancy": round(occupancy * 100, 2),
            "bookings": booking_by_showtime.get(sid, 0),
        }
    return report


def _parse_dt(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return datetime.min


def revenue_summary(bookings: List[Dict], period: Tuple[str, str]) -> Dict:
    """Summaries revenue for bookings within [start, end]."""
    start, end = period
    start_dt = _parse_dt(start)
    end_dt = _parse_dt(end)
    total = 0.0
    count = 0
    for b in bookings:
        show_dt = _parse_dt(b.get("showtime_snapshot", {}).get("datetime", ""))
        if not (start_dt <= show_dt <= end_dt):
            continue
        if b.get("status") != "active":
            continue
        total += float(b.get("pricing", {}).get("total", 0))
        count += 1
    return {"total_revenue": round(total, 2), "booking_count": count, "period": {"start": start, "end": end}}


def top_movies(bookings: List[Dict], showtimes: List[Dict], limit: int = 5) -> List[Dict]:
    """Return top movies by number of seats sold."""
    st_by_id = {st.get("id"): st for st in showtimes}
    counter = {}
    for b in bookings:
        if b.get("status") != "active":
            continue
        st = st_by_id.get(b.get("showtime_id"))
        if not st:
            continue
        movie_id = st.get("movie_id")
        counter.setdefault(movie_id, 0)
        counter[movie_id] += len(b.get("seats", []))
    ranked = sorted(counter.items(), key=lambda kv: kv[1], reverse=True)[:limit]
    return [{"movie_id": movie_id, "seats_sold": seats} for movie_id, seats in ranked]


def export_report(report: Dict, filename: str) -> str:
    """Save report dictionary to json file."""
    os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    return filename


