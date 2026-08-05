import { useEffect, useState } from "react";
import api from "../api/axios";

function Dashboard() {
  const [stats, setStats] = useState({
    stores: 0,
    shelves: 0,
    cameras: 0,
    products: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const token = localStorage.getItem("token");
        const headers = { Authorization: `Bearer ${token}` };

        const [storesRes, shelvesRes, camerasRes, productsRes] = await Promise.all([
          api.get("/stores/", { headers }),
          api.get("/shelves/", { headers }),
          api.get("/cameras/", { headers }),
          api.get("/products/", { headers }),
        ]);

        setStats({
          stores: storesRes.data.length,
          shelves: shelvesRes.data.length,
          cameras: camerasRes.data.length,
          products: productsRes.data.length,
        });
      } catch (err) {
        setError("Failed to load dashboard metrics");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) {
    return <div className="loading-state">Loading system metrics...</div>;
  }

  return (
    <div className="dashboard-content">
      {error && <p className="error">{error}</p>}
      
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">🏪</div>
          <div className="stat-info">
            <div className="stat-title">Total Stores</div>
            <div className="stat-value">{stats.stores}</div>
            <div className="stat-desc">Registered locations</div>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">🗄️</div>
          <div className="stat-info">
            <div className="stat-title">Total Shelves</div>
            <div className="stat-value">{stats.shelves}</div>
            <div className="stat-desc">Mapped store shelves</div>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">🎥</div>
          <div className="stat-info">
            <div className="stat-title">Active Cameras</div>
            <div className="stat-value">{stats.cameras}</div>
            <div className="stat-desc">IP cameras connected</div>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">📦</div>
          <div className="stat-info">
            <div className="stat-title">Total Products</div>
            <div className="stat-value">{stats.products}</div>
            <div className="stat-desc">Inventoried items</div>
          </div>
        </div>
      </div>
      
      <div className="system-status-section">
        <h3>🚀 System Pipeline Status</h3>
        <div className="status-grid">
          <div className="status-item">
            <span className="status-name">FastAPI Backend API</span>
            <span className="badge badge-success">ONLINE</span>
          </div>
          <div className="status-item">
            <span className="status-name">Video Ingestion Service</span>
            <span className="badge badge-success">ACTIVE</span>
          </div>
          <div className="status-item">
            <span className="status-name">YOLOv8 + MediaPipe Detection Engine</span>
            <span className="badge badge-warning">STANDBY</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;