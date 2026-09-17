import { jsPDF } from 'jspdf';
import fs from 'fs';
import path from 'path';

// ── Constants ─────────────────────────────────────────────────────────────────
const PAGE_WIDTH = 338.67;  // 13.333 inches in mm (16:9)
const PAGE_HEIGHT = 190.50; // 7.500 inches in mm
const CONTENT_HEIGHT = 145; // Height for the main slide content
const NOTES_Y = 150;        // Y position where speaker notes start

// Light Theme Colors
const C_BG      = [255, 255, 255]; // White background
const C_TEXT    = [31, 41, 55];    // Dark Gray main text (#1F2937)
const C_SUBTEXT = [75, 85, 99];    // Medium Gray text (#4B5563)
const C_ACCENT  = [2, 132, 199];   // Corporate Blue (#0284C7)
const C_CARD    = [248, 250, 252]; // Very Light Gray (#F8FAFC)
const C_BORDER  = [226, 232, 240]; // Light Gray Border (#E2E8F0)
const C_NOTES_BG = [254, 252, 232]; // Light Yellow for notes (#FEFCE8)
const C_NOTES_TXT = [113, 63, 18];  // Dark Brown for notes text (#713F12)

const C_GREEN  = [16, 185, 129];
const C_ORANGE = [249, 115, 22];
const C_PURPLE = [139, 92, 246];

// Image Paths
const BRAIN = '/Users/ajeetkumar/.gemini/antigravity/brain/9ed3616b-c5b8-42c2-b56f-64bc40b5eabd/.user_uploaded';
const IMG_LIVE_OPS = path.join(BRAIN, 'media_1788865897082.png');
const IMG_CAMERAS  = path.join(BRAIN, 'media_1788453380032.png');
const IMG_JOURNEY  = path.join(BRAIN, 'media_1787255174754.png');

function toBase64(filePath) {
  if (fs.existsSync(filePath)) {
    return 'data:image/png;base64,' + fs.readFileSync(filePath).toString('base64');
  }
  return null;
}

const b64LiveOps = toBase64(IMG_LIVE_OPS);
const b64Cameras = toBase64(IMG_CAMERAS);
const b64Journey = toBase64(IMG_JOURNEY);

// ── Helpers ───────────────────────────────────────────────────────────────────

function applyBackground(doc) {
  doc.setFillColor(...C_BG);
  doc.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, 'F');

  // Top accent line
  doc.setFillColor(...C_ACCENT);
  doc.rect(0, 0, PAGE_WIDTH, 2, 'F');
}

function addHeader(doc, title) {
  doc.setTextColor(...C_ACCENT);
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(22);
  doc.text(title, 20, 22);

  // Subtle divider
  doc.setDrawColor(...C_BORDER);
  doc.setLineWidth(0.5);
  doc.line(20, 28, PAGE_WIDTH - 20, 28);
}

function addSpeakerNotes(doc, notesText) {
  // Draw Notes Background
  doc.setFillColor(...C_NOTES_BG);
  doc.setDrawColor(250, 204, 21); // Yellow border
  doc.setLineWidth(0.5);
  doc.rect(15, NOTES_Y, PAGE_WIDTH - 30, PAGE_HEIGHT - NOTES_Y - 10, 'FD');

  // Notes Header
  doc.setTextColor(...C_NOTES_TXT);
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(10);
  doc.text('🎙️ SPEAKER NOTES (For Viva)', 20, NOTES_Y + 7);

  // Notes Content
  doc.setFont('helvetica', 'normal');
  doc.setFontSize(10);
  const lines = doc.splitTextToSize(notesText, PAGE_WIDTH - 40);
  doc.text(lines, 20, NOTES_Y + 14);
}

function drawCard(doc, x, y, w, h, borderColor = C_BORDER) {
  doc.setFillColor(...C_CARD);
  doc.setDrawColor(...borderColor);
  doc.setLineWidth(0.5);
  doc.rect(x, y, w, h, 'FD');
}

// ── Document Setup ────────────────────────────────────────────────────────────
const doc = new jsPDF({
  orientation: 'landscape',
  unit: 'mm',
  format: [PAGE_WIDTH, PAGE_HEIGHT]
});

