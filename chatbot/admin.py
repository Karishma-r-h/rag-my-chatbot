from django.contrib import admin
from .models import KnowledgeDocument, DocumentChunk, Conversation, Message, Agent

admin.site.register(KnowledgeDocument)
admin.site.register(DocumentChunk)
admin.site.register(Conversation)
admin.site.register(Message)
admin.site.register(Agent)