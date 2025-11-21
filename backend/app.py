import os
import uuid
from typing import Dict

from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set")

app = FastAPI(title="PDF Q&A Bot")

origins = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:5174,http://localhost:5500,http://127.0.0.1:5500",
    ).split(",")
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm = ChatOpenAI(model=MODEL_NAME, temperature=0.1)
embeddings = OpenAIEmbeddings()

# In-memory store: session_id -> vectorstore
stores: Dict[str, FAISS] = {}


class AskRequest(BaseModel):
    session_id: str
    question: str


class AskResponse(BaseModel):
    answer: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    content = await file.read()
    temp_path = f"/tmp/{uuid.uuid4()}_{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(content)

    loader = PyPDFLoader(temp_path)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(docs)

    vectorstore = FAISS.from_documents(chunks, embeddings)

    session_id = str(uuid.uuid4())
    stores[session_id] = vectorstore

    os.remove(temp_path)

    return {"session_id": session_id}


@app.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest):
    if req.session_id not in stores:
        raise HTTPException(status_code=404, detail="Unknown session_id. Upload a PDF first.")

    vs = stores[req.session_id]

    docs = vs.similarity_search(req.question, k=4)
    context = "\n\n".join(d.page_content for d in docs)

    system_prompt = (
        "You are a helpful assistant that answers ONLY using the information "
        "from the provided PDF context. If the answer is not in the PDF, say "
        "'I could not find this information in the document.'\n\n"
        f"PDF CONTEXT:\n{context}"
    )

    messages = [
        ("system", system_prompt),
        ("user", req.question),
    ]

    result = llm.invoke(messages)
    answer = result.content if hasattr(result, "content") else str(result)

    return AskResponse(answer=answer)
