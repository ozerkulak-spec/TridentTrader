# 🧪 Trident Trader Otomasyon - Test Script'leri

## Webhook Test (Manuel)

### Test 1: Health Check
```powershell
# Bot çalışıyor mu?
$url = "https://your-bot-url.onrender.com/health"
Invoke-RestMethod -Uri $url
```

**Beklenen**: `{"status":"healthy","timestamp":"...","version":"1.0.0"}`

---

### Test 2: Buy Signal
```powershell
$webhookUrl = "https://your-bot-url.onrender.com/webhook"
$secret = "your_webhook_secret"

$buySignal = @{
    action = "buy"
    symbol = "BTCUSDT"
    price = 42000
    time = (Get-Date).ToString("o")
    interval = "15m"
    secret = $secret
    tp = 43000
    sl = 41000
    strength = "normal"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri $webhookUrl `
    -ContentType "application/json" -Body $buySignal
```

**Beklenen**: `{"status":"success","message":"Position opened: BUY BTCUSDT..."}`

---

### Test 3: Strong Sell Signal
```powershell
$sellSignal = @{
    action = "sell"
    symbol = "ETHUSDT"
    price = 2500
    time = (Get-Date).ToString("o")
    interval = "1h"
    secret = $secret
    tp = 2400
    sl = 2550
    strength = "strong"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri $webhookUrl `
    -ContentType "application/json" -Body $sellSignal
```

---

### Test 4: Invalid Secret (Güvenlik Testi)
```powershell
$invalidSignal = @{
    action = "buy"
    symbol = "BTCUSDT"
    price = 42000
    time = (Get-Date).ToString("o")
    secret = "wrong_secret"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri $webhookUrl `
    -ContentType "application/json" -Body $invalidSignal
```

**Beklenen**: `403 Forbidden` veya `{"status":"error","message":"Invalid webhook secret"}`

---

## Binance API Test

### Test 5: Bakiye Kontrol
```python
# Python
from binance.client import Client
import os

api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")

client = Client(api_key, api_secret, testnet=True)

# Bakiye
balance = client.get_asset_balance(asset='USDT')
print(f"USDT Balance: {balance}")

# Açık emirler
orders = client.get_open_orders(symbol='BTCUSDT')
print(f"Open Orders: {len(orders)}")
```

---

### Test 6: Test Emri (Paper Trading)
```python
# Testnet'te küçük emir
order = client.create_test_order(
    symbol='BTCUSDT',
    side='BUY',
    type='MARKET',
    quantity=0.001
)
print("Test order successful!")
```

---

## TradingView Alert Test

### Test 7: Alarm JSON Formatı
TradingView → Alarm → Message kısmına yapıştır:
```json
{
  "action": "buy",
  "symbol": "{{ticker}}",
  "price": {{close}},
  "time": "{{timenow}}",
  "interval": "{{interval}}",
  "secret": "your_webhook_secret",
  "tp": 0,
  "sl": 0,
  "strength": "normal"
}
```

**Test**: Alarm'ı manuel tetikle (Create → Delete) ve bot loglarına bak.

---

### Test 8: Indicator JSON Doğrulama
Pine Script'te:
```pinescript
// Konsol çıktısı ile test
buyMsg = '{"action":"buy","symbol":"' + syminfo.ticker + '"...}'
log.info(buyMsg)  // Pine v5
```

**Kontrol**: JSON valid mi? [jsonlint.com](https://jsonlint.com) ile kontrol et.

---

## Performans Testleri

### Test 9: Çoklu İşlem Stres Testi
```powershell
# 10 ardışık webhook gönder
1..10 | ForEach-Object {
    $body = @{
        action = "buy"
        symbol = "BTCUSDT"
        price = 42000 + $_
        time = (Get-Date).ToString("o")
        secret = $secret
    } | ConvertTo-Json
    
    Invoke-RestMethod -Method Post -Uri $webhookUrl `
        -ContentType "application/json" -Body $body
    
    Start-Sleep -Milliseconds 500
}
```

**Kontrol**: Bot loglarında rate limiting veya crash var mı?

---

### Test 10: Database Kontrol
```powershell
# SQLite database'e bağlan
cd C:\TridentTrader\automation
sqlite3 positions.db "SELECT * FROM positions;"
```

**Beklenen**: Açık pozisyonlar listelenecek.

---

## Güvenlik Testleri

### Test 11: HTTPS Enforcement
```powershell
# HTTP ile dene (başarısız olmalı)
Invoke-RestMethod -Uri "http://your-bot-url.onrender.com/webhook"
```

**Beklenen**: Redirect to HTTPS veya 403.

---

### Test 12: SQL Injection
```powershell
$malicious = @{
    action = "buy'; DROP TABLE positions; --"
    symbol = "BTCUSDT"
    secret = $secret
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri $webhookUrl -Body $malicious
```

**Beklenen**: Hata veya ignore (parameterized queries kullandık).

---

## Deployment Testleri

### Test 13: Environment Variables
Render dashboard → Shell:
```bash
echo $BINANCE_API_KEY
echo $WEBHOOK_SECRET
```

**Kontrol**: Değerler doğru mu?

---

### Test 14: Log Rotation
```bash
# Log dosyası boyutunu kontrol et
ls -lh /app/logs/*.log
```

**Beklenen**: Log dosyaları 10MB'dan küçük (rotation çalışıyor).

---

## Monitoring

### Test 15: Uptime Check
UptimeRobot ekle:
- Monitor Type: HTTP(s)
- URL: `https://your-bot-url.onrender.com/health`
- Interval: 5 minutes

**Kontrol**: 24 saat sonra uptime > %99.

---

### Test 16: Error Rate
Render logs:
```bash
# Son 100 satırda ERROR kaç kez geçiyor?
grep -c "ERROR" <(tail -n 100 /var/log/app.log)
```

**Hedef**: < 5 (error rate < %5)

---

## Checklist (Canlıya Geçmeden Önce)

### Functional Tests
- [ ] Health endpoint çalışıyor
- [ ] Buy signal → Binance'te işlem açılıyor
- [ ] Sell signal → Binance'te short/kapatma
- [ ] TP/SL emirleri otomatik yerleşiyor
- [ ] Invalid secret reddediliyor
- [ ] Database pozisyonları kaydediyor

### Security Tests
- [ ] Webhook secret doğrulanıyor
- [ ] API key withdrawal yetkisi yok
- [ ] HTTPS zorunlu
- [ ] SQL injection korumalı
- [ ] Rate limiting aktif (optional)

### Performance Tests
- [ ] 10 ardışık webhook handle ediyor
- [ ] Response time < 500ms
- [ ] Database queries optimize
- [ ] Log rotation çalışıyor

### Deployment Tests
- [ ] Render/Railway deploy başarılı
- [ ] Environment variables doğru
- [ ] Uptime > %99 (24 saat test)
- [ ] TradingView alarmlar webhook'a ulaşıyor

### Documentation
- [ ] KURULUM_TR.md okudum
- [ ] API key kısıtlamalarını uyguladım
- [ ] Risk yönetimini anladım
- [ ] Emergency stop prosedürü biliyorum

---

## Emergency Stop (Acil Durdurma)

### Senaryo 1: Bot Çılgına Döndü (Çok Fazla İşlem)

**Hızlı Çözüm**:
1. Binance → API Management → Delete API Key
2. TradingView → Alarms → Pause All
3. Render → Environment → `TRADING_ENABLED=false` ekle

**Uzun Çözüm**:
- Bot loglarını incele
- "Once Per Bar Close" seçeneği eksik mi?
- Timeframe çok düşük mü?

---

### Senaryo 2: Database Corrupt

```bash
# Backup al
cp positions.db positions.backup.db

# Yeni database
rm positions.db
python -c "from binance_bot import init_db; init_db()"
```

---

### Senaryo 3: Render Down

**Alternatif Deploy**:
1. Railway'e geç (10 dk)
2. Environment variables kopyala
3. GitHub push → Railway auto-deploy

---

## Test Sonuçları Şablonu

```markdown
## Test Sonuçları - [Tarih]

### Functional Tests
- Health Check: ✅ PASS
- Buy Signal: ✅ PASS
- Sell Signal: ✅ PASS
- TP/SL: ✅ PASS
- Invalid Secret: ✅ PASS (403 returned)

### Performance
- Response Time: 245ms (avg)
- Concurrent Webhooks: 10/10 handled
- Uptime: 99.8% (24h)

### Security
- HTTPS: ✅ Enforced
- SQL Injection: ✅ Protected
- API Permissions: ✅ No withdrawal

### Issues Found
- [MINOR] Log file growing (10MB/day) → Add rotation
- [FIXED] TP price miscalculation → Updated ATR multiplier

### Recommendation
✅ **READY FOR PRODUCTION** (testnet → mainnet)
```

---

**Not**: Testleri sırasıyla yap. Functional testler başarısızsa deployment yapma!

---

*Test checklist versiyonu: 1.0*  
*Son güncelleme: Ocak 2025*
