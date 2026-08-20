import React, { useState, useEffect } from 'react';

function ProductHeatmap({ scores }) {
  const [selectedShelf, setSelectedShelf] = useState("Shelf A");
  const [shelves, setShelves] = useState([]);

  useEffect(() => {
    if (scores && scores.length > 0) {
      const uniqueShelves = [...new Set(scores.map(s => s.shelf).filter(s => s !== "Unknown"))];
      setShelves(uniqueShelves);
      if (uniqueShelves.length > 0 && !uniqueShelves.includes(selectedShelf)) {
        setSelectedShelf(uniqueShelves[0]);
      }
    }
  }, [scores]);

  // Filter products for the selected shelf
  const shelfProducts = scores.filter(s => s.shelf === selectedShelf);

  // Helper to determine color based on attention score
  const getHeatmapColor = (score) => {
    if (score >= 80) return "rgba(239, 68, 68, 0.9)"; // Hot (Red)
    if (score >= 60) return "rgba(249, 115, 22, 0.8)"; // Warm (Orange)
    if (score >= 40) return "rgba(234, 179, 8, 0.8)";  // Mild (Yellow)
    if (score >= 20) return "rgba(56, 189, 248, 0.7)"; // Cool (Light Blue)
    return "rgba(59, 130, 246, 0.5)";                 // Cold (Blue)
  };

  if (!scores || scores.length === 0) return null;

  return (
    <div style={{ marginTop: "40px", marginBottom: "40px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "15px" }}>
        <h3 style={{ fontSize: "1.1rem", margin: 0, color: "#cbd5e1" }}>🌡️ Product Attention Heatmap</h3>
        <select 
          value={selectedShelf} 
          onChange={(e) => setSelectedShelf(e.target.value)}
          style={{ 
            background: "#1e293b", 
            color: "#f8fafc", 
            border: "1px solid #334155", 
            padding: "6px 12px", 
            borderRadius: "4px" 
          }}
        >
          {shelves.map(shelf => (
            <option key={shelf} value={shelf}>{shelf}</option>
          ))}
        </select>
      </div>

      <div style={{ 
        background: "rgba(15, 23, 42, 0.6)", 
        border: "1px solid rgba(148, 163, 184, 0.1)", 
        borderRadius: "8px", 
        padding: "30px",
        display: "flex",
        flexDirection: "column",
        alignItems: "center"
      }}>
        
        {/* The Physical Shelf Representation */}
        <div style={{
          width: "100%",
          maxWidth: "800px",
          background: "#1e293b",
          border: "4px solid #0f172a",
          borderBottom: "12px solid #0f172a",
          borderRadius: "8px",
          padding: "20px",
          position: "relative",
          boxShadow: "0 10px 25px rgba(0,0,0,0.5)"
        }}>
          {shelfProducts.length === 0 ? (
            <p style={{ textAlign: "center", color: "#64748b" }}>No products assigned to this shelf yet.</p>
          ) : (
            <div style={{ 
              display: "grid", 
              gridTemplateColumns: "repeat(auto-fill, minmax(140px, 1fr))", 
              gap: "20px",
              justifyContent: "center"
            }}>
              {shelfProducts.map((product) => {
                const heatColor = getHeatmapColor(product.scores.attention_score);
                
                return (
                  <div key={product.product_id} style={{
                    position: "relative",
                    background: "rgba(30, 41, 59, 0.8)",
                    border: `2px solid ${heatColor}`,
                    borderRadius: "6px",
                    padding: "15px 10px",
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    justifyContent: "center",
                    boxShadow: `0 0 15px ${heatColor}`,
                    transition: "transform 0.2s",
                    cursor: "default"
                  }}>
                    {/* Fire Icon for hot products */}
                    {product.scores.attention_score >= 80 && (
                      <span style={{ position: "absolute", top: "-10px", right: "-10px", fontSize: "1.2rem" }}>🔥</span>
                    )}
                    
                    <span style={{ fontWeight: "bold", color: "#f8fafc", textAlign: "center", marginBottom: "5px" }}>
                      {product.product_name}
                    </span>
                    <span style={{ fontSize: "0.7rem", color: "#94a3b8", textAlign: "center", marginBottom: "10px" }}>
                      {product.brand}
                    </span>
                    
                    <div style={{ 
                      background: "rgba(0,0,0,0.5)", 
                      padding: "4px 8px", 
                      borderRadius: "12px",
                      fontSize: "0.75rem",
                      fontWeight: "bold",
                      color: "#fff"
                    }}>
                      Attn: {product.scores.attention_score.toFixed(0)}%
                    </div>
                  </div>
                );
              })}
            </div>
          )}
          
          {/* Legend */}
          <div style={{ 
            marginTop: "40px", 
            borderTop: "1px dashed #334155", 
            paddingTop: "15px",
            display: "flex",
            justifyContent: "center",
            gap: "15px",
            fontSize: "0.75rem",
            color: "#94a3b8"
          }}>
            <span>Legend:</span>
            <span style={{ display: "flex", alignItems: "center", gap: "5px" }}><div style={{width: "12px", height: "12px", background: "rgba(239, 68, 68, 0.9)", borderRadius: "2px"}}></div> High Attention (80-100)</span>
            <span style={{ display: "flex", alignItems: "center", gap: "5px" }}><div style={{width: "12px", height: "12px", background: "rgba(249, 115, 22, 0.8)", borderRadius: "2px"}}></div> Warm (60-79)</span>
            <span style={{ display: "flex", alignItems: "center", gap: "5px" }}><div style={{width: "12px", height: "12px", background: "rgba(234, 179, 8, 0.8)", borderRadius: "2px"}}></div> Mild (40-59)</span>
            <span style={{ display: "flex", alignItems: "center", gap: "5px" }}><div style={{width: "12px", height: "12px", background: "rgba(59, 130, 246, 0.5)", borderRadius: "2px"}}></div> Cold (0-39)</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ProductHeatmap;
