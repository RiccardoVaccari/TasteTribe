from django.urls import path
from forum.views import *

urlpatterns = [
    path("forum/", ForumHomeView.as_view(), name="forums"),
    path("forum/create/", ForumThreadCreateView.as_view(), name="forum_create_thread"),
    path("forum/thread/<uuid:thread_guid>/", ForumThreadView.as_view(), name="forum_thread"),
    path("forum/thread/toggle_interaction/", toggle_message_interaction, name="toggle_interaction"),
]