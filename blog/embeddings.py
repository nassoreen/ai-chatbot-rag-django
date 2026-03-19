from sentence_transformers import SentenceTransformer

_embedder = None

def get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer("BAAI/bge-m3")
        _embedder.eval()   # <<< สำคัญที่สุด
    return _embedder

def clean_text(t: str) -> str:
    return " ".join((t or "").strip().split())

def embed_text(text: str):
    text = clean_text(text)
    model = get_embedder()
    return model.encode(text, normalize_embeddings=True).tolist()
