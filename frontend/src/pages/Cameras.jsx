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

  // Upload states
  const [uploading, setUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState("");

  const token = localStorage.getItem("token");
  const headers = { Authorization: `Bearer ${token}` };

  useEffect(() => {
    if (token) {
      const payload = parseJwt(token);
      setIsAdmin(payload && payload.role === "Admin");
    }
    fetchCamerasAndStores();
  }, []);

  const fetchCamerasAndStores = async (selectNewest = false) => {
    try {
      setLoading(true);
      const [camerasRes, storesRes] = await Promise.all([
        api.get("/cameras/", { headers }),
        api.get("/stores/", { headers }),
      ]);
      setCameras(camerasRes.data);
      setStores(storesRes.data);
      if (camerasRes.data.length > 0) {
        if (selectNewest) {
          // Select the camera with the highest ID (newest uploaded)
          const sorted = [...camerasRes.data].sort((a, b) => b.id - a.id);
          setSelectedCamera(sorted[0]);
        } else if (!selectedCamera) {
          setSelectedCamera(camerasRes.data[0]);
        }
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

  const handleVideoUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setError("");
    setUploadSuccess("");
    setUploading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await api.post("/cameras/upload", formData, {
        headers: {
          ...headers,
          "Content-Type": "multipart/form-data",
        },
      });
      setUploadSuccess(`Successfully uploaded and registered virtual camera: ${response.data.name}`);
      await fetchCamerasAndStores(true); // reload list and auto-select newest
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to upload video file.");
      console.error(err);
    } finally {
      setUploading(false);
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

  const isVirtualCamera = (ip) => {
    return ip && (ip.startsWith("/") || ip.includes("uploads/"));
  };

  if (loading && cameras.length === 0) {
    return <div className="loading-state">Loading camera connections...</div>;
  }

  return (
    <div className="cameras-container" style={{ color: "#f8fafc" }}>
      {error && <div className="error-alert">{error}</div>}
      {uploadSuccess && <div className="error-alert" style={{ background: "rgba(34, 197, 94, 0.15)", border: "1px solid #22c55e", color: "#4ade80" }}>{uploadSuccess}</div>}

      <div className="cameras-layout-grid">
        {/* Left Side: Camera List & Upload Zone */}
        <div className="camera-list-pane">
          
          {/* --- VIDEO UPLOADER WIDGET --- */}
          <div className="login-card" style={{ width: "100%", padding: "15px", marginBottom: "20px", background: "rgba(15, 23, 42, 0.4)", border: "1px dashed #334155", borderRadius: "8px" }}>
            <h3 style={{ fontSize: "1rem", color: "#38bdf8", marginBottom: "8px" }}>📤 Upload CCTV Video for AI Run</h3>
            <p style={{ fontSize: "0.75rem", color: "#94a3b8", marginBottom: "12px" }}>Upload `.mp4` or `.avi` files to execute frame-by-frame person tracking and gaze analytics.</p>
            <input 
              type="file" 
              accept="video/*" 
              onChange={handleVideoUpload}
              disabled={uploading}
              style={{ display: "none" }}
              id="video-upload-input"
            />
            <label 
              htmlFor="video-upload-input"
              className="btn btn-primary"
              style={{ display: "block", textAlign: "center", cursor: "pointer", width: "100%", background: uploading ? "#334155" : "linear-gradient(135deg, #0284c7, #0369a1)" }}
            >
              {uploading ? "⏳ Uploading & Extracting Frames..." : "📁 Choose Video File"}
            </label>
          </div>

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

          <div className="camera-cards-list" style={{ maxHeight: "400px", overflowY: "auto" }}>
            {cameras.length === 0 ? (
              <p className="no-data-text">No cameras registered yet.</p>
            ) : (
              cameras.map((camera) => (
                <div 
                  key={camera.id} 
                  className={`camera-card-item ${selectedCamera?.id === camera.id ? "selected" : ""}`}
                  onClick={() => setSelectedCamera(camera)}
                  style={{ display: "flex", justifyContent: "space-between", alignItems: "center", border: selectedCamera?.id === camera.id ? "1.5px solid #38bdf8" : "1px solid #1e293b" }}
                >
                  <div className="camera-card-body">
                    <h4 style={{ margin: 0, fontSize: "0.95rem" }}>
                      {isVirtualCamera(camera.ip_address) ? "🎬" : "🎥"} {camera.name}
                    </h4>
                    <p className="camera-ip" style={{ fontSize: "0.75rem", color: "#64748b", margin: "4px 0" }}>
                      {isVirtualCamera(camera.ip_address) ? "Virtual Video File" : `IP: ${camera.ip_address}`}
                    </p>
                    <p className="camera-store" style={{ fontSize: "0.75rem", color: "#94a3b8", margin: 0 }}>
                      Store: {getStoreName(camera.store_id)}
                    </p>
                  </div>
                  {isAdmin && (
                    <div className="camera-card-actions" style={{ display: "flex", gap: "5px" }}>
                      {!isVirtualCamera(camera.ip_address) && (
                        <button className="btn-icon" onClick={(e) => { e.stopPropagation(); handleEdit(camera); }}>✏️</button>
                      )}
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
            <div className="video-player-container" style={{ background: "#0f172a", border: "1px solid #1e293b" }}>
              <div className="video-player-header" style={{ padding: "12px 18px", borderBottom: "1px solid #1e293b" }}>
                <h3 style={{ margin: 0, fontSize: "1rem", color: "#cbd5e1" }}>
                  🟢 Active Pipeline Feed: {selectedCamera.name}
                </h3>
                <span style={{ fontSize: "0.75rem", color: "#64748b" }}>
                  {isVirtualCamera(selectedCamera.ip_address) ? "Processing File Tracks" : `IP/Stream: ${selectedCamera.ip_address}`}
                </span>
              </div>
              <div className="video-frame" style={{ position: "relative", display: "flex", justifyContent: "center", alignItems: "center", background: "#020617", height: "450px" }}>
                <img 
                  src={`http://127.0.0.1:8000/cameras/${selectedCamera.id}/feed?token=${token}`} 
                  alt={`Simulated stream for ${selectedCamera.name}`} 
                  className="live-stream-image"
                  style={{ maxWidth: "100%", maxHeight: "100%", objectFit: "contain", borderRadius: "4px" }}
                  onError={(e) => {
                    e.target.onerror = null;
                    e.target.src = "https://images.unsplash.com/photo-1557683316-973673baf926?q=80&w=640&h=480&auto=format&fit=crop";
                  }}
                />
              </div>
              <div className="video-player-footer" style={{ padding: "12px 18px", borderTop: "1px solid #1e293b", fontSize: "0.8rem", color: "#94a3b8" }}>
                <p style={{ margin: 0 }}>
                  ⚡ **YOLOv8 & MediaPipe active**: Tracking boxes (green) and gaze estimation vector arrows (blue) are drawn on the frames in real time.
                </p>
              </div>
            </div>
          ) : (
            <div className="empty-preview-state" style={{ background: "#0f172a" }}>
              <div className="empty-icon" style={{ fontSize: "3rem" }}>📺</div>
              <h3 style={{ margin: "15px 0 8px 0" }}>No Active Camera Selected</h3>
              <p style={{ margin: 0, fontSize: "0.85rem", color: "#64748b" }}>Select a camera or upload a video file to view real-time CV analytics.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Cameras;