import { useEffect, useState } from "react";
import api from "../api/axios";
import { parseJwt } from "../components/ProtectedRoute";

function Stores() {
  const [stores, setStores] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [isAdmin, setIsAdmin] = useState(false);

  // Form states
  const [name, setName] = useState("");
  const [location, setLocation] = useState("");
  const [managerName, setManagerName] = useState("");
  const [editingId, setEditingId] = useState(null);
  const [showForm, setShowForm] = useState(false);

  const token = localStorage.getItem("token");
  const headers = { Authorization: `Bearer ${token}` };

  useEffect(() => {
    if (token) {
      const payload = parseJwt(token);
      setIsAdmin(payload && payload.role === "Admin");
    }
    fetchStores();
  }, []);

  const fetchStores = async () => {
    try {
      setLoading(true);
      const response = await api.get("/stores/", { headers });
      setStores(response.data);
    } catch (err) {
      setError("Failed to load stores");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    const payloadData = {
      name,
      location,
      manager_name: managerName,
    };

    try {
      if (editingId) {
        await api.put(`/stores/${editingId}`, payloadData, { headers });
      } else {
        await api.post("/stores/", payloadData, { headers });
      }
      setName("");
      setLocation("");
      setManagerName("");
      setEditingId(null);
      setShowForm(false);
      fetchStores();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to save store");
    }
  };

  const handleEdit = (store) => {
    setName(store.name);
    setLocation(store.location);
    setManagerName(store.manager_name || "");
    setEditingId(store.id);
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this store?")) {
      return;
    }
    setError("");
    try {
      await api.delete(`/stores/${id}`, { headers });
      fetchStores();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to delete store");
    }
  };

  if (loading && stores.length === 0) {
    return <div className="loading-state">Loading store configurations...</div>;
  }

  return (
    <div className="stores-container">
      {error && <div className="error-alert">{error}</div>}

      <div className="section-header">
        <h2>Registered Stores ({stores.length})</h2>
        {isAdmin && (
          <button 
            className="btn btn-primary"
            onClick={() => {
              setShowForm(!showForm);
              setEditingId(null);
              setName("");
              setLocation("");
              setManagerName("");
            }}
          >
            {showForm ? "Cancel" : "➕ Add New Store"}
          </button>
        )}
      </div>

      {showForm && isAdmin && (
        <form className="form-card" onSubmit={handleSubmit}>
          <h3>{editingId ? "Edit Store" : "Create New Store"}</h3>
          <div className="form-group">
            <label>Store Name</label>
            <input 
              type="text" 
              value={name} 
              onChange={(e) => setName(e.target.value)} 
              placeholder="e.g. Walmart Mall of America"
              required 
            />
          </div>
          <div className="form-group">
            <label>Location / Address</label>
            <input 
              type="text" 
              value={location} 
              onChange={(e) => setLocation(e.target.value)} 
              placeholder="e.g. Bloomington, MN"
              required 
            />
          </div>
          <div className="form-group">
            <label>Manager Name</label>
            <input 
              type="text" 
              value={managerName} 
              onChange={(e) => setManagerName(e.target.value)} 
              placeholder="e.g. John Doe"
            />
          </div>
          <button type="submit" className="btn btn-success">
            {editingId ? "Update Store" : "Save Store"}
          </button>
        </form>
      )}

      <div className="table-responsive">
        <table className="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Location</th>
              <th>Manager</th>
              {isAdmin && <th>Actions</th>}
            </tr>
          </thead>
          <tbody>
            {stores.length === 0 ? (
              <tr>
                <td colSpan={isAdmin ? 5 : 4} className="text-center">No stores registered yet.</td>
              </tr>
            ) : (
              stores.map((store) => (
                <tr key={store.id}>
                  <td>{store.id}</td>
                  <td className="font-bold">{store.name}</td>
                  <td>{store.location}</td>
                  <td>{store.manager_name || <span className="text-muted">Not assigned</span>}</td>
                  {isAdmin && (
                    <td>
                      <div className="actions-cell">
                        <button className="btn btn-sm btn-edit" onClick={() => handleEdit(store)}>✏️ Edit</button>
                        <button className="btn btn-sm btn-delete" onClick={() => handleDelete(store.id)}>🗑️ Delete</button>
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

export default Stores;