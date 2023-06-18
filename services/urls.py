from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('', views.service_list, name = 'all_services'),
    path('<uuid:category_id>/', views.service_list, name = 'services_by_category'),
    path('<uuid:category_id>/<uuid:service_id>/', views.service_detail, name = 'service_detail'),
    path('new/', views.ServiceCreateView.as_view(), name='post_service'),
    path('<uuid:service_id>/edit/', views.ServiceUpdateView.as_view(), name='edit_service'),
    path('<uuid:service_id>/delete/', views.ServiceDeleteView.as_view(), name='delete_service'),
    path('<uuid:service_id>/submit_review/', views.submit_review, name='submit_review'),
    path('provider/', views.provider_service_list, name = 'service_provider'),
]