// ═════════════════════════════════════════════════════════════════════════════
// SLIDE 1: TITLE & INTRODUCTION
// ═════════════════════════════════════════════════════════════════════════════
applyBackground(doc);

doc.setTextColor(...C_ACCENT);
doc.setFont('helvetica', 'bold');
doc.setFontSize(14);
doc.text('INFOSYS SPRINGBOARD GENAI INTERNSHIP', 30, 50);

doc.setTextColor(...C_TEXT);
doc.setFont('helvetica', 'bold');
doc.setFontSize(36);
doc.text('Consumer Attention', 30, 65);
doc.text('Mapping System', 30, 80);
doc.text('RetailEye AI', 30, 95);

doc.setTextColor(...C_SUBTEXT);
doc.setFont('helvetica', 'normal');
doc.setFontSize(14);
doc.text('Using AI to track customer behavior and attention in physical retail stores.', 30, 110);

doc.setTextColor(...C_TEXT);
doc.setFont('helvetica', 'bold');
doc.setFontSize(12);
doc.text('Presented by:', 30, 130);
doc.setFont('helvetica', 'normal');
doc.text('Ajeet Kumar | GKCIET Malda', 60, 130);

addSpeakerNotes(doc, "Good morning everyone. My name is Ajeet Kumar from GKCIET Malda. Today, I am excited to present my project: the Consumer Attention Mapping System, also known as RetailEye AI. This project was developed during my Infosys Springboard GenAI Internship. The main goal of this system is to bring online-style analytics—like tracking clicks and views—into physical retail stores using AI and CCTV cameras.");

// ═════════════════════════════════════════════════════════════════════════════
// SLIDE 2: TECHNOLOGY STACK
// ═════════════════════════════════════════════════════════════════════════════
doc.addPage();
applyBackground(doc);
addHeader(doc, 'Technology Stack: AI & Engineering Architecture');

const stacks = [
  { title: 'Backend', tech: 'FastAPI (Python)', desc: 'Handles APIs, database connection, and fast data processing.', color: C_ACCENT },
  { title: 'AI Model', tech: 'YOLOv8 + MediaPipe', desc: 'YOLOv8 detects people. MediaPipe tracks head movement/gaze.', color: C_GREEN },
  { title: 'Database', tech: 'PostgreSQL', desc: 'Stores customer data, shelf locations, and visit history safely.', color: C_PURPLE },
  { title: 'Frontend', tech: 'React.js + Vite', desc: 'Provides a fast, modern dashboard for store managers.', color: C_ORANGE }
];

stacks.forEach((st, i) => {
  const cx = 20 + (i * 75);
  drawCard(doc, cx, 50, 70, 70, st.color);
  
  doc.setTextColor(...st.color);
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(14);
  doc.text(st.title, cx + 5, 60);

  doc.setTextColor(...C_TEXT);
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(12);
  doc.text(st.tech, cx + 5, 75);

  doc.setTextColor(...C_SUBTEXT);
  doc.setFont('helvetica', 'normal');
  doc.setFontSize(10);
  const lines = doc.splitTextToSize(st.desc, 60);
  doc.text(lines, cx + 5, 85);
});

addSpeakerNotes(doc, "To build this system, I used a modern tech stack. For the backend, I used FastAPI because it is very fast in handling video data. For the AI, I used YOLOv8 to detect shoppers and MediaPipe to detect where they are looking. The data is saved securely in a PostgreSQL database. Finally, I built the user interface using React.js, which gives store managers an easy-to-use dashboard to see the analytics.");

// ═════════════════════════════════════════════════════════════════════════════
// SLIDE 3: CORE FEATURES
// ═════════════════════════════════════════════════════════════════════════════
doc.addPage();
applyBackground(doc);
addHeader(doc, 'Core Features of RetailEye AI Platform');

doc.setTextColor(...C_TEXT);
doc.setFont('helvetica', 'bold');
doc.setFontSize(16);
doc.text('1. Real-Time Customer Tracking', 30, 50);
doc.setFont('helvetica', 'normal');
doc.setFontSize(12);
doc.text('Tracks where people walk in the store without storing their personal photos (Privacy First).', 35, 60);

