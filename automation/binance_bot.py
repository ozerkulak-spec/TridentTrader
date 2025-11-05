"""
Trident Trader - Binance Auto Trading Bot
FastAPI webhook listener with Binance API integration
"""

from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import JSONResponse
from binance.client import Client
from binance.exceptions import BinanceAPIException
import uvicorn
import os
import hmac
import hashlib
import json
from datetime import datetime
from typing import Optional
import sqlite3
from contextlib import closing

# ============================================================================
# CONFIGURATION
# ============================================================================

API_KEY = os.getenv("BINANCE_API_KEY", "")
API_SECRET = os.getenv("BINANCE_API_SECRET", "")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "your_secret_key_here")  # TradingView alarmında gönderilecek
TESTNET = os.getenv("TESTNET", "false").lower() == "true"
DEFAULT_RISK_PERCENT = float(os.getenv("DEFAULT_RISK_PERCENT", "1.0"))  # Hesabın %1'i risk
MIN_USDT_ORDER = float(os.getenv("MIN_USDT_ORDER", "10.0"))  # Minimum emir büyüklüğü

# Binance Client
if TESTNET:
    client = Client(API_KEY, API_SECRET, testnet=True)
else:
    client = Client(API_KEY, API_SECRET)

# FastAPI App
app = FastAPI(title="Trident Trader Bot", version="1.0")

# ============================================================================
# DATABASE (Position Tracking)
# ============================================================================

DB_FILE = "positions.db"

def init_db():
    """Initialize SQLite database for position tracking"""
    with closing(sqlite3.connect(DB_FILE)) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS positions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    entry_price REAL NOT NULL,
                    quantity REAL NOT NULL,
                    stop_loss REAL,
                    take_profit_1 REAL,
                    take_profit_2 REAL,
                    status TEXT DEFAULT 'open',
                    opened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    closed_at TIMESTAMP
                )
            """)
            conn.commit()

init_db()

# ============================================================================
# SECURITY
# ============================================================================

def verify_webhook_signature(payload: str, signature: str) -> bool:
    """Verify webhook signature using HMAC-SHA256"""
    expected_sig = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected_sig, signature)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_account_balance() -> float:
    """Get USDT balance from Binance account"""
    try:
        balance = client.get_asset_balance(asset="USDT")
        return float(balance["free"])
    except Exception as e:
        print(f"Error getting balance: {e}")
        return 0.0

def calculate_position_size(symbol: str, risk_percent: float, stop_loss_price: float, entry_price: float) -> float:
    """Calculate position size based on account balance and risk %"""
    balance = get_account_balance()
    risk_amount = balance * (risk_percent / 100.0)
    
    # Price difference (risk per unit)
    price_diff = abs(entry_price - stop_loss_price)
    if price_diff == 0:
        return MIN_USDT_ORDER / entry_price
    
    # Calculate quantity
    quantity = risk_amount / price_diff
    
    # Ensure minimum order size
    min_quantity = MIN_USDT_ORDER / entry_price
    return max(quantity, min_quantity)

def format_quantity(symbol: str, quantity: float) -> float:
    """Format quantity according to Binance symbol filters"""
    try:
        info = client.get_symbol_info(symbol)
        for filter in info['filters']:
            if filter['filterType'] == 'LOT_SIZE':
                step_size = float(filter['stepSize'])
                precision = len(str(step_size).split('.')[-1].rstrip('0'))
                return round(quantity - (quantity % step_size), precision)
    except Exception as e:
        print(f"Error formatting quantity: {e}")
    return round(quantity, 6)

def save_position(symbol: str, side: str, entry_price: float, quantity: float, 
                  stop_loss: Optional[float] = None, tp1: Optional[float] = None, 
                  tp2: Optional[float] = None):
    """Save position to database"""
    with closing(sqlite3.connect(DB_FILE)) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute("""
                INSERT INTO positions (symbol, side, entry_price, quantity, stop_loss, take_profit_1, take_profit_2)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (symbol, side, entry_price, quantity, stop_loss, tp1, tp2))
            conn.commit()
            return cursor.lastrowid

