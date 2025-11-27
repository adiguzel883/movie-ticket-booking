from string import ascii_uppercase
from typing import Dict, List


def initialize_seat_map(screen_config: Dict[str, int]) -> Dict[str, str]:
    rows = screen_config.get("rows", 5)
    cols = screen_config.get("cols", 8)
    seat_map: Dict[str, str] = {}
    for row_index in range(rows):
        row_letter = ascii_uppercase[row_index]
        for col in range(1, cols + 1):
            seat_code = f"{row_letter}{col}"
            seat_map[seat_code] = "available"
    return seat_map


def render_seat_map(seat_map: Dict[str, str]) -> str:
    if not seat_map:
        return "No seats configured"
    rows: Dict[str, List[str]] = {}
    for seat_code, status in seat_map.items():
        row = seat_code[0]
        rows.setdefault(row, []).append(seat_code)
    rendered_rows = []
    for row in sorted(rows.keys()):
        seats = sorted(rows[row], key=lambda code: int(code[1:]))
        row_display = " ".join("X" if seat_map[s] != "available" else "O" for s in seats)
        rendered_rows.append(f"{row}: {row_display}")
    return "\n".join(rendered_rows)


def is_seat_available(seat_map: Dict[str, str], seat_code: str) -> bool:
    return seat_map.get(seat_code) == "available"


def reserve_seat(seat_map: Dict[str, str], seat_code: str) -> bool:
    if is_seat_available(seat_map, seat_code):
        seat_map[seat_code] = "reserved"
        return True
    return False


def release_seat(seat_map: Dict[str, str], seat_code: str) -> bool:
    if seat_map.get(seat_code) == "reserved":
        seat_map[seat_code] = "available"
        return True
    return False
