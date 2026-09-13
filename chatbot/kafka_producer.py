import json

try:
    from confluent_kafka import Producer
    producer = Producer({"bootstrap.servers": "localhost:9092"})
    KAFKA_AVAILABLE = True
except ImportError:
    producer = None
    KAFKA_AVAILABLE = False


def publish_chat_event(conversation_id, message_id, role, content, confidence=None):
    if not KAFKA_AVAILABLE:
        return  # Kafka isn't installed here (e.g. on Render) — safe to skip

    event = {
        "conversation_id": conversation_id,
        "message_id": message_id,
        "role": role,
        "content": content,
        "confidence": confidence,
    }
    try:
        producer.produce("chat-events", json.dumps(event).encode())
        producer.flush(timeout=1)
    except Exception:
        pass