def close_position(position_id: int):
    """Mark position as closed"""
    with closing(sqlite3.connect(DB_FILE)) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute("""
                UPDATE positions SET status = 'closed', closed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (position_id,))
            conn.commit()

def get_open_position(symbol: str) -> Optional[dict]:
    """Get open position for symbol"""
    with closing(sqlite3.connect(DB_FILE)) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute("""
                SELECT id, symbol, side, entry_price, quantity, stop_loss, take_profit_1, take_profit_2
                FROM positions WHERE symbol = ? AND status = 'open'
                ORDER BY opened_at DESC LIMIT 1
            """, (symbol,))
            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "symbol": row[1],
                    "side": row[2],
                    "entry_price": row[3],
                    "quantity": row[4],
                    "stop_loss": row[5],
                    "take_profit_1": row[6],
                    "take_profit_2": row[7]
                }
    return None

# ============================================================================
# TRADING FUNCTIONS
# ============================================================================

def execute_buy_order(symbol: str, quantity: float, entry_price: float, 
                      stop_loss: Optional[float] = None, 
                      tp1: Optional[float] = None, 
                      tp2: Optional[float] = None) -> dict:
    """Execute BUY market order on Binance"""
    try:
        # Main order
        order = client.order_market_buy(symbol=symbol, quantity=quantity)
        
        position_id = save_position(symbol, "long", entry_price, quantity, stop_loss, tp1, tp2)
        
        # Set stop-loss (if provided)
        if stop_loss:
            try:
                sl_order = client.create_order(
                    symbol=symbol,
                    side="SELL",
                    type="STOP_LOSS_LIMIT",
                    timeInForce="GTC",
                    quantity=quantity,
                    stopPrice=stop_loss,
                    price=stop_loss * 0.99  # Slightly below stop to ensure fill
                )
            except Exception as e:
                print(f"Error setting stop-loss: {e}")
        
        return {
            "success": True,
            "order": order,
            "position_id": position_id,
            "message": f"BUY {quantity} {symbol} at ~{entry_price}"
        }
    except BinanceAPIException as e:
        return {"success": False, "error": str(e)}

def execute_sell_order(symbol: str, quantity: float, entry_price: float, 
                       stop_loss: Optional[float] = None, 
                       tp1: Optional[float] = None, 
                       tp2: Optional[float] = None) -> dict:
    """Execute SELL market order on Binance"""
    try:
        # Main order
        order = client.order_market_sell(symbol=symbol, quantity=quantity)
        
        position_id = save_position(symbol, "short", entry_price, quantity, stop_loss, tp1, tp2)
        
        # Set stop-loss (if provided)
        if stop_loss:
            try:
                sl_order = client.create_order(
                    symbol=symbol,
                    side="BUY",
                    type="STOP_LOSS_LIMIT",
                    timeInForce="GTC",
                    quantity=quantity,
                    stopPrice=stop_loss,
                    price=stop_loss * 1.01  # Slightly above stop
                )
            except Exception as e:
                print(f"Error setting stop-loss: {e}")
        
        return {
            "success": True,
            "order": order,
            "position_id": position_id,
            "message": f"SELL {quantity} {symbol} at ~{entry_price}"
        }
    except BinanceAPIException as e:
        return {"success": False, "error": str(e)}

def close_open_position(symbol: str, reason: str = "exit signal") -> dict:
    """Close any open position for the symbol"""
    position = get_open_position(symbol)
    if not position:
        return {"success": False, "message": "No open position"}
    
    try:
        # Reverse the position
        if position["side"] == "long":
            order = client.order_market_sell(symbol=symbol, quantity=position["quantity"])
        else:
            order = client.order_market_buy(symbol=symbol, quantity=position["quantity"])
        
        close_position(position["id"])
        
        return {
            "success": True,
            "order": order,
            "message": f"Closed {position['side']} position: {reason}"
        }
    except BinanceAPIException as e:
        return {"success": False, "error": str(e)}

# ============================================================================
# WEBHOOK ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "running",
        "service": "Trident Trader Bot",
        "time": datetime.utcnow().isoformat(),
        "testnet": TESTNET
    }

@app.post("/webhook")
async def webhook(request: Request, x_signature: Optional[str] = Header(None)):
    """Main webhook endpoint for TradingView alerts"""
    
    # Get raw body
    body_bytes = await request.body()
    body_str = body_bytes.decode()
    
    # Verify signature (if provided)
    if x_signature:
        if not verify_webhook_signature(body_str, x_signature):
            raise HTTPException(status_code=401, detail="Invalid signature")
    elif WEBHOOK_SECRET != "your_secret_key_here":
        # If secret is set but no signature provided, require it
        raise HTTPException(status_code=401, detail="Signature required")
    
    try:
        data = json.loads(body_str)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    # Extract data
    action = data.get("action", "").lower()
    symbol_raw = data.get("symbol", "")
    price = float(data.get("price", 0))
    stop_loss = data.get("stop_loss")
    take_profit_1 = data.get("take_profit_1")
    take_profit_2 = data.get("take_profit_2")
    risk_percent = data.get("risk_percent", DEFAULT_RISK_PERCENT)
    
    # Format symbol (remove exchange prefix if present)
    symbol = symbol_raw.replace("BINANCE:", "").replace("USDT", "") + "USDT"
    
    # Validate
    if action not in ["buy", "sell", "close", "tp1", "tp2", "sl"]:
        raise HTTPException(status_code=400, detail=f"Invalid action: {action}")
    
    # Execute action
    result = {}
    
    if action == "buy":
        # Calculate position size
        sl_price = float(stop_loss) if stop_loss else price * 0.98  # Default 2% SL
        quantity = calculate_position_size(symbol, risk_percent, sl_price, price)
        quantity = format_quantity(symbol, quantity)
        
        tp1_price = float(take_profit_1) if take_profit_1 else None
        tp2_price = float(take_profit_2) if take_profit_2 else None
        
        result = execute_buy_order(symbol, quantity, price, sl_price, tp1_price, tp2_price)
    
    elif action == "sell":
        sl_price = float(stop_loss) if stop_loss else price * 1.02  # Default 2% SL
        quantity = calculate_position_size(symbol, risk_percent, sl_price, price)
        quantity = format_quantity(symbol, quantity)
        
        tp1_price = float(take_profit_1) if take_profit_1 else None
        tp2_price = float(take_profit_2) if take_profit_2 else None
        
        result = execute_sell_order(symbol, quantity, price, sl_price, tp1_price, tp2_price)
    
    elif action in ["close", "tp1", "tp2", "sl"]:
        result = close_open_position(symbol, reason=action.upper())
    
    return JSONResponse(content=result)

@app.get("/positions")
async def get_positions():
    """Get all open positions"""
    with closing(sqlite3.connect(DB_FILE)) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute("""
                SELECT id, symbol, side, entry_price, quantity, stop_loss, take_profit_1, take_profit_2, opened_at
                FROM positions WHERE status = 'open'
                ORDER BY opened_at DESC
            """)
            rows = cursor.fetchall()
            positions = []
            for row in rows:
                positions.append({
                    "id": row[0],
                    "symbol": row[1],
                    "side": row[2],
                    "entry_price": row[3],
                    "quantity": row[4],
                    "stop_loss": row[5],
                    "take_profit_1": row[6],
                    "take_profit_2": row[7],
                    "opened_at": row[8]
                })
            return {"positions": positions}

@app.get("/balance")
async def get_balance():
    """Get USDT balance"""
    balance = get_account_balance()
    return {"USDT": balance}

# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