doc.setFont('helvetica', 'bold');
doc.setFontSize(16);
doc.text('2. Shelf Attention & Gaze Estimation', 30, 80);
doc.setFont('helvetica', 'normal');
doc.setFontSize(12);
doc.text('Calculates how long a customer looks at a specific product on the shelf (Dwell Time).', 35, 90);

doc.setFont('helvetica', 'bold');
doc.setFontSize(16);
doc.text('3. Smart AI Dashboards', 30, 110);
doc.setFont('helvetica', 'normal');
doc.setFontSize(12);
doc.text('Shows heatmaps and gives automatic recommendations to store managers on how to improve sales.', 35, 120);

addSpeakerNotes(doc, "The platform has three main features. First, it tracks where customers walk in the store. It does this anonymously to protect privacy. Second, it calculates 'Dwell Time'—meaning it measures exactly how long a customer stares at a specific product on the shelf. Third, it takes all this data and displays it on a smart dashboard, providing heatmaps and tips to the manager on which products are popular but not selling well.");

// ═══════════════════════════════════════════════════════════════════════════
// SLIDE 4: CHALLENGES FACING IN-STORE RETAIL
// ═══════════════════════════════════════════════════════════════════════════
doc.addPage();
applyBackground(doc);
addHeader(doc, 'Challenges Facing In-Store Retail Management');

const chal = [
  "Blind Spots: Online stores know exactly what we click. Physical stores only know what we buy, not what we looked at.",
  "Missed Opportunities: Sometimes a product looks great and gets attention, but the price is wrong, so people don't buy it. Managers don't know this.",
  "Manual Work: Staff have to manually walk around and count stock or observe customers, which is slow and inaccurate.",
  "Privacy Issues: Old facial recognition systems violate privacy laws. Stores need anonymous tracking."
];

chal.forEach((c, i) => {
  doc.setFillColor(...C_ACCENT);
  doc.circle(30, 50 + (i * 22), 3, 'F');
  
  doc.setTextColor(...C_TEXT);
  doc.setFont('helvetica', 'normal');
  doc.setFontSize(13);
  doc.text(c, 40, 51 + (i * 22));
});

addSpeakerNotes(doc, "Why did I build this? Because physical stores face big challenges. When you shop online, Amazon knows exactly what you clicked. But in physical stores, managers only know what was sold at the billing counter. They don't know which shelves customers ignored, or which products customers looked at but decided not to buy. Also, manually watching customers is impossible, and old camera systems violate privacy. My system solves these problems.");

// ═══════════════════════════════════════════════════════════════════════════
// SLIDE 5: SYSTEM ARCHITECTURE
// ═══════════════════════════════════════════════════════════════════════════
doc.addPage();
applyBackground(doc);
addHeader(doc, 'End-to-End System Architecture Overview');

const archSteps = [
  "1. Camera Input (CCTV Video Stream)",
  "2. AI Processing (YOLOv8 + MediaPipe)",
  "3. Data Analytics (Calculating Dwell Time & Scores)",
  "4. Database Storage (PostgreSQL)",
  "5. User Dashboard (React Frontend Display)"
];

archSteps.forEach((step, i) => {
  drawCard(doc, 30, 45 + (i * 18), 280, 14, C_ACCENT);
  doc.setTextColor(...C_ACCENT);
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(12);
  doc.text(step, 40, 54 + (i * 18));
});

addSpeakerNotes(doc, "Here is a simple view of the system architecture. It works in 5 steps. First, the system receives live video from the store's CCTV cameras. Second, the AI models process the video frame by frame to detect people and where they are looking. Third, our analytics engine calculates the dwell time and scores. Fourth, this data is saved into our PostgreSQL database. Finally, the React frontend fetches this data and displays it on the dashboard for the manager.");

// ═══════════════════════════════════════════════════════════════════════════
// SLIDE 6: ENGINEERING CHALLENGES & SOLUTIONS
// ═══════════════════════════════════════════════════════════════════════════
doc.addPage();
applyBackground(doc);
addHeader(doc, 'Engineering Challenges and Implemented Solutions');

