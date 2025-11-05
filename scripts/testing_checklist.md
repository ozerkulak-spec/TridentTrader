# Trident Trader - Testing Checklist

Use this checklist before every release.

## Markets (Assets)
- [ ] BTC/USD (Crypto)
- [ ] ETH/USD (Crypto)
- [ ] EUR/USD (Forex)
- [ ] GBP/USD (Forex)
- [ ] SPY, AAPL, TSLA (Stocks)
- [ ] GOLD, OIL (Commodities)

## Timeframes
- [ ] 1m, 5m (Scalping)
- [ ] 15m, 1H (Balanced)
- [ ] 4H, Daily (Swing)
- [ ] Weekly

## Modes & Gates
- [ ] Scalping mode: Higher sensitivity (more signals)
- [ ] Balanced mode: Medium sensitivity
- [ ] Swing mode: Lower sensitivity (fewer but cleaner)
- [ ] MTF confirmation (on): Signals align with HTF trend
- [ ] ADX filter: Below threshold reduces signals
- [ ] Volatility gate: Low ATR reduces signals

## Zones
- [ ] Supply/Demand boxes render with correct thickness
- [ ] Boxes extend to current bar
- [ ] Broken zones are retired (grayed)
- [ ] Max active zones respected

## Signals
- [ ] Buy/Sell signals only on bar close (no repaint)
- [ ] Strong signals require location + RSI context
- [ ] Signals reduce in chop/low vol as expected

## Risk & Sizing
- [ ] SL/TP based on ATR distances
- [ ] Trailing stop lifts (long) / drops (short) as price moves
- [ ] R:R (TP1) matches manual calc
- [ ] Position size suggestion = riskCash / perUnitRisk

## Alerts (13 types)
- [ ] Buy
- [ ] Strong Buy
- [ ] Sell
- [ ] Strong Sell
- [ ] Price at Demand
- [ ] Price at Supply
- [ ] Momentum Bullish (optional)
- [ ] Momentum Bearish (optional)
- [ ] Trend changed (optional)
- [ ] Long SL Hit
- [ ] Short SL Hit
- [ ] Long TP1
- [ ] Short TP1

## Dashboard
- [ ] Trend, Momentum, RSI correct
- [ ] ADX >= threshold highlights strength
- [ ] Nearest Supply/Demand show correct prices
- [ ] R:R and suggested size update when trade active

## Performance
- [ ] No lag on 1m charts
- [ ] No excessive CPU usage

## Platform
- [ ] TradingView Web (Chrome/Firefox/Safari)
- [ ] TradingView Desktop App
- [ ] TradingView Mobile (iOS/Android) readable

## Publishing
- [ ] Description updated (marketing/PUBLISH_DESCRIPTION.md)
- [ ] Version bumped (indicator/version_history.md)
- [ ] Docs updated (README, USER_GUIDE, TR docs)
