import faiss
import numpy as np
import re
import os
import pickle
from textwrap import wrap

DB_DIR = "data_store"
os.makedirs(DB_DIR, exist_ok=True)

def clean_and_chunk_text(text, max_length=500, min_length=50):
   
    paragraphs = re.split(r'\n{2,}', text)
    cleaned_chunks = []

    for para in paragraphs:
        para = para.strip()
        if len(para) < min_length:
            continue  # Skip very short/noisy chunks
        if len(para) <= max_length:
            cleaned_chunks.append(para)
        else:
            # Wrap long paragraphs into smaller parts
            sub_chunks = wrap(para, max_length)
            cleaned_chunks.extend(sub_chunks)

    return cleaned_chunks


def embed_chunks(chunks, embedder):
    embeddings = embedder.encode(chunks)
    return chunks, np.array(embeddings)


def create_faiss_index(embeddings):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    return index


def search_similar_chunks(query, chunks, index, embedder, k=3):
    query_vec = embedder.encode([query])
    D, I = index.search(np.array(query_vec).astype("float32"), k)

    # Combine chunks into one context string instead of a short single line
    selected = [chunks[i] for i in I[0] if i < len(chunks)]
    return ["\n".join(selected)]


# --------- NEW: Functions for caching chunks/embeddings --------- #

def save_vector_store(filename, chunks, embeddings, index):
    """
    Save chunks, embeddings, and FAISS index to disk (pickle + FAISS).
    """
    base = os.path.splitext(os.path.basename(filename))[0]
    store_path = os.path.join(DB_DIR, f"{base}_store.pkl")

    faiss_bytes = faiss.serialize_index(index)
    with open(store_path, "wb") as f:
        pickle.dump({
            "chunks": chunks,
            "embeddings": embeddings,
            "index": faiss_bytes
        }, f)

    print(f"✅ Saved vector store: {store_path}")


def load_vector_store(filename):
    """
    Load chunks, embeddings, and FAISS index from disk.
    Returns (chunks, embeddings, index) or (None, None, None) if not found.
    """
    base = os.path.splitext(os.path.basename(filename))[0]
    store_path = os.path.join(DB_DIR, f"{base}_store.pkl")

    if not os.path.exists(store_path):
        return None, None, None

    with open(store_path, "rb") as f:
        data = pickle.load(f)

    index = faiss.deserialize_index(data["index"])
    print(f"📂 Loaded cached vector store for '{filename}'")
    return data["chunks"], data["embeddings"], index
