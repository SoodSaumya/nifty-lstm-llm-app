# =============================
# 1. Imports
# =============================
import os
from datetime import datetime
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pymongo import MongoClient
import yfinance as yf  # ✅ NEW
from ml.lstm_model import LSTMPredictor
from ml.sentiment_utils import load_sentiment_data, aggregate_sentiment, generate_recommendation
from auth import router as auth_router

# =============================
# 2. Mongo + Environment
# =============================
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "nifty_app")
MONGO_COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME", "predictions")

mongo_client = MongoClient(MONGO_URI) if MONGO_URI else None
mongo_collection = mongo_client[MONGO_DB_NAME][MONGO_COLLECTION_NAME] if mongo_client else None
live_prices_collection = mongo_client[MONGO_DB_NAME]["live_prices"] if mongo_client else None
# =============================
# Paper Trading Collections
# =============================
paper_accounts = mongo_client[MONGO_DB_NAME]["paper_accounts"] if mongo_client else None
paper_positions = mongo_client[MONGO_DB_NAME]["paper_positions"] if mongo_client else None
paper_trades = mongo_client[MONGO_DB_NAME]["paper_trades"] if mongo_client else None


# =============================
# 3. WebSocket Manager
# =============================
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        dead = []
        for ws in self.active_connections:
            try:
                await ws.send_json(message)
            except WebSocketDisconnect:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


manager = ConnectionManager()


