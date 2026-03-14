# CryptoShield Backend

This is the FastAPI backend for the CryptoShield wallet risk analyzer.

## Code Structure

We split the code up to keep things somewhat organized:

*   **`backend/internal_types.py` & `backend/database.py`**: Handles DB connections (SQLite) and data validation shapes.
*   **`backend/services/`**: The core engines. Contains the Etherscan fetchers (`blockchain.py`), the heuristic/AI analysis logic (`analysis.py`), and the graph visualizer (`graph.py`).
*   **`backend/routers/`**: The API endpoints. Includes auth logic, wallet reporting, and the main scanning routes.

## Keys Required

Make sure to set up your `.env` file before running. It needs:
*   `ETHERSCAN_API_KEY`: To pull transactions.
*   `GEMINI_API_KEY`: Used as an optional layer for summarizing risk findings. If this fails, the app will just fall back to standard heuristics.

## How to run it

Just install the requirements and hit run:
```bash
pip install -r requirements.txt
python run.py
```

The server usually bounds to port 8001.
*   Login: http://localhost:8001/
*   Dashboard: http://localhost:8001/dashboard

**Demo Credentials:**
You can use the built-in demo buttons on the login page or manually enter:
*   `sahil` / `4197546`
*   `prajval` / `4197546`
