from django.urls import path
from .views import SearchResultsListView, filterView

app_name = 'search'

urlpatterns = [
    path('', SearchResultsListView.as_view(), name='search_result'),
    path('advanced/', filterView, name='advanced_search_result'),
]
