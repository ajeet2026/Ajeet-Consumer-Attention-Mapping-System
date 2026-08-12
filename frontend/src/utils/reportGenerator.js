import jsPDF from "jspdf";
import { applyPlugin } from "jspdf-autotable";
applyPlugin(jsPDF);


/**
 * Generate a beautiful, professional PDF analytics report
 * for the RetailEye AI Consumer Attention Mapping platform.
 */
export function generateAdminReport({ liveStats, coreStats, recentSessions, dwellStats, zoneStats }) {
  const doc = new jsPDF("p", "mm", "a4");
  const pageWidth = doc.internal.pageSize.getWidth();
  const pageHeight = doc.internal.pageSize.getHeight();
  const margin = 18;
  const contentWidth = pageWidth - margin * 2;
  let y = 0;

  const now = new Date();
  const dateStr = now.toLocaleDateString("en-US", { weekday: "long", year: "numeric", month: "long", day: "numeric" });
  const timeStr = now.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" });

  // ─── Color Palette ───
  const colors = {
    navy:      [15, 23, 42],
    darkSlate: [30, 41, 59],
    slate:     [51, 65, 85],
    muted:     [148, 163, 184],
    light:     [226, 232, 240],
    white:     [255, 255, 255],
    cyan:      [56, 189, 248],
    green:     [34, 197, 94],
    amber:     [234, 179, 8],
    orange:    [249, 115, 22],
    red:       [239, 68, 68],
    indigo:    [99, 102, 241],
    gradient1: [15, 23, 42],
    gradient2: [30, 58, 95],
  };

  // ═══════════════════════════════════════════════════
  // HELPER FUNCTIONS
  // ═══════════════════════════════════════════════════

  function drawGradientRect(x, yPos, w, h, c1, c2, steps = 40) {
    const stepH = h / steps;
    for (let i = 0; i < steps; i++) {
      const r = c1[0] + (c2[0] - c1[0]) * (i / steps);
      const g = c1[1] + (c2[1] - c1[1]) * (i / steps);
      const b = c1[2] + (c2[2] - c1[2]) * (i / steps);
      doc.setFillColor(r, g, b);
      doc.rect(x, yPos + i * stepH, w, stepH + 0.5, "F");
    }
  }

  function drawRoundedRect(x, yPos, w, h, r, fillColor, borderColor) {
    if (fillColor) {
      doc.setFillColor(...fillColor);
    }
    if (borderColor) {
      doc.setDrawColor(...borderColor);
      doc.setLineWidth(0.3);
      doc.roundedRect(x, yPos, w, h, r, r, fillColor ? "FD" : "D");
    } else if (fillColor) {
      doc.roundedRect(x, yPos, w, h, r, r, "F");
    }
  }

  function addPageFooter(pageNum) {
    doc.setFontSize(8);
    doc.setTextColor(...colors.muted);
    doc.text(`RetailEye AI  •  Consumer Attention Analytics Report  •  Generated ${dateStr}`, margin, pageHeight - 8);
    doc.text(`Page ${pageNum}`, pageWidth - margin, pageHeight - 8, { align: "right" });
    // Top accent line
    doc.setDrawColor(...colors.cyan);
    doc.setLineWidth(0.6);
    doc.line(0, 0, pageWidth, 0);
  }

  function checkPageBreak(needed) {
    if (y + needed > pageHeight - 20) {
      addPageFooter(doc.internal.getNumberOfPages());
      doc.addPage();
      y = 18;
      return true;
    }
    return false;
  }

  function sectionHeader(title, icon) {
    checkPageBreak(20);
    // Accent bar
    doc.setFillColor(...colors.cyan);
    doc.rect(margin, y, 3, 9, "F");
    doc.setFontSize(13);
    doc.setFont("helvetica", "bold");
    doc.setTextColor(...colors.navy);
    doc.text(`${icon}  ${title}`, margin + 6, y + 7);
    y += 14;
    // Thin separator
    doc.setDrawColor(...colors.light);
    doc.setLineWidth(0.2);
    doc.line(margin, y, pageWidth - margin, y);
    y += 5;
  }

  // ═══════════════════════════════════════════════════
  // PAGE 1: COVER / HEADER
  // ═══════════════════════════════════════════════════

  // Dark header banner
  drawGradientRect(0, 0, pageWidth, 70, colors.navy, colors.gradient2);

  // Accent line at top
  doc.setFillColor(...colors.cyan);
  doc.rect(0, 0, pageWidth, 1.5, "F");

  // Logo text
  doc.setFontSize(28);
  doc.setFont("helvetica", "bold");
  doc.setTextColor(...colors.white);
  doc.text("RetailEye AI", margin, 28);

  // Subtitle
  doc.setFontSize(11);
  doc.setFont("helvetica", "normal");
  doc.setTextColor(...colors.cyan);
  doc.text("CONSUMER ATTENTION MAPPING", margin, 37);

  // Report title
  doc.setFontSize(16);
  doc.setFont("helvetica", "bold");
  doc.setTextColor(...colors.white);
  doc.text("Admin Analytics Report", margin, 52);

  // Date/time
  doc.setFontSize(9);
  doc.setFont("helvetica", "normal");
  doc.setTextColor(...colors.muted);
  doc.text(`${dateStr}  |  ${timeStr}`, margin, 62);

  // Decorative badge on right
  drawRoundedRect(pageWidth - 60, 20, 45, 16, 3, colors.cyan, null);
  doc.setFontSize(8);
  doc.setFont("helvetica", "bold");
  doc.setTextColor(...colors.navy);
  doc.text("LIVE REPORT", pageWidth - 37.5, 30, { align: "center" });

  y = 82;

  // ═══════════════════════════════════════════════════
  // SECTION 1: EXECUTIVE SUMMARY (KPI Cards)
  // ═══════════════════════════════════════════════════

  sectionHeader("Executive Summary", "📊");

  const kpiCards = [
    { label: "Active Shoppers", value: liveStats.active_shoppers, color: colors.cyan },
    { label: "Today's Visitors", value: liveStats.today_visitors, color: colors.green },
    { label: "Avg Dwell Time", value: `${liveStats.average_dwell_time}s`, color: colors.amber },
    { label: "Attention Events", value: liveStats.attention_events_count, color: colors.orange },
  ];

  const cardW = (contentWidth - 9) / 4;
  kpiCards.forEach((card, i) => {
    const cx = margin + i * (cardW + 3);
    // Card background
    drawRoundedRect(cx, y, cardW, 28, 3, [245, 248, 255], card.color);
    // Value
    doc.setFontSize(18);
    doc.setFont("helvetica", "bold");
    doc.setTextColor(...card.color);
    doc.text(String(card.value), cx + cardW / 2, y + 14, { align: "center" });
    // Label
    doc.setFontSize(7);
    doc.setFont("helvetica", "normal");
    doc.setTextColor(...colors.slate);
    doc.text(card.label, cx + cardW / 2, y + 22, { align: "center" });
  });

  y += 38;

  // ═══════════════════════════════════════════════════
  // SECTION 2: INFRASTRUCTURE OVERVIEW
  // ═══════════════════════════════════════════════════

  sectionHeader("Infrastructure Overview", "🏪");

  const infraCards = [
    { label: "Stores", value: coreStats.stores, color: colors.indigo },
    { label: "Shelves", value: coreStats.shelves, color: colors.cyan },
    { label: "Cameras", value: coreStats.cameras, color: colors.green },
    { label: "Products", value: coreStats.products, color: colors.amber },
  ];

  infraCards.forEach((card, i) => {
    const cx = margin + i * (cardW + 3);
    drawRoundedRect(cx, y, cardW, 24, 3, [240, 245, 255], card.color);
    doc.setFontSize(16);
    doc.setFont("helvetica", "bold");
    doc.setTextColor(...card.color);
    doc.text(String(card.value), cx + cardW / 2, y + 12, { align: "center" });
    doc.setFontSize(7);
    doc.setFont("helvetica", "normal");
    doc.setTextColor(...colors.slate);
    doc.text(card.label, cx + cardW / 2, y + 19, { align: "center" });
  });

  y += 34;

  // ═══════════════════════════════════════════════════
  // SECTION 3: SHELF ATTENTION ANALYSIS (Bar Chart)
  // ═══════════════════════════════════════════════════

  sectionHeader("Shelf Attention Analysis", "📈");

  if (dwellStats.length === 0) {
    doc.setFontSize(9);
    doc.setTextColor(...colors.muted);
    doc.text("No shelf dwell data recorded yet.", margin, y);
    y += 10;
  } else {
    const totalDwell = dwellStats.reduce((a, c) => a + c.total_dwell_time, 0) || 1;
    const barColors = [colors.cyan, colors.green, colors.amber, colors.orange, colors.indigo, colors.red];

    dwellStats.forEach((item, i) => {
      checkPageBreak(14);
      const pct = Math.round((item.total_dwell_time / totalDwell) * 100);
      const barW = (contentWidth - 50) * (pct / 100);
      const color = barColors[i % barColors.length];

      // Label
      doc.setFontSize(8);
      doc.setFont("helvetica", "bold");
      doc.setTextColor(...colors.navy);
      doc.text(`Shelf #${item.shelf_id}`, margin, y + 5);

      // Bar background
      doc.setFillColor(230, 235, 245);
      doc.roundedRect(margin + 30, y, contentWidth - 50, 7, 2, 2, "F");
      // Bar fill
      if (barW > 0) {
        doc.setFillColor(...color);
        doc.roundedRect(margin + 30, y, Math.max(barW, 4), 7, 2, 2, "F");
      }

      // Percentage
      doc.setFontSize(8);
      doc.setFont("helvetica", "bold");
      doc.setTextColor(...colors.navy);
      doc.text(`${pct}%  (${Math.round(item.total_dwell_time)}s)`, margin + 30 + contentWidth - 48, y + 5, { align: "right" });

      y += 12;
    });
    y += 4;
  }

  // ═══════════════════════════════════════════════════
  // SECTION 4: ZONE TRAFFIC DISTRIBUTION
  // ═══════════════════════════════════════════════════

  sectionHeader("Zone Traffic Distribution", "🗺️");

  if (zoneStats.length === 0) {
    doc.setFontSize(9);
    doc.setTextColor(...colors.muted);
    doc.text("No zone traffic data recorded yet.", margin, y);
    y += 10;
  } else {
    // Zone table
    const zoneTableBody = zoneStats.map((z) => {
      const totalVisits = zoneStats.reduce((a, c) => a + c.visit_count, 0) || 1;
      const pct = Math.round((z.visit_count / totalVisits) * 100);
      return [z.zone_id, String(z.visit_count), `${z.average_duration}s`, `${pct}%`];
    });

    doc.autoTable({
      startY: y,
      head: [["Zone", "Visits", "Avg Duration", "Traffic Share"]],
      body: zoneTableBody,
      margin: { left: margin, right: margin },
      styles: {
        fontSize: 8,
        cellPadding: 4,
        lineColor: [226, 232, 240],
        lineWidth: 0.2,
      },
      headStyles: {
        fillColor: colors.navy,
        textColor: colors.white,
        fontStyle: "bold",
        fontSize: 8,
      },
      alternateRowStyles: {
        fillColor: [245, 248, 255],
      },
      columnStyles: {
        0: { fontStyle: "bold", textColor: colors.navy },
        3: { textColor: colors.orange, fontStyle: "bold" },
      },
    });
    y = doc.lastAutoTable.finalY + 10;
  }

  // ═══════════════════════════════════════════════════
  // SECTION 5: RECENT CONSUMER SESSIONS TABLE
  // ═══════════════════════════════════════════════════

  checkPageBreak(30);
  sectionHeader("Recent Consumer Sessions", "📋");

  if (recentSessions.length === 0) {
    doc.setFontSize(9);
    doc.setTextColor(...colors.muted);
    doc.text("No tracking sessions captured yet.", margin, y);
    y += 10;
  } else {
    const sessionBody = recentSessions.map((s) => [
      `#${s.id}`,
      `ID_${s.tracking_id}`,
      `Camera ${s.camera_id}`,
      new Date(s.entry_time).toLocaleTimeString(),
      s.exit_time ? new Date(s.exit_time).toLocaleTimeString() : "Active",
      s.duration ? `${Math.round(s.duration)}s` : "-",
      s.exit_time ? "COMPLETED" : "IN PROGRESS",
    ]);

    doc.autoTable({
      startY: y,
      head: [["Session", "Track ID", "Camera", "Entry", "Exit", "Duration", "Status"]],
      body: sessionBody,
      margin: { left: margin, right: margin },
      styles: {
        fontSize: 7,
        cellPadding: 3,
        lineColor: [226, 232, 240],
        lineWidth: 0.2,
      },
      headStyles: {
        fillColor: colors.navy,
        textColor: colors.white,
        fontStyle: "bold",
        fontSize: 7.5,
      },
      alternateRowStyles: {
        fillColor: [245, 248, 255],
      },
      columnStyles: {
        1: { textColor: colors.cyan, fontStyle: "bold" },
        6: { fontStyle: "bold" },
      },
      didParseCell: (data) => {
        if (data.section === "body" && data.column.index === 6) {
          if (data.cell.raw === "COMPLETED") {
            data.cell.styles.textColor = colors.green;
          } else {
            data.cell.styles.textColor = colors.amber;
          }
        }
      },
    });
    y = doc.lastAutoTable.finalY + 10;
  }

  // ═══════════════════════════════════════════════════
  // SECTION 6: INSIGHTS & RECOMMENDATIONS
  // ═══════════════════════════════════════════════════

  checkPageBreak(55);
  sectionHeader("AI Insights & Recommendations", "🧠");

  const insights = [];

  // Generate dynamic insights based on data
  if (liveStats.active_shoppers > 0) {
    insights.push({
      type: "info",
      text: `There are currently ${liveStats.active_shoppers} active shoppers being tracked in real-time across all camera feeds.`
    });
  }

  if (liveStats.average_dwell_time > 30) {
    insights.push({
      type: "success",
      text: `Average dwell time of ${liveStats.average_dwell_time}s is above the 30s engagement threshold — strong customer engagement detected.`
    });
  } else if (liveStats.average_dwell_time > 0) {
    insights.push({
      type: "warning",
      text: `Average dwell time of ${liveStats.average_dwell_time}s is below the 30s engagement threshold. Consider improving product placement or signage.`
    });
  }

  if (dwellStats.length > 0) {
    const topShelf = dwellStats.reduce((max, item) => item.total_dwell_time > max.total_dwell_time ? item : max, dwellStats[0]);
    insights.push({
      type: "info",
      text: `Shelf #${topShelf.shelf_id} receives the highest attention with ${Math.round(topShelf.total_dwell_time)}s total dwell time. Consider placing premium products there.`
    });
  }

  if (zoneStats.length > 0) {
    const hotZone = zoneStats.reduce((max, z) => z.visit_count > max.visit_count ? z : max, zoneStats[0]);
    insights.push({
      type: "success",
      text: `The "${hotZone.zone_id}" zone is the busiest with ${hotZone.visit_count} visits. Maximize promotional placement in this area.`
    });
  }

  insights.push({
    type: "info",
    text: `System is currently monitoring ${coreStats.stores} store(s) with ${coreStats.cameras} camera(s) covering ${coreStats.shelves} shelf zones and ${coreStats.products} tracked products.`
  });

  const insightColors = {
    info: colors.cyan,
    success: colors.green,
    warning: colors.amber,
  };
  const insightIcons = {
    info: "ℹ",
    success: "✓",
    warning: "⚠",
  };

  insights.forEach((insight) => {
    checkPageBreak(16);
    const color = insightColors[insight.type] || colors.cyan;
    // Accent bar
    doc.setFillColor(...color);
    doc.rect(margin, y, 2, 10, "F");
    // Background
    drawRoundedRect(margin + 3, y, contentWidth - 3, 10, 2, [245, 248, 255], null);
    // Text
    doc.setFontSize(8);
    doc.setFont("helvetica", "normal");
    doc.setTextColor(...colors.navy);
    const lines = doc.splitTextToSize(`${insightIcons[insight.type]}  ${insight.text}`, contentWidth - 12);
    const lineHeight = lines.length * 4;
    // Resize rect if needed
    if (lineHeight > 10) {
      drawRoundedRect(margin + 3, y, contentWidth - 3, lineHeight + 4, 2, [245, 248, 255], null);
      doc.setFillColor(...color);
      doc.rect(margin, y, 2, lineHeight + 4, "F");
    }
    doc.text(lines, margin + 7, y + 5);
    y += Math.max(lineHeight + 4, 10) + 4;
  });

  // ═══════════════════════════════════════════════════
  // FOOTER ON ALL PAGES
  // ═══════════════════════════════════════════════════

  const totalPages = doc.internal.getNumberOfPages();
  for (let i = 1; i <= totalPages; i++) {
    doc.setPage(i);
    addPageFooter(i);
  }

  // ═══════════════════════════════════════════════════
  // SAVE
  // ═══════════════════════════════════════════════════

  const filename = `RetailEye_Report_${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")}_${String(now.getHours()).padStart(2, "0")}${String(now.getMinutes()).padStart(2, "0")}.pdf`;
  doc.save(filename);
}
