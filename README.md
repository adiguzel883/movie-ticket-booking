# Python Term Project – Movie Ticket Booking System

## Kurulum
1. Python 3.10+ kurulu olmalı.
2. Depo kökünde aşağıdaki komutla sanal ortam (isteğe bağlı) kurun:
   ```
   python -m venv .venv
   .venv\Scripts\activate
   ```
3. Bağımlılık gerektirmez; standart kütüphaneler kullanılır.

## Çalıştırma
```
python main.py
```
- Müşteri menüsünden gösterim seçip koltuk ayırtabilir, bilet çıktısı alabilir.
- Admin menüsünden film ekleyebilir, gösterim planlayabilir, koltuk haritası oluşturabilir.

## Veri Dosyaları
- `data/movies.json`
- `data/showtimes.json` (içinde seat_maps dahil)
- `data/bookings.json`
- Yedekler: `backups/`
- Üretilen biletler: `tickets/`

## Testler
```
python -m pytest
```

## Modüller
- `movies.py` – film kataloğu ve gösterim planlama
- `seating.py` – koltuk haritası oluşturma ve durum yönetimi
- `bookings.py` – rezervasyon, iptal, ücret hesaplama, bilet üretimi
- `storage.py` – veri yükleme/kaydetme, yedekleme, doğrulama
- `reports.py` – doluluk ve gelir raporları
- `main.py` – CLI menüler

## Örnek Akış
1. Admin menüsünde film ekle.
2. Gösterim planla, koltuk haritası oluştur.
3. Müşteri menüsünde gösterim seç, koltuk(lar)ı gir, rezervasyonu tamamla.
4. `tickets/` klasöründen bilet çıktısını al.


