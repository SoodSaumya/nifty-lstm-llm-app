import React from "react";

export default function RecommendationCard({ recommendation }) {
  if (!recommendation) return null;
  const { action, reason, expected_change_pct } = recommendation;

  return (
    <div className="card recommendation">
      <h3>AI Recommendation</h3>
      <p className={`action action-${action.toLowerCase()}`}>{action}</p>
      <p className="change">
        Expected price change (7 days):{" "}
        <strong>{expected_change_pct}%</strong>
      </p>
      <p className="reason">{reason}</p>
      <small>
        ⚠️ Not financial advice. Use this as a decision support tool only.
      </small>
    </div>
  );
}
