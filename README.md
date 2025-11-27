# Movie Ticket Booking System

Terminal tabanlı bir sinema biletleme sistemi. Müşteri ve admin menüleri içerir; koltuk haritaları, rezervasyon, iptal, yedekleme ve raporlama akışlarını destekler.

## Proje Yapısı
- `main.py`: Uygulama girişi ve menü akışları
- `movies.py`: Film ve seans yönetimi yardımcıları
- `seating.py`: Koltuk haritası oluşturma/görüntüleme ve rezervasyon kontrolleri
- `bookings.py`: Rezervasyon oluşturma, iptal, toplam hesaplama ve bilet üretimi
- `storage.py`: JSON tabanlı kalıcılık, yükleme/kaydetme ve yedekleme
- `reports.py`: Doluluk, gelir ve popüler film raporları, dışa aktarma
- `data/`: Örnek `movies.json`, `showtimes.json`, `bookings.json`
- `tests/`: Pytest senaryoları (koltuk uygunluğu, çift rezervasyon engelleme, iptal ve fiyat hesaplama)

## Çalıştırma
```bash
python main.py
```

## Testler
```bash
pytest
```

## JSON Örnekleri
`data/` dizinindeki dosyalar başlangıç verisini içerir; uygulama çalışırken değişiklikler otomatik kaydedilir.
