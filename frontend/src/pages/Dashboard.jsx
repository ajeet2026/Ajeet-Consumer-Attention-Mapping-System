import { useEffect, useState } from "react";
import api from "../api/axios";
import { generateAdminReport } from "../utils/reportGenerator";

function Dashboard() {
  const [liveStats, setLiveStats] = useState({
    active_shoppers: 0,
    today_visitors: 0,
    average_dwell_time: 0.0,
    attention_events_count: 0,
    top_shelf_id: null,
  });

  const [coreStats, setCoreStats] = useState({
    stores: 0,
    shelves: 0,
    cameras: 0,
    products: 0,
  });

  const [recentSessions, setRecentSessions] = useState([]);
  const [dwellStats, setDwellStats] = useState([]);
  const [zoneStats, setZoneStats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    let intervalId = null;

    const fetchAllData = async () => {
      try {
        const token = localStorage.getItem("token");
        if (!token) {
          // No token — stop polling and let the user log in
          if (intervalId) clearInterval(intervalId);
          setError("Session expired. Please log in again.");
          setLoading(false);
          return;
        }
        const headers = { Authorization: `Bearer ${token}` };

        // Fetch core counts
        const [storesRes, shelvesRes, camerasRes, productsRes] = await Promise.all([
          api.get("/stores/", { headers }),
          api.get("/shelves/", { headers }),
          api.get("/cameras/", { headers }),
          api.get("/products/", { headers }),
        ]);

        setCoreStats({
          stores: storesRes.data.length,
          shelves: shelvesRes.data.length,
          cameras: camerasRes.data.length,
          products: productsRes.data.length,
        });

        // Fetch analytics
        const [liveRes, shoppersRes, dwellRes, zonesRes] = await Promise.all([
          api.get("/analytics/live", { headers }),
          api.get("/analytics/shoppers", { headers }),
          api.get("/analytics/dwell", { headers }),
          api.get("/analytics/zones", { headers }),
        ]);

        setLiveStats(liveRes.data);
        setRecentSessions(shoppersRes.data);
        setDwellStats(dwellRes.data);
        setZoneStats(zonesRes.data);
        setError("");
      } catch (err) {
        // On 401, the axios interceptor will redirect to login.
        // Stop polling to prevent flood of requests.
        if (err.response && err.response.status === 401) {
          if (intervalId) clearInterval(intervalId);
          return;
        }
        setError("Failed to load dashboard metrics");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchAllData();
    // Poll live data every 5 seconds to show real-time changes
    intervalId = setInterval(fetchAllData, 5000);
    return () => clearInterval(intervalId);
  }, []);

  if (loading) {
    return <div className="loading-state">Loading system analytics...</div>;
  }

  const handleGenerateReport = () => {
    setGenerating(true);
    try {
      generateAdminReport({ liveStats, coreStats, recentSessions, dwellStats, zoneStats });
    } catch (err) {
      console.error("Failed to generate report:", err);
    } finally {
      setTimeout(() => setGenerating(false), 1200);
    }
  };

  return (
    <div className="dashboard-content" style={{ color: "#f8fafc" }}>
      {error && <p className="error" style={{ color: "#ef4444" }}>{error}</p>}

      {/* --- HEADER ROW WITH REPORT BUTTON --- */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "12px", marginBottom: "20px" }}>
        <h2 style={{ fontSize: "1.4rem", margin: 0, color: "#38bdf8" }}>
          ⚡ Real-Time Attention Analytics
        </h2>
        <button
          onClick={handleGenerateReport}
          disabled={generating}
          style={{
            display: "flex",
            alignItems: "center",
            gap: "8px",
            padding: "10px 22px",
            background: generating ? "rgba(56, 189, 248, 0.15)" : "linear-gradient(135deg, #0ea5e9, #6366f1)",
            color: "#fff",
            border: "1px solid rgba(56, 189, 248, 0.3)",
            borderRadius: "8px",
            fontSize: "0.85rem",
            fontWeight: "600",
            cursor: generating ? "not-allowed" : "pointer",
            transition: "all 0.3s ease",
            boxShadow: generating ? "none" : "0 4px 15px rgba(56, 189, 248, 0.25)",
            opacity: generating ? 0.7 : 1,
          }}
          onMouseEnter={(e) => { if (!generating) e.target.style.boxShadow = "0 6px 25px rgba(56, 189, 248, 0.4)"; }}
          onMouseLeave={(e) => { if (!generating) e.target.style.boxShadow = "0 4px 15px rgba(56, 189, 248, 0.25)"; }}
        >
          {generating ? (
            <>
              <span style={{ display: "inline-block", width: "14px", height: "14px", border: "2px solid rgba(255,255,255,0.3)", borderTop: "2px solid #fff", borderRadius: "50%", animation: "spin 0.8s linear infinite" }} />
              Generating...
            </>
          ) : (
            <>
              📄 Download PDF Report
            </>
          )}
        </button>
      </div>

      <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
      <div className="stats-grid" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "20px", marginBottom: "30px" }}>
        <div className="stat-card" style={{ background: "rgba(30, 41, 59, 0.7)", border: "1px solid #38bdf8", boxShadow: "0 0 15px rgba(56, 189, 248, 0.1)" }}>
          <div className="stat-icon" style={{ fontSize: "2rem" }}>👤</div>
          <div className="stat-info">
            <div className="stat-title" style={{ fontSize: "0.85rem", color: "#94a3b8" }}>Active Shoppers</div>
            <div className="stat-value" style={{ fontSize: "2.2rem", fontWeight: "bold", color: "#38bdf8" }}>{liveStats.active_shoppers}</div>
            <div className="stat-desc" style={{ fontSize: "0.75rem", color: "#64748b" }}>Currently in camera view</div>
          </div>
        </div>

        <div className="stat-card" style={{ background: "rgba(30, 41, 59, 0.7)", border: "1px solid #22c55e" }}>
          <div className="stat-icon" style={{ fontSize: "2rem" }}>👥</div>
          <div className="stat-info">
            <div className="stat-title" style={{ fontSize: "0.85rem", color: "#94a3b8" }}>Today's Visitors</div>
            <div className="stat-value" style={{ fontSize: "2.2rem", fontWeight: "bold", color: "#22c55e" }}>{liveStats.today_visitors}</div>
            <div className="stat-desc" style={{ fontSize: "0.75rem", color: "#64748b" }}>Cumulative unique tracks</div>
          </div>
        </div>

        <div className="stat-card" style={{ background: "rgba(30, 41, 59, 0.7)", border: "1px solid #eab308" }}>
          <div className="stat-icon" style={{ fontSize: "2rem" }}>⏱️</div>
          <div className="stat-info">
            <div className="stat-title" style={{ fontSize: "0.85rem", color: "#94a3b8" }}>Avg Dwell Time</div>
            <div className="stat-value" style={{ fontSize: "2.2rem", fontWeight: "bold", color: "#eab308" }}>{liveStats.average_dwell_time}s</div>
            <div className="stat-desc" style={{ fontSize: "0.75rem", color: "#64748b" }}>Session duration average</div>
          </div>
        </div>

        <div className="stat-card" style={{ background: "rgba(30, 41, 59, 0.7)", border: "1px solid #f97316" }}>
          <div className="stat-icon" style={{ fontSize: "2rem" }}>👁️</div>
          <div className="stat-info">
            <div className="stat-title" style={{ fontSize: "0.85rem", color: "#94a3b8" }}>Attention Events</div>
            <div className="stat-value" style={{ fontSize: "2.2rem", fontWeight: "bold", color: "#f97316" }}>{liveStats.attention_events_count}</div>
            <div className="stat-desc" style={{ fontSize: "0.75rem", color: "#64748b" }}>Shelf focal gaze triggers</div>
          </div>
        </div>
      </div>

      {/* --- VISUAL CHARTS ROW --- */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "30px", marginBottom: "30px" }}>
        
        {/* Shelf Dwell Time Chart */}
        <div className="login-card" style={{ width: "100%", padding: "20px", background: "rgba(15, 23, 42, 0.6)", borderRadius: "8px", border: "1px solid rgba(148, 163, 184, 0.1)" }}>
          <h3 style={{ fontSize: "1.1rem", marginBottom: "20px", color: "#f8fafc" }}>📊 Shelf Attention Share</h3>
          {dwellStats.length === 0 ? (
            <p style={{ color: "#94a3b8", fontSize: "0.9rem" }}>No shelf focus events recorded yet.</p>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "15px" }}>
              {dwellStats.map((item) => {
                const totalDwell = dwellStats.reduce((acc, curr) => acc + curr.total_dwell_time, 0) || 1;
                const percentage = Math.round((item.total_dwell_time / totalDwell) * 100);
                return (
                  <div key={item.shelf_id}>
                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem", color: "#cbd5e1", marginBottom: "4px" }}>
                      <span>Shelf ID #{item.shelf_id} (Dwell: {Math.round(item.total_dwell_time)}s)</span>
                      <span>{percentage}%</span>
                    </div>
                    <div style={{ width: "100%", height: "10px", background: "#334155", borderRadius: "5px", overflow: "hidden" }}>
                      <div style={{ width: `${percentage}%`, height: "100%", background: "linear-gradient(90deg, #38bdf8, #0284c7)", borderRadius: "5px" }} />
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Zone Traffic Distribution */}
        <div className="login-card" style={{ width: "100%", padding: "20px", background: "rgba(15, 23, 42, 0.6)", borderRadius: "8px", border: "1px solid rgba(148, 163, 184, 0.1)" }}>
          <h3 style={{ fontSize: "1.1rem", marginBottom: "20px", color: "#f8fafc" }}>🗺️ Zone Traffic Density</h3>
          {zoneStats.length === 0 ? (
            <p style={{ color: "#94a3b8", fontSize: "0.9rem" }}>No zone metrics calculated.</p>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "15px" }}>
              {zoneStats.map((item) => {
                const totalVisits = zoneStats.reduce((acc, curr) => acc + curr.visit_count, 0) || 1;
                const percentage = Math.round((item.visit_count / totalVisits) * 100);
                return (
                  <div key={item.zone_id}>
                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem", color: "#cbd5e1", marginBottom: "4px" }}>
                      <span>{item.zone_id} Zone ({item.visit_count} visits)</span>
                      <span>Avg: {item.average_duration}s</span>
                    </div>
                    <div style={{ width: "100%", height: "10px", background: "#334155", borderRadius: "5px", overflow: "hidden" }}>
                      <div style={{ width: `${percentage}%`, height: "100%", background: "linear-gradient(90deg, #f97316, #ea580c)", borderRadius: "5px" }} />
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* --- RECENT TRACKED SESSIONS LIST --- */}
      <div className="login-card" style={{ width: "100%", padding: "20px", background: "rgba(15, 23, 42, 0.6)", borderRadius: "8px", border: "1px solid rgba(148, 163, 184, 0.1)", marginBottom: "30px" }}>
        <h3 style={{ fontSize: "1.1rem", marginBottom: "15px", color: "#cbd5e1" }}>📋 Recent Consumer Sessions</h3>
        {recentSessions.length === 0 ? (
          <p style={{ color: "#94a3b8", fontSize: "0.9rem" }}>No tracking sessions captured yet.</p>
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.85rem", textAlign: "left" }}>
              <thead>
                <tr style={{ borderBottom: "1px solid #334155", color: "#94a3b8" }}>
                  <th style={{ padding: "10px" }}>Session ID</th>
                  <th style={{ padding: "10px" }}>Tracking ID</th>
                  <th style={{ padding: "10px" }}>Camera ID</th>
                  <th style={{ padding: "10px" }}>Entry Time</th>
                  <th style={{ padding: "10px" }}>Exit Time</th>
                  <th style={{ padding: "10px" }}>Dwell Duration</th>
                  <th style={{ padding: "10px" }}>Status</th>
                </tr>
              </thead>
              <tbody>
                {recentSessions.map((session) => (
                  <tr key={session.id} style={{ borderBottom: "1px solid #1e293b", color: "#e2e8f0" }}>
                    <td style={{ padding: "10px" }}>#{session.id}</td>
                    <td style={{ padding: "10px", fontWeight: "bold", color: "#38bdf8" }}>ID_{session.tracking_id}</td>
                    <td style={{ padding: "10px" }}>Camera {session.camera_id}</td>
                    <td style={{ padding: "10px" }}>{new Date(session.entry_time).toLocaleTimeString()}</td>
                    <td style={{ padding: "10px" }}>{session.exit_time ? new Date(session.exit_time).toLocaleTimeString() : "Active"}</td>
                    <td style={{ padding: "10px" }}>{session.duration ? `${Math.round(session.duration)} seconds` : "-"}</td>
                    <td style={{ padding: "10px" }}>
                      <span className={`badge ${session.exit_time ? 'badge-success' : 'badge-warning'}`} style={{ fontSize: "0.7rem", padding: "2px 6px" }}>
                        {session.exit_time ? "COMPLETED" : "IN PROGRESS"}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* --- CORE RESOURCE COUNTS --- */}
      <h3 style={{ fontSize: "1.1rem", marginBottom: "15px", color: "#cbd5e1" }}>🏪 Inventory & Camera Resources</h3>
      <div className="stats-grid" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "15px" }}>
        <div className="stat-card" style={{ background: "rgba(15, 23, 42, 0.4)", border: "1px solid rgba(148, 163, 184, 0.1)" }}>
          <div className="stat-icon" style={{ fontSize: "1.5rem" }}>🏪</div>
          <div className="stat-info">
            <div className="stat-title" style={{ fontSize: "0.75rem", color: "#94a3b8" }}>Stores</div>
            <div className="stat-value" style={{ fontSize: "1.4rem", fontWeight: "bold" }}>{coreStats.stores}</div>
          </div>
        </div>

        <div className="stat-card" style={{ background: "rgba(15, 23, 42, 0.4)", border: "1px solid rgba(148, 163, 184, 0.1)" }}>
          <div className="stat-icon" style={{ fontSize: "1.5rem" }}>🗄️</div>
          <div className="stat-info">
            <div className="stat-title" style={{ fontSize: "0.75rem", color: "#94a3b8" }}>Shelves</div>
            <div className="stat-value" style={{ fontSize: "1.4rem", fontWeight: "bold" }}>{coreStats.shelves}</div>
          </div>
        </div>

        <div className="stat-card" style={{ background: "rgba(15, 23, 42, 0.4)", border: "1px solid rgba(148, 163, 184, 0.1)" }}>
          <div className="stat-icon" style={{ fontSize: "1.5rem" }}>🎥</div>
          <div className="stat-info">
            <div className="stat-title" style={{ fontSize: "0.75rem", color: "#94a3b8" }}>Cameras</div>
            <div className="stat-value" style={{ fontSize: "1.4rem", fontWeight: "bold" }}>{coreStats.cameras}</div>
          </div>
        </div>

        <div className="stat-card" style={{ background: "rgba(15, 23, 42, 0.4)", border: "1px solid rgba(148, 163, 184, 0.1)" }}>
          <div className="stat-icon" style={{ fontSize: "1.5rem" }}>📦</div>
          <div className="stat-info">
            <div className="stat-title" style={{ fontSize: "0.75rem", color: "#94a3b8" }}>Products</div>
            <div className="stat-value" style={{ fontSize: "1.4rem", fontWeight: "bold" }}>{coreStats.products}</div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;