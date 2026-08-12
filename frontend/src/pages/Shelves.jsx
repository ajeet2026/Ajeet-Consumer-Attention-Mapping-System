import { useEffect, useState } from "react";
import api from "../api/axios";
import { parseJwt } from "../components/ProtectedRoute";
import HeatmapCanvas from "../components/HeatmapCanvas";

function Shelves() {
  const [shelves, setShelves] = useState([]);
  const [stores, setStores] = useState([]);
  const [heatmapPoints, setHeatmapPoints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [isAdmin, setIsAdmin] = useState(false);

  // Form states
  const [name, setName] = useState("");
  const [storeId, setStoreId] = useState("");
  const [editingId, setEditingId] = useState(null);
  const [showForm, setShowForm] = useState(false);

  const token = localStorage.getItem("token");
  const headers = { Authorization: `Bearer ${token}` };

  useEffect(() => {
    let heatmapInterval = null;

    if (token) {
      const payload = parseJwt(token);
      setIsAdmin(payload && payload.role === "Admin");
    }
    fetchShelvesAndStores();

    const pollHeatmap = async () => {
      try {
        await fetchHeatmap();
      } catch (err) {
        if (err.response && err.response.status === 401) {
          if (heatmapInterval) clearInterval(heatmapInterval);
        }
      }
    };

    pollHeatmap();
    // Poll heatmap coordinates every 5 seconds
    heatmapInterval = setInterval(pollHeatmap, 5000);
    return () => clearInterval(heatmapInterval);
  }, []);

  const fetchShelvesAndStores = async () => {
    try {
      setLoading(true);
      const [shelvesRes, storesRes] = await Promise.all([
        api.get("/shelves/", { headers }),
        api.get("/stores/", { headers }),
      ]);
      setShelves(shelvesRes.data);
      setStores(storesRes.data);
    } catch (err) {
      setError("Failed to load shelf or store data");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchHeatmap = async () => {
    try {
      const res = await api.get("/analytics/attention", { headers });
      setHeatmapPoints(res.data);
    } catch (err) {
      console.error("Failed to load heatmap data", err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!storeId) {
      setError("Please select a store");
      return;
    }

    const payloadData = {
      name,
      store_id: parseInt(storeId),
    };

    try {
      if (editingId) {
        await api.put(`/shelves/${editingId}`, payloadData, { headers });
      } else {
        await api.post("/shelves/", payloadData, { headers });
      }
      setName("");
      setStoreId("");
      setEditingId(null);
      setShowForm(false);
      fetchShelvesAndStores();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to save shelf");
    }
  };

  const handleEdit = (shelf) => {
    setName(shelf.name);
    setStoreId(shelf.store_id.toString());
    setEditingId(shelf.id);
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this shelf?")) {
      return;
    }
    setError("");
    try {
      await api.delete(`/shelves/${id}`, { headers });
      fetchShelvesAndStores();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to delete shelf");
    }
  };

  const getStoreName = (id) => {
    const store = stores.find((s) => s.id === id);
    return store ? store.name : `Store #${id}`;
  };

  if (loading && shelves.length === 0) {
    return <div className="loading-state">Loading shelf configurations...</div>;
  }

  return (
    <div className="shelves-container" style={{ color: "#f8fafc" }}>
      {error && <div className="error-alert">{error}</div>}

      {/* --- VISUAL PLANOGRAM HEATMAP VIEW --- */}
      <h2 style={{ fontSize: "1.4rem", margin: "10px 0 10px 0", color: "#38bdf8" }}>
        📊 Store Planogram & Attention Heatmap
      </h2>
      <p style={{ color: "#94a3b8", fontSize: "0.85rem", marginBottom: "20px" }}>
        Gaze interaction density overlay calculated from media tracks and head pose vectors in real-time.
      </p>

      <div style={{ display: "flex", justifyContent: "center", marginBottom: "40px" }}>
        <div style={{
          position: "relative",
          width: "640px",
          height: "480px",
          background: "#1e293b",
          border: "2px solid #334155",
          borderRadius: "8px",
          boxShadow: "0 10px 25px rgba(0, 0, 0, 0.4)"
        }}>
          {/* Planogram Shelves Layout Background */}
          <div style={{
            position: "absolute",
            top: "60px",
            left: "40px",
            width: "200px",
            height: "220px",
            border: "2px dashed #0284c7",
            borderRadius: "6px",
            background: "rgba(2, 132, 199, 0.05)",
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            alignItems: "center"
          }}>
            <span style={{ fontSize: "1.1rem", fontWeight: "bold", color: "#38bdf8" }}>Shelf A</span>
            <span style={{ fontSize: "0.75rem", color: "#64748b" }}>Beverages Section</span>
          </div>

          <div style={{
            position: "absolute",
            top: "60px",
            left: "380px",
            width: "200px",
            height: "220px",
            border: "2px dashed #ea580c",
            borderRadius: "6px",
            background: "rgba(234, 88, 12, 0.05)",
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            alignItems: "center"
          }}>
            <span style={{ fontSize: "1.1rem", fontWeight: "bold", color: "#f97316" }}>Shelf B</span>
            <span style={{ fontSize: "0.75rem", color: "#64748b" }}>Snacks Section</span>
          </div>

          {/* Checkout Zone */}
          <div style={{
            position: "absolute",
            bottom: "20px",
            left: "40px",
            width: "560px",
            height: "80px",
            border: "2px dashed #22c55e",
            borderRadius: "6px",
            background: "rgba(34, 197, 94, 0.05)",
            display: "flex",
            justifyContent: "center",
            alignItems: "center"
          }}>
            <span style={{ fontSize: "1rem", fontWeight: "bold", color: "#4ade80" }}>🛒 Checkout Counter Area</span>
          </div>

          {/* Active Heatmap Overlay Canvas */}
          <HeatmapCanvas points={heatmapPoints} width={640} height={480} />
        </div>
      </div>

      {/* --- SHELVES LIST & CRUD TABLE --- */}
      <div className="section-header">
        <h2>Shelf Configuration List ({shelves.length})</h2>
        {isAdmin && (
          <button 
            className="btn btn-primary"
            onClick={() => {
              setShowForm(!showForm);
              setEditingId(null);
              setName("");
              setStoreId(stores[0]?.id?.toString() || "");
            }}
          >
            {showForm ? "Cancel" : "➕ Add New Shelf"}
          </button>
        )}
      </div>

      {showForm && isAdmin && (
        <form className="form-card" onSubmit={handleSubmit}>
          <h3>{editingId ? "Edit Shelf" : "Create New Shelf"}</h3>
          <div className="form-group">
            <label>Shelf Name / Identifier</label>
            <input 
              type="text" 
              value={name} 
              onChange={(e) => setName(e.target.value)} 
              placeholder="e.g. Shelf A1 - Beverages"
              required 
            />
          </div>
          <div className="form-group">
            <label>Assign to Store</label>
            <select 
              value={storeId} 
              onChange={(e) => setStoreId(e.target.value)}
              required
            >
              <option value="">-- Select Store --</option>
              {stores.map((store) => (
                <option key={store.id} value={store.id}>
                  {store.name} ({store.location})
                </option>
              ))}
            </select>
          </div>
          <button type="submit" className="btn btn-success">
            {editingId ? "Update Shelf" : "Save Shelf"}
          </button>
        </form>
      )}

      <div className="table-responsive">
        <table className="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Shelf Name</th>
              <th>Store</th>
              {isAdmin && <th>Actions</th>}
            </tr>
          </thead>
          <tbody>
            {shelves.length === 0 ? (
              <tr>
                <td colSpan={isAdmin ? 4 : 3} className="text-center">No shelves registered yet.</td>
              </tr>
            ) : (
              shelves.map((shelf) => (
                <tr key={shelf.id}>
                  <td>{shelf.id}</td>
                  <td className="font-bold">{shelf.name}</td>
                  <td>{getStoreName(shelf.store_id)}</td>
                  {isAdmin && (
                    <td>
                      <div className="actions-cell">
                        <button className="btn btn-sm btn-edit" onClick={() => handleEdit(shelf)}>✏️ Edit</button>
                        <button className="btn btn-sm btn-delete" onClick={() => handleDelete(shelf.id)}>🗑️ Delete</button>
                      </div>
                    </td>
                  )}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default Shelves;