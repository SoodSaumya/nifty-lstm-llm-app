from pathlib import Path
import pandas as pd

# Path to the FinBERT sentiment CSV
DATA_PATH = (
    Path(__file__)
    .resolve()
    .parent
    .parent
    / "data"
    / "finbert_sentiment_results_batched.csv"
)

def load_sentiment_data():
    """
    Load the pre-computed FinBERT sentiment results from CSV.
    The CSV must have a column named 'FinBERT_Sentiment' with
    values like 'Positive', 'Neutral', 'Negative'.
    """
    df = pd.read_csv(DATA_PATH)
    return df

def aggregate_sentiment(df, lookback_days: int = 7):
    """
    For now, we just compute overall sentiment distribution.
    If your CSV has a Date column, you can later filter the last N days.
    """
    counts = df["FinBERT_Sentiment"].value_counts(normalize=True).to_dict()

    pos = float(counts.get("Positive", 0.0))
    neu = float(counts.get("Neutral", 0.0))
    neg = float(counts.get("Negative", 0.0))

    return {
        "positive": round(pos, 3),
        "neutral": round(neu, 3),
        "negative": round(neg, 3),
    }

def generate_recommendation(predicted_prices, sentiment_summary):
    """
    Simple heuristic:
      - Upward price trend + positive sentiment -> BUY
      - Downward trend + negative sentiment -> SELL
      - Otherwise -> HOLD
    """
    start = predicted_prices[0]
    end = predicted_prices[-1]
    change_pct = (end - start) / start * 100.0

    pos = sentiment_summary["positive"]
    neg = sentiment_summary["negative"]

    if change_pct > 2 and pos > 0.5 and neg < 0.2:
        action = "BUY"
        reason = "Price trend is upward and sentiment is mostly positive."
    elif change_pct < -2 and neg > 0.4:
        action = "SELL"
        reason = "Price trend is downward and sentiment is mostly negative."
    else:
        action = "HOLD"
        reason = "Mixed signals or sideways trend; better to wait."

    return {
        "action": action,
        "reason": reason,
        "expected_change_pct": round(change_pct, 2),
    }
