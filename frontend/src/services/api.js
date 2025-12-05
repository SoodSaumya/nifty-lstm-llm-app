// frontend/src/services/api.js

// 👇 BACKEND URL – must match uvicorn (127.0.0.1:9000)
const API_BASE = "https://nifty-lstm-llm-app.onrender.com";

export async function getPrediction() {
  try {
    const res = await fetch(`${API_BASE}/api/predict`);
    if (!res.ok) {
      console.error("getPrediction: HTTP error", res.status);
      throw new Error("Failed to fetch prediction");
    }
    return await res.json();
  } catch (err) {
    console.error("getPrediction: fetch failed", err);
    throw err;
  }
}

export async function getHistory() {
  try {
    const res = await fetch(`${API_BASE}/api/history`);
    if (!res.ok) {
      console.error("getHistory: HTTP error", res.status);
      throw new Error("Failed to fetch history");
    }
    return await res.json();
  } catch (err) {
    console.error("getHistory: fetch failed", err);
    throw err;
  }
}

export async function initPaper() {
  const res = await fetch(`${API_BASE}/api/paper/init`, { method: "POST" });
  return res.json();
}

export async function placeTrade(action, quantity) {
  const res = await fetch(
    `${API_BASE}/api/paper/trade?action=${action}&quantity=${quantity}`,
    { method: "POST" }
  );
  return res.json();
}

export async function getPortfolio() {
  const res = await fetch(`${API_BASE}/api/paper/portfolio`);
  return res.json();
}
