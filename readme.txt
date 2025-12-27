===========================
📘 README.txt – Offline PDF Chatbot Setup
===========================

This chatbot allows you to upload a PDF and ask questions about it using a local LLM – all completely offline.

--------------------------------------------
📁 Folder Structure (Keep it Like This):
--------------------------------------------
offline_pdf_bot/
├── main.py
├── pdf_utils.py
├── vector_utils.py              <-- updated to load embedder locally
├── ollama_utils.py
├── templates/
│   └── index.html               <-- your web UI
├── static/
│   └── style.css                <-- optional styling
├── models/
│   └── all-MiniLM-L6-v2/               <-- saved SentenceTransformer model
├── .ollama/                    <-- local Ollama models (e.g., llama3)
├── offline_env/                       <-- full Python virtual environment
├── requirements.txt            <-- optional for reinstalling
├── run_offline.bat             <-- run this on Windows
├── run_offline.sh              <-- run this on Linux/macOS (optional)
└── README.txt                  <-- this file


--------------------------------------------
🚀 How to Run on Offline PC (Windows):
--------------------------------------------
1. Make sure Python is installed (already downloaded installer is OK).
2. Copy the entire 'offline_pdf_bot' folder to the new PC.
3. Double-click `run_offline.bat`

   OR 
   
   run manually in terminal:
   
   ```
   cd offline_pdf_bot
   offline_env\Scripts\activate
   uvicorn main:app --reload
   ```

4. Open a browser and go to:
   http://localhost:8000

   OR

   Ctrl + Click "http://127.0.0.1:8000" in Terminal

✅ You're ready to use the PDF bot without internet!

--------------------------------------------
🧠 About Local Models:
--------------------------------------------
✅ SentenceTransformer
  - Already saved in: `models/embedder/`
  - You must NOT call online models like 'all-MiniLM-L6-v2' in code.

✅ Ollama LLM (e.g., llama3)
  - Ollama must already be installed.
  - Copy `.ollama/` folder from internet-connected PC
  - Contains downloaded models like llama3, mistral, etc.


--------------------------------------------
🛠️ Developer Notes:
--------------------------------------------
- `vector_utils.py` is updated to load the embedder from `models/embedder/`
- `ask_ollama()` should work offline if Ollama + model are installed
- Make sure FAISS index is built from local embeddings
- Any file saving (chunks, indexes) should use relative paths like 'data/'


--------------------------------------------
📦 Tips for Zipping & Transferring:
--------------------------------------------
- ZIP the entire `offline_pdf_bot` folder
- Transfer using USB / LAN / external HDD
- Total size may increase due to virtual environment + model weights
- Optional: use `venv` wheels instead of copying full environment
