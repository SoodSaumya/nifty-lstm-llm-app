import React from "react";
import {
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

export default function PriceChart({ recent, predicted }) {
  // recent: { dates: [...], prices: [...] }
  if (
    !recent ||
    !Array.isArray(recent.dates) ||
    !Array.isArray(recent.prices) ||
    recent.dates.length === 0 ||
    recent.prices.length === 0
  ) {
    return (
      <div className="card" style={{ width: "100%", padding: 16 }}>
        <h3>Actual vs Predicted</h3>
        <p style={{ color: "#9ca3af", fontSize: "0.9rem" }}>
          Chart data not available – recent.dates / recent.prices missing.
        </p>
      </div>
    );
  }

  const dates = recent.dates;
  const prices = recent.prices;

  // Base data: actual + predicted initially same
  const data = dates.map((date, idx) => ({
    date,
    actual: prices[idx],
    predicted: prices[idx], // default: follow actual
  }));

  // If we have 7-day forecast, overwrite ONLY last N points
  if (Array.isArray(predicted) && predicted.length > 0) {
    const n = predicted.length;
    const len = data.length;
    const start = Math.max(len - n, 0);

    for (let i = 0; i < n; i++) {
      const index = start + i;
      if (index < len) {
        data[index].predicted = predicted[i];
      }
    }
  }

  return (
    <div style={{ width: "100%", height: 400 }}>
      <h3 style={{ color: "white", marginBottom: 8 }}>
        Actual vs Predicted (Next 7 Days Projection)
      </h3>
      <ResponsiveContainer>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis dataKey="date" tick={{ fill: "#a1a1aa", fontSize: 10 }} />
          <YAxis
            tick={{ fill: "#a1a1aa", fontSize: 10 }}
            domain={["dataMin", "dataMax"]}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "#0f172a",
              border: "1px solid #475569",
              color: "#f8fafc",
            }}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="actual"
            stroke="#2563eb"
            strokeWidth={2}
            dot={false}
            name="Actual Close"
          />
          <Line
            type="monotone"
            dataKey="predicted"
            stroke="#f97316"
            strokeWidth={2}
            dot={{ r: 3 }}
            name="Predicted Close"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
