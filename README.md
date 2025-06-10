# 🚀 Human Rights Monitor Management Information System (MIS)⚖️

## Overview 💡

This project offers a platform to manage 📁 and analyze 📊 human rights cases. It includes:
 **Case Management System**: A FastAPI backend ⚙️ for CRUD operations on cases, with search & filter options.


## Technologies Used 🛠️

*   Python 3.8+ 🐍
*   FastAPI 🌐
*   Streamlit 🎨
*   MongoDB ☁️


## Project Structure 📂

*   `backend/`: FastAPI app (`main.py`) for case management API.
*   `frontend/`: Streamlit app (`app.py`) for case management UI.
*   `requirements.txt`:A file listing the project's Python dependencies for easy installation.

## Setup & Deployment ☁️

Follow these steps to deploy the project:

### 1. FastAPI Backend ⚙️

a.  **Render Account**: Sign up at [Render](https://render.com/).

b.  **Upload Files**: Put `main.py` in a GitHub repo 🐙.

c.  **Connect to Render**: Create a web service on Render and link it to your repo.

d.  **Configure**:

    *   Build command: `pip install -r requirements.txt`
    *   Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
    *   Set env vars, especially `MONGODB_URI`.

e.  **Deploy**: Render builds & deploys! 🎉


### 2. Streamlit Frontend 🎈

a.  **Upload Files**: Put `app.py` in a separate GitHub repo 🐙.

b.  **Streamlit Cloud**: Sign up at [Streamlit Cloud](https://streamlit.io/cloud).

c.  **Create New App**: Connect Streamlit Cloud to your repo.

d.  **Configure**:

    *   Set main file path: `app.py`.
    *   Add `API_BASE` env var (FastAPI backend URL).

e.  **Deploy**: Streamlit Cloud builds & deploys! 🚀


## API Endpoints 🌐

*   `POST /cases/`: Create case ➕
*   `GET /cases/{case_id}`: Get case ℹ️
*   `GET /cases/`: List cases 📜
*   `PATCH /cases/{case_id}`: Update case ✏️
*   `DELETE /cases/{case_id}`: Archive case 🗑️


## MongoDB Aggregations ☁️
* cases (main case records)
* case_status_history (track status changes)




