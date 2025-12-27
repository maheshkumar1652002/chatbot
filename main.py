from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from contextlib import asynccontextmanager
import uvicorn
import webbrowser
import subprocess
import time

ollama_server = subprocess.Popen([
    "powershell",
    "-NoExit",
    "-Command",
    "ollama serve"
])
print("Ollama server started in background...")
time.sleep(0.5)

import transformers

if hasattr(transformers.models.auto, "auto_factory"):
    auto_factory = transformers.models.auto.auto_factory
    if hasattr(auto_factory, "_model_mapping"):
        auto_factory._model_mapping = {}

from helper import load_embedder

from pdf_utils import extract_text_from_pdf
from vector_utils import (
    clean_and_chunk_text,
    embed_chunks,
    create_faiss_index,
    search_similar_chunks,
    save_vector_store,
    load_vector_store
)
from ollama_utils import ask_ollama
from helper import resource_path

@asynccontextmanager
async def lifespan(app: FastAPI):
    webbrowser.open("http://127.0.0.1:8000", new=2)

    yield

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory=resource_path("static")), name="static")
templates = Jinja2Templates(directory=resource_path("templates"))

# Load model once at startup
embedder = load_embedder()

# Global memory cache
chunks, index, embeddings = [], None, None
filename = ""

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload/")
async def upload_pdf(request: Request, file: UploadFile = File(...)):
    global chunks, index, embeddings, filename
    try:
        filename = file.filename

        # Try loading previously saved vector store for this PDF
        chunks, embeddings, index = load_vector_store(filename)
        if chunks is not None and index is not None:
            return templates.TemplateResponse("index.html", {
                "request": request,
                "message": f"📂 Loaded cached data for '{filename}'!",
                "filename": filename
            })

        # If no cache found, process the PDF
        text = extract_text_from_pdf(file)
        chunks = clean_and_chunk_text(text)
        chunks, embeddings = embed_chunks(chunks, embedder)
        index = create_faiss_index(embeddings)

        # Save the processed data for future use
        save_vector_store(filename, chunks, embeddings, index)

        return templates.TemplateResponse("index.html", {
            "request": request,
            "message": f"✅ PDF '{filename}' processed and stored for future use!",
            "filename": filename
        })

    except Exception as e:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "message": f"❌ Error processing PDF: {str(e)}",
            "filename": filename
        })


@app.post("/ask/")
async def ask_question(request: Request, question: str = Form(...)):
    global filename
    if not chunks or not index:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "message": "⚠️ Please upload a PDF first.",
            "filename": filename
        })

    try:
        # Retrieve top relevant chunks for the question
        relevant_chunks = search_similar_chunks(question, chunks, index, embedder)
        context = "\n".join(relevant_chunks)


        # Get model answer
        raw_answer = ask_ollama(context, question).strip()

        # Format output: convert numbered lists to HTML lists if needed
        if raw_answer.startswith("1."):
            lines = raw_answer.split('\n')
            html_items = []
            for line in lines:
                if '.' in line:
                    parts = line.split('.', 1)
                    if len(parts) == 2:
                        heading_body = parts[1].strip().split(':', 1)
                        if len(heading_body) == 2:
                            heading, body = heading_body
                            html_items.append(f"<li><strong>{heading.strip()}:</strong> {body.strip()}</li>")
                        else:
                            html_items.append(f"<li>{line.strip()}</li>")
                else:
                    html_items.append(f"<li>{line.strip()}</li>")
            answer = "<ol>\n" + "\n".join(html_items) + "\n</ol>"
        else:
            answer = raw_answer.replace('\n', '<br>')

        return templates.TemplateResponse("index.html", {
            "request": request,
            "message": answer,
            "question": question,
            "filename": filename
        })

    except Exception as e:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "message": f"❌ Error during question answering: {str(e)}",
            "question": question,
            "filename": filename
        })
    
if __name__ == "__main__":
    try:
        import uvicorn
        uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)
        
    except Exception:
        import traceback
        traceback.print_exc()
    
    finally:
        ollama_server.terminate()
        ollama_server.wait()
        print("Ollama server stopped.")