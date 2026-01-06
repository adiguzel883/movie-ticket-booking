from typing import Dict


def initialize_seat_map(screen_config: Dict) -> Dict:
    """Generate seat map based on screen configuration."""
    rows = screen_config.get("rows") or list("ABCDEFGH")
    seats_per_row = int(screen_config.get("seats_per_row", 12))
    premium_rows = set(screen_config.get("premium_rows", []))
    seat_map: Dict[str, Dict] = {}
    for row in rows:
        for num in range(1, seats_per_row + 1):
            code = f"{row}{num}"
            zone = "premium" if row in premium_rows else "standard"
            seat_map[code] = {"row": row, "number": num, "zone": zone, "status": "available"}
    return seat_map


def render_seat_map(seat_map: Dict) -> str:
    """Return a human-friendly seat grid with occupancy markers."""
    rows = {}
    for code, meta in seat_map.items():
        rows.setdefault(meta["row"], {})[meta["number"]] = meta["status"]
    lines = []
    for row in sorted(rows.keys()):
        seats = rows[row]
        markers = []
        for num in sorted(seats.keys()):
            status = seats[num]
            marker = "O" if status == "available" else "X"
            markers.append(f"{marker}")
        lines.append(f"{row}: {' '.join(markers)}")
    return "\n".join(lines)


def is_seat_available(seat_map: Dict, seat_code: str) -> bool:
    return seat_code in seat_map and seat_map[seat_code]["status"] == "available"


def reserve_seat(seat_map: Dict, seat_code: str) -> Dict:
    if not is_seat_available(seat_map, seat_code):
        raise ValueError(f"Seat {seat_code} is not available")
    seat_map[seat_code]["status"] = "reserved"
    return seat_map


def release_seat(seat_map: Dict, seat_code: str) -> Dict:
    if seat_code in seat_map:
        seat_map[seat_code]["status"] = "available"
    return seat_map


