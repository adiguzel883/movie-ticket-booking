import pytest

from bookings import create_booking
from seating import initialize_seat_map


def test_double_booking_prevention():
    showtimes = [
        {
            "id": "s1",
            "movie_id": "m1",
            "start_time": "2099-01-01T20:00:00",
            "pricing": {"standard": 10.0},
            "screen_config": {"rows": 2, "cols": 2},
        }
    ]
    seat_maps = {"s1": initialize_seat_map({"rows": 2, "cols": 2})}
    bookings = []

    create_booking(
        showtimes,
        seat_maps,
        {
            "showtime_id": "s1",
            "email": "a@example.com",
            "seats": ["A1"],
            "bookings": bookings,
        },
    )

    with pytest.raises(ValueError):
        create_booking(
            showtimes,
            seat_maps,
            {
                "showtime_id": "s1",
                "email": "b@example.com",
                "seats": ["A1"],
                "bookings": bookings,
            },
        )
