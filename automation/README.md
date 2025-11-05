# 🔱 Trident Trader PRO v2.0 - Professional Auto Trading System

**Complete TradingView + Binance automation with web dashboard**

---

## 🎯 What Is This?

Professional-grade cryptocurrency auto-trading system that:
1. **Receives signals** from TradingView (Trident Trader indicator)
2. **Executes trades** automatically on Binance
3. **Manages positions** with TP/SL and risk management
4. **Provides dashboard** for real-time monitoring

---

## ✅ What's Included

### 📊 TradingView Indicator
- **File**: `../indicator/trident_trader_v1_pro.pine`
- Triple confluence signals (Trend + Momentum + Liquidity)
- Non-repainting, MTF-confirmed
- Webhook JSON messages included

### 🤖 Trading Bot
- **File**: `bot_v2_pro.py`
- FastAPI webhook listener
- Binance API integration (spot/futures)
- SQLite position tracking
- Risk management built-in
- **715 lines** of professional code

### 🖥️ Web Dashboard
- **File**: `templates/dashboard.html`
- Real-time position monitoring
- P&L charts
- Activity logs
- Emergency stop button
- Modern UI (glassmorphism)

### 🚀 Deployment
- One-click PowerShell script (`deploy.ps1`)
- Docker & Docker Compose
- Render.com config
- Full documentation (EN + TR)

---

## 🚀 Quick Start (30 Minutes)

### 1. Get API Keys (5 min)
```powershell
# Binance API Key
https://binance.com → Profile → API Management → Create API
✅ Enable Spot Trading
❌ Disable Withdrawals
```

### 2. Deploy Bot (10 min)
```powershell
cd C:\TridentTrader\automation

# Run deployment script
.\deploy.ps1

# Choose option 1 (Local Development)
# Script will:
# - Create virtual environment
# - Install dependencies
# - Setup .env file
# - Create directories
# - Test bot
```

### 3. Configure (5 min)
Edit `.env` file:
```bash
BINANCE_API_KEY=your_key_here
BINANCE_API_SECRET=your_secret_here
WEBHOOK_SECRET=random_32_characters
USE_TESTNET=true  # Start with testnet!
DEFAULT_RISK_PERCENT=1.0
```

### 4. Start Bot (1 min)
```powershell
python bot_v2_pro.py

# Or with auto-reload:
uvicorn bot_v2_pro:app --reload --host 0.0.0.0 --port 8000
```

Dashboard: **http://localhost:8000**

### 5. Setup TradingView (10 min)
1. Open indicator: `trident_trader_v1_pro.pine`
2. Edit webhook secret (line 366-370): `"secret":"your_webhook_secret"`
3. Add to TradingView chart
4. Create alerts:
   - Buy Signal → Webhook URL: `http://your-bot-url/webhook`
   - Strong Buy → Same URL
   - Sell Signal → Same URL
   - Strong Sell → Same URL
5. ✅ Check "Once Per Bar Close"

---

## 📁 Project Structure

```
automation/
├── bot_v2_pro.py              # 🤖 Main bot (715 lines)
├── binance_bot.py             # Legacy v1 (keep for reference)
├── requirements.txt           # Dependencies
├── .env.example               # Config template
├── deploy.ps1                 # One-click deploy script
├── Dockerfile                 # Container build
├── docker-compose.yml         # Multi-service setup
├── render.yaml                # Render.com config
│
├── templates/
│   └── dashboard.html         # 🖥️ Web UI
│
├── data/                      # SQLite database (auto-created)
├── logs/                      # Bot logs (auto-created)
├── static/                    # Static files (auto-created)
│
└── docs/
    ├── DEPLOYMENT_GUIDE.md    # Full deployment guide (EN)
    ├── KURULUM_TR.md          # Turkish setup (30 min)
    ├── TESTING.md             # 16 test scenarios
    ├── FEATURES_ROADMAP.md    # Complete feature list + roadmap
    └── SUMMARY.md             # Project overview
```

---

## 🎛️ Key Features