doc.setTextColor(...C_TEXT);
doc.setFont('helvetica', 'bold');
doc.setFontSize(14);
doc.text('Challenge 1: People blocking each other (Occlusion)', 30, 50);
doc.setFont('helvetica', 'normal');
doc.setFontSize(12);
doc.text('Solution: I used ByteTrack, an advanced algorithm that remembers a person\'s path even if they are hidden for a second.', 35, 60);

doc.setFont('helvetica', 'bold');
doc.setFontSize(14);
doc.text('Challenge 2: System running too slow', 30, 85);
doc.setFont('helvetica', 'normal');
doc.setFontSize(12);
doc.text('Solution: I optimized the database to group data together instead of saving every single millisecond, making it much faster.', 35, 95);

doc.setFont('helvetica', 'bold');
doc.setFontSize(14);
doc.text('Challenge 3: Confusing UI for different users', 30, 120);
doc.setFont('helvetica', 'normal');
doc.setFontSize(12);
doc.text('Solution: I created Role-Based Access. Store Managers see different screens than Data Analysts, keeping it simple for everyone.', 35, 130);

addSpeakerNotes(doc, "During development, I faced several technical challenges. The biggest was 'Occlusion'—when one shopper walks in front of another, the camera loses track. I solved this using the ByteTrack algorithm, which predicts movement. Another challenge was speed; saving too much video data caused lag. I solved this by aggregating the data before saving it to the database. Lastly, I implemented Role-Based Access so different employees only see the data they need to see.");

// ═══════════════════════════════════════════════════════════════════════════
// SLIDE 7: MEASURABLE OUTCOMES
// ═══════════════════════════════════════════════════════════════════════════
doc.addPage();
applyBackground(doc);
addHeader(doc, 'Measurable Outcomes and Business Impact');

const outcomes = [
  { stat: 'Real-Time', desc: 'The AI processes video smoothly without lagging.' },
  { stat: '100% Automated', desc: 'No manual clipboard counting needed anymore.' },
  { stat: 'Fast Reports', desc: 'Managers can generate PDF and CSV reports in 1 click.' },
  { stat: 'High Accuracy', desc: 'Successfully tracks attention even in crowded aisles.' }
];

outcomes.forEach((o, i) => {
  drawCard(doc, 30 + (i * 70), 55, 60, 50, C_GREEN);
  doc.setTextColor(...C_GREEN);
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(16);
  doc.text(o.stat, 60 + (i * 70), 75, { align: 'center' });
  
  doc.setTextColor(...C_TEXT);
  doc.setFont('helvetica', 'normal');
  doc.setFontSize(11);
  const lines = doc.splitTextToSize(o.desc, 50);
  doc.text(lines, 60 + (i * 70), 85, { align: 'center' });
});

addSpeakerNotes(doc, "The impact of this project is significant. The system runs in real-time, providing immediate data to managers. It completely replaces the need for staff to manually count customers or observe shelves. It also allows managers to instantly download PDF reports with one click, saving them hours of manual data entry. Overall, it brings high accuracy to physical retail analytics.");

// ═══════════════════════════════════════════════════════════════════════════
// SLIDE 8: PLATFORM INTERFACE
// ═══════════════════════════════════════════════════════════════════════════
doc.addPage();
applyBackground(doc);
addHeader(doc, 'Platform Interface: Implemented Dashboards & UI Evidence');

if (b64LiveOps) {
  doc.addImage(b64LiveOps, 'PNG', 20, 40, 140, 75);
}
if (b64Cameras) {
  doc.addImage(b64Cameras, 'PNG', 170, 40, 140, 75);
}

doc.setTextColor(...C_TEXT);
doc.setFont('helvetica', 'bold');
doc.setFontSize(12);
doc.text('Live Analytics Dashboard (Left) and Camera Stream View (Right)', 20, 125);

addSpeakerNotes(doc, "Here is the evidence of the implemented UI. On the left, you can see the Live Operations dashboard, which shows active shoppers, total visitors, and average dwell time. On the right, you can see the Camera Stream interface, where managers can view the active AI tracking the shoppers in real-time through the web browser. The UI is clean, modern, and very easy for non-technical staff to understand.");

