import os
from google import genai

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def embed(text: str):
    """Turn text into a 768-number vector representing its meaning, using Gemini's API."""
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
        config={"output_dimensionality": 768},
    )
    return result.embeddings[0].values