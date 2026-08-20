import { useEffect, useState } from "react";
import api from "../api/axios";

function ShelfAnalytics() {
  const [shelfSummary, setShelfSummary] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [scanning, setScanning] = useState({});

  const fetchSummary = async () => {
    try {
      const token = localStorage.getItem("token");
      const res = await api.get("/analytics/shelf/summary", {
        headers: { Authorization: `Bearer ${token}` }
      });
      setShelfSummary(res.data);
    } catch (err) {
      console.error("Failed to load shelf analytics", err);
      setError("Failed to load shelf analytics data.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSummary();
    const interval = setInterval(fetchSummary, 10000); // Poll every 10s
    return () => clearInterval(interval);
  }, []);

  const handleScan = async (shelfId) => {
    setScanning(prev => ({ ...prev, [shelfId]: true }));
    try {
      const token = localStorage.getItem("token");
      await api.post(`/analytics/shelf/${shelfId}/scan`, null, {
        headers: { Authorization: `Bearer ${token}` }
      });
      await fetchSummary();
    } catch (err) {
      console.error(`Failed to scan shelf ${shelfId}`, err);
      alert("Scan failed. Ensure the camera is running and video stream is active.");
    } finally {
      setScanning(prev => ({ ...prev, [shelfId]: false }));
    }
  };

  if (loading && shelfSummary.length === 0) {
    return <div style={{ color: "#94a3b8" }}>Loading AI Shelf Analytics...</div>;
  }

  return (
    <div style={{ marginBottom: "40px" }}>
      <h2 style={{ fontSize: "1.4rem", margin: "10px 0 10px 0", color: "#38bdf8" }}>
        🛍️ AI Shelf Inventory Analytics (SKU-110K)
      </h2>
      <p style={{ color: "#94a3b8", fontSize: "0.85rem", marginBottom: "20px" }}>
        Real-time product detection and density analysis using YOLOv8 trained on the SKU-110K dataset.
      </p>

      {error && <div className="error-alert">{error}</div>}

      <div style={{ display: "flex", gap: "20px", flexWrap: "wrap" }}>
        {shelfSummary.length === 0 ? (
          <p style={{ color: "#64748b" }}>No shelves configured yet.</p>
        ) : (
          shelfSummary.map((shelf) => {
            const snap = shelf.latest_snapshot;
            const imageUrl = snap?.snapshot_path ? `http://127.0.0.1:8000/${snap.snapshot_path}` : null;

            return (
              <div key={shelf.shelf_id} style={{
                background: "#1e293b",
                border: "1px solid #334155",
                borderRadius: "8px",
                padding: "20px",
                width: "100%",
                maxWidth: "480px",
                boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.2)"
              }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "15px" }}>
                  <h3 style={{ margin: 0, color: "#f8fafc", fontSize: "1.1rem" }}>{shelf.shelf_name}</h3>
                  <button 
                    onClick={() => handleScan(shelf.shelf_id)}
                    disabled={scanning[shelf.shelf_id]}
                    style={{
                      background: scanning[shelf.shelf_id] ? "#475569" : "#0284c7",
                      color: "#fff",
                      border: "none",
                      padding: "6px 12px",
                      borderRadius: "4px",
                      cursor: scanning[shelf.shelf_id] ? "not-allowed" : "pointer",
                      fontSize: "0.8rem",
                      fontWeight: "bold"
                    }}
                  >
                    {scanning[shelf.shelf_id] ? "Scanning..." : "📸 Force Scan"}
                  </button>
                </div>

                {!shelf.has_bbox && (
                  <div style={{ color: "#fbbf24", fontSize: "0.85rem", marginBottom: "15px" }}>
                    ⚠️ Bounding box not configured. Full frame will be scanned.
                  </div>
                )}

                <div style={{ display: "flex", gap: "15px", marginBottom: "20px" }}>
                  <div style={{ flex: 1, background: "#0f172a", padding: "12px", borderRadius: "6px", textAlign: "center" }}>
                    <div style={{ color: "#94a3b8", fontSize: "0.75rem", textTransform: "uppercase", marginBottom: "4px" }}>Products Detected</div>
                    <div style={{ color: "#38bdf8", fontSize: "1.8rem", fontWeight: "bold" }}>
                      {snap ? snap.product_count : "-"}
                    </div>
                  </div>
                  
                  <div style={{ flex: 1, background: "#0f172a", padding: "12px", borderRadius: "6px", textAlign: "center" }}>
                    <div style={{ color: "#94a3b8", fontSize: "0.75rem", textTransform: "uppercase", marginBottom: "4px" }}>Occupancy</div>
                    <div style={{ color: "#4ade80", fontSize: "1.8rem", fontWeight: "bold" }}>
                      {snap ? `${snap.occupancy_pct}%` : "-"}
                    </div>
                  </div>
                </div>

                <div style={{ 
                  background: "#000", 
                  height: "240px", 
                  borderRadius: "6px", 
                  overflow: "hidden",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  border: "1px solid #334155"
                }}>
                  {imageUrl ? (
                    <img 
                      src={imageUrl} 
                      alt={`Shelf ${shelf.shelf_name} snapshot`} 
                      style={{ width: "100%", height: "100%", objectFit: "contain" }}
                    />
                  ) : (
                    <span style={{ color: "#475569", fontSize: "0.9rem" }}>No snapshot available</span>
                  )}
                </div>

                {/* Specific Product Recognition Breakdown */}
                {snap && snap.product_breakdown && Object.keys(snap.product_breakdown).length > 0 && (
                  <div style={{ marginTop: "15px", background: "#0f172a", padding: "12px", borderRadius: "6px" }}>
                    <div style={{ color: "#94a3b8", fontSize: "0.85rem", textTransform: "uppercase", marginBottom: "8px", fontWeight: "bold" }}>
                      Recognized Products (RPC Match)
                    </div>
                    <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
                      {Object.entries(snap.product_breakdown).map(([productName, count]) => (
                        <li key={productName} style={{ display: "flex", justifyContent: "space-between", color: "#f8fafc", fontSize: "0.9rem", padding: "4px 0", borderBottom: "1px solid #1e293b" }}>
                          <span>{productName.replace(/_/g, " ")}</span>
                          <span style={{ fontWeight: "bold", color: "#38bdf8" }}>{count}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {snap && (
                  <div style={{ color: "#64748b", fontSize: "0.75rem", textAlign: "right", marginTop: "10px" }}>
                    Last scanned: {new Date(snap.timestamp).toLocaleTimeString()}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

export default ShelfAnalytics;
