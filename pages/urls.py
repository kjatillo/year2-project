from django.urls import path 
from .views import HomePageView, TeamView

urlpatterns = [
    path('', HomePageView.as_view(), name = 'home'),
    path('team', TeamView.as_view(), name = 'team'),
]
