"""
Trident Trader PRO - Advanced Auto Trading Bot v2.0
Professional-grade bot with web dashboard, analytics, and advanced features
"""

from fastapi import FastAPI, Request, HTTPException, WebSocket, WebSocketDisconnect, Depends, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from binance.client import Client
from binance.exceptions import BinanceAPIException
import uvicorn
import os
import hmac
import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import sqlite3
from contextlib import closing
import asyncio
import logging
from dataclasses import dataclass, asdict
from decimal import Decimal
import aiofiles
import httpx
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class BotConfig:
    """Bot configuration"""
    api_key: str = os.getenv("BINANCE_API_KEY", "")
    api_secret: str = os.getenv("BINANCE_API_SECRET", "")
    webhook_secret: str = os.getenv("WEBHOOK_SECRET", "")
    testnet: bool = os.getenv("USE_TESTNET", "false").lower() == "true"
    default_risk_percent: float = float(os.getenv("DEFAULT_RISK_PERCENT", "1.0"))
    max_open_positions: int = int(os.getenv("MAX_OPEN_POSITIONS", "5"))
    min_usdt_order: float = float(os.getenv("MIN_USDT_ORDER", "10.0"))
    trading_mode: str = os.getenv("TRADING_MODE", "spot")  # spot or futures
    leverage: int = int(os.getenv("LEVERAGE", "3"))
    enable_trailing_stop: bool = os.getenv("ENABLE_TRAILING_STOP", "false").lower() == "true"
    trailing_stop_percent: float = float(os.getenv("TRAILING_STOP_PERCENT", "1.5"))
    enable_partial_close: bool = os.getenv("ENABLE_PARTIAL_CLOSE", "true").lower() == "true"
    partial_close_percent: float = float(os.getenv("PARTIAL_CLOSE_PERCENT", "50"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    dashboard_auth_token: str = os.getenv("DASHBOARD_AUTH_TOKEN", "")
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_chat_id: str = os.getenv("TELEGRAM_CHAT_ID", "")
    
config = BotConfig()

# Binance Client - with error handling
try:
    if config.testnet:
        client = Client(config.api_key, config.api_secret, testnet=True)
        logger.info("[TESTNET] Running in TESTNET mode")
    else:
        client = Client(config.api_key, config.api_secret)
        logger.info("[PRODUCTION] Running in PRODUCTION mode")
except Exception as e:
    logger.error(f"[ERROR] Failed to initialize Binance client: {e}")
    logger.error("Please check BINANCE_API_KEY and BINANCE_API_SECRET")
    client = None

# FastAPI App
app = FastAPI(
    title="Trident Trader PRO Bot",
    version="2.0",
    description="Professional Auto Trading Bot with Web Dashboard"
)

# Templates and static files
templates = Jinja2Templates(directory="templates")
os.makedirs("static", exist_ok=True)
os.makedirs("logs", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# WebSocket connections for real-time updates
active_connections: List[WebSocket] = []

# ============================================================================
# AUTH HELPERS
# ============================================================================

def require_auth(request: Request):
    """Optional bearer token auth for dashboard and APIs.
    If DASHBOARD_AUTH_TOKEN is set, require 'Authorization: Bearer <token>' header
    or 'token' query parameter to match. Health/Webhook remain public.
    """
    if not config.dashboard_auth_token:
        return True

    # Header takes precedence
    auth_header = request.headers.get("Authorization", "")
    token = None
    if auth_header.lower().startswith("bearer "):
        token = auth_header.split(" ", 1)[1].strip()
    else:
        # Fallback to query param
        token = request.query_params.get("token")

    if token != config.dashboard_auth_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return True

# ============================================================================
# VALIDATION HELPERS
# ============================================================================

def validate_symbol(symbol: str) -> bool:
    """Basic symbol validation (uppercase, ends with USDT/BTC/etc)"""
    if not symbol or len(symbol) < 5:
        return False
    # Basic check: alphanumeric and common quote currencies
    return symbol.isupper() and any(symbol.endswith(q) for q in ["USDT", "BUSD", "BTC", "ETH"])

def validate_risk_percent(risk: float) -> bool:
    """Validate risk percentage is within safe range"""
    return 0.1 <= risk <= 10.0

def validate_price(price: float) -> bool:
    """Validate price is positive and reasonable"""
    return price > 0 and price < 1_000_000_000

# ============================================================================
# DATABASE MODELS
# ============================================================================

DB_FILE = os.getenv("DB_PATH", "data/positions.db")
os.makedirs("data", exist_ok=True)

def init_db():
    """Initialize enhanced database with analytics tables"""
    with closing(sqlite3.connect(DB_FILE)) as conn:
        with closing(conn.cursor()) as cursor:
            # Positions table
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
                    trailing_stop REAL,
                    status TEXT DEFAULT 'open',
                    pnl REAL DEFAULT 0,
                    pnl_percent REAL DEFAULT 0,
                    opened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    closed_at TIMESTAMP,
                    close_reason TEXT,
                    strategy_signal TEXT,
                    notes TEXT
                )
            """)
            
            # Trades table (for analytics)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    position_id INTEGER,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    order_type TEXT,
                    price REAL NOT NULL,
                    quantity REAL NOT NULL,
                    commission REAL DEFAULT 0,
                    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    binance_order_id TEXT,
                    FOREIGN KEY (position_id) REFERENCES positions(id)
                )
            """)
            
            # Performance metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL UNIQUE,
                    total_trades INTEGER DEFAULT 0,
                    winning_trades INTEGER DEFAULT 0,
                    losing_trades INTEGER DEFAULT 0,
                    total_pnl REAL DEFAULT 0,
                    win_rate REAL DEFAULT 0,
                    avg_win REAL DEFAULT 0,
                    avg_loss REAL DEFAULT 0,
                    largest_win REAL DEFAULT 0,
                    largest_loss REAL DEFAULT 0,
                    drawdown REAL DEFAULT 0
                )
            """)
            
            # Bot events log
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bot_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT,
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    logger.info("[OK] Database initialized")

init_db()

# ============================================================================
# SECURITY & VALIDATION
# ============================================================================

def verify_webhook_signature(payload: str, signature: str) -> bool:
    """Verify webhook signature using HMAC-SHA256"""
    if not config.webhook_secret:
        logger.warning("[WARNING] No webhook secret configured!")
        return True  # Allow if not configured (dev mode)
    
    expected_sig = hmac.new(
        config.webhook_secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected_sig, signature)

def log_event(event_type: str, severity: str, message: str, details: Dict = None):
    """Log bot event to database"""
    with closing(sqlite3.connect(DB_FILE)) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute("""
                INSERT INTO bot_events (event_type, severity, message, details)
                VALUES (?, ?, ?, ?)
            """, (event_type, severity, message, json.dumps(details) if details else None))
            conn.commit()

# ============================================================================
# NOTIFICATIONS
# ============================================================================

async def send_telegram_message(text: str):
    """Send a Telegram message if credentials are provided."""
    if not (config.telegram_bot_token and config.telegram_chat_id):
        return
    url = f"https://api.telegram.org/bot{config.telegram_bot_token}/sendMessage"
    payload = {"chat_id": config.telegram_chat_id, "text": text, "parse_mode": "Markdown"}
    try:
        async with httpx.AsyncClient(timeout=10) as client_http:
            await client_http.post(url, json=payload)
    except Exception as e:
        logger.warning(f"Telegram notify failed: {e}")

# ============================================================================
# BINANCE API HELPERS
# ============================================================================

def get_account_balance() -> Dict[str, float]:
    """Get account balances"""
    try:
        account = client.get_account()
        balances = {}
        for asset in account['balances']:
            free = float(asset['free'])
            locked = float(asset['locked'])
            if free > 0 or locked > 0:
                balances[asset['asset']] = {
                    'free': free,
                    'locked': locked,
                    'total': free + locked
                }
        return balances
    except Exception as e:
        logger.error(f"Error getting balance: {e}")
        return {}

def get_usdt_balance() -> float:
    """Get available USDT balance"""
    balances = get_account_balance()
    return balances.get('USDT', {}).get('free', 0.0)

def get_symbol_info(symbol: str) -> Dict:
    """Get symbol trading info"""
    try:
        info = client.get_symbol_info(symbol)
        return info
    except Exception as e:
        logger.error(f"Error getting symbol info for {symbol}: {e}")
        return {}

def format_quantity(symbol: str, quantity: float) -> float:
    """Format quantity according to Binance filters"""
    try:
        info = get_symbol_info(symbol)
        for filter in info.get('filters', []):
            if filter['filterType'] == 'LOT_SIZE':
                step_size = float(filter['stepSize'])
                precision = len(str(step_size).rstrip('0').split('.')[-1])
                formatted = round(quantity - (quantity % step_size), precision)
                return formatted
    except Exception as e:
        logger.error(f"Error formatting quantity: {e}")
    return round(quantity, 6)

def format_price(symbol: str, price: float) -> float:
    """Format price according to Binance filters"""
    try:
        info = get_symbol_info(symbol)
        for filter in info.get('filters', []):
            if filter['filterType'] == 'PRICE_FILTER':
                tick_size = float(filter['tickSize'])
                precision = len(str(tick_size).rstrip('0').split('.')[-1])
                return round(price - (price % tick_size), precision)
    except Exception as e:
        logger.error(f"Error formatting price: {e}")
    return round(price, 2)

def calculate_position_size(symbol: str, risk_percent: float, entry_price: float, stop_loss: float) -> float:
    """Calculate position size based on risk %"""
    balance = get_usdt_balance()
    risk_amount = balance * (risk_percent / 100.0)
    
    price_diff = abs(entry_price - stop_loss)
    if price_diff == 0:
        quantity = config.min_usdt_order / entry_price
    else:
        quantity = risk_amount / price_diff
    
    # Ensure minimum order size
    min_quantity = config.min_usdt_order / entry_price
    quantity = max(quantity, min_quantity)
    
    return format_quantity(symbol, quantity)

# ============================================================================
# POSITION MANAGEMENT
# ============================================================================

def save_position(symbol: str, side: str, entry_price: float, quantity: float,
                  stop_loss: Optional[float] = None, tp1: Optional[float] = None,
                  tp2: Optional[float] = None, signal: str = "") -> int:
    """Save position to database"""
    with closing(sqlite3.connect(DB_FILE)) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute("""
                INSERT INTO positions (symbol, side, entry_price, quantity, stop_loss, 
                                       take_profit_1, take_profit_2, strategy_signal)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (symbol, side, entry_price, quantity, stop_loss, tp1, tp2, signal))
            conn.commit()
            position_id = cursor.lastrowid
            
    logger.info(f"💾 Position saved: {side.upper()} {quantity} {symbol} @ {entry_price}")
    log_event("position_open", "INFO", f"Opened {side} position", {
        "symbol": symbol, "quantity": quantity, "entry": entry_price
    })
    return position_id

