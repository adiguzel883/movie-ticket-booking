import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from seating import is_seat_available, reserve_seat, release_seat, initialize_seat_map


def _find_showtime(showtimes: List[Dict[str, Any]], showtime_id: str) -> Optional[Dict[str, Any]]:
    for showtime in showtimes:
        if showtime.get("id") == showtime_id:
            return showtime
    return None


def create_booking(
    showtimes: List[Dict[str, Any]], seat_maps: Dict[str, Dict[str, str]], booking_data: Dict[str, Any]
) -> Dict[str, Any]:
    showtime_id = booking_data["showtime_id"]
    showtime = _find_showtime(showtimes, showtime_id)
    if not showtime:
        raise ValueError("Showtime not found")

    seat_map = seat_maps.get(showtime_id)
    if not seat_map:
        seat_map = initialize_seat_map(showtime.get("screen_config", {"rows": 5, "cols": 8}))
        seat_maps[showtime_id] = seat_map
        showtime["seat_map"] = seat_map

    seats = booking_data["seats"]
    unavailable = [s for s in seats if not is_seat_available(seat_map, s)]
    if unavailable:
        raise ValueError(f"Seats already reserved or invalid: {', '.join(unavailable)}")

    for seat in seats:
        if not reserve_seat(seat_map, seat):
            raise ValueError(f"Seat {seat} is not available")

    total = calculate_booking_total(
        seats,
        booking_data.get("pricing", showtime.get("pricing", {"standard": 10.0})),
        booking_data.get("tax_rate", 0.18),
        booking_data.get("discounts"),
    )

    booking = {
        "id": booking_data.get("id") or str(uuid.uuid4()),
        "customer_name": booking_data.get("customer_name", "Guest"),
        "email": booking_data["email"],
        "showtime_id": showtime_id,
        "showtime_time": showtime.get("start_time"),
        "seats": seats,
        "status": "active",
        "created_at": datetime.utcnow().isoformat(),
        "total": total,
    }
    bookings_list: Optional[List[Dict[str, Any]]] = booking_data.get("bookings")
    if bookings_list is not None:
        bookings_list.append(booking)
    return booking


def cancel_booking(
    bookings: List[Dict[str, Any]], booking_id: str, seat_maps: Dict[str, Dict[str, str]]
) -> bool:
    now = datetime.utcnow()
    for booking in bookings:
        if booking.get("id") == booking_id and booking.get("status") == "active":
            showtime_id = booking.get("showtime_id")
            showtime_time_str = booking.get("showtime_time")
            if showtime_time_str:
                booking_showtime = datetime.fromisoformat(showtime_time_str)
                if booking_showtime - now < timedelta(minutes=30):
                    raise ValueError("Cancellations must be 30 minutes before showtime")
            seat_map = seat_maps.get(showtime_id, {})
            for seat in booking.get("seats", []):
                release_seat(seat_map, seat)
            booking["status"] = "cancelled"
            booking["cancelled_at"] = now.isoformat()
            return True
    return False


def calculate_booking_total(
    seats: List[str], pricing: Dict[str, float], tax_rate: float, discounts: Optional[Dict[str, Any]] = None
) -> float:
    base_price = pricing.get("standard", 10.0)
    subtotal = base_price * len(seats)

    if discounts:
        if discounts.get("type") == "percentage":
            subtotal -= subtotal * (discounts.get("amount", 0) / 100)
        elif discounts.get("type") == "flat":
            subtotal -= discounts.get("amount", 0)
        subtotal = max(subtotal, 0)

    total = subtotal * (1 + tax_rate)
    return round(total, 2)


def list_customer_bookings(bookings: List[Dict[str, Any]], email: str) -> List[Dict[str, Any]]:
    return [b for b in bookings if b.get("email") == email]


def generate_ticket(booking: Dict[str, Any], directory: str) -> str:
    os.makedirs(directory, exist_ok=True)
    ticket_path = os.path.join(directory, f"ticket_{booking['id']}.txt")
    seats = ", ".join(booking.get("seats", []))
    qr_block = "\n".join([
        "+------+",
        "| ####|",
        "|# ## |",
        "| ## #|",
        "|#### |",
        "+------+",
    ])
    content = (
        f"Movie Ticket\n"
        f"Booking ID: {booking['id']}\n"
        f"Customer: {booking.get('customer_name', 'Guest')}\n"
        f"Seats: {seats}\n"
        f"Total: ${booking.get('total', 0):.2f}\n"
        f"QR:\n{qr_block}\n"
    )
    with open(ticket_path, "w", encoding="utf-8") as f:
        f.write(content)
    return ticket_path
