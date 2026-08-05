import { useEffect, useState } from "react";
import api from "../api/axios";
import { parseJwt } from "../components/ProtectedRoute";

function Cameras() {
  const [cameras, setCameras] = useState([]);
  const [stores, setStores] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [isAdmin, setIsAdmin] = useState(false);

  // Form states
  const [name, setName] = useState("");
  const [ipAddress, setIpAddress] = useState("");
  const [storeId, setStoreId] = useState("");
  const [editingId, setEditingId] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [selectedCamera, setSelectedCamera] = useState(null);

  const token = localStorage.getItem("token");
  const headers = { Authorization: `Bearer ${token}` };

  useEffect(() => {
    if (token) {
      const payload = parseJwt(token);
      setIsAdmin(payload && payload.role === "Admin");
    }
    fetchCamerasAndStores();
  }, []);

  const fetchCamerasAndStores = async () => {
    try {
      setLoading(true);
      const [camerasRes, storesRes] = await Promise.all([
        api.get("/cameras/", { headers }),
        api.get("/stores/", { headers }),
      ]);
      setCameras(camerasRes.data);
      setStores(storesRes.data);
      if (camerasRes.data.length > 0) {
        setSelectedCamera(camerasRes.data[0]);
      }
    } catch (err) {
      setError("Failed to load camera or store data");
      console.error(err);
    } finally {
      setLoading(false);
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
      ip_address: ipAddress,
      store_id: parseInt(storeId),
    };

    try {
      if (editingId) {
        await api.put(`/cameras/${editingId}`, payloadData, { headers });
      } else {
        await api.post("/cameras/", payloadData, { headers });
      }
      setName("");
      setIpAddress("");
      setStoreId("");
      setEditingId(null);
      setShowForm(false);
      fetchCamerasAndStores();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to save camera");
    }
  };

  const handleEdit = (camera) => {
    setName(camera.name);
    setIpAddress(camera.ip_address);
    setStoreId(camera.store_id.toString());
    setEditingId(camera.id);
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this camera?")) {
      return;
    }
    setError("");
    try {
      await api.delete(`/cameras/${id}`, { headers });
      if (selectedCamera?.id === id) {
        setSelectedCamera(null);
      }
      fetchCamerasAndStores();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to delete camera");
    }
  };

  const getStoreName = (id) => {
    const store = stores.find((s) => s.id === id);
    return store ? store.name : `Store #${id}`;
  };

  if (loading && cameras.length === 0) {
    return <div className="loading-state">Loading camera connections...</div>;
  }

  return (
    <div className="cameras-container">
      {error && <div className="error-alert">{error}</div>}

      <div className="cameras-layout-grid">
        {/* Left Side: Camera List */}
        <div className="camera-list-pane">
          <div className="section-header">
            <h2>Connected Cameras ({cameras.length})</h2>
            {isAdmin && (
              <button 
                className="btn btn-primary"
                onClick={() => {
                  setShowForm(!showForm);
                  setEditingId(null);
                  setName("");
                  setIpAddress("");
                  setStoreId(stores[0]?.id?.toString() || "");
                }}
              >
                {showForm ? "Cancel" : "➕ Register"}
              </button>
            )}
          </div>

          {showForm && isAdmin && (
            <form className="form-card" onSubmit={handleSubmit}>
              <h3>{editingId ? "Edit Camera Settings" : "Register New Camera"}</h3>
              <div className="form-group">
                <label>Camera Name / Location Identifier</label>
                <input 
                  type="text" 
                  value={name} 
                  onChange={(e) => setName(e.target.value)} 
                  placeholder="e.g. Entrance Cam A"
                  required 
                />
              </div>
              <div className="form-group">
                <label>IP Address / Stream URL</label>
                <input 
                  type="text" 
                  value={ipAddress} 
                  onChange={(e) => setIpAddress(e.target.value)} 
                  placeholder="e.g. 192.168.1.105"
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
                      {store.name}
                    </option>
                  ))}
                </select>
              </div>
              <button type="submit" className="btn btn-success">
                {editingId ? "Update Camera" : "Save Camera"}
              </button>
            </form>
          )}

          <div className="camera-cards-list">
            {cameras.length === 0 ? (
              <p className="no-data-text">No cameras registered yet.</p>
            ) : (
              cameras.map((camera) => (
                <div 
                  key={camera.id} 
                  className={`camera-card-item ${selectedCamera?.id === camera.id ? "selected" : ""}`}
                  onClick={() => setSelectedCamera(camera)}
                >
                  <div className="camera-card-body">
                    <h4>🎥 {camera.name}</h4>
                    <p className="camera-ip">IP: {camera.ip_address}</p>
                    <p className="camera-store">Store: {getStoreName(camera.store_id)}</p>
                  </div>
                  {isAdmin && (
                    <div className="camera-card-actions">
                      <button className="btn-icon" onClick={(e) => { e.stopPropagation(); handleEdit(camera); }}>✏️</button>
                      <button className="btn-icon" onClick={(e) => { e.stopPropagation(); handleDelete(camera.id); }}>🗑️</button>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>

        {/* Right Side: Feed Preview Screen */}
        <div className="camera-preview-pane">
          {selectedCamera ? (
            <div className="video-player-container">
              <div className="video-player-header">
                <h3>🟢 Live Feed: {selectedCamera.name}</h3>
                <span>IP: {selectedCamera.ip_address}</span>
              </div>
              <div className="video-frame">
                <img 
                  src={`http://127.0.0.1:8000/cameras/${selectedCamera.id}/feed?token=${token}`} 
                  alt={`Simulated stream for ${selectedCamera.name}`} 
                  className="live-stream-image"
                />
              </div>
              <div className="video-player-footer">
                <p>Simulating real-time retail analysis. YOLOv8 is detecting objects and customers in the background...</p>
              </div>
            </div>
          ) : (
            <div className="empty-preview-state">
              <div className="empty-icon">📺</div>
              <h3>No Camera Selected</h3>
              <p>Select a camera from the list to view its real-time video analytics feed stream.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Cameras;