def save_trade(position_id: int, symbol: str, side: str, order_type: str,
               price: float, quantity: float, binance_order_id: str = "") -> int:
    """Save trade execution to database"""
    with closing(sqlite3.connect(DB_FILE)) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute("""
                INSERT INTO trades (position_id, symbol, side, order_type, price, quantity, binance_order_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (position_id, symbol, side, order_type, price, quantity, binance_order_id))
            conn.commit()
            return cursor.lastrowid

def get_open_positions() -> List[Dict]:
    """Get all open positions"""
    with closing(sqlite3.connect(DB_FILE)) as conn:
        conn.row_factory = sqlite3.Row
        with closing(conn.cursor()) as cursor:
            cursor.execute("""
                SELECT * FROM positions WHERE status = 'open' ORDER BY opened_at DESC
            """)
            return [dict(row) for row in cursor.fetchall()]

def get_position_by_id(position_id: int) -> Optional[Dict]:
    """Get position by ID"""
    with closing(sqlite3.connect(DB_FILE)) as conn:
        conn.row_factory = sqlite3.Row
        with closing(conn.cursor()) as cursor:
            cursor.execute("SELECT * FROM positions WHERE id = ?", (position_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

def close_position(position_id: int, close_price: float, reason: str = "manual"):
    """Close position and calculate P&L"""
    position = get_position_by_id(position_id)
    if not position:
        return
    
    entry = position['entry_price']
    quantity = position['quantity']
    side = position['side']
    
    # Calculate P&L
    if side == 'long':
        pnl = (close_price - entry) * quantity
    else:  # short
        pnl = (entry - close_price) * quantity
    
    pnl_percent = (pnl / (entry * quantity)) * 100
    
    with closing(sqlite3.connect(DB_FILE)) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute("""
                UPDATE positions 
                SET status = 'closed', closed_at = CURRENT_TIMESTAMP, 
                    pnl = ?, pnl_percent = ?, close_reason = ?
                WHERE id = ?
            """, (pnl, pnl_percent, reason, position_id))
            conn.commit()
    
    logger.info(f"[CLOSE] Position closed: {position['symbol']} P&L: ${pnl:.2f} ({pnl_percent:.2f}%)")
    log_event("position_close", "INFO", f"Closed position with {reason}", {
        "symbol": position['symbol'], "pnl": pnl, "pnl_percent": pnl_percent
    })
    
    # Update daily stats
    update_daily_stats(pnl)

def update_daily_stats(pnl: float):
    """Update daily statistics"""
    today = datetime.now().date().isoformat()
    
    with closing(sqlite3.connect(DB_FILE)) as conn:
        with closing(conn.cursor()) as cursor:
            # Check if today's record exists
            cursor.execute("SELECT * FROM daily_stats WHERE date = ?", (today,))
            row = cursor.fetchone()
            
            if row:
                cursor.execute("""
                    UPDATE daily_stats SET
                        total_trades = total_trades + 1,
                        winning_trades = winning_trades + ?,
                        losing_trades = losing_trades + ?,
                        total_pnl = total_pnl + ?,
                        win_rate = (winning_trades * 100.0) / total_trades
                    WHERE date = ?
                """, (1 if pnl > 0 else 0, 1 if pnl < 0 else 0, pnl, today))
            else:
                cursor.execute("""
                    INSERT INTO daily_stats (date, total_trades, winning_trades, losing_trades, total_pnl)
                    VALUES (?, 1, ?, ?, ?)
                """, (today, 1 if pnl > 0 else 0, 1 if pnl < 0 else 0, pnl))
            
            conn.commit()

# ============================================================================
# TRADING EXECUTION
# ============================================================================

async def execute_trade(action: str, symbol: str, price: float, 
                       stop_loss: Optional[float] = None,
                       take_profit: Optional[float] = None,
                       signal_strength: str = "normal") -> Dict:
    """Execute trade on Binance"""
    try:
        # Validate client initialized
        if client is None:
            return {"success": False, "error": "Binance client not initialized"}
        
        # Validate inputs
        if not validate_symbol(symbol):
            return {"success": False, "error": f"Invalid symbol format: {symbol}"}
        if not validate_price(price):
            return {"success": False, "error": f"Invalid price: {price}"}
        if not validate_risk_percent(config.default_risk_percent):
            return {"success": False, "error": f"Risk percent out of range: {config.default_risk_percent}"}
        
        # Check max positions
        open_positions = get_open_positions()
        if len(open_positions) >= config.max_open_positions:
            return {"success": False, "error": f"Max positions ({config.max_open_positions}) reached"}
        
        # Calculate position size
        if not stop_loss:
            # Default SL: 2% from entry
            stop_loss = price * 0.98 if action == "buy" else price * 1.02
        
        quantity = calculate_position_size(symbol, config.default_risk_percent, price, stop_loss)
        
        # Execute order
        if action == "buy":
            order = client.order_market_buy(symbol=symbol, quantity=quantity)
            side = "long"
        else:
            order = client.order_market_sell(symbol=symbol, quantity=quantity)
            side = "short"
        
        # Get actual fill price
        fill_price = float(order.get('fills', [{}])[0].get('price', price))
        
        # Save position
        position_id = save_position(
            symbol, side, fill_price, quantity,
            stop_loss, take_profit, None, signal_strength
        )
        
        # Save trade
        save_trade(position_id, symbol, action.upper(), "MARKET", 
                  fill_price, quantity, order.get('orderId', ''))
        
        # Set stop-loss order
        if stop_loss:
            await set_stop_loss(symbol, side, quantity, stop_loss)
        
        # Broadcast to WebSocket clients
        await broadcast_update({
            "type": "new_position",
            "data": {"id": position_id, "symbol": symbol, "side": side, "price": fill_price}
        })
        
        # Notify via Telegram (optional)
        try:
            await send_telegram_message(
                f"[NEW] New {side.upper()} position opened\n{symbol} @ {fill_price}\nQty: {quantity}"
            )
        except Exception:
            pass

        return {
            "success": True,
            "position_id": position_id,
            "order": order,
            "message": f"{action.upper()} {quantity} {symbol} @ {fill_price}"
        }
        
    except BinanceAPIException as e:
        logger.error(f"Binance API error: {e}")
        log_event("trade_error", "ERROR", str(e), {"symbol": symbol, "action": action})
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error(f"Trade execution error: {e}")
        return {"success": False, "error": str(e)}

async def set_stop_loss(symbol: str, side: str, quantity: float, stop_price: float):
    """Set stop-loss order"""
    try:
        stop_price = format_price(symbol, stop_price)
        limit_price = format_price(symbol, stop_price * 0.99 if side == "long" else stop_price * 1.01)
        
        order_side = "SELL" if side == "long" else "BUY"
        
        sl_order = client.create_order(
            symbol=symbol,
            side=order_side,
            type="STOP_LOSS_LIMIT",
            timeInForce="GTC",
            quantity=quantity,
            stopPrice=stop_price,
            price=limit_price
        )
        logger.info(f"🛡️ Stop-loss set: {symbol} @ {stop_price}")
        return sl_order
    except Exception as e:
        logger.error(f"Error setting stop-loss: {e}")
        return None

# ============================================================================
# WEBSOCKET FOR REAL-TIME UPDATES
# ============================================================================

async def broadcast_update(message: Dict):
    """Broadcast update to all connected WebSocket clients"""
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except:
            active_connections.remove(connection)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    # Optional token validation via query param when auth token is set
    if config.dashboard_auth_token:
        token = websocket.query_params.get("token")
        if token != config.dashboard_auth_token:
            await websocket.close(code=1008)
            return
    await websocket.accept()
    active_connections.append(websocket)
    logger.info(f"📡 WebSocket client connected (total: {len(active_connections)})")
    
    try:
        while True:
            # Send periodic updates
            await asyncio.sleep(5)
            positions = get_open_positions()
            balance = get_usdt_balance()
            await websocket.send_json({
                "type": "update",
                "positions": positions,
                "balance": balance,
                "timestamp": datetime.now().isoformat()
            })
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logger.info(f"📡 WebSocket client disconnected (remaining: {len(active_connections)})")

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, auth: bool = Depends(require_auth)):
    """Main dashboard page"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    client_ok = client is not None
    return {
        "status": "healthy" if client_ok else "degraded",
        "version": "2.0",
        "mode": "testnet" if config.testnet else "production",
        "timestamp": datetime.now().isoformat(),
        "open_positions": len(get_open_positions()),
        "balance": get_usdt_balance() if client_ok else 0,
        "binance_connected": client_ok
    }

@app.post("/webhook")
async def webhook_handler(request: Request):
    """Handle TradingView webhook"""
    try:
        body = await request.body()
        payload = body.decode('utf-8')
        
        # Verify signature (if header provided)
        signature = request.headers.get("X-Webhook-Signature", "")
        if signature and not verify_webhook_signature(payload, signature):
            log_event("webhook_error", "WARNING", "Invalid webhook signature", {"ip": request.client.host})
            raise HTTPException(status_code=403, detail="Invalid signature")
        
        data = json.loads(payload)
        logger.info(f"📥 Webhook received: {data}")
        
        # Validate required fields
        required = ["action", "symbol", "price", "secret"]
        if not all(k in data for k in required):
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        # Verify secret
        if data.get("secret") != config.webhook_secret:
            log_event("webhook_error", "WARNING", "Invalid secret", {"ip": request.client.host})
            raise HTTPException(status_code=403, detail="Invalid secret")
        
        # Execute trade
        result = await execute_trade(
            action=data["action"],
            symbol=data["symbol"],
            price=float(data["price"]),
            stop_loss=float(data.get("sl", 0)) or None,
            take_profit=float(data.get("tp", 0)) or None,
            signal_strength=data.get("strength", "normal")
        )
        
        return JSONResponse(content=result)
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/positions")
async def get_positions_api(auth: bool = Depends(require_auth)):
    """Get all positions"""
    positions = get_open_positions()
    return {"positions": positions, "count": len(positions)}

@app.get("/api/performance")
async def get_performance(auth: bool = Depends(require_auth)):
    """Get performance metrics"""
    with closing(sqlite3.connect(DB_FILE)) as conn:
        conn.row_factory = sqlite3.Row
        with closing(conn.cursor()) as cursor:
            # Overall stats
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_trades,
                    SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
                    SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) as losses,
                    SUM(pnl) as total_pnl,
                    AVG(CASE WHEN pnl > 0 THEN pnl END) as avg_win,
                    AVG(CASE WHEN pnl < 0 THEN pnl END) as avg_loss,
                    MAX(pnl) as best_trade,
                    MIN(pnl) as worst_trade
                FROM positions WHERE status = 'closed'
            """)
            overall = dict(cursor.fetchone())
            
            # Calculate win rate
            if overall['total_trades'] > 0:
                overall['win_rate'] = (overall['wins'] / overall['total_trades']) * 100
            else:
                overall['win_rate'] = 0
            
            # Last 30 days
            cursor.execute("""
                SELECT date, total_pnl, win_rate 
                FROM daily_stats 
                ORDER BY date DESC 
                LIMIT 30
            """)
            daily = [dict(row) for row in cursor.fetchall()]
            
    return {"overall": overall, "daily": daily}

@app.get("/api/logs")
async def get_logs(limit: int = 100, auth: bool = Depends(require_auth)):
    """Get recent bot events"""
    with closing(sqlite3.connect(DB_FILE)) as conn:
        conn.row_factory = sqlite3.Row
        with closing(conn.cursor()) as cursor:
            cursor.execute("""
                SELECT * FROM bot_events 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]

