import os
import re
from google import genai
from tavily import TavilyClient

gemini_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

LIVE_KEYWORDS = [
    "today", "current", "currently", "right now", "latest", "live",
    "happening", "this week", "news", "weather", "temperature",
    "score", "price", "stock", "now"
]

# If the closest matching chunk is farther than this, treat it as "not really relevant"
DISTANCE_THRESHOLD = 0.5


def needs_live_search(question: str) -> bool:
    q = question.lower()
    return any(word in q for word in LIVE_KEYWORDS)


def answer_question(user_question, retrieved_chunks):
    context_text = "\n\n".join(
        f"[doc:{c.document_id}] {c.text}" for c in retrieved_chunks
    )

    # Signal 1: retrieval-based confidence
    retrieval_low_confidence = True
    if retrieved_chunks:
        closest_distance = min(c.distance for c in retrieved_chunks)
        retrieval_low_confidence = closest_distance > DISTANCE_THRESHOLD

    live_info = ""
    if needs_live_search(user_question):
        search_results = tavily_client.search(user_question, max_results=3)
        live_info = "\n\n".join(
            f"{r['title']}: {r['content']}" for r in search_results.get("results", [])
        )

    prompt = f"""You are a helpful, friendly assistant that can answer any question.
If asked who created you, made you, or built you, say: "I was built by Karishma as a personal project, using Google's Gemini AI under the hood."
If CONTEXT below is relevant, use it.
If LIVE WEB RESULTS are provided, use them for anything current or time-sensitive.
Otherwise, just answer the question normally using your own knowledge.
Only say you're not sure if you genuinely don't know the answer at all.
Sprinkle in a few relevant emojis naturally where they fit the content.

After your answer, on a new line, add a hidden confidence tag like this:
<confidence>high</confidence> or <confidence>medium</confidence> or <confidence>low</confidence>
Use "low" if you are genuinely unsure or guessing.

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
    raw_text = response.text

    # Pull out the hidden confidence tag, then strip it from what the user sees
    match = re.search(r"<confidence>(low|medium|high)</confidence>", raw_text, re.IGNORECASE)
    self_reported_confidence = match.group(1).lower() if match else "medium"
    clean_answer = re.sub(r"<confidence>.*?</confidence>", "", raw_text, flags=re.IGNORECASE).strip()

    # Combine both signals: if EITHER signal is worried, mark it low
    final_confidence = "low" if (retrieval_low_confidence and self_reported_confidence == "low") else self_reported_confidence

    return clean_answer, final_confidence