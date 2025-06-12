from django.urls import path
from .views import create_log, list_logs

app_name = 'logging_api'

urlpatterns = [
    path('logs/create/', create_log, name='create_log'),
    path('logs/', list_logs, name='list_logs'),
]
