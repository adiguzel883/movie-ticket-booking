import os
from datetime import datetime, timedelta

import bookings
import movies
import reports
import seating
import storage

DATA_DIR = "data"
TICKET_DIR = "tickets"
BACKUP_DIR = "backups"


def _init_state():
    movie_path = os.path.join(DATA_DIR, "movies.json")
    movies_list = movies.load_movies(movie_path)
    showtimes, seat_maps, bookings_list = storage.load_state(DATA_DIR)

    # auto-generate seat maps for showtimes missing one
    for st in showtimes:
        sid = st.get("id")
        if sid not in seat_maps:
            seat_maps[sid] = seating.initialize_seat_map(st.get("screen_config", {}))
    return movies_list, showtimes, seat_maps, bookings_list


def _persist(movies_list, showtimes, seat_maps, bookings_list):
    movies.save_movies(os.path.join(DATA_DIR, "movies.json"), movies_list)
    storage.save_state(DATA_DIR, showtimes, seat_maps, bookings_list)


def _print_movies(movies_list):
    print("\nMovies:")
    for mv in movies_list:
        print(f"- {mv['id']}: {mv['title']} ({mv.get('genre','')}, {mv.get('duration_min','')} min)")


def _print_showtimes(showtimes, movies_list):
    movie_by_id = {m["id"]: m for m in movies_list}
    print("\nShowtimes:")
    for st in showtimes:
        movie_title = movie_by_id.get(st["movie_id"], {}).get("title", "Unknown")
        print(
            f"- {st['id']} | {movie_title} | {st.get('datetime')} | {st.get('screen')} | {st.get('language')} | "
            f"Price S/P: {st.get('pricing',{}).get('standard',0)}/{st.get('pricing',{}).get('premium',0)}"
        )


def customer_menu(movies_list, showtimes, seat_maps, bookings_list):
    while True:
        print("\n-- Customer Menu --")
        print("1) List movies")
        print("2) List showtimes")
        print("3) View seats & book")
        print("4) Cancel booking")
        print("5) My bookings")
        print("0) Back")
        choice = input("Select: ").strip()
        if choice == "1":
            _print_movies(movies_list)
        elif choice == "2":
            _print_showtimes(showtimes, movies_list)
        elif choice == "3":
            _print_showtimes(showtimes, movies_list)
            sid = input("Showtime ID: ").strip()
            seat_map = seat_maps.get(sid)
            if not seat_map:
                print("Seat map not found.")
                continue
            print(seating.render_seat_map(seat_map))
            seats = input("Seats (comma separated, e.g., A1,A2): ").replace(" ", "").split(",")
            name = input("Name: ").strip()
            email = input("Email: ").strip()
            phone = input("Phone (optional): ").strip()
            try:
                booking = bookings.create_booking(
                    showtimes,
                    seat_maps,
                    {"showtime_id": sid, "seats": seats, "customer": {"name": name, "email": email, "phone": phone}, "bookings": bookings_list},
                )
                path = bookings.generate_ticket(booking, TICKET_DIR)
                print(f"Booking confirmed! ID: {booking['id']}. Ticket saved to {path}")
            except Exception as exc:
                print(f"Booking failed: {exc}")
        elif choice == "4":
            bid = input("Booking ID: ").strip()
            if bookings.cancel_booking(bookings_list, bid, seat_maps):
                print("Booking cancelled.")
            else:
                print("Booking not found or already cancelled.")
        elif choice == "5":
            email = input("Email: ").strip()
            mine = bookings.list_customer_bookings(bookings_list, email)
            if not mine:
                print("No active bookings.")
            for b in mine:
                print(f"- {b['id']} | {b['showtime_snapshot'].get('datetime')} | Seats: {', '.join(b['seats'])} | Total: {b['pricing']['total']}")
        elif choice == "0":
            return
        else:
            print("Invalid option.")


