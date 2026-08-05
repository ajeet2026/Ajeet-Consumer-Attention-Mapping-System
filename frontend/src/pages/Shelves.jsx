import { useEffect, useState } from "react";
import api from "../api/axios";
import { parseJwt } from "../components/ProtectedRoute";

function Shelves() {
  const [shelves, setShelves] = useState([]);
  const [stores, setStores] = useState([]);
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
    if (token) {
      const payload = parseJwt(token);
      setIsAdmin(payload && payload.role === "Admin");
    }
    fetchShelvesAndStores();
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
    <div className="shelves-container">
      {error && <div className="error-alert">{error}</div>}

      <div className="section-header">
        <h2>Store Shelves ({shelves.length})</h2>
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