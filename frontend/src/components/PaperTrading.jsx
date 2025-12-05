import React, { useState, useEffect } from "react";
import { initPaper, placeTrade, getPortfolio } from "../services/api.js";

export default function PaperTrading({ livePrice }) {
  const [portfolio, setPortfolio] = useState(null);
  const [qty, setQty] = useState(1);

  async function refresh() {
    const data = await getPortfolio();
    setPortfolio(data);
  }

  async function handleInit() {
    await initPaper();
    refresh();
  }

  async function handleTrade(action) {
    await placeTrade(action, qty);
    refresh();
  }

  useEffect(() => {
    refresh();
  }, []);

  return (
    <div className="card" style={{ marginTop: "2rem" }}>
      <h2>📈 Paper Trading Simulator</h2>

      <button onClick={handleInit} className="primary-btn">
        Reset Account
      </button>

      {portfolio && (
        <div style={{ marginTop: "1rem" }}>
          <p>💰 Cash: ₹{portfolio.cash.toFixed(2)}</p>
          <p>📦 Holdings: {portfolio.quantity} units</p>
          <p>📊 Position Value: ₹{portfolio.positionValue?.toFixed(2)}</p>
          <p>🏦 Total Equity: ₹{portfolio.totalEquity?.toFixed(2)}</p>
        </div>
      )}

      <div style={{ marginTop: "1rem" }}>
        <input
          type="number"
          value={qty}
          min={1}
          onChange={(e) => setQty(Number(e.target.value))}
          style={{ width: "80px", marginRight: "1rem" }}
        />

        <button
          onClick={() => handleTrade("buy")}
          className="primary-btn"
          style={{ marginRight: "1rem" }}
        >
          Buy
        </button>

        <button
          onClick={() => handleTrade("sell")}
          className="primary-btn"
        >
          Sell
        </button>
      </div>

      {livePrice && (
        <p style={{ marginTop: "1rem", color: "#9ca3af" }}>
          Live Price: ₹{livePrice.price.toFixed(2)}
        </p>
      )}
    </div>
  );
}
