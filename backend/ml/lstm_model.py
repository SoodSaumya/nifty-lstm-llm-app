# =========================================
# Render-SAFE LSTMPredictor (NO TensorFlow)
# =========================================
import numpy as np
import pandas as pd
from pathlib import Path

DATA_PATH = (
    Path(__file__)
    .resolve()
    .parent
    .parent / "data" / "NIFTY50_10yearsdata1.csv"
)

class LSTMPredictor:
    def __init__(self, time_step=60, predict_days=7):
        self.time_step = time_step
        self.predict_days = predict_days
        df = pd.read_csv(DATA_PATH)
        df.columns = df.columns.str.strip()
        df["Date"] = pd.to_datetime(df["Date"])
        df.set_index("Date", inplace=True)
        self.df = df

    def predict_next_7(self):
        # Dummy simulated forecast based on average of last 7 days
        last_prices = self.df["Close"].tail(7).values
        avg = np.mean(last_prices)
        simulated = avg + np.linspace(-10, 10, 7)
        return simulated.tolist()

    def get_recent_actual(self, days=180):
        recent = self.df.tail(days)
        return {
            "dates": [d.strftime("%Y-%m-%d") for d in recent.index],
            "prices": recent["Close"].tolist()
        }
