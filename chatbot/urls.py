from django.urls import path
from .views import chat_view, chat_page, agent_dashboard, agent_event_stream

urlpatterns = [
    path("chat/", chat_view, name="chat"),
    path("chat-ui/", chat_page, name="chat-ui"),
    path("dashboard/", agent_dashboard, name="dashboard"),
    path("events/", agent_event_stream, name="events"),
]