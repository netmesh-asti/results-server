from django.urls import path

from rfc6349 import views

app_name = "rfc6349"

urlpatterns = [
    path("result/", views.Rfc6349ResView.as_view(), name="result"),
    path("device/", views.RfcDeviceView.as_view(), name="device")
    ]
