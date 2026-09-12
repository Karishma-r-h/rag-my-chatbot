from django.core.management.base import BaseCommand
from confluent_kafka import Consumer
import json


class Command(BaseCommand):
    help = "Listens to chat-events and prints simple analytics"

    def handle(self, *args, **options):
        consumer = Consumer({
            "bootstrap.servers": "localhost:9092",
            "group.id": "analytics-consumer",
            "auto.offset.reset": "earliest",
        })
        consumer.subscribe(["chat-events"])

        message_count = 0
        confidence_counts = {"high": 0, "medium": 0, "low": 0}

        self.stdout.write("Analytics consumer running... (Ctrl+C to stop)")

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
                message_count += 1

                if event.get("confidence") in confidence_counts:
                    confidence_counts[event["confidence"]] += 1

                role = event.get("role", "unknown")
                content = event.get("content", "")
                self.stdout.write(
                    f"[{message_count}] {role}: {content[:50]}... "
                    f"(confidence: {event.get('confidence')})"
                )
                self.stdout.write(f"Totals so far: {confidence_counts}")
        except KeyboardInterrupt:
            consumer.close()