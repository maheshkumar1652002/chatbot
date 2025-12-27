import sys
import os

def resource_path(relative_path):
    try:
        # running in PyInstaller exe
        base_path = sys._MEIPASS
    except AttributeError:
        # running normally
        base_path = os.path.abspath(".")
        
    return os.path.join(base_path, relative_path)

def load_embedder():    
    from sentence_transformers import SentenceTransformer

    model_path = resource_path("models/all-MiniLM-L6-v2")
    return SentenceTransformer(model_path, local_files_only=True, trust_remote_code=False)


