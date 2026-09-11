import json
from confluent_kafka import Producer

producer = Producer({"bootstrap.servers": "localhost:9092"})


def publish_chat_event(conversation_id, message_id, role, content, confidence=None):
    event = {
        "conversation_id": conversation_id,
        "message_id": message_id,
        "role": role,
        "content": content,
        "confidence": confidence,
    }
    producer.produce("chat-events", json.dumps(event).encode())
    producer.flush()