# 🤖 Trident Trader Otomatik İşlem Sistemi - Türkçe Kurulum

## 🎯 Ne Yapacağız?

TradingView'deki Trident Trader PRO göstergeniz sinyal verdiğinde **otomatik olarak** Binance'te işlem açacak bir sistem kuracağız.

**İş Akışı**:
```
TradingView Alarm → Webhook → Python Bot → Binance API → İşlem Açıldı!
```

## 📋 Gereksinimler

### 1. TradingView Hesabı
- **TradingView Pro** veya üzeri (webhook özelliği için)
- Fiyat: $14.95/ay
- Link: [tradingview.com/pricing](https://www.tradingview.com/pricing/)

### 2. Binance Hesabı
- KYC doğrulaması tamamlanmış
- Kayıt: [binance.com](https://www.binance.com/tr/register)
- En az $100 bakiye önerilir (testler için)

### 3. Bilgisayar/Sunucu
- **Seçenek A**: Ücretsiz bulut (Render.com) ✅ Önerilen
- **Seçenek B**: Kendi bilgisayarın (7/24 açık olmalı)
- **Seçenek C**: Ücretli VPS ($5/ay)

---

## 🚀 Hızlı Kurulum (30 Dakika)

### Adım 1: Binance API Key Al (5 dk)

1. **Binance'e giriş yap** → Profil → API Management
2. **Create API** butonuna tıkla
3. API Key Label: `TridentTrader-Bot`
4. **API Restrictions** (ÇOK ÖNEMLİ!):
   - ✅ **Enable Spot & Margin Trading** (aç)
   - ✅ **Enable Futures** (isterseniz)
   - ❌ **Enable Withdrawals** (KAPALI OLMALI! - güvenlik için)
5. **Trusted IPs**: 
   - Herhangi bir IP seçeneğini seç (sonra güncelleyeceğiz)
6. **2FA Doğrula** → API Key ve Secret'ı kopyala

⚠️ **ÖNEMLİ**: Secret Key sadece bir kez gösterilir! Güvenli bir yere kaydet (şifre yöneticisi veya `.env` dosyası).

**Test (Opsiyonel - Testnet API)**:
- Gerçek para riskini istemiyorsan önce testnet kullan
- [testnet.binance.vision](https://testnet.binance.vision/) → API Key al
- Ücretsiz test parası verir

---

### Adım 2: Bot Sunucusunu Kur (10 dk)

#### Seçenek A: Render.com (Ücretsiz - Önerilen)

1. **GitHub Hesabı Aç** (yoksa):
   - [github.com](https://github.com/signup)

2. **Trident Trader Dosyalarını Yükle**:
   ```powershell
   cd C:\TridentTrader\automation
   git init
   git add .
   git commit -m "Trident Trader Bot"
   
   # GitHub'da yeni repo oluştur: trident-bot
   git remote add origin https://github.com/KULLANICI_ADIN/trident-bot.git
   git push -u origin main
   ```

3. **Render.com'a Kayıt Ol**:
   - [render.com](https://render.com) → Sign Up (GitHub ile giriş yap)

4. **Web Service Oluştur**:
   - Dashboard → **New +** → **Web Service**
   - **Connect GitHub**: `trident-bot` repo'sunu seç
   - Ayarlar:
     - Name: `trident-trader-bot`
     - Region: `Frankfurt` (Avrupa)
     - Branch: `main`
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `uvicorn binance_bot:app --host 0.0.0.0 --port $PORT`
   - **Free Plan** seç (0$/ay)
   - "Create Web Service"

5. **Environment Variables Ekle**:
   - Render dashboard → **Environment** sekmesi
   - Aşağıdaki değişkenleri ekle:

   ```
   BINANCE_API_KEY = (Binance'ten aldığın API key)
   BINANCE_API_SECRET = (Binance'ten aldığın secret)
   WEBHOOK_SECRET = (random 32 karakter - sonra lazım olacak)
   DEFAULT_RISK_PERCENT = 1.0
   USE_TESTNET = true
   TRADING_MODE = spot
   LOG_LEVEL = INFO
   ```

   **WEBHOOK_SECRET Oluştur**:
   ```powershell
   # PowerShell'de çalıştır:
   -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})
   ```
   Çıktıyı `WEBHOOK_SECRET`'a yapıştır.

6. **Deploy İzle**:
   - Logs sekmesinde build işlemini izle
   - 2-3 dakika sürer
   - Başarılı olursa: `Application startup complete`

7. **Webhook URL'ini Kopyala**:
   - Üstte URL görünecek: `https://trident-trader-bot-xxxx.onrender.com`
   - Tam webhook adresi: `https://trident-trader-bot-xxxx.onrender.com/webhook`
   - Bunu not et (TradingView'de kullanacağız)

8. **Test Et**:
   - Tarayıcıda aç: `https://your-bot-url.onrender.com/health`
   - Görmen gereken:
     ```json
     {"status":"healthy","timestamp":"2025-01-...","version":"1.0.0"}
     ```

✅ Bot hazır! Şimdi TradingView'e bağlayacağız.

---

#### Seçenek B: Kendi Bilgisayarında Çalıştır

**Gereksinimler**: Python 3.9+, 7/24 açık bilgisayar

1. **Python Kur** (yoksa):
   - [python.org/downloads](https://www.python.org/downloads/)
   - Kurulumda "Add to PATH" seçeneğini işaretle

2. **Bot'u Çalıştır**:
   ```powershell
   cd C:\TridentTrader\automation
   
   # .env dosyası oluştur
   Copy-Item .env.example .env
   notepad .env  # API key'leri gir
   
   # Sanal ortam
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   
   # Bağımlılıklar
   pip install -r requirements.txt
   
   # Başlat
   uvicorn binance_bot:app --host 0.0.0.0 --port 8000
   ```

3. **Dışarıya Aç (Ngrok)**:
   - [ngrok.com](https://ngrok.com/download) → İndir ve kayıt ol
   - PowerShell:
     ```powershell
     ngrok http 8000
     ```
   - Çıkan URL'i kopyala: `https://xxxx-xx-xx.ngrok-free.app`
   - Webhook URL: `https://xxxx-xx-xx.ngrok-free.app/webhook`

⚠️ **Not**: Ngrok free planı 8 saatte bir yeni URL verir. Pro plan alabilirsin ($8/ay) veya Render kullan.

---

### Adım 3: TradingView Indicator'ü Ayarla (5 dk)

1. **Indicator'ü Yükle**:
   - TradingView → Chart aç (BTCUSDT önerilir)
   - Indicators → Favorites → "Trident Trader PRO v1"
   - Eğer listede yoksa:
     - Pine Editor aç
     - `C:\TridentTrader\indicator\trident_trader_v1_pro.pine` dosyasını kopyala
     - "Add to chart"

2. **Webhook Secret'ı Gir**:
   - Indicator Settings (⚙️)
   - İçerideki kodu bul: `"secret":"YOUR_WEBHOOK_SECRET"`
   - `YOUR_WEBHOOK_SECRET` yerine Render'daki `WEBHOOK_SECRET` değerini yaz
   - CTRL+F ile ara, 4 yerde değiştir (buyMsg, strongBuyMsg, sellMsg, strongSellMsg)
   - "Save" → "Update"

---

### Adım 4: TradingView Alarm Kur (5 dk)

1. **Alarm Oluştur**:
   - Sağ üst köşe → **Alarm saati** simgesi (⏰)
   - Condition:
     - Indicator: **Trident Trader PRO v1**
     - Alert: **"Buy Signal"** seç
   
2. **Alarm Ayarları**:
   - Name: `Trident Buy Alert`
   - **Once Per Bar Close** ✅ (ÇOK ÖNEMLİ! - yoksa her tick'te alarm gelir)
   - Expiration: `Open-ended`

3. **Notification Settings**:
   - Notify on App: İsteğe bağlı
   - Show Popup: İsteğe bağlı
   - Send Email: İsteğe bağlı
   - **Webhook URL**: `https://your-bot-url.onrender.com/webhook` (Adım 2'den)
   
4. **Message**:
   - Varsayılan mesajı kullan (indicator içindeki JSON formatı)
   - Dokunma, otomatik dolacak

5. **"Create"** → Alarm aktif! 🎉

6. **Diğer Alarmları da Kur**:
   - Aynı adımları tekrarla:
     - "Strong Buy" için alarm
     - "Sell Signal" için alarm
     - "Strong Sell" için alarm

**Alarm Listesi** (toplam 4 alarm):
- ✅ Trident Buy Alert
- ✅ Trident Strong Buy Alert
- ✅ Trident Sell Alert
- ✅ Trident Strong Sell Alert

---

### Adım 5: Test Et! (5 dk)

#### Manual Test (Webhook Gönder)

PowerShell'de test isteği:
```powershell
$webhookUrl = "https://your-bot-url.onrender.com/webhook"
$secret = "your_webhook_secret_here"

$body = @{
    action = "buy"
    symbol = "BTCUSDT"
    price = 42000
    time = (Get-Date).ToString("o")
    secret = $secret
    tp = 43000
    sl = 41000
    strength = "strong"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri $webhookUrl `
    -ContentType "application/json" -Body $body
```

**Beklenen Cevap**:
```json
{
  "status": "success",
  "message": "Position opened: BUY BTCUSDT at 42000...",
  "order_id": "123456789"
}
```

**Binance'te Kontrol Et**:
- Spot Wallet → Open Orders
- Emir görünmeli (testnet kullanıyorsan testnet.binance.vision'da kontrol et)

---

#### Gerçek Alarm Testi

1. **TradingView'de Chart İzle**:
   - BTCUSDT 15m grafiği aç
   - Trident Trader PRO aktif
   - Sinyal bekle (sabırlı ol, kaliteli sinyal gelene kadar 1-2 saat sürebilir)

2. **Sinyal Geldiğinde**:
   - Chart'ta ok işareti göreceksin
   - Alarm çalacak (TradingView app/mail)
   - Bot otomatik işlem açacak

3. **Bot Loglarını İzle**:
   - Render Dashboard → Logs
   - Göreceğin:
     ```
     INFO: Webhook received: {'action': 'buy', 'symbol': 'BTCUSDT'...}
     INFO: Position opened: BUY BTCUSDT at 42150...
     INFO: TP/SL orders placed: TP=43200 SL=41500
     ```

4. **Binance'te Doğrula**:
   - Spot Wallet → Open Orders
   - İşlem açıldı mı? ✅
   - TP/SL emirleri var mı? ✅

---

## ⚙️ Önemli Ayarlar

### Risk Yönetimi

`.env` dosyasında (veya Render Environment Variables):

```bash
# Hesap başına risk yüzdesi (önerilen: 1-2%)
DEFAULT_RISK_PERCENT=1.0

# Maksimum pozisyon boyutu (USDT)
MAX_POSITION_SIZE=100

# Testnet kullan (gerçek para istemiyorsan)
USE_TESTNET=true

# İşlem tipi (spot veya futures)
TRADING_MODE=spot

# Leverage (sadece futures'ta)
LEVERAGE=3
```

**Risk Hesaplama Örneği**:
- Hesap: $1000
- Risk: 1% → $10
- SL mesafesi: 2% → Entry-SL = $840 (eğer entry $42000)
- Pozisyon boyutu: $10 / 0.02 = $500 → 0.0119 BTC

Bot bunu otomatik hesaplar!

---

### Hangi Sinyalleri Kullanmalı?

**Muhafazakar Strateji** (önerilen yeni başlayanlar için):
- Sadece "Strong Buy" ve "Strong Sell" alarmlarını aktif et
- Daha az işlem ama daha yüksek kalite
- Win rate: ~%60-70

**Agresif Strateji**:
- Tüm "Buy" ve "Sell" alarmlarını aktif et
- Daha fazla işlem
- Win rate: ~%50-55
- Daha fazla takip gerektirir

**Hybrid Strateji**:
- Strong sinyaller: Full risk (1%)
- Normal sinyaller: Yarı risk (0.5%)
- Bot'ta henüz desteklenmiyor (gelecek versiyonda)

---

## 🛡️ Güvenlik İpuçları

### ✅ Yapılması Gerekenler

1. **API Key Kısıtlamaları**:
   - ❌ Withdrawal (çekim) yetkisi verme!
   - ✅ Sadece trading yetkisi
   - ✅ IP whitelist kullan (bot IP'sini ekle)

2. **Webhook Secret**:
   - En az 32 karakter
   - Random karakterler
   - Kimseyle paylaşma

3. **Risk Limitleri**:
   - Başlangıç: 1% risk
   - Hiçbir zaman %5'ten fazla değil
   - Maksimum pozisyon sayısı: 3-5

4. **Testnet Kullan**:
   - İlk 1 hafta testnet'te test et
   - Gerçek para ile başlamadan önce sistemin çalıştığından emin ol

5. **Günlük Kontrol**:
   - Sabah/akşam pozisyonları kontrol et
   - Bot loglarına bak
   - Binance bakiyesini doğrula

### ❌ Yapılmaması Gerekenler

1. ❌ API key'i herkese açık GitHub repo'ya yükleme
2. ❌ Tüm paranı bot'a emanet etme (başlangıç: %10-20)
3. ❌ Testnet atlamak
4. ❌ "Once Per Bar Close" seçeneğini kapatmak (spam alarm!)
5. ❌ Logları silmek (sorun çıkarsa gerekir)

---

## 🐛 Sorun Giderme

### Bot Webhook Almıyor

**Semptom**: TradingView alarm çalıyor ama Binance'te işlem yok

**Çözümler**:
1. Render logs kontrol et:
   - Dashboard → Logs
   - Hata var mı?
2. Webhook URL doğru mu?
   - Alarm ayarlarını kontrol et
   - `https://` ile başlamalı
3. Bot uyuyor mu? (Render free plan)
   - `/health` endpoint'e gir → uyandır
   - UptimeRobot ekle (5dk'da bir ping)

---

### "Invalid Signature" Hatası

**Semptom**: Bot loglarında `Binance APIError: Invalid signature`

**Çözüm**:
1. API Secret doğru mu?
   - `.env` veya Render'da kontrol et
2. Sistem saati senkron mu?
   - Windows: Ayarlar → Zaman → Otomatik saat
3. Binance API permissions:
   - Spot Trading aktif mi?

---

### "Insufficient Balance" Hatası

**Semptom**: `Insufficient balance for BUY order`

**Çözüm**:
1. Binance spot wallet bakiyeni kontrol et
2. Testnet kullanıyorsan testnet wallet'ına para ekle
   - [testnet.binance.vision](https://testnet.binance.vision) → Faucet
3. Risk yüzdesi çok yüksek mi?
   - `DEFAULT_RISK_PERCENT` düşür

---

### Alarmlar Çok Sık Geliyor

**Semptom**: Dakikada 10+ alarm (spam!)

**Çözüm**:
1. "Once Per Bar Close" seçilmiş mi?
   - Alarm ayarlarını kontrol et
   - ✅ işareti olmalı
2. Timeframe çok düşük mü?
   - 1m yerine 15m veya 1h kullan
   - Daha az gürültü, daha kaliteli sinyaller

---

### İşlemler Açılıyor Ama TP/SL Yok

**Semptom**: Binance'te pozisyon var ama TP/SL emirleri yok

**Çözüm**:
1. Bot loglarına bak:
   - TP/SL placement hatası var mı?
2. Indicator'de TP/SL hesaplanıyor mu?
   - Chart'ta dashboard kontrol et
   - "N/A" yazıyorsa ATR çok düşük
3. Binance API permissions:
   - "Enable Spot Trading" aktif olmalı

---

## 📊 Performans İzleme

### Günlük Checklist

**Sabah** (9:00):
- [ ] Bot çalışıyor mu? (`/health` check)
- [ ] Gece açılan pozisyonlar var mı?
- [ ] Render logs temiz mi? (hata yok)

**Akşam** (21:00):
- [ ] Günlük P&L ne? (Binance → Wallet → History)
- [ ] Kaç işlem yapıldı?
- [ ] Risk limitleri aşıldı mı?

### Haftalık Review

**Pazar** (hafta sonu):
- [ ] Win rate hesapla:
  - Kazanan işlemler / Toplam işlemler
  - Hedef: > %50
- [ ] Max drawdown:
  - En büyük kayıp serisi
  - Hedef: < %10
- [ ] Risk-Reward:
  - Ortalama kazanç / Ortalama kayıp
  - Hedef: > 1.5:1
- [ ] Strateji ayarlaması gerekli mi?
  - Win rate düşükse: Sadece Strong sinyaller kullan
  - Çok az işlem varsa: Normal sinyaller ekle

---

## 🎓 İleri Seviye

### Trailing Stop Ekle

Bot'ta zaten var! Aktifleştirmek için:

1. `.env` dosyasına ekle:
   ```bash
   ENABLE_TRAILING_STOP=true
   TRAILING_STOP_PERCENT=1.5
   ```

2. Çalışma şekli:
   - İşlem %3 kâra geçince trailing aktif olur
   - Fiyat geri dönerse %1.5'te stop olur
   - Uptrend devam ederse kar kilitleme devam eder

### Multiple Timeframe Strategy

**Örnek**:
- 15m chart: Trident PRO ile sinyaller
- 1h chart: Trident PRO ile trend filtre
- Sadece her iki timeframe'de aynı yönde sinyal varsa işlem aç

**Kurulum**:
1. 15m chart'a Trident PRO ekle → Alarmlar kur
2. 1h chart'a Trident PRO ekle
3. Pine Script'te:
   ```pinescript
   htfBullish = request.security(syminfo.tickerid, "60", trendBullish)
   buyWithHTF = buySignal and htfBullish
   alertcondition(buyWithHTF, ...)
   ```

(Bu özellik Trident PRO v1'de built-in!)

---

## 🎉 Başarılı Kurulum!

Tebrikler! Otomatik işlem sisteminiz hazır 🚀

**Son Kontrol**:
- ✅ Binance API key alındı (withdrawal kapalı)
- ✅ Bot deploy edildi (Render/Railway/Replit)
- ✅ TradingView alarmları kuruldu
- ✅ Testnet'te test edildi
- ✅ Gerçek para ile küçük başlandı

**İlk Gün**:
- Testnet kullan
- Logları izle
- Her sinyali manuel kontrol et

**İlk Hafta**:
- Hala testnet
- Win rate hesapla
- Risk ayarlarını optimize et

**Canlıya Geçiş**:
- `USE_TESTNET=false`
- Küçük başla ($100-500)
- İlk ay %1 risk, sonra artırabilirsin

---

## 📞 Destek

Sorun yaşıyorsan:
1. Bu dokümanın "Sorun Giderme" bölümüne bak
2. Bot loglarını kontrol et (`automation/logs/` veya Render logs)
3. Discord: [Trident Trader Community](#)
4. Email: support@tridenttrader.com

**Önemli**: Destek isterken API key'lerini ASLA paylaşma!

---

## ⚠️ Risk Uyarısı

**OKUDUĞUNU ANLADIĞINA EMİN OL**:

- Otomatik ticaret risklidir
- Geçmiş performans gelecek getiriyi garanti etmez
- Kaybetmeyi göze alamayacağın para ile işlem yapma
- Bot bir araçtır, sihirli değnek değil
- Her zaman stop-loss kullan
- Risk yönetimi senin sorumluluğundur
- Bu bot finansal tavsiye değildir

**Önerilen Başlangıç**:
- Testnet'te 1 hafta
- Gerçek para ile $100-200
- 1% risk ile başla
- İlk ay manuel kontrol et

Bol kazançlar! 💰🚀

---

*Son güncelleme: Ocak 2025*  
*Versiyon: 1.0*  
*Trident Trader © 2025*
