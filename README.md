# 🛡️ CryptoShield.AI: Advanced Blockchain Fraud Detection

![Project Demo](Demo.mp4)

**CryptoShield.AI** is a high-performance web application designed to protect crypto users by analyzing wallet history for malicious patterns, money laundering, and fraud using a multi-layered detection engine.

---

## 🚀 Key Features

*   **Real-time Blockchain Tracing**: Integrates directly with Etherscan/PolygonScan to fetch and analyze transaction history.
*   **Multi-Layer Detection Engine**:
    *   **Layer 1 (Heuristics)**: Detects interaction with known mixers (Tornado Cash), peeling chains, and rapid fund movement.
    *   **Layer 2 (Machine Learning)**: Uses a local **Random Forest Classifier** to predict fraud probability based on 8+ transaction features.
    *   **Layer 3 (AI analysis)**: Leverages **Google Gemini 1.5 Flash** to provide human-readable risk summaries and explanations.
*   **Community Reporting**: Collaborative database for flagging malicious addresses.
*   **Interactive Visualization**: (Coming Soon) Dynamic money-flow graph to trace fund movement.

## 🛠️ Tech Stack

*   **Backend**: Python, FastAPI
*   **Database**: SQLite (SQLAlchemy ORM)
*   **AI/ML**: Scikit-Learn (Random Forest), Google GenAI (Gemini)
*   **Frontend**: HTML5, Vanilla CSS, JavaScript (Glassmorphism UI)
*   **Security**: JWT Authentication, Argon2 Hashing, Rate Limiting

## 📦 Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Ouroboros-code-ux/Crypto-v7.git
   cd Crypto-v7
   ```

2. **Setup environment variables** (`.env`):
   ```env
   ETHERSCAN_API_KEY=your_key
   GEMINI_API_KEY=your_key
   SECRET_KEY=your_secure_hash
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the server**:
   ```bash
   python run.py
   ```

## 📐 Architecture Overview

The system is built with a focus on **Graceful Fallback**. If the AI Analysis service is unavailable, the system automatically defaults to the local ML model and heuristic scanners to ensure constant protection.

---

## 👨‍💻 Developer Notes
This project was built to demonstrate proficiency in backend architecture, API integration, and applied machine learning for cybersecurity. 
