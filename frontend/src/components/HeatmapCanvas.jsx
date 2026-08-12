import { useEffect, useRef } from "react";

function HeatmapCanvas({ points = [], width = 640, height = 480 }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Draw heatmap points with radial gradient densities
    points.forEach((p) => {
      // Map normalized layout coordinates if necessary, assuming already matched to 640x480 canvas size
      const { x, y, value = 1 } = p;
      const radius = 30 * value;

      const gradient = ctx.createRadialGradient(x, y, 2, x, y, radius);
      gradient.addColorStop(0, "rgba(239, 68, 68, 0.65)");  // Hot red core
      gradient.addColorStop(0.2, "rgba(249, 115, 22, 0.4)"); // Orange mid-ring
      gradient.addColorStop(0.6, "rgba(234, 179, 8, 0.15)"); // Yellow outer glow
      gradient.addColorStop(1, "rgba(34, 197, 94, 0)");     // Fade to transparent

      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(x, y, radius, 0, 2 * Math.PI);
      ctx.fill();
    });
  }, [points, width, height]);

  return (
    <canvas
      ref={canvasRef}
      width={width}
      height={height}
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        pointerEvents: "none", // Allows mouse clicks to pass through to elements beneath
        zIndex: 10,
        borderRadius: "8px",
      }}
    />
  );
}

export default HeatmapCanvas;
