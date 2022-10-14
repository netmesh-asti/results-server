from django.urls import path

from server import views


app_name = "server"

urlpatterns = [
    path("", views.ServerAPIView.as_view(), name='servers')
    ]