def admin_menu(movies_list, showtimes, seat_maps):
    while True:
        print("\n-- Admin Menu --")
        print("1) Add movie")
        print("2) Schedule showtime")
        print("3) Create/Rebuild seat map")
        print("4) Update showtime pricing/date")
        print("0) Back")
        choice = input("Select: ").strip()
        if choice == "1":
            title = input("Title: ").strip()
            genre = input("Genre: ").strip()
            duration = int(input("Duration (min): ") or "100")
            rating = input("Rating (e.g., PG-13): ").strip() or "NR"
            desc = input("Description: ").strip()
            mv = movies.add_movie(
                movies_list,
                {"title": title, "genre": genre, "duration_min": duration, "rating": rating, "description": desc},
            )
            print(f"Added movie {mv['id']}")
        elif choice == "2":
            _print_movies(movies_list)
            movie_id = input("Movie ID: ").strip()
            screen = input("Screen name: ").strip() or "Screen 1"
            dt = input("Date/time (YYYY-MM-DD HH:MM): ").strip() or datetime.utcnow().strftime("%Y-%m-%d %H:%M")
            lang = input("Language: ").strip() or "OV"
            std_price = float(input("Standard price: ") or "10")
            prem_price = float(input("Premium price: ") or "14")
            rows = input("Rows (e.g., ABCDEF): ").strip() or "ABCDEFGH"
            seats_per_row = int(input("Seats per row: ") or "12")
            premium_rows = list(input("Premium rows (e.g., AB): ").strip() or "AB")
            showtime = movies.schedule_showtime(
                showtimes,
                {
                    "movie_id": movie_id,
                    "screen": screen,
                    "datetime": dt,
                    "language": lang,
                    "pricing": {"standard": std_price, "premium": prem_price},
                    "screen_config": {"rows": list(rows), "seats_per_row": seats_per_row, "premium_rows": premium_rows},
                },
            )
            seat_maps[showtime["id"]] = seating.initialize_seat_map(showtime["screen_config"])
            print(f"Showtime created: {showtime['id']}")
        elif choice == "3":
            sid = input("Showtime ID: ").strip()
            st = next((s for s in showtimes if s.get("id") == sid), None)
            if not st:
                print("Showtime not found.")
                continue
            seat_maps[sid] = seating.initialize_seat_map(st.get("screen_config", {}))
            print("Seat map rebuilt.")
        elif choice == "4":
            sid = input("Showtime ID: ").strip()
            new_dt = input("New datetime (leave blank to keep): ").strip()
            new_std = input("New standard price (blank to keep): ").strip()
            new_pre = input("New premium price (blank to keep): ").strip()
            updates = {}
            if new_dt:
                updates["datetime"] = new_dt
            if new_std or new_pre:
                pricing = next((s.get("pricing", {}).copy() for s in showtimes if s.get("id") == sid), {})
                if new_std:
                    pricing["standard"] = float(new_std)
                if new_pre:
                    pricing["premium"] = float(new_pre)
                updates["pricing"] = pricing
            updated = movies.update_showtime(showtimes, sid, updates)
            if updated:
                print("Showtime updated.")
            else:
                print("Showtime not found.")
        elif choice == "0":
            return
        else:
            print("Invalid option.")


def reports_menu(showtimes, seat_maps, bookings_list):
    print("\n-- Reports --")
    occ = reports.occupancy_report(showtimes, seat_maps, bookings_list)
    for sid, data in occ.items():
        print(f"{sid} | {data['datetime']} | {data['screen']} | {data['occupancy']}% full ({data['reserved']}/{data['total_seats']})")

    start = datetime.utcnow().strftime("%Y-%m-%d 00:00")
    end = (datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%d 23:59")
    rev = reports.revenue_summary(bookings_list, (start, end))
    print(f"Projected revenue {start} to {end}: {rev['total_revenue']} ({rev['booking_count']} bookings)")


def main():
    movies_list, showtimes, seat_maps, bookings_list = _init_state()
    os.makedirs(TICKET_DIR, exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)

    while True:
        print("\n=== Movie Ticket Booking System ===")
        print("1) Customer")
        print("2) Admin")
        print("3) Reports snapshot")
        print("9) Backup data")
        print("0) Exit")
        choice = input("Select: ").strip()
        if choice == "1":
            customer_menu(movies_list, showtimes, seat_maps, bookings_list)
            _persist(movies_list, showtimes, seat_maps, bookings_list)
        elif choice == "2":
            admin_menu(movies_list, showtimes, seat_maps)
            _persist(movies_list, showtimes, seat_maps, bookings_list)
        elif choice == "3":
            reports_menu(showtimes, seat_maps, bookings_list)
        elif choice == "9":
            paths = storage.backup_state(DATA_DIR, showtimes, seat_maps, bookings_list, BACKUP_DIR)
            print(f"Backups created: {paths}")
        elif choice == "0":
            _persist(movies_list, showtimes, seat_maps, bookings_list)
            print("Goodbye!")
            break
        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()


