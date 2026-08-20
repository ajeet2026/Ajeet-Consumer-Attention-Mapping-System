import React, { useState, useEffect } from 'react';
import api from '../api/axios';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { Doughnut } from 'react-chartjs-2';

ChartJS.register(ArcElement, Tooltip, Legend);

function BehaviorAnalytics() {
  const [segments, setSegments] = useState([]);
  const [journeyAnalytics, setJourneyAnalytics] = useState(null);
  const [preferences, setPreferences] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchBehaviorData = async () => {
      try {
        const [segRes, journeyRes, prefRes] = await Promise.all([
          api.get('/behavior/segments'),
          api.get('/behavior/journeys/analytics'),
          api.get('/behavior/preferences/leaderboard')
        ]);
        setSegments(segRes.data);
        setJourneyAnalytics(journeyRes.data);
        setPreferences(prefRes.data);
      } catch (err) {
        console.error("Failed to load behavior analytics", err);
      } finally {
        setLoading(false);
      }
    };
    fetchBehaviorData();
  }, []);

  const chartData = {
    labels: segments.map(s => s.segment),
    datasets: [
      {
        data: segments.map(s => s.percentage),
        backgroundColor: [
          '#3b82f6', // blue
          '#10b981', // light blue
          '#8b5cf6', // purple
          '#f59e0b', // yellow
          '#ef4444', // orange
          '#64748b', // slate
        ],
        borderWidth: 1,
      },
    ],
  };

  const formatTime = (seconds) => {
    if (!seconds) return "0s";
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return m > 0 ? `${m}m ${s}s` : `${s}s`;
  };

  const getZoneColor = (zone) => {
    switch (zone) {
      case 'Entrance': return { bg: 'rgba(34, 197, 94, 0.15)', text: '#4ade80', dot: '#22c55e' };
      case 'Checkout': return { bg: 'rgba(56, 189, 248, 0.15)', text: '#38bdf8', dot: '#0ea5e9' };
      case 'Shelf A': return { bg: 'rgba(239, 68, 68, 0.15)', text: '#f87171', dot: '#ef4444' };
      case 'Shelf B': return { bg: 'rgba(249, 115, 22, 0.15)', text: '#fb923c', dot: '#f97316' };
      default: return { bg: 'rgba(148, 163, 184, 0.15)', text: '#94a3b8', dot: '#64748b' };
    }
  };

  const renderRoutePills = (routeStr) => {
    const zones = routeStr.split(' → ');
    return (
      <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '6px' }}>
        {zones.map((z, i) => {
          const colors = getZoneColor(z);
          return (
            <React.Fragment key={i}>
              <span style={{ background: colors.bg, color: colors.text, padding: '3px 8px', borderRadius: '4px', fontSize: '0.7rem', fontWeight: '600', border: `1px solid ${colors.bg}` }}>
                {z}
              </span>
              {i < zones.length - 1 && <span style={{ color: '#475569', fontSize: '0.6rem' }}>▶</span>}
            </React.Fragment>
          );
        })}
      </div>
    );
  };

  const renderHeatNode = (zoneName, heatValue, maxShoppers) => {
    const colors = getZoneColor(zoneName);
    const intensity = maxShoppers > 0 ? heatValue / maxShoppers : 0;
    
    // Scale size from 12px to 24px based on intensity
    const size = 12 + (intensity * 12);
    // Glow based on intensity
    const glow = intensity > 0 ? `0 0 ${10 + (intensity * 15)}px ${colors.dot}` : 'none';

    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px' }}>
        <div style={{ 
          width: `${size}px`, 
          height: `${size}px`, 
          borderRadius: '50%', 
          backgroundColor: colors.dot, 
          boxShadow: glow,
          opacity: intensity > 0 ? 0.8 + (intensity * 0.2) : 0.3,
          transition: 'all 0.3s ease'
        }}></div>
        <span style={{ color: colors.text, fontWeight: '600', fontSize: '0.85rem' }}>{zoneName}</span>
        <span style={{ color: '#64748b', fontSize: '0.7rem' }}>
          {heatValue} visits
        </span>
      </div>
    );
  };

  if (loading) {
    return <div className="p-6">Loading Behavior Intelligence Engine...</div>;
  }

  return (
    <div className="dashboard-content" style={{ color: "#f8fafc" }}>
      <h2 style={{ fontSize: "1.4rem", margin: "0 0 20px 0", color: "#38bdf8" }}>
        🧠 Consumer Behavior Intelligence
      </h2>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "30px", marginBottom: "30px" }}>
        {/* Segment Chart */}
        <div className="login-card" style={{ width: "100%", padding: "20px", background: "rgba(15, 23, 42, 0.6)", borderRadius: "8px", border: "1px solid rgba(148, 163, 184, 0.1)" }}>
          <h3 style={{ fontSize: "1.1rem", marginBottom: "20px", color: "#f8fafc" }}>📊 Shopper Segmentation</h3>
          {segments.length === 0 ? (
            <p style={{ color: "#94a3b8", fontSize: "0.9rem" }}>No session data available yet. Start the camera tracking to generate behavior profiles.</p>
          ) : (
            <div style={{ width: "100%", maxWidth: "300px", margin: "0 auto" }}>
              <Doughnut data={chartData} options={{ color: '#94a3b8', plugins: { legend: { labels: { color: '#cbd5e1' } } } }} />
            </div>
          )}
        </div>

        {/* Product Preferences Leaderboard */}
        <div className="login-card" style={{ width: "100%", padding: "20px", background: "rgba(15, 23, 42, 0.6)", borderRadius: "8px", border: "1px solid rgba(148, 163, 184, 0.1)" }}>
          <h3 style={{ fontSize: "1.1rem", marginBottom: "20px", color: "#f8fafc" }}>🏆 Preferred Product Categories</h3>
          {preferences.length === 0 ? (
            <p style={{ color: "#94a3b8", fontSize: "0.9rem" }}>No preference data available.</p>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "15px" }}>
              {preferences.map((pref, idx) => (
                <div key={idx} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid #1e293b", paddingBottom: "10px" }}>
                  <span style={{ fontWeight: "500", color: "#cbd5e1" }}>
                    {idx === 0 ? "🥇 " : idx === 1 ? "🥈 " : idx === 2 ? "🥉 " : ""} 
                    {pref.category}
                  </span>
                  <span style={{ background: "rgba(56, 189, 248, 0.1)", color: "#38bdf8", fontSize: "0.75rem", fontWeight: "600", padding: "4px 8px", borderRadius: "4px" }}>
                    {pref.count} Sessions
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Customer Journey Analytics */}
      <div className="login-card" style={{ width: "100%", padding: "20px", background: "rgba(15, 23, 42, 0.6)", borderRadius: "8px", border: "1px solid rgba(148, 163, 184, 0.1)", marginBottom: "30px" }}>
        <h3 style={{ fontSize: "1.1rem", marginBottom: "15px", color: "#cbd5e1" }}>🗺️ Customer Journey Analytics</h3>
        
        {!journeyAnalytics || journeyAnalytics.total_shoppers === 0 ? (
          <p style={{ color: "#94a3b8", fontSize: "0.9rem" }}>No journey data available.</p>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: "25px" }}>
            
            {/* Top Metrics */}
            <div style={{ display: "flex", gap: "20px", borderBottom: "1px solid #1e293b", paddingBottom: "15px" }}>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: "0.8rem", color: "#94a3b8", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "4px" }}>Total Shoppers</div>
                <div style={{ fontSize: "1.6rem", fontWeight: "bold", color: "#f8fafc" }}>{journeyAnalytics.total_shoppers}</div>
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: "0.8rem", color: "#94a3b8", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "4px" }}>Avg Journey Time</div>
                <div style={{ fontSize: "1.6rem", fontWeight: "bold", color: "#f8fafc" }}>{formatTime(journeyAnalytics.avg_journey_time)}</div>
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: "0.8rem", color: "#94a3b8", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "4px" }}>Avg Path Length</div>
                <div style={{ fontSize: "1.6rem", fontWeight: "bold", color: "#f8fafc" }}>{journeyAnalytics.avg_path_length} <span style={{fontSize: "1rem", color: "#64748b"}}>zones</span></div>
              </div>
            </div>
            
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "30px" }}>
              {/* Store Movement Map */}
              <div style={{ background: "rgba(30, 41, 59, 0.4)", padding: "20px", borderRadius: "8px", border: "1px solid #334155" }}>
                <h4 style={{ fontSize: "0.95rem", color: "#94a3b8", marginBottom: "25px", textTransform: "uppercase", letterSpacing: "0.05em" }}>Store Movement Map</h4>
                
                <div style={{ position: "relative", padding: "30px 20px", border: "1px dashed #475569", borderRadius: "8px", minHeight: "200px", display: "flex", flexDirection: "column", justifyContent: "space-between", background: "rgba(15, 23, 42, 0.4)" }}>
                  <div style={{ display: "flex", justifyContent: "center", marginBottom: "20px" }}>
                    {renderHeatNode("Shelf A", journeyAnalytics.zone_heat["Shelf A"] || 0, journeyAnalytics.total_shoppers)}
                  </div>
                  
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", margin: "10px 0" }}>
                    {renderHeatNode("Entrance", journeyAnalytics.zone_heat["Entrance"] || 0, journeyAnalytics.total_shoppers)}
                    <div style={{ flex: 1, height: "2px", background: "linear-gradient(90deg, rgba(71,85,105,0.5) 0%, rgba(148,163,184,0.5) 100%)", margin: "0 20px", position: "relative", top: "-10px" }}>
                      <div style={{ position: "absolute", right: "-5px", top: "-5px", color: "#94a3b8", fontSize: "12px" }}>▶</div>
                    </div>
                    {renderHeatNode("Checkout", journeyAnalytics.zone_heat["Checkout"] || 0, journeyAnalytics.total_shoppers)}
                  </div>
                  
                  <div style={{ display: "flex", justifyContent: "center", marginTop: "20px" }}>
                    {renderHeatNode("Shelf B", journeyAnalytics.zone_heat["Shelf B"] || 0, journeyAnalytics.total_shoppers)}
                  </div>
                </div>
              </div>
              
              {/* Lists Container */}
              <div style={{ display: "flex", flexDirection: "column", gap: "30px" }}>
                {/* Top Routes */}
                <div>
                  <h4 style={{ fontSize: "0.95rem", color: "#94a3b8", marginBottom: "15px", textTransform: "uppercase", letterSpacing: "0.05em" }}>Top Customer Routes</h4>
                  <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                    {journeyAnalytics.top_routes.map((route, idx) => (
                      <div key={idx} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", background: "rgba(30, 41, 59, 0.4)", padding: "10px", borderRadius: "6px", border: "1px solid #334155" }}>
                        <div style={{ flex: 1 }}>{renderRoutePills(route.route)}</div>
                        <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", minWidth: "60px" }}>
                          <span style={{ color: "#f8fafc", fontWeight: "bold", fontSize: "0.9rem" }}>{route.count}</span>
                          <span style={{ color: "#64748b", fontSize: "0.7rem" }}>{route.percentage}%</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                
                {/* Zone Transitions */}
                <div>
                  <h4 style={{ fontSize: "0.95rem", color: "#94a3b8", marginBottom: "15px", textTransform: "uppercase", letterSpacing: "0.05em" }}>Zone Transitions</h4>
                  <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                    {journeyAnalytics.zone_transitions.map((trans, idx) => (
                      <div key={idx} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid #1e293b", paddingBottom: "8px" }}>
                        <div>{renderRoutePills(trans.transition)}</div>
                        <span style={{ color: "#38bdf8", fontWeight: "bold", fontSize: "0.9rem", background: "rgba(56, 189, 248, 0.1)", padding: "2px 8px", borderRadius: "12px" }}>{trans.count}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
              
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default BehaviorAnalytics;