@app.post("/api/emergency-stop")
async def emergency_stop(auth: bool = Depends(require_auth)):
    """Emergency stop - close all positions"""
    logger.warning("🚨 EMERGENCY STOP TRIGGERED")
    log_event("emergency_stop", "CRITICAL", "Emergency stop activated", {})
    
    positions = get_open_positions()
    closed_count = 0
    
    for pos in positions:
        try:
            symbol = pos['symbol']
            quantity = pos['quantity']
            side = pos['side']
            
            # Close position on Binance
            if side == 'long':
                order = client.order_market_sell(symbol=symbol, quantity=quantity)
            else:
                order = client.order_market_buy(symbol=symbol, quantity=quantity)
            
            # Get close price
            close_price = float(order.get('fills', [{}])[0].get('price', 0))
            
            # Close in database
            close_position(pos['id'], close_price, "emergency_stop")
            closed_count += 1
            
        except Exception as e:
            logger.error(f"Error closing position {pos['id']}: {e}")
    
    await broadcast_update({"type": "emergency_stop", "closed": closed_count})
    try:
        await send_telegram_message(f"🚨 Emergency Stop executed. Closed positions: {closed_count}")
    except Exception:
        pass
    
    return {"success": True, "closed_positions": closed_count}

@app.get("/api/balance")
async def get_balance_api(auth: bool = Depends(require_auth)):
    """Get account balance"""
    if client is None:
        return {"error": "Binance client not initialized", "balances": {}, "usdt": 0}
    try:
        balance = get_account_balance()
        return {"balances": balance, "usdt": balance.get('USDT', {}).get('total', 0)}
    except Exception as e:
        logger.error(f"Error fetching balance: {e}")
        return {"error": str(e), "balances": {}, "usdt": 0}

