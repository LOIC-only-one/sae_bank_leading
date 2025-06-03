from django.urls import include, path

urlpatterns = [
    path('', include('frontend_app.urls')),
]
