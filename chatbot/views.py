from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Conversation, Message
from .rag.retriever import retrieve_chunks
from .rag.answer import answer_question


@api_view(["POST"])
def chat_view(request):
    question = request.data.get("message")
    conversation_id = request.data.get("conversation_id")

    if not question:
        return Response({"error": "message is required"}, status=400)

    if conversation_id:
        conversation, _ = Conversation.objects.get_or_create(id=conversation_id)
    else:
        conversation = Conversation.objects.create()

    Message.objects.create(conversation=conversation, role="user", content=question)

    chunks = retrieve_chunks(question)
    answer = answer_question(question, chunks)

    Message.objects.create(conversation=conversation, role="bot", content=answer)

    return Response({
        "conversation_id": conversation.id,
        "answer": answer,
    })