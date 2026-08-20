import React, { useState } from 'react';

const ShopperPathVisualizer = ({ sessionData, width = 640, height = 480 }) => {
  const [hoveredPoint, setHoveredPoint] = useState(null);

  if (!sessionData || !sessionData.path || sessionData.path.length === 0) {
    return (
      <div style={{
        width: '100%', height: '100%', minHeight: '300px',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        background: '#0f172a', color: '#64748b', borderRadius: '8px',
        border: '1px solid #1e293b'
      }}>
        No tracking path data available for this session.
      </div>
    );
  }

  const { path, zones } = sessionData;
  const startPoint = path[0];
  const endPoint = path[path.length - 1];

  // Map zone events to points on the path (closest by time)
  // Since we don't store exactly which (x,y) corresponds to the zone entry,
  // we estimate it by matching timestamps.
  const getPointForZone = (zone) => {
    const zoneTime = new Date(zone.entry_time).getTime();
    let closest = path[0];
    let minDiff = Infinity;
    
    path.forEach(p => {
      const pTime = new Date(p.timestamp).getTime();
      const diff = Math.abs(pTime - zoneTime);
      if (diff < minDiff) {
        minDiff = diff;
        closest = p;
      }
    });
    return closest;
  };

  const zoneMarkers = zones ? zones.map(z => ({
    ...z,
    point: getPointForZone(z)
  })) : [];

  // Create SVG path string
  const polylinePoints = path.map(p => `${p.x},${p.y}`).join(' ');

  const formatTime = (ts) => {
    return new Date(ts).toLocaleTimeString([], { hour12: false, hour: '2-digit', minute:'2-digit', second:'2-digit' });
  };

  return (
    <div style={{ position: 'relative', width: '100%', maxWidth: '800px', margin: '0 auto' }}>
      
      {/* Background Container (Floor Plan / Camera view) */}
      <div style={{
        position: 'relative',
        width: '100%',
        paddingBottom: `${(height / width) * 100}%`, // Maintain aspect ratio
        background: '#0f172a', // Dark slate
        backgroundImage: `
          linear-gradient(rgba(56, 189, 248, 0.05) 1px, transparent 1px),
          linear-gradient(90deg, rgba(56, 189, 248, 0.05) 1px, transparent 1px)
        `,
        backgroundSize: '40px 40px',
        borderRadius: '8px',
        border: '1px solid #1e293b',
        overflow: 'hidden',
        boxShadow: 'inset 0 0 20px rgba(0,0,0,0.5)'
      }}>
        
        {/* SVG Overlay */}
        <svg 
          viewBox={`0 0 ${width} ${height}`}
          style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%' }}
        >
          {/* Main Path Line */}
          <polyline 
            points={polylinePoints} 
            fill="none" 
            stroke="#38bdf8" 
            strokeWidth="3" 
            strokeDasharray="8 4"
            opacity="0.8"
            style={{ animation: 'dash 20s linear infinite' }}
          />

          <style>
            {`
              @keyframes dash {
                to { stroke-dashoffset: -1000; }
              }
              @keyframes pulse {
                0% { transform: scale(1); opacity: 1; }
                50% { transform: scale(1.5); opacity: 0.5; }
                100% { transform: scale(1); opacity: 1; }
              }
            `}
          </style>

          {/* Interactive path nodes (hidden until hover) */}
          {path.map((p, i) => {
            // Don't render nodes for every single point if there are hundreds, to save DOM nodes.
            // Just render every 5th point or so for interaction, unless it's start/end.
            if (i % 5 !== 0 && i !== 0 && i !== path.length - 1) return null;
            
            return (
              <circle 
                key={`p-${i}`}
                cx={p.x} 
                cy={p.y} 
                r="6" 
                fill="transparent"
                onMouseEnter={() => setHoveredPoint({ x: p.x, y: p.y, label: `Time: ${formatTime(p.timestamp)}` })}
                onMouseLeave={() => setHoveredPoint(null)}
                style={{ cursor: 'pointer' }}
              />
            );
          })}

          {/* Start Marker */}
          <g transform={`translate(${startPoint.x}, ${startPoint.y})`}>
            <circle cx="0" cy="0" r="8" fill="#22c55e" />
            <circle cx="0" cy="0" r="14" fill="none" stroke="#22c55e" strokeWidth="2" style={{ animation: 'pulse 2s infinite' }} />
            <text x="12" y="4" fill="#22c55e" fontSize="12" fontWeight="bold" style={{ textShadow: '0 2px 4px rgba(0,0,0,0.8)' }}>START</text>
          </g>

          {/* End Marker */}
          <g transform={`translate(${endPoint.x}, ${endPoint.y})`}>
            <circle cx="0" cy="0" r="8" fill="#ef4444" />
            <circle cx="0" cy="0" r="14" fill="none" stroke="#ef4444" strokeWidth="2" style={{ animation: 'pulse 2s infinite' }} />
            <text x="12" y="4" fill="#ef4444" fontSize="12" fontWeight="bold" style={{ textShadow: '0 2px 4px rgba(0,0,0,0.8)' }}>END</text>
          </g>

          {/* Zone Markers */}
          {zoneMarkers.map((zm, idx) => (
            <g 
              key={`z-${idx}`} 
              transform={`translate(${zm.point.x}, ${zm.point.y})`}
              onMouseEnter={() => setHoveredPoint({ 
                x: zm.point.x, 
                y: zm.point.y, 
                label: `Zone: ${zm.zone_id}\\nIn: ${formatTime(zm.entry_time)}\\nDur: ${zm.duration ? zm.duration.toFixed(1)+'s' : 'Active'}` 
              })}
              onMouseLeave={() => setHoveredPoint(null)}
              style={{ cursor: 'help' }}
            >
              <rect x="-6" y="-6" width="12" height="12" fill="#f59e0b" rx="2" />
              <text x="10" y="4" fill="#f59e0b" fontSize="10" fontWeight="bold" style={{ textShadow: '0 2px 4px rgba(0,0,0,0.8)' }}>{zm.zone_id}</text>
            </g>
          ))}

        </svg>

        {/* Tooltip Overlay (HTML) */}
        {hoveredPoint && (
          <div style={{
            position: 'absolute',
            left: `${(hoveredPoint.x / width) * 100}%`,
            top: `${(hoveredPoint.y / height) * 100}%`,
            transform: 'translate(-50%, -120%)',
            background: 'rgba(15, 23, 42, 0.9)',
            border: '1px solid #38bdf8',
            padding: '8px 12px',
            borderRadius: '6px',
            color: '#e2e8f0',
            fontSize: '0.8rem',
            whiteSpace: 'pre-line',
            pointerEvents: 'none',
            zIndex: 10,
            boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
            backdropFilter: 'blur(4px)'
          }}>
            {hoveredPoint.label}
          </div>
        )}

      </div>

      <div style={{ marginTop: '12px', display: 'flex', gap: '16px', fontSize: '0.85rem', color: '#94a3b8', justifyContent: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><span style={{ display: 'inline-block', width: '12px', height: '12px', borderRadius: '50%', background: '#22c55e' }}></span> Start</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><span style={{ display: 'inline-block', width: '12px', height: '12px', borderRadius: '50%', background: '#ef4444' }}></span> End</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><span style={{ display: 'inline-block', width: '12px', height: '12px', borderRadius: '2px', background: '#f59e0b' }}></span> Zone Event</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><span style={{ display: 'inline-block', width: '20px', height: '2px', borderBottom: '2px dashed #38bdf8' }}></span> Path</div>
      </div>
    </div>
  );
};

export default ShopperPathVisualizer;
