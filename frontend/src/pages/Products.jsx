import { useEffect, useState } from "react";
import api from "../api/axios";
import { parseJwt } from "../components/ProtectedRoute";

function Products() {
  const [products, setProducts] = useState([]);
  const [shelves, setShelves] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [isAdmin, setIsAdmin] = useState(false);

  // Form states
  const [name, setName] = useState("");
  const [brand, setBrand] = useState("");
  const [price, setPrice] = useState("");
  const [shelfId, setShelfId] = useState("");
  const [editingId, setEditingId] = useState(null);
  const [showForm, setShowForm] = useState(false);

  const token = localStorage.getItem("token");
  const headers = { Authorization: `Bearer ${token}` };

  useEffect(() => {
    if (token) {
      const payload = parseJwt(token);
      setIsAdmin(payload && payload.role === "Admin");
    }
    fetchProductsAndShelves();
  }, []);

  const fetchProductsAndShelves = async () => {
    try {
      setLoading(true);
      const [productsRes, shelvesRes] = await Promise.all([
        api.get("/products/", { headers }),
        api.get("/shelves/", { headers }),
      ]);
      setProducts(productsRes.data);
      setShelves(shelvesRes.data);
    } catch (err) {
      setError("Failed to load products or shelf details");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!shelfId) {
      setError("Please assign the product to a shelf");
      return;
    }

    const payloadData = {
      name,
      brand,
      price: parseInt(price),
      shelf_id: parseInt(shelfId),
    };

    try {
      if (editingId) {
        await api.put(`/products/${editingId}`, payloadData, { headers });
      } else {
        await api.post("/products/", payloadData, { headers });
      }
      setName("");
      setBrand("");
      setPrice("");
      setShelfId("");
      setEditingId(null);
      setShowForm(false);
      fetchProductsAndShelves();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to save product");
    }
  };

  const handleEdit = (product) => {
    setName(product.name);
    setBrand(product.brand);
    setPrice(product.price.toString());
    setShelfId(product.shelf_id.toString());
    setEditingId(product.id);
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this product?")) {
      return;
    }
    setError("");
    try {
      await api.delete(`/products/${id}`, { headers });
      fetchProductsAndShelves();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to delete product");
    }
  };

  const getShelfName = (id) => {
    const shelf = shelves.find((s) => s.id === id);
    return shelf ? shelf.name : `Shelf #${id}`;
  };

  if (loading && products.length === 0) {
    return <div className="loading-state">Loading product database...</div>;
  }

  return (
    <div className="products-container">
      {error && <div className="error-alert">{error}</div>}

      <div className="section-header">
        <h2>Inventoried Products ({products.length})</h2>
        {isAdmin && (
          <button 
            className="btn btn-primary"
            onClick={() => {
              setShowForm(!showForm);
              setEditingId(null);
              setName("");
              setBrand("");
              setPrice("");
              setShelfId(shelves[0]?.id?.toString() || "");
            }}
          >
            {showForm ? "Cancel" : "➕ Add Product"}
          </button>
        )}
      </div>

      {showForm && isAdmin && (
        <form className="form-card" onSubmit={handleSubmit}>
          <h3>{editingId ? "Edit Product Details" : "Register Product"}</h3>
          <div className="form-group">
            <label>Product Name</label>
            <input 
              type="text" 
              value={name} 
              onChange={(e) => setName(e.target.value)} 
              placeholder="e.g. Diet Coke 12oz"
              required 
            />
          </div>
          <div className="form-group">
            <label>Brand</label>
            <input 
              type="text" 
              value={brand} 
              onChange={(e) => setBrand(e.target.value)} 
              placeholder="e.g. Coca-Cola"
              required 
            />
          </div>
          <div className="form-group">
            <label>Price ($)</label>
            <input 
              type="number" 
              value={price} 
              onChange={(e) => setPrice(e.target.value)} 
              placeholder="e.g. 2"
              required 
            />
          </div>
          <div className="form-group">
            <label>Place on Shelf</label>
            <select 
              value={shelfId} 
              onChange={(e) => setShelfId(e.target.value)}
              required
            >
              <option value="">-- Select Shelf --</option>
              {shelves.map((shelf) => (
                <option key={shelf.id} value={shelf.id}>
                  {shelf.name}
                </option>
              ))}
            </select>
          </div>
          <button type="submit" className="btn btn-success">
            {editingId ? "Update Product" : "Save Product"}
          </button>
        </form>
      )}

      <div className="table-responsive">
        <table className="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Product Name</th>
              <th>Brand</th>
              <th>Price</th>
              <th>Shelf Location</th>
              {isAdmin && <th>Actions</th>}
            </tr>
          </thead>
          <tbody>
            {products.length === 0 ? (
              <tr>
                <td colSpan={isAdmin ? 6 : 5} className="text-center">No products inventoried yet.</td>
              </tr>
            ) : (
              products.map((product) => (
                <tr key={product.id}>
                  <td>{product.id}</td>
                  <td className="font-bold">{product.name}</td>
                  <td>{product.brand}</td>
                  <td>${product.price}</td>
                  <td>{getShelfName(product.shelf_id)}</td>
                  {isAdmin && (
                    <td>
                      <div className="actions-cell">
                        <button className="btn btn-sm btn-edit" onClick={() => handleEdit(product)}>✏️ Edit</button>
                        <button className="btn btn-sm btn-delete" onClick={() => handleDelete(product.id)}>🗑️ Delete</button>
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

export default Products;