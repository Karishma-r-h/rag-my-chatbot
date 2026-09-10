from pgvector.django import CosineDistance
from chatbot.models import DocumentChunk
from chatbot.rag.embeddings import embed


def retrieve_chunks(query_text, top_k=3):
    """Find the chunks whose meaning is closest to the query."""
    query_embedding = embed(query_text)
    return (
        DocumentChunk.objects
        .annotate(distance=CosineDistance("embedding", query_embedding))
        .order_by("distance")[:top_k]
    )