from django.urls import path
from .views import (AccountDeleteView, ProfileEditView, ProfilePageView, SignUpView)

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('edit_profile/<slug:username>/', ProfileEditView.as_view(), name='edit_profile'),
    path('profile/<slug:username>/', ProfilePageView.as_view(), name='view_profile'),
    path('<int:pk>/delete/', AccountDeleteView.as_view(), name='account_delete'),
]
