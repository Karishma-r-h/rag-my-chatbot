from django.db import models
from pgvector.django import VectorField


class KnowledgeDocument(models.Model):
    title = models.CharField(max_length=255)
    source_text = models.TextField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class DocumentChunk(models.Model):
    document = models.ForeignKey(KnowledgeDocument, on_delete=models.CASCADE, related_name="chunks")
    text = models.TextField()
    embedding = VectorField(dimensions=384)  # size depends on the embedding model we use later

    def __str__(self):
        return f"Chunk of {self.document.title}"


class Conversation(models.Model):
    STATUS_CHOICES = [
        ("bot_active", "Bot Active"),
        ("escalated", "Escalated"),
        ("closed", "Closed"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="bot_active")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation #{self.id} ({self.status})"


class Message(models.Model):
    ROLE_CHOICES = [
        ("user", "User"),
        ("bot", "Bot"),
        ("agent", "Agent"),
    ]
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    confidence_score = models.CharField(max_length=10, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role}: {self.content[:30]}"


class Agent(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name