import os
import json
import requests
import redis
from django.core.management.base import BaseCommand
from confluent_kafka import Consumer

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
                if msg.error():
                    continue
                try:
                    event = json.loads(msg.value())
                except (json.JSONDecodeError, TypeError):
                    continue

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
                            self.send_slack_alert(conversation_id, reason, event.get("content", ""))
                    except Conversation.DoesNotExist:
                        pass
        except KeyboardInterrupt:
            consumer.close()

    def send_slack_alert(self, conversation_id, reason, last_message):
        webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
        self.stdout.write(f"DEBUG: webhook_url is {webhook_url}")
        if not webhook_url:
            self.stdout.write("DEBUG: no webhook URL found, skipping")
            return

        response = requests.post(webhook_url, json={
            "text": f"🚨 *Conversation #{conversation_id} needs a human*\n*Reason:* {reason}\n*Last message:* {last_message}"
        })
        self.stdout.write(f"DEBUG: Slack response {response.status_code} - {response.text}")

        redis_client = redis.from_url(os.environ["REDIS_URL"])
        redis_client.publish("agent-notifications", json.dumps({
            "conversation_id": conversation_id,
            "reason": reason,
            "last_message": last_message,
        }))