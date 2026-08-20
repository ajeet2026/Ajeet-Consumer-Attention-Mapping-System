import React, { useState, useEffect } from 'react';
import api from '../api/axios';
import ProductHeatmap from './ProductHeatmap';

function ProductAnalytics() {
  const [scores, setScores] = useState([]);
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(true);
  const [recalculating, setRecalculating] = useState(false);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [scoresRes, recsRes] = await Promise.all([
        api.get('/analytics/products/scores'),
        api.get('/analytics/products/recommendations')
      ]);
      setScores(scoresRes.data);
      setRecommendations(recsRes.data);
    } catch (err) {
      console.error("Failed to fetch analytics data", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleRecalculate = async () => {
    try {
      setRecalculating(true);
      await api.post('/analytics/products/scores/calculate');
      await fetchData();
    } catch (err) {
      console.error("Failed to recalculate scores", err);
    } finally {
      setRecalculating(false);
    }
  };

  const renderProgressBar = (value, color) => {
    return (
      <div style={{ width: '100%', background: 'rgba(30, 41, 59, 0.5)', borderRadius: '4px', height: '6px', overflow: 'hidden' }}>
        <div style={{ width: `${value}%`, background: color, height: '100%', borderRadius: '4px' }}></div>
      </div>
    );
  };

  if (loading) {
    return <div style={{ color: "#94a3b8" }}>Loading Product Analytics...</div>;
  }

  return (
    <div className="dashboard-content" style={{ color: "#f8fafc" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
        <h2 style={{ fontSize: "1.4rem", margin: 0, color: "#38bdf8" }}>
          ⭐ Product Attractiveness Leaderboard
        </h2>
        <button 
          onClick={handleRecalculate} 
          disabled={recalculating}
          style={{ 
            background: recalculating ? "#475569" : "#3b82f6", 
            color: "white", 
            border: "none", 
            padding: "8px 16px", 
            borderRadius: "6px", 
            cursor: recalculating ? "not-allowed" : "pointer",
            fontWeight: "bold",
            display: "flex",
            alignItems: "center",
            gap: "8px"
          }}
        >
          {recalculating ? "🔄 Calculating..." : "🔄 Recalculate Scores"}
        </button>
      </div>

      {/* AI Recommendations Section */}
      {recommendations && recommendations.insights && recommendations.insights.length > 0 && (
        <div style={{ marginBottom: "30px" }}>
          <h3 style={{ fontSize: "1.1rem", marginBottom: "15px", color: "#cbd5e1" }}>🤖 AI Optimization Engine</h3>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "20px" }}>
            {recommendations.insights.map((insight, idx) => (
              <div key={idx} style={{ 
                background: insight.priority === "High" ? "rgba(239, 68, 68, 0.1)" : "rgba(59, 130, 246, 0.1)", 
                border: `1px solid ${insight.priority === "High" ? "rgba(239, 68, 68, 0.3)" : "rgba(59, 130, 246, 0.3)"}`,
                borderRadius: "8px", 
                padding: "15px" 
              }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
                  <span style={{ 
                    background: insight.priority === "High" ? "#ef4444" : "#3b82f6", 
                    color: "white", 
                    fontSize: "0.7rem", 
                    fontWeight: "bold", 
                    padding: "2px 6px", 
                    borderRadius: "4px",
                    textTransform: "uppercase"
                  }}>
                    {insight.type}
                  </span>
                  <span style={{ fontSize: "0.75rem", color: "#94a3b8", fontWeight: "bold" }}>{insight.target}</span>
                </div>
                <p style={{ fontSize: "0.9rem", color: "#f8fafc", marginBottom: "10px", lineHeight: "1.4" }}>
                  {insight.insight}
                </p>
                <div style={{ fontSize: "0.85rem", color: "#34d399", fontWeight: "600", display: "flex", gap: "5px" }}>
                  <span>💡</span> <span>{insight.action}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Visual Product Heatmap */}
      <ProductHeatmap scores={scores} />

      <h3 style={{ fontSize: "1.1rem", marginBottom: "15px", color: "#cbd5e1" }}>📊 Product Attractiveness Leaderboard</h3>

      <div className="login-card" style={{ width: "100%", padding: "20px", background: "rgba(15, 23, 42, 0.6)", borderRadius: "8px", border: "1px solid rgba(148, 163, 184, 0.1)" }}>
        {scores.length === 0 ? (
          <p style={{ color: "#94a3b8", fontSize: "0.9rem" }}>No product scores generated yet. Click 'Recalculate Scores' or add tracking data.</p>
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.85rem", textAlign: "left" }}>
              <thead style={{ color: "#94a3b8", background: "rgba(15, 23, 42, 0.4)", textTransform: "uppercase", letterSpacing: "0.05em", fontSize: "0.75rem" }}>
                <tr>
                  <th style={{ padding: "12px 16px", borderBottom: "1px solid #334155" }}>Rank</th>
                  <th style={{ padding: "12px 16px", borderBottom: "1px solid #334155" }}>Product</th>
                  <th style={{ padding: "12px 16px", borderBottom: "1px solid #334155" }}>Location</th>
                  <th style={{ padding: "12px 16px", borderBottom: "1px solid #334155" }}>Final Score</th>
                  <th style={{ padding: "12px 16px", borderBottom: "1px solid #334155", width: "40%" }}>Weighted Metrics Breakdown</th>
                </tr>
              </thead>
              <tbody>
                {scores.map((score, idx) => (
                  <tr key={score.product_id} style={{ borderBottom: "1px solid #1e293b", color: "#e2e8f0" }}>
                    <td style={{ padding: "16px", fontWeight: "bold", color: idx < 3 ? "#f59e0b" : "#94a3b8", fontSize: "1.1rem" }}>
                      #{idx + 1}
                    </td>
                    <td style={{ padding: "16px" }}>
                      <div style={{ fontWeight: "600", color: "#f8fafc", fontSize: "0.95rem" }}>{score.product_name}</div>
                      <div style={{ color: "#64748b", fontSize: "0.75rem" }}>{score.brand}</div>
                    </td>
                    <td style={{ padding: "16px" }}>
                      <span style={{ background: "rgba(148, 163, 184, 0.15)", color: "#cbd5e1", padding: "4px 8px", borderRadius: "4px", fontSize: "0.75rem" }}>
                        {score.shelf}
                      </span>
                    </td>
                    <td style={{ padding: "16px" }}>
                      <div style={{ fontSize: "1.2rem", fontWeight: "bold", color: score.scores.final_score > 70 ? "#22c55e" : score.scores.final_score > 40 ? "#eab308" : "#ef4444" }}>
                        {score.scores.final_score.toFixed(1)}
                      </div>
                    </td>
                    <td style={{ padding: "16px" }}>
                      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px", fontSize: "0.7rem", color: "#94a3b8" }}>
                        
                        <div>
                          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "2px" }}>
                            <span>👁️ Attention (35%)</span>
                            <span>{score.scores.attention_score.toFixed(0)}</span>
                          </div>
                          {renderProgressBar(score.scores.attention_score, "#38bdf8")}
                        </div>

                        <div>
                          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "2px" }}>
                            <span>✋ Interaction (25%)</span>
                            <span>{score.scores.interaction_score.toFixed(0)}</span>
                          </div>
                          {renderProgressBar(score.scores.interaction_score, "#a855f7")}
                        </div>

                        <div>
                          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "2px" }}>
                            <span>🛒 Pickup (20%)</span>
                            <span>{score.scores.pickup_score.toFixed(0)}</span>
                          </div>
                          {renderProgressBar(score.scores.pickup_score, "#f97316")}
                        </div>

                        <div>
                          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "2px" }}>
                            <span>💳 Purchase (15%)</span>
                            <span>{score.scores.purchase_score.toFixed(0)}</span>
                          </div>
                          {renderProgressBar(score.scores.purchase_score, "#22c55e")}
                        </div>

                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default ProductAnalytics;
