import os
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Optional

import seating


def create_booking(showtimes: List[Dict], seat_maps: Dict, booking_data: Dict) -> Dict:
    """Create a booking, reserve seats, and return the booking record."""
    showtime_id = booking_data["showtime_id"]
    seats = booking_data.get("seats") or []
    customer = booking_data.get("customer") or {}
    bookings_list: Optional[List[Dict]] = booking_data.get("bookings")

    showtime = next((s for s in showtimes if s.get("id") == showtime_id), None)
    if not showtime:
        raise ValueError("Showtime not found")
    if showtime_id not in seat_maps:
        raise ValueError("Seat map missing for showtime")

    seat_map = seat_maps[showtime_id]
    unavailable = [code for code in seats if not seating.is_seat_available(seat_map, code)]
    if unavailable:
        raise ValueError(f"Seats not available: {', '.join(unavailable)}")

    for code in seats:
        seating.reserve_seat(seat_map, code)

    pricing = calculate_booking_total(seats, showtime.get("pricing", {}), seat_map=seat_map)
    booking = {
        "id": booking_data.get("id") or str(uuid.uuid4())[:10],
        "showtime_id": showtime_id,
        "seats": seats,
        "customer": {
            "name": customer.get("name", "Guest"),
            "email": customer.get("email", ""),
            "phone": customer.get("phone", ""),
        },
        "pricing": pricing,
        "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "showtime_snapshot": {
            "movie_id": showtime.get("movie_id"),
            "screen": showtime.get("screen"),
            "datetime": showtime.get("datetime"),
            "language": showtime.get("language"),
        },
    }

    if bookings_list is not None:
        bookings_list.append(booking)
    return booking


def cancel_booking(bookings: List[Dict], booking_id: str, seat_maps: Dict) -> bool:
    """Cancel booking and free seats. Returns True if cancelled."""
    booking = next((b for b in bookings if b.get("id") == booking_id), None)
    if not booking or booking.get("status") == "cancelled":
        return False

    showtime_id = booking.get("showtime_id")
    seat_map = seat_maps.get(showtime_id)
    if seat_map:
        for code in booking.get("seats", []):
            seating.release_seat(seat_map, code)

    booking["status"] = "cancelled"
    booking["cancelled_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return True


def calculate_booking_total(
    seats: List[str],
    pricing: Dict,
    tax_rate: float = 0.08,
    discounts: Optional[List[Dict]] = None,
    seat_map: Optional[Dict] = None,
) -> Dict:
    """Calculate subtotal, discount, tax, and total."""
    discounts = discounts or []
    subtotal = 0.0
    for code in seats:
        zone = None
        if seat_map and code in seat_map:
            zone = seat_map[code].get("zone")
        price = pricing.get(zone or "standard", pricing.get("standard", 0.0))
        subtotal += float(price)

    discount_value = 0.0
    for disc in discounts:
        if disc.get("type") == "percent":
            discount_value += subtotal * float(disc.get("value", 0)) / 100.0
        elif disc.get("type") == "flat":
            discount_value += float(disc.get("value", 0))
    discount_value = min(discount_value, subtotal)

    taxable = subtotal - discount_value
    tax = round(taxable * tax_rate, 2)
    total = round(taxable + tax, 2)
    return {
        "subtotal": round(subtotal, 2),
        "discount": round(discount_value, 2),
        "tax": tax,
        "total": total,
    }


def list_customer_bookings(bookings: List[Dict], email: str) -> List[Dict]:
    """Return active bookings for a given customer email."""
    return [b for b in bookings if b.get("customer", {}).get("email") == email and b.get("status") == "active"]


def generate_ticket(booking: Dict, directory: str) -> str:
    """Create a text ticket file and return its path."""
    os.makedirs(directory, exist_ok=True)
    filename = os.path.join(directory, f"ticket_{booking['id']}.txt")
    showtime = booking.get("showtime_snapshot", {})
    lines = [
        "=== MOVIE TICKET ===",
        f"Booking ID : {booking['id']}",
        f"Showtime   : {showtime.get('datetime', '')}",
        f"Screen     : {showtime.get('screen', '')}",
        f"Seats      : {', '.join(booking.get('seats', []))}",
        f"Status     : {booking.get('status')}",
        f"Name       : {booking.get('customer', {}).get('name', '')}",
        f"Email      : {booking.get('customer', {}).get('email', '')}",
        f"Total      : {booking.get('pricing', {}).get('total', 0):.2f}",
    ]
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return filename


