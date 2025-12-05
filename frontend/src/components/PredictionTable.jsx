import React from "react";

export default function PredictionTable({ prices }) {
  if (!prices || prices.length === 0) return null;

  return (
    <div className="card">
      <h3>Predicted Next 7 Closing Prices</h3>
      <table className="table">
        <thead>
          <tr>
            <th>Day</th>
            <th>Predicted Close (₹)</th>
          </tr>
        </thead>
        <tbody>
          {prices.map((p, idx) => (
            <tr key={idx}>
              <td>Day {idx + 1}</td>
              <td>₹{p.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
