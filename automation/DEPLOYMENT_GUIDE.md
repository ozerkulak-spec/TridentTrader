# 🚀 Trident Trader Otomasyon Bot - Deployment Kılavuzu

## 📋 İçindekiler
1. [Render.com ile Deploy](#1-rendercom-ile-deploy-ücretsiz)
2. [Railway ile Deploy](#2-railway-ile-deploy)
3. [Replit ile Deploy](#3-replit-ile-deploy-en-kolay)
4. [Lokal Test](#4-lokal-test)
5. [TradingView Alarm Kurulumu](#5-tradingview-alarm-kurulumu)
6. [Güvenlik Kontrol Listesi](#6-güvenlik-kontrol-listesi)

---

## 1. Render.com ile Deploy (ÜCRETSİZ)

### Adım 1: GitHub Repo Oluştur
```bash
cd C:\TridentTrader\automation
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/KULLANICI_ADINIZ/trident-bot.git
git push -u origin main
```

### Adım 2: Render.com'a Kayıt
1. [render.com](https://render.com) → Sign Up (GitHub ile)
2. New → Web Service
3. Connect GitHub repo: `trident-bot`
4. Ayarlar:
   - **Name**: `trident-trader-bot`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn binance_bot:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free (0$/ay)

### Adım 3: Environment Variables Ekle
Render dashboard → Environment:
```
BINANCE_API_KEY=xxxxxxxxxxxxx
BINANCE_API_SECRET=xxxxxxxxxxxxx
WEBHOOK_SECRET=güçlü_random_string_12345
DEFAULT_RISK_PERCENT=1.0
USE_TESTNET=true
TRADING_MODE=spot
LOG_LEVEL=INFO
```

### Adım 4: Deploy!
- "Create Web Service" → 2-3 dakika bekle
- URL: `https://trident-trader-bot-XXXX.onrender.com`
- Test: `https://your-url.onrender.com/health` → `{"status":"healthy"}`

### ⚠️ Render Free Plan Uyarı
- 15 dakika inaktif olursa uyur (ilk istek 30sn gecikir)
- Çözüm: [UptimeRobot](https://uptimerobot.com) ile 5 dakikada bir `/health` ping at

---

## 2. Railway ile Deploy

### Adım 1: Railway Kurulum
```bash
npm install -g @railway/cli
railway login
```

### Adım 2: Proje Oluştur
```bash
cd C:\TridentTrader\automation
railway init
railway link
```

### Adım 3: Environment Variables
```bash
railway variables set BINANCE_API_KEY=xxxxx
railway variables set BINANCE_API_SECRET=xxxxx
railway variables set WEBHOOK_SECRET=xxxxx
railway variables set USE_TESTNET=true
```

### Adım 4: Deploy
```bash
railway up
railway open
```

### Fiyat
- İlk 5$ ücretsiz kredi
- Sonra ~5$/ay (hobby plan)

---

## 3. Replit ile Deploy (EN KOLAY)

### Adım 1: Replit'e Git
1. [replit.com](https://replit.com) → Sign Up
2. Create Repl → Import from GitHub: `your-repo/trident-bot`
3. Language: Python

### Adım 2: Secrets Ekle
Sol menü → Secrets (🔒):
```
BINANCE_API_KEY=xxxxx
BINANCE_API_SECRET=xxxxx
WEBHOOK_SECRET=xxxxx
USE_TESTNET=true
```

### Adım 3: .replit Dosyası Oluştur
```toml
run = "uvicorn binance_bot:app --host 0.0.0.0 --port 8000"

[nix]
channel = "stable-22_11"

[deployment]
run = ["sh", "-c", "uvicorn binance_bot:app --host 0.0.0.0 --port 8000"]
```

### Adım 4: Run!
- "Run" butonuna bas
- URL: Sağ üstte görünecek
- Always On için Replit Hacker plan gerekli ($7/ay)

---

## 4. Lokal Test

### Windows PowerShell
```powershell
cd C:\TridentTrader\automation

# .env dosyası oluştur (.env.example'dan kopyala)
Copy-Item .env.example .env
notepad .env  # API key'leri gir

# Sanal ortam oluştur
python -m venv venv
.\venv\Scripts\Activate.ps1

# Bağımlılıkları kur
pip install -r requirements.txt

# Botu başlat
uvicorn binance_bot:app --reload --host 127.0.0.1 --port 8000
```

### Ngrok ile Dışarı Aç (TradingView için)
```powershell
# Ngrok indir: https://ngrok.com/download
ngrok http 8000
```
Webhook URL: `https://xxxx-xx-xx-xx.ngrok-free.app/webhook`

### Test İsteği Gönder
```powershell
$body = @{
    action = "buy"
    symbol = "BTCUSDT"
    price = 42000
    time = (Get-Date).ToString("o")
    secret = "güçlü_random_string_12345"
    tp = 43000
    sl = 41000
    strength = "strong"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://localhost:8000/webhook" `
    -ContentType "application/json" -Body $body
```

Cevap: `{"status":"success","message":"Position opened: BUY BTCUSDT..."}`

---

## 5. TradingView Alarm Kurulumu

### Adım 1: Indicator'ü Yükle
1. TradingView → Chart aç (BTCUSDT)
2. Indicators → Favorites → "Trident Trader PRO v1"
3. Settings → `YOUR_WEBHOOK_SECRET` yerine gerçek secret'ını yaz

### Adım 2: Alert Oluştur
1. Sağ üst köşe → Alarm saati simgesi
2. Condition:
   - **Indicator**: Trident Trader PRO v1
   - **Alert**: "Buy Signal" veya "Strong Buy"
3. Options:
   - "Once Per Bar Close" ✅ (önemli!)
4. Notifications:
   - **Webhook URL**: `https://your-bot-url.onrender.com/webhook`
5. Message:
   ```
   Varsayılan mesaj kullan (indicator içindeki JSON)
   ```
6. "Create"

### Adım 3: Alarmları Test Et
- Paper trading ile test et!
- Binance Testnet kullan (`USE_TESTNET=true`)
- Gerçek para ile başlamadan önce 1 hafta test et

### ⚠️ Önemli Notlar
- **Once Per Bar Close** seçilmezse her tick'te alarm gelir (çok fazla işlem!)
- **Webhook URL**'de `https://` olmalı (http:// çalışmaz)
- **Secret** hem indicator hem bot'ta aynı olmalı

---

## 6. Güvenlik Kontrol Listesi

### ✅ Deployment Öncesi
- [ ] `.env` dosyası `.gitignore`'da
- [ ] `WEBHOOK_SECRET` 32+ karakter random string
- [ ] Binance API key **SADECE** spot trading/futures yetkisi (withdrawal yok!)
- [ ] `USE_TESTNET=true` ile test et
- [ ] IP whitelist aktif (Binance API ayarları)
- [ ] Log dosyalarında API key yok

### ✅ Binance API Ayarları
1. Binance → Profile → API Management
2. Create API
3. Restrictions:
   - ✅ Enable Spot & Margin Trading
   - ✅ Enable Futures (opsiyonel)
   - ❌ Enable Withdrawals (KAPALI!)
   - ✅ Restrict access to trusted IPs (bot sunucu IP'si)
4. API Key → Copy
5. Secret Key → Copy (bir daha göstermez!)

### ✅ Canlıya Geçiş
- [ ] Testnet'te en az 1 hafta test edildi
- [ ] Win rate > %50 (backtest)
- [ ] Max drawdown < %20
- [ ] `USE_TESTNET=false` yap
- [ ] `DEFAULT_RISK_PERCENT=1.0` (başlangıç için düşük tut)
- [ ] Emergency stop kodu hazır (botları durdur script)

---

## 🆘 Sorun Giderme

### Bot Çalışmıyor
```bash
# Logları kontrol et
railway logs  # Railway
render logs   # Render
# veya Replit console'a bak
```

Yaygın hatalar:
- `401 Unauthorized`: Binance API key yanlış
- `Invalid signature`: API secret yanlış veya timestamp hatalı
- `Insufficient balance`: Binance'te bakiye yok
- `Invalid webhook secret`: Indicator'daki secret bot'la uyuşmuyor

### Alarmlar Gelmiyor
- TradingView Pro hesap gerekli (webhook için)
- Webhook URL `https://` ile başlıyor mu?
- Bot `/health` endpoint'i çalışıyor mu?
- Render free plan uyuyorsa 30sn bekle

### İşlemler Açılmıyor
- `LOG_LEVEL=DEBUG` yap, detaylı log göreceksin
- Binance API restrictions kontrol et
- Testnet'te çalışıyor ama mainnet'te çalışmıyorsa API key kısıtlaması var

---

## 📞 Destek

Sorun yaşıyorsan:
1. `automation/logs/` klasöründeki loglara bak
2. GitHub Issues: `your-repo/issues`
3. Discord: [davet linki]
4. Email: support@tridenttrader.com

**Önemli**: API key'lerini asla paylaşma!

---

## 🎉 Başarıyla Deploy Edildi!

Webhook URL'in: `https://your-bot.onrender.com/webhook`

Test et:
```bash
curl https://your-bot.onrender.com/health
```

Cevap: `{"status":"healthy","timestamp":"...","version":"1.0.0"}`

Artık TradingView alarmları otomatik işlem yapacak! 🚀

---

**⚠️ Risk Uyarısı**: Otomatik ticaret risklidir. Kaybetmeyi göze alamayacağın para ile işlem yapma. Bu bot kar garantisi vermez. Her zaman stop-loss kullan ve risk yönetimine dikkat et.