### 🤖 Trading Bot
- ✅ Automatic order execution
- ✅ Position sizing (risk % based)
- ✅ Stop-loss & take-profit
- ✅ Multi-symbol support
- ✅ Spot & futures modes
- ✅ Emergency stop
- ✅ Real-time WebSocket updates

### 📊 Web Dashboard
- ✅ Live position tracking
- ✅ P&L chart (Chart.js)
- ✅ Activity log viewer
- ✅ Balance monitor
- ✅ Win rate calculator
- ✅ Emergency stop button
- ✅ Mobile-friendly

### 🔒 Security
- ✅ HMAC signature verification
- ✅ Environment variables
- ✅ No hardcoded secrets
- ✅ Withdrawal disabled by default
- ✅ Testnet mode

### 📈 Analytics
- ✅ Position history (SQLite)
- ✅ Daily performance stats
- ✅ Win/loss tracking
- ✅ P&L calculation
- ✅ Event logging

---

## 📊 System Architecture

```
┌─────────────────┐
│  TradingView    │
│  Indicator      │
│  (Pine Script)  │
└────────┬────────┘
         │ Webhook (JSON)
         │ {"action":"buy", "symbol":"BTCUSDT"...}
         ▼
┌─────────────────┐
│  FastAPI Bot    │◄──────┐
│  (Python)       │       │
│  Port 8000      │       │ WebSocket
└────────┬────────┘       │
         │                │
         │ Binance API    │
         ▼                │
┌─────────────────┐       │
│  Binance        │       │
│  Exchange       │       │
│  (Spot/Futures) │       │
└─────────────────┘       │
                          │
┌─────────────────┐       │
│  Web Dashboard  ├───────┘
│  (Browser)      │
│  Real-time UI   │
└─────────────────┘

Database: SQLite (positions, trades, stats)
```

---

## 🧪 Testing

### Testnet (Recommended First!)
```bash
USE_TESTNET=true  # In .env file
```
- Get testnet API key: https://testnet.binance.vision
- Free test USDT
- Zero risk!

### Manual Test
```powershell
# Test webhook
$body = @{
    action = "buy"
    symbol = "BTCUSDT"
    price = 42000
    secret = "your_webhook_secret"
} | ConvertTo-Json

Invoke-RestMethod -Method Post `
    -Uri "http://localhost:8000/webhook" `
    -ContentType "application/json" `
    -Body $body
```

### Production Checklist
- [ ] Testnet tested for 1+ week
- [ ] Win rate > 50%
- [ ] Risk settings validated
- [ ] Emergency stop tested
- [ ] Dashboard monitoring daily
- [ ] Backups configured

See `TESTING.md` for 16 test scenarios.

---

## 📈 Performance Monitoring

### Dashboard Metrics
- **Balance**: Real-time USDT balance
- **Open Positions**: Active trades count
- **Total P&L**: Cumulative profit/loss
- **Win Rate**: Winning trades %

### API Endpoints
```
GET  /health              # Bot status
GET  /api/positions       # All positions
GET  /api/performance     # Performance metrics
GET  /api/logs            # Recent events
GET  /api/balance         # Account balance
POST /api/emergency-stop  # Close all positions
```

---

## 🚀 Deployment Options

### Option 1: Local (Windows/Mac/Linux)
```powershell
.\deploy.ps1  # PowerShell script
# Or:
python bot_v2_pro.py
```

### Option 2: Render.com (Free!)
```powershell
.\deploy.ps1
# Choose option 2 (Production Deploy)
# Follow on-screen instructions
```
- **Cost**: $0/month (free tier)
- **Uptime**: 99%+
- **URL**: https://your-app.onrender.com

### Option 3: Docker
```powershell
# Build image
docker build -t trident-bot .

# Run container
docker run -d --name trident-bot `
    -p 8000:8000 `
    --env-file .env `
    trident-bot
```

### Option 4: Docker Compose (Advanced)
```powershell
docker-compose up -d

# With monitoring:
docker-compose --profile monitoring up -d
```
Includes:
- Trading bot
- Auto-backup
- Prometheus (metrics)
- Grafana (visualization)

