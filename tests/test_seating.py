import pytest

from seating import initialize_seat_map, is_seat_available, reserve_seat, release_seat


def test_seat_selection_and_availability():
    seat_map = initialize_seat_map({"rows": 2, "cols": 2})
    assert is_seat_available(seat_map, "A1")
    assert reserve_seat(seat_map, "A1")
    assert not is_seat_available(seat_map, "A1")
    assert not reserve_seat(seat_map, "A1")
    assert release_seat(seat_map, "A1")
    assert is_seat_available(seat_map, "A1")