// ═══════════════════════════════════════════════════════════════════════════
// SLIDE 9: OPERATIONAL PIPELINE
// ═══════════════════════════════════════════════════════════════════════════
doc.addPage();
applyBackground(doc);
addHeader(doc, 'End-to-End Operational Pipeline & User Journey');

doc.setTextColor(...C_ACCENT);
doc.setFont('helvetica', 'bold');
doc.setFontSize(14);
doc.text('Step 1: Setup', 30, 50);
doc.setTextColor(...C_TEXT);
doc.setFont('helvetica', 'normal');
doc.setFontSize(12);
doc.text('Manager connects cameras and draws boxes over the shelves on the screen.', 30, 60);

doc.setTextColor(...C_ACCENT);
doc.setFont('helvetica', 'bold');
doc.setFontSize(14);
doc.text('Step 2: AI Tracking', 30, 85);
doc.setTextColor(...C_TEXT);
doc.setFont('helvetica', 'normal');
doc.setFontSize(12);
doc.text('Customers walk in. AI automatically tracks where they go and what they look at.', 30, 95);

doc.setTextColor(...C_ACCENT);
doc.setFont('helvetica', 'bold');
doc.setFontSize(14);
doc.text('Step 3: Actionable Insights', 30, 120);
doc.setTextColor(...C_TEXT);
doc.setFont('helvetica', 'normal');
doc.setFontSize(12);
doc.text('Manager checks the dashboard, sees a heatmap, and decides to move popular items to better shelves.', 30, 130);

addSpeakerNotes(doc, "How does a user actually use this software? It's a 3-step journey. First, the store manager connects the cameras and simply draws a box over the shelves on their screen. Second, they let the system run. The AI silently and automatically tracks customer interactions. Third, at the end of the day, the manager opens the dashboard, looks at the heatmaps, and makes smart decisions—like moving a highly viewed but poorly selling product to the front of the store.");

// ═══════════════════════════════════════════════════════════════════════════
// SLIDE 10: FUTURE ENHANCEMENTS
// ═══════════════════════════════════════════════════════════════════════════
doc.addPage();
applyBackground(doc);
addHeader(doc, 'Future Enhancements & Scalability Roadmap');

const fut = [
  "Edge Computing: Run the AI directly on small cameras in the store to save internet bandwidth.",
  "Multi-Camera Linking: Track the same person perfectly across 20 different cameras in a massive mall.",
  "Smart Digital Signs: If the AI sees a customer looking at a phone for 10 seconds, instantly show a discount for that phone on a nearby digital screen."
];

fut.forEach((f, i) => {
  drawCard(doc, 30, 50 + (i * 25), 280, 18, C_BORDER);
  doc.setTextColor(...C_TEXT);
  doc.setFont('helvetica', 'normal');
  doc.setFontSize(12);
  doc.text('• ' + f, 35, 61 + (i * 25));
});

addSpeakerNotes(doc, "For future enhancements, the project can be expanded in three ways. First, Edge Computing: running the AI directly on the camera hardware to save internet costs. Second, Multi-Camera Linking: tracking a single shopper perfectly across dozens of cameras in a large mall. Third, Smart Digital Signs: connecting the AI to TV screens in the store, so if a customer stares at an item, the TV automatically shows a 10% discount for that specific item to encourage a sale.");

// ═══════════════════════════════════════════════════════════════════════════
// SLIDE 11: PROJECT CONTRIBUTOR
// ═══════════════════════════════════════════════════════════════════════════
doc.addPage();
applyBackground(doc);
addHeader(doc, 'Project Contributor & Internship Context');

drawCard(doc, 30, 45, 280, 85, C_BORDER);

doc.setTextColor(...C_ACCENT);
doc.setFont('helvetica', 'bold');
doc.setFontSize(20);
doc.text('Ajeet Kumar', 40, 60);

doc.setTextColor(...C_TEXT);
doc.setFont('helvetica', 'bold');
doc.setFontSize(12);
doc.text('Degree: B.Tech Computer Science (AI & ML)', 40, 75);
doc.text('College: GKCIET, Malda', 40, 85);
doc.text('Internship: Infosys Springboard GenAI & Advanced Tech Internship', 40, 95);
doc.text('Role: Full-Stack AI Developer', 40, 105);

