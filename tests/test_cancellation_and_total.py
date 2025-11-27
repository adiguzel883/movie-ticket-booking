
from datetime import datetime, timedelta

from bookings import create_booking, cancel_booking, calculate_booking_total
from seating import initialize_seat_map, is_seat_available


def test_cancellation_releases_seat():
    future_time = (datetime.utcnow() + timedelta(hours=2)).isoformat()
    showtimes = [
        {
            "id": "s2",
            "movie_id": "m2",
            "start_time": future_time,
            "pricing": {"standard": 15.0},
            "screen_config": {"rows": 2, "cols": 2},
        }
    ]
    seat_map = initialize_seat_map({"rows": 2, "cols": 2})
    seat_maps = {"s2": seat_map}
    bookings = []
    booking = create_booking(
        showtimes,
        seat_maps,
        {
            "showtime_id": "s2",
            "email": "test@example.com",
            "seats": ["A1"],
            "bookings": bookings,
        },
    )
    assert not is_seat_available(seat_map, "A1")
    cancelled = cancel_booking(bookings, booking["id"], seat_maps)
    assert cancelled
    assert is_seat_available(seat_map, "A1")


def test_calculate_booking_total_with_discount():
    seats = ["A1", "A2"]
    pricing = {"standard": 10.0}
    total = calculate_booking_total(
        seats,
        pricing,
        tax_rate=0.1,
        discounts={"type": "percentage", "amount": 10},
    )
    # subtotal 20 -10% =18 ; tax 10% =>19.8
    assert total == 19.8
