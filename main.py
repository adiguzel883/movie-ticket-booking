import os
import sys
from datetime import datetime

from bookings import create_booking, cancel_booking, list_customer_bookings, generate_ticket
from movies import load_movies, save_movies, add_movie, schedule_showtime
from seating import render_seat_map, initialize_seat_map
from storage import load_state, save_state, backup_state
from reports import occupancy_report, revenue_summary, top_movies, export_report

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
TICKET_DIR = os.path.join(BASE_DIR, "tickets")


def print_header(title: str) -> None:
    print("\n" + "=" * 40)
    print(title)
    print("=" * 40)


def load_data():
    os.makedirs(DATA_DIR, exist_ok=True)
    movies = load_movies(os.path.join(DATA_DIR, "movies.json"))
    movies, showtimes, seat_maps, bookings = load_state(BASE_DIR)
    return movies, showtimes, seat_maps, bookings


def save_all(showtimes, seat_maps, bookings):
    save_state(BASE_DIR, showtimes, seat_maps, bookings)


def show_movies(movies):
    print_header("Filmler")
    for movie in movies:
        print(f"{movie['id']}: {movie['title']} ({movie.get('duration', 0)} dk) - {movie.get('rating')}")


def show_showtimes(showtimes):
    print_header("Seanslar")
    for st in showtimes:
        print(f"{st['id']}: Film {st['movie_id']} - {st['start_time']} - {st.get('screen')}")


def customer_menu(movies, showtimes, seat_maps, bookings):
    while True:
        print_header("Müşteri Menüsü")
        print("1) Seansları Listele")
        print("2) Rezervasyon Yap")
        print("3) Rezervasyonlarımı Gör")
        print("0) Geri Dön")
        choice = input("Seçim: ")
        if choice == "1":
            show_showtimes(showtimes)
            st_id = input("Seans ID girin: ")
            seat_map = seat_maps.get(st_id)
            if seat_map:
                print(render_seat_map(seat_map))
        elif choice == "2":
            customer_name = input("Ad Soyad: ")
            email = input("E-posta: ")
            show_showtimes(showtimes)
            st_id = input("Seans ID: ")
            seat_map = seat_maps.get(st_id)
            if not seat_map:
                found = next((s for s in showtimes if s['id'] == st_id), None)
                if found:
                    seat_map = initialize_seat_map(found.get('screen_config', {'rows': 5, 'cols': 8}))
                    seat_maps[st_id] = seat_map
            print(render_seat_map(seat_map))
            seats = input("Koltuk kodları (virgülle): ").split(",")
            seats = [s.strip().upper() for s in seats if s.strip()]
            try:
                booking = create_booking(
                    showtimes,
                    seat_maps,
                    {
                        "showtime_id": st_id,
                        "customer_name": customer_name,
                        "email": email,
                        "seats": seats,
                        "bookings": bookings,
                        "tax_rate": 0.18,
                    },
                )
                save_all(showtimes, seat_maps, bookings)
                ticket_path = generate_ticket(booking, TICKET_DIR)
                print(f"Rezervasyon başarılı! Bilet: {ticket_path}")
            except Exception as exc:  # noqa: BLE001
                print(f"Hata: {exc}")
        elif choice == "3":
            email = input("E-posta: ")
            my_bookings = list_customer_bookings(bookings, email)
            for b in my_bookings:
                print(f"{b['id']} - {b['showtime_id']} - {b['seats']} - {b['status']}")
        elif choice == "0":
            return
        else:
            print("Geçersiz seçim")


def admin_menu(movies, showtimes, seat_maps, bookings):
    while True:
        print_header("Admin Menüsü")
        print("1) Film Ekle")
        print("2) Seans Planla")
        print("3) Rezervasyon İptal")
        print("4) Raporlar")
        print("5) Yedek Al")
        print("0) Geri Dön")
        choice = input("Seçim: ")
        if choice == "1":
            title = input("Film adı: ")
            duration = int(input("Süre (dk): "))
            rating = input("Rating: ")
            movie = add_movie(movies, {"title": title, "duration": duration, "rating": rating})
            save_movies(os.path.join(DATA_DIR, "movies.json"), movies)
            print(f"Eklendi: {movie['id']}")
        elif choice == "2":
            show_movies(movies)
            movie_id = input("Film ID: ")
            start_time = input("Başlangıç (ISO): ")
            screen = input("Salon adı: ")
            config = {"rows": int(input("Sıra sayısı: ")), "cols": int(input("Koltuk sayısı: "))}
            showtime = schedule_showtime(
                showtimes,
                {
                    "movie_id": movie_id,
                    "start_time": start_time,
                    "screen": screen,
                    "screen_config": config,
                },
            )
            seat_maps[showtime["id"]] = initialize_seat_map(config)
            save_all(showtimes, seat_maps, bookings)
            print(f"Seans oluşturuldu: {showtime['id']}")
        elif choice == "3":
            bid = input("Rezervasyon ID: ")
            try:
                if cancel_booking(bookings, bid, seat_maps):
                    save_all(showtimes, seat_maps, bookings)
                    print("İptal edildi")
                else:
                    print("Rezervasyon bulunamadı")
            except Exception as exc:  # noqa: BLE001
                print(f"Hata: {exc}")
        elif choice == "4":
            occ = occupancy_report(showtimes, seat_maps, bookings)
            print("Doluluk Raporu:")
            for row in occ:
                print(row)
            rev = revenue_summary(bookings, "daily")
            print("Gelir Özeti:", rev)
            top = top_movies(bookings, showtimes)
            print("Top Filmler:", top)
            export_report(occ, os.path.join(DATA_DIR, "occupancy_report.json"))
        elif choice == "5":
            backup_dir = os.path.join(BASE_DIR, "backups")
            path = backup_state(BASE_DIR, backup_dir)
            print(f"Yedek oluşturuldu: {path}")
        elif choice == "0":
            return
        else:
            print("Geçersiz seçim")


def main():
    movies, showtimes, seat_maps, bookings = load_data()
    while True:
        print_header("Movie Ticket Booking System")
        print("1) Müşteri")
        print("2) Admin")
        print("0) Çıkış")
        choice = input("Seçim: ")
        if choice == "1":
            customer_menu(movies, showtimes, seat_maps, bookings)
        elif choice == "2":
            admin_menu(movies, showtimes, seat_maps, bookings)
        elif choice == "0":
            print("Güle güle!")
            save_all(showtimes, seat_maps, bookings)
            sys.exit(0)
        else:
            print("Geçersiz seçim")


if __name__ == "__main__":
    main()
