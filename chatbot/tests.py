from django.test import TestCase, Client
from .models import KnowledgeDocument, DocumentChunk, Conversation, Message
from .rag.embeddings import embed


class EmbeddingTests(TestCase):
    def test_embed_returns_correct_dimensions(self):
        """A piece of text should turn into a 768-number vector."""
        result = embed("hello world")
        self.assertEqual(len(result), 768)

    def test_embed_returns_a_list_of_numbers(self):
        result = embed("test")
        self.assertTrue(all(isinstance(x, float) for x in result))


class RetrievalTests(TestCase):
    def setUp(self):
        """Create one real document + chunk before each test."""
        doc = KnowledgeDocument.objects.create(
            title="Refund Policy",
            source_text="Our refund policy is 30 days from purchase."
        )
        DocumentChunk.objects.create(
            document=doc,
            text="Our refund policy is 30 days from purchase.",
            embedding=embed("Our refund policy is 30 days from purchase.")
        )

    def test_retrieval_finds_relevant_chunk(self):
        """Asking about refunds should find the refund policy chunk,
        even with completely different wording."""
        from .rag.retriever import retrieve_chunks
        results = retrieve_chunks("how long do I have to return something")
        self.assertEqual(len(results), 1)
        self.assertIn("30 days", results[0].text)


class ChatEndpointTests(TestCase):
    def test_chat_view_requires_a_message(self):
        """Posting with no message should return a 400 error, not crash."""
        client = Client()
        response = client.post("/api/chat/", {}, content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_chat_view_creates_a_conversation(self):
        """A real chat request should create a Conversation and 2 Messages."""
        client = Client()
        response = client.post(
            "/api/chat/",
            {"message": "what is your refund policy"},
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Conversation.objects.count(), 1)
        self.assertEqual(Message.objects.count(), 2)  # one user, one bot


class EscalationLogicTests(TestCase):
    def test_conversation_starts_as_bot_active(self):
        """A brand new conversation should default to bot_active, not escalated."""
        conversation = Conversation.objects.create()
        self.assertEqual(conversation.status, "bot_active")