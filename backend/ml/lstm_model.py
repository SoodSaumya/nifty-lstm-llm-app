import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.preprocessing import MinMaxScaler
#from tensorflow.keras.models import Sequential
#from tensorflow.keras.layers import LSTM, Dense
#from tensorflow.keras.callbacks import EarlyStopping

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "NIFTY50_10yearsdata1.csv"

def load_price_data():
    df = pd.read_csv(DATA_PATH)
    df.columns = df.columns.str.strip()
    df["Date"] = pd.to_datetime(df["Date"])
    df.set_index("Date", inplace=True)
    close = df["Close"].values.reshape(-1, 1)
    return df, close

def create_dataset(dataset, time_step=60, predict_days=7):
    x, y = [], []
    for i in range(time_step, len(dataset) - predict_days + 1):
        x.append(dataset[i - time_step:i, 0])
        y.append(dataset[i:i + predict_days, 0])
    return np.array(x), np.array(y)

def build_lstm_model(time_step=60, predict_days=7):
    model = Sequential([
        LSTM(64, return_sequences=True, input_shape=(time_step, 1)),
        LSTM(64),
        Dense(predict_days)
    ])
    model.compile(optimizer="adam", loss="mean_squared_error")
    return model

class LSTMPredictor:
    def __init__(self, time_step=60, predict_days=7):
        self.time_step = time_step
        self.predict_days = predict_days
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.model = None
        self.df = None

    def train(self, epochs=30, batch_size=64):
        self.df, close = load_price_data()
        scaled = self.scaler.fit_transform(close)

        x, y = create_dataset(scaled, self.time_step, self.predict_days)
        x = x.reshape((x.shape[0], x.shape[1], 1))

        train_size = int(len(x) * 0.8)
        x_train, y_train = x[:train_size], y[:train_size]

        self.model = build_lstm_model(self.time_step, self.predict_days)
        early_stop = EarlyStopping(monitor="loss", patience=5, restore_best_weights=True)

        self.model.fit(
            x_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[early_stop],
            verbose=0
        )

    def predict_next_7(self):
        if self.model is None:
            raise RuntimeError("Model not trained yet")

        close = self.df["Close"].values.reshape(-1, 1)
        scaled = self.scaler.transform(close)
        last_60 = scaled[-self.time_step:]
        last_60 = last_60.reshape((1, self.time_step, 1))

        pred_scaled = self.model.predict(last_60)
        preds = self.scaler.inverse_transform(pred_scaled).flatten()
        return preds.tolist()

    def get_recent_actual(self, days=180):
        """Return last `days` of actual closing prices for chart."""
        recent = self.df.tail(days)
        return {
            "dates": [d.strftime("%Y-%m-%d") for d in recent.index],
            "prices": recent["Close"].tolist()
        }
class LSTMPredictor:
    def predict(self, data):
        return {"prediction": "Model disabled on Render free tier"}
