import os
from google import genai
from tavily import TavilyClient

gemini_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

LIVE_KEYWORDS = ["today", "current", "currently", "right now", "latest", "live", "happening", "this week", "news"]


def needs_live_search(question: str) -> bool:
    q = question.lower()
    return any(word in q for word in LIVE_KEYWORDS)


def answer_question(user_question, retrieved_chunks):
    context_text = "\n\n".join(
        f"[doc:{c.document_id}] {c.text}" for c in retrieved_chunks
    )

    live_info = ""
    if needs_live_search(user_question):
        search_results = tavily_client.search(user_question, max_results=3)
        live_info = "\n\n".join(
            f"{r['title']}: {r['content']}" for r in search_results.get("results", [])
        )

    prompt = f"""You are a helpful assistant that can answer any question.
If CONTEXT below is relevant, use it.
If LIVE WEB RESULTS are provided, use them for anything current or time-sensitive.
Otherwise, just answer the question normally using your own knowledge.
Only say you're not sure if you genuinely don't know the answer at all.

CONTEXT:
{context_text if context_text else "(none relevant)"}

LIVE WEB RESULTS:
{live_info if live_info else "(none needed for this question)"}

QUESTION: {user_question}
"""

    response = gemini_client.models.generate_content(
        model="gemini-flash-lite-latest",
        contents=prompt,
    )
    return response.text

    