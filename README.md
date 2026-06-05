# 📄 PDF‑Aware Smart Chatbot (PS4)

## Overview
This project is a **PDF‑aware conversational chatbot** built with:
- **FastAPI** backend exposing three endpoints (`/upload/`, `/autocomplete/`, `/chat/`).
- **Streamlit** front‑end that lets users upload a PDF, ask questions, and see a live PDF preview.
- **ChromaDB** vector store for semantic search (RAG).
- **Groq LLM (llama‑3.1‑8b‑instant)** for generating answers and automatic executive‑summary pages.

When a user asks a *modification* query (e.g. "add an executive summary …"), the backend generates a summary via the LLM, inserts a new first page into the PDF and returns the updated file so the UI instantly refreshes.

---
## Features
- 📂 **PDF upload** → automatic text extraction and chunking.
- 🔍 **Semantic search** over the PDF using ChromaDB.
- 🤖 **RAG**: retrieve relevant passages and answer questions.
- ✍️ **Smart PDF modification**: generate and prepend an executive‑summary page.
- ⚡ **Live preview**: updated PDF appears instantly on the right pane.
- 📦 **Modular architecture** – clean separation of UI, API, services, and storage.

---
## Quick Start
```bash
# 1️⃣ Clone the repo (you already have the code)
cd c:\Users\rishi\aiden\ps4_chatbot

# 2️⃣ Create a virtual environment & install deps
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt  # (fastapi, streamlit, chromadb, langchain, groq, pymupdf, etc.)

# 3️⃣ Run the backend (FastAPI)
uvicorn backend.main:app --reload --port 8001

# 4️⃣ In another terminal, run the front‑end (Streamlit)
.\venv\Scripts\streamlit.exe run frontend/app.py
```
Open the Streamlit UI at <http://localhost:8501>.

---
## Architecture
```mermaid
flowchart TB
    subgraph FE[Streamlit Front‑end (frontend/app.py)]
        UI[UI (Uploader + Chat + PDF Viewer)]
    end
    subgraph GW[FastAPI (backend/main.py)]
        Router[/API Router (backend/api/routes.py)/]
    end
    subgraph SVC[Backend Services]
        PDFSrv[PDF Service<br/>pdf_service.py]
        AISrv[AI Service<br/>ai_service.py]
        DB[Vector Store (ChromaDB)<br/>get_vectorstore()]
    end
    subgraph LLM[Groq LLM (ChatGroq)]
        LLMModel[(Llama‑3.1‑8B)]
    end
    UI -->|POST /upload/| Router
    Router -->|process_and_store_pdf| PDFSrv
    PDFSrv -->|store chunks| DB
    UI -->|POST /chat/| Router
    Router -->|process_chat| AISrv
    AISrv -->|retriever| DB
    AISrv -->|LLM invoke| LLMModel
    LLMModel -->|summary / answer| AISrv
    AISrv -->|modify_pdf_with_summary| PDFSrv
    PDFSrv -->|save updated PDF| UI
    style FE fill:#f9f9f9,stroke:#333,stroke-width:2px
    style GW fill:#e6f7ff,stroke:#0055aa,stroke-width:2px
    style SVC fill:#fff8e1,stroke:#ff9900,stroke-width:2px
    style LLM fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
```
---
## API Endpoints
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/upload/` | Accepts a PDF file, extracts text, stores chunks in ChromaDB, and starts a background task that generates autocomplete suggestions. |
| `GET`  | `/autocomplete/` | Returns up‑to‑5 suggested questions based on the user's current query. |
| `POST` | `/chat/` | Handles normal Q&A (RAG) **or** modification requests. If the query contains keywords like `summarize and add`, `add an executive summary`, `update pdf`, the endpoint returns an `updated_pdf_url` pointing to the newly created PDF. |

---
## Development notes
- **PDF parsing** uses **PyMuPDF** (`fitz`).
- **Chunking** is done with `RecursiveCharacterTextSplitter` (size = 1000, overlap = 200).
- **Autocomplete** is generated in a FastAPI background task (`background_tasks.add_task`).
- **Vector store** lives in `backend/config/database.py`; you can change the persistence location by editing the `CHROMA_SETTINGS` there.
- **Environment variables** (e.g. `GROQ_API_KEY`) are read from `.env` via `python‑dotenv`.

---
## Contributing
1. Fork the repo.
2. Create a feature branch (`git checkout -b feat/awesome‑feature`).
3. Ensure the app runs locally and all linting passes (`ruff` / `black`).
4. Open a Pull Request describing the change.

---
## License
This project is licensed under the MIT License.

---
*Happy hacking!*
# Team-H
