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

## Tech Stack

| Layer | Technology |
|---------|------------|
| Frontend | React + Tailwind CSS |
| Backend | FastAPI (Python) |
| Vector Database | ChromaDB (Local) |
| AI Layer | Claude API + OpenAI Embeddings |

---

## Project Structure

### Backend

```text
backend/
├── main.py                 # FastAPI app entry point
├── routes/
│   ├── chat.py             # Chat endpoints
│   └── pdf.py              # Upload + edit endpoints
├── services/
│   ├── rag.py              # Chunking + retrieval
│   ├── llm.py              # Claude API calls
│   ├── pdf_edit.py         # PDF modification logic
│   └── chroma.py           # ChromaDB integration
└── db/
    └── chroma.py
```

### Frontend

```text
frontend/src/
├── components/
│   ├── ChatBox.jsx
│   ├── PDFViewer.jsx
│   ├── Autocomplete.jsx
│   └── EditPanel.jsx
├── pages/
│   └── Dashboard.jsx
├── hooks/
│   └── useChat.js
└── api/
    └── client.js           # Axios API calls
```

---

## Core RAG Pipeline

### 1. PDF Upload

```text
PDF → PyMuPDF → Extract Text
```

### 2. Chunking

```text
Chunk Size: 500 tokens
Overlap: 50 tokens
```

### 3. Embedding & Storage

```text
Chunks
   ↓
text-embedding-3-small
   ↓
ChromaDB
```

### 4. Retrieval

```text
User Query
   ↓
Embedding
   ↓
Top-5 Similar Chunks
```

### 5. Answer Generation

```text
Retrieved Context
   +
User Question
   ↓
Claude API
   ↓
Answer + Page Citations
```

### 6. Streaming Response

```text
Backend (SSE)
   ↓
React UI
```

---

## Autocomplete Engine

### Workflow

1. User types in chat input.
2. Frontend debounces requests (300 ms).
3. Request sent to:

```http
GET /autocomplete
```

4. Backend:
   - Embeds partial query
   - Searches similar chunks
   - Extracts relevant question patterns

5. Claude generates:

```text
3 context-aware question suggestions
```

6. Suggestions displayed in UI.

---

## PDF Editing Engine

### Flow

```text
User Command
    ↓
Claude Function Calling
    ↓
Intent Detection
    ↓
Edit Action
    ↓
PyMuPDF + ReportLab
    ↓
Updated PDF Download
```

### Example

```text
"Summarize Section 3 and insert as Page 1"
```

Process:

```text
Section Retrieval
    ↓
Claude Summary
    ↓
ReportLab Creates New Page
    ↓
PyMuPDF Merges Pages
    ↓
Updated PDF Returned
```

---

## API Endpoints

### Upload PDF

```http
POST /upload
```

**Responsibilities**
- Accept PDF
- Extract text using PyMuPDF
- Chunk content
- Generate embeddings
- Store in ChromaDB

**Response**

```json
{
  "doc_id": "12345"
}
```

---

### Chat

```http
POST /chat
```

**Request**

```json
{
  "doc_id": "12345",
  "message": "Summarize section 2"
}
```

**Flow**

```text
Question
   ↓
Embedding
   ↓
Retrieve Top-5 Chunks
   ↓
Claude
   ↓
Streaming Response
```

---

### Autocomplete

```http
GET /autocomplete
```

**Query Params**

```text
doc_id
partial
```

**Target Latency**

```text
< 200ms
```

---

### Edit PDF

```http
POST /edit
```

**Request**

```json
{
  "doc_id": "12345",
  "command": "Summarize section 3 and insert at page 1"
}
```

**Response**

```text
Updated PDF File
```

---

## Development Roadmap

| Hour | Deliverable |
|--------|------------|
| Hour 1 | PDF Upload + RAG Pipeline |
| Hour 2 | Chat UI + Streaming |
| Hour 3 | Autocomplete Endpoint |
| Hour 4 | PDF Editing + Export |
| Hour 5 | Page Citations + UI Polish |
| Hour 6 | Demo Preparation + Sample PDFs |

---

## End-to-End Flow

```text
Upload PDF
    ↓
Extract Text (PyMuPDF)
    ↓
Chunk Content
    ↓
Generate Embeddings
    ↓
Store in ChromaDB
    ↓
User Question
    ↓
Retrieve Top-5 Chunks
    ↓
Claude Generates Answer
    ↓
Stream Response to React UI
    ↓
(Optional)
Edit PDF & Export Updated Version
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
