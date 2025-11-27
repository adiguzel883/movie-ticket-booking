# Movie Ticket Booking System

A terminal-based cinema ticketing system with customer and admin menus. It supports seat maps, reservations, cancellations, backups, and reporting.

## Project Structure
- `main.py`: Application entry point and menu flows
- `movies.py`: Helpers for movie and showtime management
- `seating.py`: Seat map creation, rendering, and availability checks
- `bookings.py`: Booking creation, cancellation, total calculation, and ticket generation
- `storage.py`: JSON-based persistence, loading/saving state, and backups
- `reports.py`: Occupancy, revenue, and top-movie reports, including export
- `data/`: Sample `movies.json`, `showtimes.json`, `bookings.json`
- `tests/`: Pytest scenarios (seat availability, double-booking prevention, cancellation, price calculation)

## Running
```bash
python main.py
```

## Testing
```bash
pytest
```

## JSON Samples
The `data/` directory contains initial JSON data for movies, showtimes, bookings, and seat maps. The system automatically persists updates to these files during runtime.
