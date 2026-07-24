# 🛒 AI Consumer Attention Mapping System

An AI-powered retail analytics platform that uses **Computer Vision**, **Artificial Intelligence**, and **Behavioral Analytics** to understand how customers interact with products, shelves, and store layouts. The system helps retailers optimize product placement, improve customer engagement, and increase sales through data-driven insights.

---

## 📌 Project Overview

The Consumer Attention Mapping System analyzes customer behavior inside retail stores using surveillance cameras and AI models. It detects customer movement, estimates gaze direction, measures dwell time, tracks product interactions, and generates actionable insights such as attention heatmaps and product attractiveness scores.

---

## 🎯 Objectives

- Detect and track customers in real time.
- Analyze customer attention and gaze direction.
- Monitor product interactions (pickup, return, purchase).
- Generate attention heatmaps.
- Calculate product attractiveness scores.
- Recommend better shelf layouts and product placements.
- Provide dashboards and reports for business decisions.

---

## ✨ Features

- 🔐 User Authentication & Role-Based Access
- 🏪 Store & Shelf Management
- 👥 Consumer Detection & Tracking
- 👀 Attention & Gaze Analysis
- 📦 Product Interaction Detection
- 📊 Consumer Behavior Analytics
- 🔥 Attention Heatmap Generation
- ⭐ Product Attractiveness Scoring
- 💡 AI-Based Recommendations
- 📈 Interactive Dashboards
- 🔔 Notifications & Alerts
- 📄 PDF & Excel Report Export

---

## 🛠️ Tech Stack

### Frontend
- React.js
- JavaScript
- Next.js
- Tailwind CSS
- Chart.js

### Backend
- Python
- FastAPI

### Database
- PostgreSQL
- MongoDB

### AI & Machine Learning
- YOLOv8
- OpenCV
- TensorFlow
- PyTorch
- MediaPipe
- Scikit-learn
- XGBoost
- Pandas
- NumPy

### Video Analytics
- DeepSORT
- ByteTrack
- FFmpeg

### Visualization
- Plotly
- Matplotlib
- Seaborn

### DevOps & Cloud
- Docker
- Docker Compose
- AWS / Azure
- Git & GitHub
- GitHub Actions
- Postman

---

## 📂 Project Structure

```text
ConsumerAttentionMapping/
│
├── backend/
│   ├── app/
│   │   ├── database/
│   │   ├── models/
│   │   ├── routers/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── utils/
│   │   ├── config.py
│   │   └── main.py
│   └── venv/
│
├── frontend/
├── datasets/
├── docs/
├── README.md
└── .gitignore
```

---

## 🚀 Installation

### Clone the Repository

```bash
git clone https://github.com/ajeet2026/Ajeet-Consumer-Attention-Mapping-System.git
```

```bash
cd Ajeet-Consumer-Attention-Mapping-System
```

### Create Virtual Environment

```bash
python3 -m venv venv
```

Activate the virtual environment:

**macOS/Linux**

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the Backend

```bash
uvicorn app.main:app --reload
```

Open your browser:

```
http://127.0.0.1:8000
```

Swagger Documentation:

```
http://127.0.0.1:8000/docs
```

---

## 📊 Workflow

```
Customer
      │
      ▼
Store Cameras
      │
      ▼
AI & Computer Vision
(YOLOv8 + OpenCV + MediaPipe)
      │
      ▼
FastAPI Backend
      │
      ▼
PostgreSQL / MongoDB
      │
      ▼
Behavior Analytics
      │
      ▼
Heatmaps & Recommendations
      │
      ▼
React Dashboard
```

---

## 📈 Future Enhancements

- Real-time multi-camera support
- Mobile dashboard
- AI-based demand prediction
- Smart inventory integration
- Personalized marketing recommendations
- Cloud deployment with Kubernetes

---

## 👨‍💻 Author

**Ajeet Kumar**

B.Tech CSE (AI & ML)  
Ghani Khan Choudhury Institute of Engineering & Technology (GKCIET), Malda

GitHub: https://github.com/ajeet2026

---

## 📄 License

This project is developed for educational and learning purposes.
