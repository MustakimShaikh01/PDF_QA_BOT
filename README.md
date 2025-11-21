# PDF Q&A Bot (Upload a File → Ask Questions)

Hi, I'm Mustakim 👋

This project is a **PDF question-answering app**:
- You upload a PDF
- Backend builds embeddings with **LangChain + OpenAI**
- Stores them in an in-memory **FAISS** vector store
- You then ask questions and get answers grounded in the PDF

This showcases:
- File upload handling in FastAPI
- Text extraction from PDFs
- Chunking, embeddings, and retrieval (RAG)
- Simple web UI with upload + chat

---

## 1. Tech Stack

**Backend**
- Python 3.10+
- FastAPI
- LangChain (langchain, langchain-openai, langchain-community, langchain-text-splitters)
- FAISS vector store
- PyPDF2
- python-dotenv

**Frontend**
- HTML + CSS + JS (no framework)
- File upload + question input

---

## 2. Structure

```text
pdf_qa_bot/
  README.md
  backend/
    app.py
    requirements.txt
    .env.example
  frontend/
    index.html
    style.css
    main.js
```

---

## 3. Environment Variables

Create `backend/.env`:

```env
OPENAI_API_KEY=your_openai_api_key_here
MODEL_NAME=gpt-4o-mini
ALLOWED_ORIGINS=http://localhost:5174,http://localhost:5500,http://127.0.0.1:5500
```

---

## 4. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # then fill OPENAI_API_KEY, etc.
uvicorn app:app --reload --port 8002
```

Backend runs at: `http://localhost:8002`

---

## 5. Frontend Setup

```bash
cd frontend
python -m http.server 5174
```

Then open: `http://localhost:5174`

---

## 6. API Flow

1. **Upload PDF**

   `POST /upload` (multipart form-data)
   - `file`: PDF file
   - returns: `{ "session_id": "uuid" }`

   Backend:
   - Reads PDF pages
   - Splits into chunks
   - Embeds with OpenAI
   - Stores vector store in memory for that `session_id`

2. **Ask Questions**

   `POST /ask`
   ```json
   {
     "session_id": "uuid-from-upload",
     "question": "What is the main idea of this document?"
   }
   ```

   Backend:
   - Looks up vector store by `session_id`
   - Retrieves top relevant chunks
   - Builds context prompt
   - Uses `ChatOpenAI` to answer based only on PDF content

---

## 7. What This Demonstrates for the Job

- **AI Integration & Custom Training Modules**
  - RAG-style flow over user data (PDF)
  - Building embeddings, vector search, and context windows

- **Backend Engineering**
  - Robust file upload handling
  - Session-based state in-memory (could be swapped for DB/Redis easily)

- **Practical AI Product Skill**
  - This matches many real business use-cases: policy Q&A, contracts, SOP manuals, etc.

You can describe this as:  
> “I built a PDF Q&A bot using LangChain RAG. Users upload PDFs, I create embeddings and let them ask grounded questions. The system never answers outside the provided document.”

---

## 8. Run Summary

```bash
# backend
cd backend
uvicorn app:app --reload --port 8002

# frontend
cd ../frontend
python -m http.server 5174
```

Then open your browser and test the full flow 🚀
