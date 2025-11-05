# Trident Trader - Version History

## v1.0 (Indicator)
- Initial release (EN)
- Core triple confluence: Trend + Momentum + Liquidity
- Risk management (ATR SL/TP), dashboard, alerts

## v1.0 PRO (Indicator)
- Non-repaint discipline (signals on bar close)
- MTF confirmation with lookahead_off
- ADX chop filter and volatility gate
- Box-based Supply/Demand with lifecycle
- Position sizing suggestion (account size + risk %)

Files:
- `indicator/trident_trader_v1_pro.pine`

## v1.0 (Strategy)
- Backtest version using the same gates in `strategy()`
- SL/TP and optional trailing exits

Files:
- `indicator/trident_trader_strategy_v1.pine`

## Roadmap
- v1.1: Session markers, divergence detection, enhanced volume
- v1.2: AI/ML signal classification, mobile-optimized dashboard
- v2.0: Screener, broker API automation, social trading
