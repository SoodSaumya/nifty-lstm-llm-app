import React from "react";

export default function SentimentGauge({ summary }) {
  if (!summary) return null;
  const { positive, neutral, negative } = summary;

  const toPct = (x) => (x * 100).toFixed(1);

  return (
    <div className="card sentiment-card">
      <h3>Market Sentiment (FinBERT)</h3>
      <div className="sentiment-bars">
        <div className="bar-row">
          <span>Positive</span>
          <div className="bar">
            <div
              className="bar-fill positive"
              style={{ width: `${toPct(positive)}%` }}
            />
          </div>
          <span>{toPct(positive)}%</span>
        </div>
        <div className="bar-row">
          <span>Neutral</span>
          <div className="bar">
            <div
              className="bar-fill neutral"
              style={{ width: `${toPct(neutral)}%` }}
            />
          </div>
          <span>{toPct(neutral)}%</span>
        </div>
        <div className="bar-row">
          <span>Negative</span>
          <div className="bar">
            <div
              className="bar-fill negative"
              style={{ width: `${toPct(negative)}%` }}
            />
          </div>
          <span>{toPct(negative)}%</span>
        </div>
      </div>
    </div>
  );
}
