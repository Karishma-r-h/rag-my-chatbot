from django.core.management.base import BaseCommand
from confluent_kafka import Consumer
import json

FRUSTRATION_WORDS = [
    "frustrated", "annoyed", "angry", "useless", "terrible", "worst",
    "not helpful", "doesn't work", "waste of time", "ridiculous", "unacceptable"
]


class Command(BaseCommand):
    help = "Listens to chat-events and flags frustrated-sounding user messages"

    def handle(self, *args, **options):
        consumer = Consumer({
            "bootstrap.servers": "localhost:9092",
            "group.id": "sentiment-consumer",
            "auto.offset.reset": "earliest",
        })
        consumer.subscribe(["chat-events"])

        self.stdout.write("Sentiment consumer running... (Ctrl+C to stop)")

        try:
            while True:
                msg = consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                event = json.loads(msg.value())

                if event.get("role") != "user":
                    continue  # only check what the user said, not the bot's replies

                content = event.get("content", "").lower()
                is_frustrated = any(word in content for word in FRUSTRATION_WORDS)

                if is_frustrated:
                    self.stdout.write(self.style.WARNING(
                        f"⚠️  Frustration detected in conversation {event['conversation_id']}: \"{event['content']}\""
                    ))
                else:
                    self.stdout.write(f"OK: {event['content'][:50]}...")
        except KeyboardInterrupt:
            consumer.close()
            