doc.setFont('helvetica', 'normal');
doc.text('I built this entire project from scratch, including the AI models, backend API, and React frontend.', 40, 115);

addSpeakerNotes(doc, "To give some context about my role: My name is Ajeet Kumar, currently pursuing my B.Tech in AI & ML at GKCIET Malda. This project was developed entirely by me during my Infosys Springboard GenAI Internship. I acted as a Full-Stack AI Developer, meaning I coded the computer vision models, built the FastAPI backend, and designed the React frontend dashboard from scratch.");

// ═══════════════════════════════════════════════════════════════════════════
// SLIDE 12: DEMONSTRATION & REPOSITORY
// ═══════════════════════════════════════════════════════════════════════════
doc.addPage();
applyBackground(doc);
addHeader(doc, 'Demonstration & Source Code Repository');

doc.setTextColor(...C_TEXT);
doc.setFont('helvetica', 'bold');
doc.setFontSize(16);
doc.text('Live Demonstration', 30, 60);
doc.setFont('helvetica', 'normal');
doc.setFontSize(12);
doc.text('The system is ready for a live walkthrough showing the dashboard and AI tracking.', 30, 70);

doc.setFont('helvetica', 'bold');
doc.setFontSize(16);
doc.text('Source Code', 30, 100);
doc.setFont('helvetica', 'normal');
doc.setFontSize(12);
doc.text('All code is documented and managed via Git.', 30, 110);
doc.text('Tech Stack: Python, React, PostgreSQL, YOLOv8.', 30, 120);

addSpeakerNotes(doc, "We have now reached the demonstration part of the Viva. The system is fully functional locally. I am prepared to show a live walkthrough of the React dashboard, demonstrate the video processing pipeline, and explain any part of the source code. All code is properly structured and maintained.");

// ═══════════════════════════════════════════════════════════════════════════
// SLIDE 13: QUESTIONS & ANSWERS
// ═══════════════════════════════════════════════════════════════════════════
doc.addPage();
applyBackground(doc);

doc.setTextColor(...C_ACCENT);
doc.setFont('helvetica', 'bold');
doc.setFontSize(36);
doc.text('Questions & Answers', PAGE_WIDTH/2, 60, { align: 'center' });

doc.setTextColor(...C_SUBTEXT);
doc.setFont('helvetica', 'normal');
doc.setFontSize(16);
doc.text('Open for Project Evaluation, Code Review & Technical Viva', PAGE_WIDTH/2, 80, { align: 'center' });

addSpeakerNotes(doc, "Thank you for listening to my presentation. I am now open to any questions regarding the AI algorithms, the backend architecture, the React frontend, or my overall experience building this platform.");

// ═══════════════════════════════════════════════════════════════════════════
// SLIDE 14: THANK YOU
// ═══════════════════════════════════════════════════════════════════════════
doc.addPage();
applyBackground(doc);

doc.setTextColor(...C_ACCENT);
doc.setFont('helvetica', 'bold');
doc.setFontSize(40);
doc.text('Thank You!', PAGE_WIDTH/2, 60, { align: 'center' });

doc.setTextColor(...C_TEXT);
doc.setFont('helvetica', 'bold');
doc.setFontSize(18);
doc.text('RetailEye AI • Consumer Attention Mapping System', PAGE_WIDTH/2, 80, { align: 'center' });

doc.setTextColor(...C_SUBTEXT);
doc.setFont('helvetica', 'normal');
doc.setFontSize(14);
doc.text('Ajeet Kumar | GKCIET Malda | Infosys Springboard', PAGE_WIDTH/2, 95, { align: 'center' });

addSpeakerNotes(doc, "Thank you very much for your time and evaluation.");

// ═══════════════════════════════════════════════════════════════════════════
// SAVE PDF
// ═══════════════════════════════════════════════════════════════════════════
const outPath = path.join(process.cwd(), 'Final_Viva_Presentation_Light.pdf');
fs.writeFileSync(outPath, Buffer.from(doc.output('arraybuffer')));
console.log('Successfully generated clean Light Theme PDF at: ' + outPath);
