// frontend/src/App.jsx
import React, { useState, useEffect } from "react";
import "./App.css";

import Loader from "./components/Loader.jsx";
import PredictionTable from "./components/PredictionTable.jsx";
import PriceChart from "./components/PriceChart.jsx";
import SentimentGauge from "./components/SentimentGauge.jsx";
import RecommendationCard from "./components/RecommendationCard.jsx";
import { getPrediction, getHistory } from "./services/api.js";
import PaperTrading from "./components/PaperTrading.jsx";

function App() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [history, setHistory] = useState([]);
  const [livePrice, setLivePrice] = useState(null);

  // WebSocket for live NIFTY price
  useEffect(() => {
    let ws;

    try {
    ws = new WebSocket("wss://nifty-lstm-llm-app.onrender.com/ws/prices");


      ws.onopen = () => {
        console.log("✅ WebSocket connected");
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === "live_price") {
            console.log("📡 live price:", data.payload);
            setLivePrice(data.payload);
          }
        } catch (err) {
          console.error("WS message parse error:", err);
        }
      };

      ws.onerror = (err) => {
        console.error("WS error:", err);
      };

      ws.onclose = () => {
        console.log("❌ WebSocket closed");
      };
    } catch (err) {
      console.error("Failed to open WebSocket:", err);
    }

    return () => {
      if (ws) ws.close();
    };
  }, []);

  const handlePredict = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await getPrediction();
      setPrediction(data);

      const hist = await getHistory();
      setHistory(hist.history ?? []);
    } catch (err) {
      console.error("Predict error:", err);
      setError("Failed to fetch prediction from server.");
    } finally {
      setLoading(false);
    }
  };

  return (
    // ✅ use app-shell so CSS centers everything
    <div className="app-shell">
      <header className="hero">
        <h1>NIFTY50 AI Advisor</h1>
        <p>
          LSTM price forecasting + FinBERT news sentiment to help you decide
          when to buy, hold, or sell.
        </p>

        <button
          className="primary-btn"
          onClick={handlePredict}
          disabled={loading}
        >
          {loading ? "Running model..." : "Predict Next 7 Days"}
        </button>

        {error && <p className="error-text">{error}</p>}
      </header>

      {/* Live price bar */}
      {livePrice && (
        <div className="card" style={{ margin: "1.5rem auto", maxWidth: 600 }}>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <div style={{ fontWeight: 600 }}>NIFTY 50 (Live)</div>
            <div>
              ₹{livePrice.price.toFixed(2)}{" "}
              <span
                style={{
                  fontSize: "0.8rem",
                  marginLeft: 8,
                  color: "#9ca3af",
                }}
              >
                {new Date(livePrice.time).toLocaleTimeString()}
              </span>
            </div>
          </div>
        </div>
      )}
       <PaperTrading livePrice={livePrice} />

      {loading && <Loader />}

      {prediction && !loading && (
        <main className="grid">
          <section className="card">
            <h2>Predicted Next 7 Closing Prices</h2>
            <PredictionTable prices={prediction.predictedPrices} />
          </section>

          <section className="card">
            <h2>AI Recommendation</h2>
            <RecommendationCard recommendation={prediction.recommendation} />
          </section>

          <section className="card wide">
            <h2>Actual vs Predicted (Next 7 Days Projection)</h2>
            <PriceChart
              recent={prediction.recent}
              predicted={prediction.predictedPrices}
            />
          </section>

          <section className="card">
            <h2>Market Sentiment (FinBERT)</h2>
            <SentimentGauge summary={prediction.sentimentSummary} />
          </section>

          <section className="card wide">
            <h2>Previous Runs</h2>
            {history.length === 0 ? (
              <p>No history yet.</p>
            ) : (
              <ul className="history-list">
                {history.map((run) => (
                  <li key={run.id}>
                    {new Date(run.createdAt).toLocaleString()} —{" "}
                    {run.recommendation?.action?.toUpperCase() ?? "N/A"}
                  </li>
                ))}
              </ul>
            )}
          </section>
        </main>
      )}
    </div>
  );
}

export default App;
