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
REPORT_DIR = "reports"


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
        print(f"- {mv['id']}: {mv['title']} | {mv.get('genre','')} | {mv.get('duration_min','')} min | Rating: {mv.get('rating','')}")


def _print_showtimes(showtimes, movies_list):
    movie_by_id = {m["id"]: m for m in movies_list}
    print("\nShowtimes:")
    for st in showtimes:
        movie_title = movie_by_id.get(st["movie_id"], {}).get("title", "Unknown")
        print(
            f"- {st['id']} | {movie_title} | {st.get('datetime')} | {st.get('screen')} | {st.get('language')} | "
            f"Std/Prem: {st.get('pricing',{}).get('standard',0)}/{st.get('pricing',{}).get('premium',0)}"
        )


def _parse_input_datetime(value: str) -> str:
    """Validate and normalize datetime input (YYYY-MM-DD HH:MM)."""
    try:
        dt = datetime.strptime(value, "%Y-%m-%d %H:%M")
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        raise ValueError("Invalid datetime format. Use YYYY-MM-DD HH:MM.")


def customer_menu(movies_list, showtimes, seat_maps, bookings_list):
    while True:
        print("\n-- Customer Menu --")
        print("1) List movies")
        print("2) List showtimes")
        print("3) View seats & book")
        print("4) Cancel booking")
        print("5) My bookings")
        print("0) Back")
        choice = input("Select option: ").strip()
        if choice == "1":
            _print_movies(movies_list)
        elif choice == "2":
            _print_showtimes(showtimes, movies_list)
        elif choice == "3":
            _print_showtimes(showtimes, movies_list)
            sid = input("Showtime ID (0=back): ").strip()
            if sid == "0" or not sid:
                continue
            seat_map = seat_maps.get(sid)
            if not seat_map:
                print("Seat map not found. Choose a valid showtime ID.")
                continue
            showtime = next((s for s in showtimes if s.get("id") == sid), None)
            if not showtime:
                print("Showtime not found. Choose a valid showtime ID.")
                continue
            print(seating.render_seat_map(seat_map))
            premium_rows = sorted({meta["row"] for meta in seat_map.values() if meta.get("zone") == "premium"})
            standard_rows = sorted({meta["row"] for meta in seat_map.values() if meta.get("zone") != "premium"})
            print("\nLegend: O = available, X = reserved")
            print(
                f"Pricing: Premium rows {''.join(premium_rows) or '-'} = premium price; "
                f"rows {''.join(standard_rows) or '-'} = standard price."
            )
            seats = input("Seats (comma, e.g., A1,A2): ").replace(" ", "").split(",")
            seats = [s for s in seats if s]
            if not seats:
                print("No seats selected.")
                continue
            price_preview = bookings.calculate_booking_total(seats, showtime.get("pricing", {}), seat_map=seat_map)
            confirm = input(
                f"Confirm booking? Seats: {', '.join(seats)} | Total: {price_preview['total']:.2f} (y/n): "
            ).strip().lower()
            if confirm != "y":
                print("Booking cancelled by user.")
                continue
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
            confirm = input("Are you sure you want to cancel? (y/n): ").strip().lower()
            if confirm != "y":
                print("Cancellation aborted.")
                continue
            success, msg = bookings.cancel_booking(bookings_list, bid, seat_maps)
            print(msg if msg else ("Booking cancelled." if success else "Cancellation failed."))
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
        choice = input("Select option: ").strip()
        if choice == "1":
            title = input("Title: ").strip()
            genre = input("Genre: ").strip()
            duration = int(input("Duration (min): ") or "100")
            print("Rating options: 1) General  2) 7+  3) 13+  4) 18+")
            rating_choice = input("Select rating (1-4): ").strip() or "1"
            rating_map = {"1": "General", "2": "7+", "3": "13+", "4": "18+"}
            rating = rating_map.get(rating_choice, "General")
            mv = movies.add_movie(
                movies_list,
                {"title": title, "genre": genre, "duration_min": duration, "rating": rating},
            )
            print(f"Added movie {mv['id']}")
        elif choice == "2":
            _print_movies(movies_list)
            movie_id = input("Movie ID (from list): ").strip()
            screen = input("Screen name: ").strip() or "Screen 1"
            dt_input = input("Date/time (YYYY-MM-DD HH:MM): ").strip() or datetime.utcnow().strftime("%Y-%m-%d %H:%M")
            try:
                dt = _parse_input_datetime(dt_input)
            except ValueError as exc:
                print(exc)
                continue
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
            sid = input("Showtime ID (0=back): ").strip()
            if sid == "0" or not sid:
                continue
            st = next((s for s in showtimes if s.get("id") == sid), None)
            if not st:
                print("Showtime not found.")
                continue
            seat_maps[sid] = seating.initialize_seat_map(st.get("screen_config", {}))
            print("Seat map rebuilt. All seats set to available.")
        elif choice == "4":
            sid = input("Showtime ID: ").strip()
            new_dt = input("New datetime (blank=keep): ").strip()
            new_std = input("New standard price (blank=keep): ").strip()
            new_pre = input("New premium price (blank=keep): ").strip()
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

    top = reports.top_movies(bookings_list, showtimes, limit=5)
    if top:
        print("Top movies by seats sold:")
        for item in top:
            print(f"- {item['movie_id']}: {item['seats_sold']} seats")

    export_choice = input("Export report to file? (y/n): ").strip().lower()
    if export_choice == "y":
        os.makedirs(REPORT_DIR, exist_ok=True)
        ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        path = os.path.join(REPORT_DIR, f"report-{ts}.json")
        payload = {"generated_at": ts, "occupancy": occ, "revenue": rev, "top_movies": top}
        reports.export_report(payload, path)
        print(f"Report saved to {path}")


def main():
    movies_list, showtimes, seat_maps, bookings_list = _init_state()
    os.makedirs(TICKET_DIR, exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)

    while True:
        print("\n=== Movie Ticket Booking System ===")
        print("1) Customer (buy/cancel tickets)")
        print("2) Admin (manage movies & showtimes)")
        print("3) Reports (occupancy, revenue)")
        print("9) Backup data")
        print("0) Exit")
        choice = input("Select option: ").strip()
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


