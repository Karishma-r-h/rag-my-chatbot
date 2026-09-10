from sentence_transformers import SentenceTransformer

# This loads the AI model into memory once, the first time it's needed.
# First run will download the model (~90MB) — that's normal, only happens once.
_model = SentenceTransformer("all-MiniLM-L6-v2")


def embed(text: str):
    """Turn a piece of text into a list of 384 numbers representing its meaning."""
    vector = _model.encode(text)
    return vector.tolist()