# Python Term Project – Movie Ticket Booking System

Terminal tabanlı sinema biletleme prototipi. Gösterim planlama, koltuk yönetimi, rezervasyon/iptal, bilet üretimi, veri kalıcılığı, yedekleme ve raporlama içerir.

## Gereksinimler
- Python 3.10+
- Ek bağımlılık yok (yalnızca standart kütüphane).

## Kurulum (isteğe bağlı sanal ortam)
```
python -m venv .venv
.venv\Scripts\activate   # Windows
```

## Çalıştırma
```
python main.py
```

## Kullanım Özeti
- Admin menüsü
  - Film ekle: Başlık, tür, süre ve rating seçimi (1) General, (2) 7+, (3) 13+, (4) 18+.
  - Gösterim planla: Salon adı, tarih/saat (YYYY-MM-DD HH:MM), dil, standart/premium fiyat, satır harfleri, sıra başına koltuk sayısı, premium satırlar.
  - Koltuk haritasını yeniden oluştur: Seçilen gösterimin seat map’ini sıfırlar (tüm koltuklar tekrar available).
  - Fiyat/tarih güncelle: Standart/premium fiyat veya tarih/saat güncellemesi.
- Müşteri menüsü
  - Filmleri ve gösterimleri listele.
  - Koltuk seç ve rezervasyon yap: O/X grid gösterilir, premium/standart satırlar legend ile belirtilir. Seçilen koltuklar için toplam tutar gösterilir ve onay istenir; onaylanınca bilet `tickets/` altına yazılır.
  - Rezervasyon iptali: ID ile iptal; gösterime 30 dakikadan az kaldıysa iptal reddedilir.
  - Kendi rezervasyonlarını görüntüle (e-posta ile).
- Raporlar
  - Doluluk ve önümüzdeki 30 gün için gelir özeti.
  - En çok koltuk satılan filmler listesi.
  - İstenirse rapor JSON olarak `reports/` klasörüne kaydedilir.
- Yedekleme
  - Ana menüden “Backup data” ile `backups/` içine zaman damgalı yedekler (`showtimes`, `seat_maps`, `bookings`, `movies`).

## Veri Dosyaları
- `data/movies.json`
- `data/showtimes.json` (içinde `seat_maps` dahil)
- `data/bookings.json`
- Yedekler: `backups/`
- Üretilen biletler: `tickets/`
- Rapor çıktıları: `reports/`

## Testler
```
python -m pytest
```

## Modüller
- `main.py` – CLI menüler ve akış
- `movies.py` – film kataloğu, gösterim planlama/güncelleme
- `seating.py` – koltuk haritası üretimi ve durum yönetimi
- `bookings.py` – rezervasyon, iptal politikası, fiyat/indirim/vergi, bilet üretimi
- `storage.py` – veri yükleme/kaydetme, yedekleme, doğrulama
- `reports.py` – doluluk, gelir, top movies, rapor dışa aktarma

## Örnek Akış
1) Admin: Film ekle.
2) Admin: Gösterim planla, premium satırları belirt, koltuk haritası oluşsun.
3) Müşteri: Gösterim seç, koltuk(lar)ı gir, toplamı gör, onayla.
4) Bileti `tickets/` klasöründen al; gerekirse `backups/` ile yedek oluştur; `reports/` ile rapor dışa aktar.


