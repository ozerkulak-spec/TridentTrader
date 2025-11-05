# 🎓 Trident Trader v2.0 - Quick Reference Card

## 📋 Essential Environment Variables

```bash
# Required
BINANCE_API_KEY=your_key_here
BINANCE_API_SECRET=your_secret_here
WEBHOOK_SECRET=random_32char_string
USE_TESTNET=true  # false for production

# Optional Security
DASHBOARD_AUTH_TOKEN=random_32char_string

# Trading
DEFAULT_RISK_PERCENT=1.0
MAX_OPEN_POSITIONS=5
MIN_USDT_ORDER=10

# Optional Features
ENABLE_TRAILING_STOP=true
TRAILING_STOP_PERCENT=1.5
ENABLE_PARTIAL_CLOSE=true
PARTIAL_CLOSE_PERCENT=50
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

## 🚀 Quick Start Commands

### Docker Deployment
```bash
cd automation
docker build -t trident-bot .
docker compose up -d
docker logs -f trident-bot
```

### Local Python
```bash
cd automation
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python bot_v2_pro.py
```

### Render.com
```bash
git add .
git commit -m "Deploy bot"
git push origin main
# Then connect in Render dashboard
```

## 📡 API Endpoints

### Public
- `GET /health` - Bot status
- `POST /webhook` - TradingView alerts

### Protected (require auth token)
- `GET /` - Dashboard UI
- `GET /api/positions` - Open positions
- `GET /api/performance` - Stats
- `GET /api/logs?limit=50` - Recent events
- `GET /api/balance` - Account balance
- `GET /api/config` - Current settings
- `POST /api/config` - Update settings
- `GET /api/readiness` - System checks
- `POST /api/position/{id}/close` - Close position
- `POST /api/emergency-stop` - Close all
- `WS /ws?token=...` - Real-time updates

## 🔔 TradingView Alert Template

**Webhook URL**: `https://your-bot.com/webhook`

**Message**:
```json
{"action":"{{strategy.order.action}}","symbol":"{{ticker}}","price":{{close}},"time":"{{timenow}}","interval":"{{interval}}","secret":"YOUR_WEBHOOK_SECRET","tp":0,"sl":0,"strength":"normal"}
```

Replace:
- `{{strategy.order.action}}` → `buy` or `sell` for indicators
- `YOUR_WEBHOOK_SECRET` → Your actual secret

## 🎯 Dashboard Features

- **Real-time stats**: Balance, positions, P&L, win rate
- **Active positions**: Entry, SL, TP, current P&L, close button
- **Activity log**: All events with timestamps
- **Performance chart**: Daily P&L visualization
- **Settings modal**: Adjust risk, trailing, partial close
- **Readiness checks**: Verify all systems green
- **Emergency stop**: One-click close all positions

## 🛡️ Security Checklist

- [ ] Strong WEBHOOK_SECRET (32+ chars)
- [ ] DASHBOARD_AUTH_TOKEN set
- [ ] Binance API: NO withdraw permission
- [ ] Test with USE_TESTNET=true first
- [ ] HTTPS enabled for webhook
- [ ] Database backups scheduled
- [ ] Monitor logs daily

## 🔧 Common Tasks

### Check Bot Health
```bash
curl https://your-bot.com/health
```

### Test Webhook
```bash
curl -X POST https://your-bot.com/webhook \
  -H "Content-Type: application/json" \
  -d '{"action":"buy","symbol":"BTCUSDT","price":50000,"secret":"YOUR_SECRET","tp":0,"sl":0,"strength":"normal"}'
```

### View Logs
```bash
# Docker
docker logs trident-bot --tail 100

# Local
tail -f logs/bot.log
```

### Update Settings
```bash
# Via dashboard Settings button, or:
curl -X POST https://your-bot.com/api/config \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"risk_percent":1.5,"max_positions":3}'
```

### Emergency Close All
```bash
curl -X POST https://your-bot.com/api/emergency-stop \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 📊 Performance Targets

| Metric | Target | Red Flag |
|--------|--------|----------|
| Win Rate | 45-65% | <35% |
| R:R Ratio | ≥1.5:1 | <1:1 |
| Max Drawdown | <15% | >20% |
| Avg Position | 1-5% account | >10% |

## 🆘 Quick Troubleshooting

| Issue | Quick Fix |
|-------|-----------|
| Dashboard disconnected | Check auth token in Settings |
| No signals | Verify webhook URL in TradingView |
| Order rejected | Check balance, MIN_USDT_ORDER |
| Positions not closing | Check SL orders on Binance |
| Telegram silent | Verify bot token + chat ID |

## 📚 Documentation Links

- Full Setup: `/automation/KURULUM_TR.md`
- Deployment: `/automation/DEPLOYMENT_GUIDE.md`
- Testing: `/automation/TESTING.md`
- Troubleshooting: `/automation/TROUBLESHOOTING.md`
- Production: `/automation/PRODUCTION_CHECKLIST.md`
- Features: `/automation/FEATURES_ROADMAP.md`

## 🔗 Quick Links

- Binance Testnet: https://testnet.binance.vision/
- Binance API Docs: https://binance-docs.github.io/apidocs/spot/en/
- TradingView Alerts: https://www.tradingview.com/support/solutions/43000529348-about-webhooks/
- Telegram BotFather: https://t.me/BotFather

---

**Version**: v2.0  
**Last Updated**: 2025-11-05  
**Support**: support@tridenttrader.com

*Keep this card handy for quick reference during setup and daily operations.*
