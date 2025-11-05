# Trident Trader Suite - Kullanıcı Kılavuzu (TR)

## Hoş Geldiniz
**Trident Trader**, trend + momentum + likidite bileşenlerini tek bir profesyonel sistemde birleştirir. Bu kılavuz kurulumdan strateji kullanımına kadar tüm detayları içerir.

---

## İçindekiler
1. Hızlı Başlangıç
2. Kurulum
3. Pano (Dashboard) ve Metrikler
4. İşlem Modları
5. Sinyal Türleri
6. Likidite Zonları (Supply/Demand)
7. Risk Yönetimi ve Pozisyon Boyutu
8. Alert Sistemi
9. Gelişmiş Ayarlar (MTF, filtreler)
10. Stratejiler
11. İpuçları & En İyi Uygulamalar
12. Sorun Giderme

---

## 1) Hızlı Başlangıç
- TradingView → Göstergeler → “Trident Trader Suite PRO”
- Ayarlar → “Trading Mode” = Balanced (önerilir)
- Alert kurulumu → “Buy Signal” ve “Sell Signal”

Detaylı 5 dakikalık rehber: `documentation/QUICK_START_TR.md`

---

## 2) Kurulum
- Tüm piyasalarda çalışır (Kripto/Forex/Hisse/Endeks/Emtia)
- Tüm zaman dilimlerinde çalışır (1dk’dan Aylık’a)
- Free plan yeterli; yoğun alert kullanımı için Pro önerilir

---

## 3) Dashboard
- Trend: BULLISH ▲ / BEARISH ▼ / NEUTRAL →
- Momentum: BULLISH / BEARISH / NEUTRAL
- RSI: <30 aşırı satım, >70 aşırı alım
- Trend Strength (ADX): >20 ise chop daha az
- Nearest Demand / Supply: En yakın canlı zon fiyatı
- R:R (TP1): İşlem aktifken risk/ödül oranı
- Size @ Risk%: Hesap büyüklüğü ve risk % ile önerilen pozisyon boyutu

---

## 4) İşlem Modları
- Scalping: Daha hassas, sık sinyal, 1–15dk
- Balanced: Dengeli, 15dk–4s (varsayılan)
- Swing: Daha seçici, 4s–Günlük

Mod seçimi, pivot hassasiyeti ve trend/momentum tepki hızını optimize eder.

---

## 5) Sinyal Türleri
- Buy / Sell: Trend + Momentum + (opsiyonel) Zon lokasyonu onaylı girişler
- Strong Buy / Strong Sell (★): RSI aşırı bölgeden dönüş + lokasyon konfluensi

Sinyaller **bar kapanışında** üretilir; repaint yoktur.

---

## 6) Likidite Zonları
- Otomatik **Supply/Demand**: Pivot esaslı, box.new ile kutular
- Zon yaşam döngüsü: Kırılan zonlar pasifleştirilir (gri)
- **Order Block** (opsiyonel): Güçlü hareket öncesi ters mum
- **FVG** (opsiyonel): Hızlı hareket dengesizliği

Taktik: Long için demand dokunuş + Buy; Short için supply dokunuş + Sell.

---

## 7) Risk Yönetimi ve Pozisyon Boyutu
- SL: ATR x slATR veya en yakın zon sınırına göre ayarlama
- TP1/TP2: ATR x çarpanlarına göre; karşı zon varsa TP1 oraya hizalanır
- Trailing: Kâr aldıkça SL’i takip ettirir
- Pozisyon boyutu önerisi: Hesap büyüklüğü * risk% / birim risk

Örnek: 10.000$ hesap, %1 risk, SL mesafesi 100$: önerilen boyut = 100$/100$ = 1 birim.

---

## 8) Alert Sistemi
- Buy / Strong Buy / Sell / Strong Sell
- Price at Demand / Price at Supply
- (İsteğe bağlı) Trend veya Momentum uyarıları

Öneri: Swing için Strong sinyaller + zon uyarıları; scalping için standart Buy/Sell.

---

## 9) Gelişmiş Ayarlar
- **HTF Onayı**: Üst zaman dilimi trendi ile aynı yönde sinyal (lookahead_off)
- **Chop Filtresi**: ADX eşiği (varsayılan 20)
- **Volatilite Filtresi**: ATR ortalamasına göre düşük volatiliteyi eleme

Bunlar sahte sinyalleri azaltır, toplam sinyal sayısını da düşürür.

---

## 10) Stratejiler (Özet)
1) Trend Takip (1s/4s)  
Giriş: Strong sinyal + ADX yeterli  
Çıkış: TP1’de %50 kapat, SL’i BE, kalan için trailing

2) Zon Dönüşü (15dk/1s)  
Giriş: Fiyat demand/supply’a dokunduktan sonra sinyal  
Çıkış: Karşı zon hedeflenir

3) Scalping (1–5dk)  
Giriş: Buy/Sell; yoğun seanslarda  
Çıkış: TP1 odaklı, sıkı trailing

4) Swing (Günlük/Haftalık)  
Giriş: HTF onaylı Strong sinyal  
Çıkış: TP2’ye kadar sabır + geniş SL

---

## 11) İpuçları
- Mum kapanışı olmadan trade etmeyin
- ADX < 20 ise sabırlı olun (ranging)
- R:R < 2 ise pozisyonu küçültün veya bekleyin
- Çoklu varlıkta alert kurarak ekran süresini azaltın
- Günlük/Haftalık HTF onayında başarı artar

---

## 12) Sorun Giderme
- Sinyal yok: Mod/timeframe uyuşmazlığı olabilir; HTF onayı sinyali kesiyor olabilir
- Zonlar kalabalık: maxActiveZones’u düşürün, pivotları artırın
- Alert gelmiyor: Alarmı gösterge başlığındaki zilden oluşturun, “Once Per Bar Close” seçin

---

### Yasal Uyarı
Bu bir finansal tavsiye değildir. İşlemler yüksek risk içerir. Geçmiş performans geleceği garanti etmez. Sorumluluk kullanıcıya aittir.
