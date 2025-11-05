# 🚀 Production Deployment Checklist

## Pre-Deployment

### Security
- [ ] Set strong `WEBHOOK_SECRET` (min 32 chars, random)
- [ ] Set `DASHBOARD_AUTH_TOKEN` (min 32 chars, random)
- [ ] Verify Binance API key permissions (NO withdraw enabled)
- [ ] Test with `USE_TESTNET=true` for at least 1 week
- [ ] Review all logs for suspicious activity

### Configuration
- [ ] `DEFAULT_RISK_PERCENT` ≤ 2% (recommended 1%)
- [ ] `MAX_OPEN_POSITIONS` ≤ 5
- [ ] `MIN_USDT_ORDER` ≥ 10
- [ ] Leverage settings appropriate for risk tolerance
- [ ] Trailing stop and partial close configured

### Testing
- [ ] Health endpoint returns 200
- [ ] Webhook receives test alerts correctly
- [ ] Dashboard loads and displays data
- [ ] Readiness check shows all green
- [ ] Test emergency stop functionality
- [ ] Telegram notifications working (if enabled)

### Infrastructure
- [ ] Database backups scheduled (daily minimum)
- [ ] Log rotation configured
- [ ] Monitoring/alerting set up (optional)
- [ ] SSL/TLS enabled for webhook endpoint
- [ ] Container health checks passing

## Go-Live Steps

1. **Final Testnet Verification**
   ```bash
   # Check balance
   curl https://your-bot.com/api/balance?token=YOUR_TOKEN
   
   # Verify mode
   curl https://your-bot.com/health
   # Should show "mode": "testnet"
   ```

2. **Switch to Production**
   - Set `USE_TESTNET=false`
   - Update API keys to production
   - Restart bot
   - Verify mode changed to "production"

3. **Initial Production Test**
   - Start with minimal position size
   - Send 1-2 manual test signals
   - Monitor dashboard for 24h
   - Check P&L accuracy

## Post-Deployment

### Daily Monitoring
- [ ] Check open positions count
- [ ] Review daily P&L
- [ ] Check for error logs
- [ ] Verify balance matches expected
- [ ] Review Telegram notifications

### Weekly Review
- [ ] Analyze win rate trends
- [ ] Review largest drawdown
- [ ] Check database size/performance
- [ ] Update risk parameters if needed
- [ ] Backup database manually

### Monthly Maintenance
- [ ] Review and rotate auth tokens
- [ ] Update dependencies (if needed)
- [ ] Archive old logs
- [ ] Performance tuning based on data
- [ ] Strategy adjustments

## Emergency Procedures

### If Bot Behaves Unexpectedly
1. Click **EMERGENCY STOP** in dashboard
2. Check `/api/logs` for recent errors
3. Verify balance on Binance directly
4. Set `TRADING_MODE=paper` temporarily
5. Review configuration

### If Dashboard Inaccessible
```bash
# Check bot health via curl
curl https://your-bot.com/health

# View logs (Docker)
docker logs trident-bot --tail 100

# Emergency stop via API
curl -X POST https://your-bot.com/api/emergency-stop \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### If Telegram Alerts Stop
1. Verify bot token still valid
2. Check chat_id correct
3. Test manually:
   ```bash
   curl -X POST "https://api.telegram.org/botYOUR_TOKEN/sendMessage" \
     -d "chat_id=YOUR_CHAT_ID&text=Test"
   ```

## Performance Benchmarks

### Expected Metrics (After 30 Days)
- Win rate: 45-65% (depends on strategy)
- Average R:R: ≥ 1.5:1
- Max drawdown: < 15%
- Daily signals: 1-10 (depends on timeframe)

### Red Flags
- ⚠️ Win rate < 35% for 2+ weeks
- ⚠️ Max drawdown > 20%
- ⚠️ Frequent API errors
- ⚠️ Position sizes inconsistent
- ⚠️ Dashboard not updating

## Support Contacts

- Email: support@tridenttrader.com
- Documentation: `/automation/README.md`
- Troubleshooting: `/automation/TESTING.md`

---

**Remember**: Never trade with more capital than you can afford to lose. Start small, scale gradually.

*Last Updated: 2025-11-05*
