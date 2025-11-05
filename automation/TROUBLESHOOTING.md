# 🆘 Troubleshooting Guide

## Common Issues & Solutions

### 1. Bot Won't Start

**Symptom**: Container crashes or Python error on startup

**Possible Causes**:
- Missing or invalid API keys
- Database file permissions
- Port already in use

**Solutions**:
```bash
# Check logs
docker logs trident-bot --tail 50

# Verify environment variables
docker exec trident-bot env | grep BINANCE

# Test API keys
python -c "from binance.client import Client; c = Client('YOUR_KEY', 'YOUR_SECRET', testnet=True); print(c.get_account())"

# Check port availability
netstat -an | findstr :8000
```

### 2. Dashboard Shows "Disconnected"

**Symptom**: WebSocket connection fails, dashboard not updating

**Possible Causes**:
- Auth token mismatch
- Firewall/proxy blocking WebSocket
- Bot not running

**Solutions**:
1. Check health endpoint: `curl https://your-bot.com/health`
2. Verify auth token matches in Settings modal
3. Check browser console (F12) for WebSocket errors
4. Try accessing without proxy/VPN
5. Restart bot container

### 3. Webhook Not Receiving Signals

**Symptom**: TradingView alerts fire but bot doesn't react

**Possible Causes**:
- Wrong webhook URL
- Invalid webhook secret
- Firewall blocking incoming requests
- SSL certificate issues

**Solutions**:
```bash
# Test webhook manually
curl -X POST https://your-bot.com/webhook \
  -H "Content-Type: application/json" \
  -d '{"action":"buy","symbol":"BTCUSDT","price":50000,"secret":"YOUR_SECRET","tp":0,"sl":0,"strength":"normal"}'

# Check logs for webhook attempts
docker logs trident-bot | grep "Webhook"

# Verify TradingView alert format matches expected JSON
```

**Alert Message Template**:
```json
{"action":"buy","symbol":"{{ticker}}","price":{{close}},"time":"{{timenow}}","interval":"{{interval}}","secret":"YOUR_WEBHOOK_SECRET","tp":0,"sl":0,"strength":"normal"}
```

### 4. Orders Failing on Binance

**Symptom**: "Insufficient balance" or "LOT_SIZE" errors

**Possible Causes**:
- Insufficient USDT balance
- Symbol filters (min/max quantity)
- Market closed or delisted
- API restrictions

**Solutions**:
```bash
# Check balance
curl https://your-bot.com/api/balance?token=YOUR_TOKEN

# Verify symbol info
python -c "from binance.client import Client; c = Client('KEY', 'SECRET'); print(c.get_symbol_info('BTCUSDT'))"

# Check MIN_USDT_ORDER setting (default 10)
# Increase if needed for higher-priced assets
```

### 5. Positions Not Showing in Dashboard

**Symptom**: Trade executed but not in dashboard

**Possible Causes**:
- Database write failed
- WebSocket not broadcasting
- Browser cache issue

**Solutions**:
1. Hard refresh browser (Ctrl+Shift+R)
2. Check `/api/positions` directly
3. Verify database file exists and writable:
   ```bash
   docker exec trident-bot ls -la /app/data/
   ```
4. Check for DB errors in logs

### 6. Stop-Loss Not Triggering

**Symptom**: Price hit SL but position not closed

**Possible Causes**:
- Binance SL order rejected (insufficient balance for fees)
- Order expired
- Price gap (slippage)

**Solutions**:
1. Check Binance open orders manually
2. Verify sufficient balance for fees (~0.1%)
3. Use market SL instead of limit
4. Monitor logs for order placement errors

### 7. Emergency Stop Not Working

**Symptom**: Emergency button doesn't close positions

**Possible Causes**:
- Auth token invalid
- Network issue
- Binance API down

**Solutions**:
```bash
# Try via curl
curl -X POST https://your-bot.com/api/emergency-stop \
  -H "Authorization: Bearer YOUR_TOKEN"

# Close manually on Binance if needed
# Then update DB:
# docker exec -it trident-bot sqlite3 /app/data/positions.db
# UPDATE positions SET status='closed' WHERE status='open';
```

### 8. Telegram Notifications Not Sending

**Symptom**: No messages despite bot running

**Solutions**:
```bash
# Test Telegram bot token
curl "https://api.telegram.org/botYOUR_TOKEN/getMe"

# Get your chat ID
curl "https://api.telegram.org/botYOUR_TOKEN/getUpdates"

# Send test message
curl -X POST "https://api.telegram.org/botYOUR_TOKEN/sendMessage" \
  -d "chat_id=YOUR_CHAT_ID&text=Test from Trident Bot"

# Verify env vars set
docker exec trident-bot env | grep TELEGRAM
```

### 9. Dashboard Settings Not Saving

**Symptom**: Settings modal updates but changes don't persist

**Cause**: POST /api/config is runtime only (not persistent)

**Solution**: 
- Update `.env` file for permanent changes
- Runtime changes via dashboard are temporary (until restart)
- For production, update env vars and redeploy

### 10. High CPU/Memory Usage

**Symptom**: Container using excessive resources

**Possible Causes**:
- Too many open WebSocket connections
- Database bloat
- Memory leak

**Solutions**:
```bash
# Check container stats
docker stats trident-bot

# Restart container
docker restart trident-bot

# Clear old logs/database entries
docker exec trident-bot sqlite3 /app/data/positions.db \
  "DELETE FROM bot_events WHERE timestamp < date('now', '-30 days');"

# Limit WebSocket connections (review code)
```

## Error Messages Decoded

| Error | Meaning | Fix |
|-------|---------|-----|
| `Import "binance.client" could not be resolved` | Missing python-binance | `pip install python-binance` |
| `401 Unauthorized` | Invalid API key or token | Check credentials in .env |
| `403 Forbidden` | Webhook secret mismatch | Verify WEBHOOK_SECRET matches alert |
| `Invalid symbol format` | Symbol validation failed | Use format like BTCUSDT |
| `Binance client not initialized` | API key error on startup | Check logs for init error |
| `Max positions reached` | Hit MAX_OPEN_POSITIONS limit | Close positions or increase limit |
| `LOT_SIZE` | Quantity doesn't meet exchange filters | Adjust MIN_USDT_ORDER |
| `Insufficient balance` | Not enough USDT | Add funds or reduce risk % |

## Debug Mode

Enable detailed logging:

**.env**:
```bash
LOG_LEVEL=DEBUG
```

View logs in real-time:
```bash
# Docker
docker logs -f trident-bot

# Local Python
tail -f logs/bot.log
```

## Health Check Quick Test

```bash
# 1. Bot responsive
curl https://your-bot.com/health
# Expected: {"status":"healthy", ...}

# 2. Auth working
curl https://your-bot.com/api/config -H "Authorization: Bearer YOUR_TOKEN"
# Expected: {...config...}

# 3. Readiness
curl https://your-bot.com/api/readiness -H "Authorization: Bearer YOUR_TOKEN"
# Expected: {"overall":true, ...}

# 4. Dashboard loads
# Open https://your-bot.com in browser
```

## Still Having Issues?

1. Review `/automation/TESTING.md` test scenarios
2. Check `/automation/README.md` architecture docs
3. Review logs for specific error messages
4. Email: support@tridenttrader.com

Include in support request:
- Bot version (v2.0)
- Error message (exact text)
- Logs (last 100 lines)
- Environment (Docker/local/Render)
- Steps to reproduce

---

*Most issues resolve with proper .env configuration and API key permissions.*
