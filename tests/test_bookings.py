import bookings
import seating
import pytest
from datetime import datetime, timedelta


def setup_state():
    showtimes = [
        {
            "id": "ST-TST",
            "movie_id": "MV001",
            "screen": "Screen 1",
            "datetime": "2026-01-07 19:30",
            "language": "OV",
            "pricing": {"standard": 10.0, "premium": 14.0},
            "screen_config": {"rows": ["A", "B"], "seats_per_row": 3, "premium_rows": ["A"]},
        }
    ]
    seat_maps = {"ST-TST": seating.initialize_seat_map(showtimes[0]["screen_config"])}
    bookings_list = []
    return showtimes, seat_maps, bookings_list


def test_double_booking_blocked():
    showtimes, seat_maps, bookings_list = setup_state()
    booking_data = {
        "showtime_id": "ST-TST",
        "seats": ["A1"],
        "customer": {"name": "Test", "email": "a@test.com"},
        "bookings": bookings_list,
    }
    bookings.create_booking(showtimes, seat_maps, booking_data)
    # second attempt on same seat should fail
    try:
        bookings.create_booking(showtimes, seat_maps, booking_data)
        assert False, "Expected ValueError for double booking"
    except ValueError:
        assert True


def test_cancellation_releases_seat():
    showtimes, seat_maps, bookings_list = setup_state()
    booking = bookings.create_booking(
        showtimes,
        seat_maps,
        {"showtime_id": "ST-TST", "seats": ["A1"], "customer": {"name": "Test", "email": "a@test.com"}, "bookings": bookings_list},
    )
    assert not seating.is_seat_available(seat_maps["ST-TST"], "A1")
    success, msg = bookings.cancel_booking(bookings_list, booking["id"], seat_maps)
    assert success, msg
    assert seating.is_seat_available(seat_maps["ST-TST"], "A1")


def test_cost_calculation_with_tax_and_discounts():
    seat_map = seating.initialize_seat_map({"rows": ["A"], "seats_per_row": 2, "premium_rows": []})
    pricing = {"standard": 10.0}
    result = bookings.calculate_booking_total(["A1", "A2"], pricing, tax_rate=0.1, discounts=[{"type": "flat", "value": 5}])
    assert result["subtotal"] == 20.0
    assert result["discount"] == 5.0
    assert result["tax"] == 1.5
    assert result["total"] == 16.5


def test_invalid_seat_code_rejected():
    showtimes, seat_maps, bookings_list = setup_state()
    with pytest.raises(ValueError):
        bookings.create_booking(
            showtimes,
            seat_maps,
            {"showtime_id": "ST-TST", "seats": ["Z9"], "customer": {"name": "Test", "email": "a@test.com"}, "bookings": bookings_list},
        )


def test_cancellation_blocked_within_window():
    st_dt = (datetime.now() + timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M")
    showtimes = [
        {
            "id": "ST-CUT",
            "movie_id": "MV001",
            "screen": "Screen 1",
            "datetime": st_dt,
            "language": "OV",
            "pricing": {"standard": 10.0, "premium": 14.0},
            "screen_config": {"rows": ["A"], "seats_per_row": 2, "premium_rows": []},
        }
    ]
    seat_maps = {"ST-CUT": seating.initialize_seat_map(showtimes[0]["screen_config"])}
    bookings_list = []
    booking = bookings.create_booking(
        showtimes,
        seat_maps,
        {"showtime_id": "ST-CUT", "seats": ["A1"], "customer": {"name": "Test", "email": "a@test.com"}, "bookings": bookings_list},
    )
    success, msg = bookings.cancel_booking(bookings_list, booking["id"], seat_maps, now=datetime.now(), cancellation_window_min=30)
    assert not success
    assert "30 minutes" in msg


