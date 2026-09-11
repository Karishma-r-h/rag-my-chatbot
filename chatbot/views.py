from .kafka_producer import publish_chat_event
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Conversation, Message
from .rag.retriever import retrieve_chunks
from .rag.answer import answer_question


def chat_page(request):
    return render(request, "chatbot/chat.html")


@csrf_exempt
@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def chat_view(request):
    question = request.data.get("message")
    conversation_id = request.data.get("conversation_id")

    if not question:
        return Response({"error": "message is required"}, status=400)

    if conversation_id:
        conversation, _ = Conversation.objects.get_or_create(id=conversation_id)
    else:
        conversation = Conversation.objects.create()

    user_message = Message.objects.create(conversation=conversation, role="user", content=question)
    publish_chat_event(conversation.id, user_message.id, "user", question)

    chunks = retrieve_chunks(question)
    answer, confidence = answer_question(question, chunks)

    bot_message = Message.objects.create(conversation=conversation, role="bot", content=answer, confidence_score=confidence)
    publish_chat_event(conversation.id, bot_message.id, "bot", answer, confidence)

    if confidence == "low":
        conversation.status = "escalated"
        conversation.save()

    return Response({
        "conversation_id": conversation.id,
        "answer": answer,
        "confidence": confidence,
    })