# =============================
# 4. FastAPI App
# =============================
app = FastAPI(title="NIFTY LSTM + LLM API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://stock-savvy-i2oj.vercel.app",
        "https://nifty-lstm-llm-app.onrender.com",
        "http://localhost:5173",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# =============================
# 5. WebSocket Endpoint
# =============================
@app.websocket("/ws/prices")
async def websocket_prices(ws: WebSocket):
    await manager.connect(ws)
    try:
        await ws.send_json({"type": "info", "message": "Connected to price stream"})
        while True:
            await asyncio.sleep(30)
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(ws)


# =============================
# 6. Live Price Fetch + Background Poller
# =============================
def get_latest_nifty_price():
    try:
        ticker = yf.Ticker("^NSEI")
        data = ticker.history(period="1d", interval="1m")
        if data.empty:
            return None

        last_row = data.iloc[-1]
        price = float(last_row["Close"])
        ts = last_row.name.to_pydatetime()
        return {"symbol": "NIFTY50", "time": ts, "price": price}
    except Exception as e:
        print("Error fetching NIFTY:", e)
        return None


async def poll_live_prices():
    if live_prices_collection is None:
        print("⚠ No MongoDB live collection configured.")
        return
    while True:
        latest = get_latest_nifty_price()
        if latest:
            live_prices_collection.insert_one({
                "symbol": latest["symbol"],
                "time": latest["time"],
                "price": latest["price"],
                "createdAt": datetime.utcnow(),
            })
            await manager.broadcast({
                "type": "live_price",
                "payload": {
                    "symbol": latest["symbol"],
                    "time": latest["time"].isoformat(),
                    "price": latest["price"],
                },
            })
            print("📡 Broadcast live NIFTY price:", latest["price"])
        await asyncio.sleep(60)  # every 1 min


@app.on_event("startup")
async def on_startup():
    asyncio.create_task(poll_live_prices())


# =============================
# 7. LSTM + Sentiment Model
# =============================
lstm = LSTMPredictor(time_step=60, predict_days=7)
print("LSTM predictor loaded (no training on Render).")


sentiment_df = load_sentiment_data()
print("Loaded sentiment data.")

# =============================
# Paper Trading Helpers
# =============================
def get_live_price_for_trading():
    try:
        ticker = yf.Ticker("^NSEI")
        data = ticker.history(period="1d", interval="1m")
        if data.empty:
            return None
        last_row = data.iloc[-1]
        return float(last_row["Close"])
    except:
        return None

# =============================
# 8. REST Endpoints
# =============================
@app.get("/api/predict")
def predict_next_7():
    predicted_prices = lstm.predict_next_7()
    recent = lstm.get_recent_actual(days=180)
    sentiment_summary = aggregate_sentiment(sentiment_df)
    recommendation = generate_recommendation(predicted_prices, sentiment_summary)

    doc = {
        "symbol": "NIFTY50",
        "createdAt": datetime.utcnow(),
        "predictedPrices": predicted_prices,
        "sentimentSummary": sentiment_summary,
        "recommendation": recommendation,
    }
    if mongo_collection is not None:
        mongo_collection.insert_one(doc)

    return {
        "symbol": "NIFTY50",
        "predictedPrices": predicted_prices,
        "recent": recent,
        "sentimentSummary": sentiment_summary,
        "recommendation": recommendation,
    }


@app.get("/api/history")
def get_prediction_history(limit: int = 10):
    if not mongo_collection:
        return {"history": []}
    cursor = mongo_collection.find({}).sort("createdAt", -1).limit(limit)
    history = [
        {
            "id": str(doc["_id"]),
            "createdAt": doc["createdAt"],
            "predictedPrices": doc["predictedPrices"],
            "recommendation": doc["recommendation"],
        }
        for doc in cursor
    ]
    return {"history": history}

@app.post("/api/paper/init")
def init_paper_account():
    if paper_accounts is None:
        return {"error": "MongoDB not configured"}

    paper_accounts.delete_many({})
    paper_positions.delete_many({})
    paper_trades.delete_many({})

    starting_cash = 100000

    paper_accounts.insert_one({
        "cash": starting_cash,
        "createdAt": datetime.utcnow()
    })

    return {"message": "Paper trading account reset", "cash": starting_cash}

@app.post("/api/paper/trade")
def place_trade(action: str, quantity: int):
    if paper_accounts is None:
        return {"error": "MongoDB not configured"}

    action = action.lower()
    if action not in ["buy", "sell"]:
        return {"error": "Invalid action"}

    price = get_live_price_for_trading()
    if not price:
        return {"error": "Could not fetch live price"}

    account = paper_accounts.find_one({})
    if not account:
        return {"error": "Account not initialized"}

    cash = account["cash"]
    cost = price * quantity

    # BUY
    if action == "buy":
        if cash < cost:
            return {"error": "Not enough cash"}
        paper_accounts.update_one({}, {"$inc": {"cash": -cost}})
        paper_positions.update_one(
            {"symbol": "NIFTY50"},
            {"$inc": {"quantity": quantity}},
            upsert=True
        )

    # SELL
    else:
        pos = paper_positions.find_one({"symbol": "NIFTY50"})
        if not pos or pos["quantity"] < quantity:
            return {"error": "Not enough quantity to sell"}
        paper_accounts.update_one({}, {"$inc": {"cash": cost}})
        paper_positions.update_one(
            {"symbol": "NIFTY50"},
            {"$inc": {"quantity": -quantity}}
        )

    paper_trades.insert_one({
        "symbol": "NIFTY50",
        "action": action,
        "quantity": quantity,
        "price": price,
        "timestamp": datetime.utcnow()
    })

    return {"message": "Trade executed", "price": price}

@app.get("/api/paper/portfolio")
def get_portfolio():
    if paper_accounts is None:
        return {"error": "MongoDB not configured"}

    account = paper_accounts.find_one({})
    pos = paper_positions.find_one({"symbol": "NIFTY50"})
    live_price = get_live_price_for_trading()

    qty = pos["quantity"] if pos else 0
    value = qty * (live_price if live_price else 0)

    return {
        "cash": account["cash"] if account else 0,
        "quantity": qty,
        "livePrice": live_price,
        "positionValue": value,
        "totalEquity": value + (account["cash"] if account else 0)
    }
app.include_router(auth_router)