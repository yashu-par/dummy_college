from django.urls import path
from . import views

urlpatterns = [
    path('send_connection_request/', views.send_connection_request, name='send_connection_request'),
    path('accept_connection_request/', views.accept_connection_request, name='accept_connection_request'),
    path('reject_connection_request/', views.reject_connection_request, name='reject_connection_request'),
    path('cancel_connection_request/', views.cancel_connection_request, name='cancel_connection_request'),
] 