@app.get("/api/config")
async def get_config(auth: bool = Depends(require_auth)):
    """Get bot configuration"""
    return {
        "testnet": config.testnet,
        "risk_percent": config.default_risk_percent,
        "max_positions": config.max_open_positions,
        "trading_mode": config.trading_mode,
        "trailing_stop": config.enable_trailing_stop,
        "trailing_stop_percent": config.trailing_stop_percent,
        "partial_close": config.enable_partial_close,
        "partial_close_percent": config.partial_close_percent
    }

@app.post("/api/config")
async def update_config(request: Request, auth: bool = Depends(require_auth)):
    """Update bot configuration at runtime (non-persistent)."""
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # Update safe subset of config
    if "risk_percent" in data:
        config.default_risk_percent = float(data["risk_percent"])
    if "max_positions" in data:
        config.max_open_positions = int(data["max_positions"])
    if "trailing_stop" in data:
        config.enable_trailing_stop = bool(data["trailing_stop"])
    if "trailing_stop_percent" in data:
        config.trailing_stop_percent = float(data["trailing_stop_percent"])
    if "partial_close" in data:
        config.enable_partial_close = bool(data["partial_close"])
    if "partial_close_percent" in data:
        config.partial_close_percent = float(data["partial_close_percent"])

    log_event("config_update", "INFO", "Config updated", data)
    return {"success": True, "config": {
        "risk_percent": config.default_risk_percent,
        "max_positions": config.max_open_positions,
        "trailing_stop": config.enable_trailing_stop,
        "trailing_stop_percent": config.trailing_stop_percent,
        "partial_close": config.enable_partial_close,
        "partial_close_percent": config.partial_close_percent
    }}

