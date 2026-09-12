from django.core.management.base import BaseCommand
from confluent_kafka import Consumer
import json
import os
import django

FRUSTRATION_WORDS = [
    "frustrated", "annoyed", "angry", "useless", "terrible", "worst",
    "not helpful", "doesn't work", "waste of time", "ridiculous", "unacceptable"
]


class Command(BaseCommand):
    help = "Listens to chat-events and escalates conversations that need a human"

    def handle(self, *args, **options):
        from chatbot.models import Conversation

        consumer = Consumer({
            "bootstrap.servers": "localhost:9092",
            "group.id": "escalation-consumer",
            "auto.offset.reset": "earliest",
        })
        consumer.subscribe(["chat-events"])

        self.stdout.write("Escalation consumer running... (Ctrl+C to stop)")

        try:
            while True:
                msg = consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                event = json.loads(msg.value())

                conversation_id = event.get("conversation_id")
                if not conversation_id:
                    continue

                should_escalate = False
                reason = ""

                if event.get("role") == "bot" and event.get("confidence") == "low":
                    should_escalate = True
                    reason = "low confidence answer"

                if event.get("role") == "user":
                    content = event.get("content", "").lower()
                    if any(word in content for word in FRUSTRATION_WORDS):
                        should_escalate = True
                        reason = "user sounds frustrated"

                if should_escalate:
                    try:
                        conversation = Conversation.objects.get(id=conversation_id)
                        if conversation.status != "escalated":
                            conversation.status = "escalated"
                            conversation.save()
                            self.stdout.write(self.style.ERROR(
                                f"🚨 Escalated conversation {conversation_id} — reason: {reason}"
                            ))
                    except Conversation.DoesNotExist:
                        pass
        except KeyboardInterrupt:
            consumer.close()