---

## ⚙️ Configuration

### Essential Settings (.env)
```bash
# API Keys (REQUIRED)
BINANCE_API_KEY=your_key
BINANCE_API_SECRET=your_secret
WEBHOOK_SECRET=random_32_chars

# Mode
USE_TESTNET=true          # true = safe, false = real money
TRADING_MODE=spot         # spot or futures

# Risk Management
DEFAULT_RISK_PERCENT=1.0  # 1% account risk per trade
MAX_OPEN_POSITIONS=5      # Max concurrent trades
MIN_USDT_ORDER=10.0       # Minimum order size

# Futures Only
LEVERAGE=3                # Leverage (if futures)

# Optional
ENABLE_TRAILING_STOP=false
TRAILING_STOP_PERCENT=1.5
ENABLE_PARTIAL_CLOSE=true
PARTIAL_CLOSE_PERCENT=50
LOG_LEVEL=INFO
```

---

## 📚 Documentation

### English
- **DEPLOYMENT_GUIDE.md** - Complete deployment (3 platforms)
- **TESTING.md** - 16 test scenarios + checklist
- **FEATURES_ROADMAP.md** - Full feature list + roadmap

### Türkçe 🇹🇷
- **KURULUM_TR.md** - 30 dakikada kurulum (adım adım)
- **SUMMARY.md** - Proje özeti

### General
- **../documentation/USER_GUIDE.md** - 50+ page indicator guide
- **../documentation/QUICK_START.md** - 5-minute setup

---

## 🆘 Troubleshooting

### Bot Won't Start
```powershell
# Check Python version
python --version  # Need 3.9+

# Reinstall dependencies
pip install -r requirements.txt

# Check .env file
cat .env  # Keys correct?
```

### No Trades Executing
- ✅ Bot running? Check `/health` endpoint
- ✅ Webhook URL correct? (https://)
- ✅ Secret matches? (indicator vs .env)
- ✅ TradingView Pro? (webhook feature)
- ✅ Binance API permissions? (spot trading enabled)

### Dashboard Not Loading
```powershell
# Check port
netstat -an | findstr "8000"

# Check logs
cat logs/bot.log

# Restart bot
python bot_v2_pro.py
```

See `KURULUM_TR.md` Sorun Giderme section for more.

---

## 🛡️ Security Best Practices

### ✅ DO
- Use testnet first (1+ week)
- Start with low risk (1%)
- Enable stop-loss always
- Monitor dashboard daily
- Backup database weekly
- Use strong webhook secret (32+ chars)
- Restrict Binance API (no withdrawal!)

### ❌ DON'T
- Share API keys
- Commit .env to GitHub
- Skip testnet
- Risk >5% per trade
- Ignore logs
- Use same secret as example

---

## 📞 Support

### Community
- **Discord**: [Coming soon]
- **Telegram**: [Coming soon]
- **GitHub Issues**: [Your repo]/issues

### Documentation
- All guides in `automation/` directory
- Turkish docs included
- Code comments in English

### Emergency
- Use **Emergency Stop** button in dashboard
- Or: `POST /api/emergency-stop`
- Or: Delete Binance API key

---

## 📜 License

**Proprietary** - For personal use or with license.

---

## 🎉 You're Ready!

### Next Steps:
1. ✅ Run `.\deploy.ps1`
2. ✅ Configure `.env`
3. ✅ Start bot: `python bot_v2_pro.py`
4. ✅ Open dashboard: http://localhost:8000
5. ✅ Setup TradingView alerts
6. ✅ Test with testnet
7. ✅ Start trading! 🚀

---

**Status**: ✅ Production Ready v2.0  
**Last Updated**: January 2025  
**Made with** 💜 **by Trident Trader Team**

---

*⚠️ Risk Warning: Automated trading involves substantial risk. Only trade with money you can afford to lose. Past performance does not guarantee future results. This is not financial advice.*