@app.get("/api/readiness")
async def readiness(auth: bool = Depends(require_auth)):
    """Readiness checklist for safe Testnet/Live operations."""
    checks = []
    def add_check(name, ok, hint=""):
        checks.append({"name": name, "ok": bool(ok), "hint": hint})

    add_check("API key configured", bool(config.api_key), "Set BINANCE_API_KEY")
    add_check("API secret configured", bool(config.api_secret), "Set BINANCE_API_SECRET")
    add_check("Webhook secret set", bool(config.webhook_secret), "Set WEBHOOK_SECRET")
    add_check("Database path accessible", os.path.isdir(os.path.dirname(DB_FILE)) or DB_FILE != "", f"DB_PATH={DB_FILE}")
    add_check("Binance client connected", client is not None, "Check API keys valid")
    add_check("Mode", True, "TESTNET" if config.testnet else "PRODUCTION")

    overall = all(c["ok"] for c in checks if c["name"] not in ["Mode"])
    return {"overall": overall, "mode": ("testnet" if config.testnet else "production"), "checks": checks}

@app.post("/api/position/{position_id}/close")
async def close_position_endpoint(position_id: int, auth: bool = Depends(require_auth)):
    """Manually close a specific position"""
    if client is None:
        return {"success": False, "error": "Binance client not initialized"}
    
    try:
        position = get_position_by_id(position_id)
        if not position:
            return {"success": False, "error": "Position not found"}
        
        if position['status'] != 'open':
            return {"success": False, "error": "Position already closed"}
        
        symbol = position['symbol']
        quantity = position['quantity']
        side = position['side']
        
        # Close on Binance
        if side == 'long':
            order = client.order_market_sell(symbol=symbol, quantity=quantity)
        else:
            order = client.order_market_buy(symbol=symbol, quantity=quantity)
        
        # Get close price
        close_price = float(order.get('fills', [{}])[0].get('price', 0))
        
        # Update DB
        close_position(position_id, close_price, "manual")
        
        # Broadcast
        await broadcast_update({"type": "position_closed", "position_id": position_id})
        
        return {"success": True, "close_price": close_price, "order_id": order.get('orderId')}
        
    except BinanceAPIException as e:
        logger.error(f"Error closing position {position_id}: {e}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error closing position: {e}")
        return {"success": False, "error": str(e)}

# ============================================================================
# STARTUP & SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Bot startup"""
    logger.info("[START] Trident Trader PRO Bot v2.0 starting...")
    logger.info(f"[MODE] {'TESTNET' if config.testnet else 'PRODUCTION'}")
    logger.info(f"[BALANCE] ${get_usdt_balance():.2f} USDT")
    logger.info(f"[POSITIONS] Open positions: {len(get_open_positions())}")
    log_event("bot_start", "INFO", "Bot started successfully", {"version": "2.0"})

@app.on_event("shutdown")
async def shutdown_event():
    """Bot shutdown"""
    logger.info("[STOP] Bot shutting down...")
    log_event("bot_stop", "INFO", "Bot stopped", {})

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level=config.log_level.lower())
