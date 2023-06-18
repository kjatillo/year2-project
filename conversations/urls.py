from django.urls import path
from .views import ConversationDeleteView, detail, inbox, new_conversation

app_name = 'conversation'

urlpatterns = [
    path('', inbox, name='inbox'),
    path('<int:pk>/', detail, name='conversation_detail'),
    path('new/<uuid:service_pk>/', new_conversation, name='new_conversation'),
    path('<int:pk>/delete/', ConversationDeleteView.as_view(), name='delete_conversation'),
]
