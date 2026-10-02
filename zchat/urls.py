from django.urls import path

from .views import MessageView

urlpatterns = [
    # GET /api/messages/ [JWT], header: receiver=<user id> -> [{id, sender, receiver, content}]
    # POST /api/messages/ [JWT], body: {receiver, content} -> 201 {id, sender, receiver, content}
    path("api/messages/", MessageView.as_view(), name="messages"),
]
