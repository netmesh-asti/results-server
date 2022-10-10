from django.urls import path
from rest_framework import routers

from rfc6349 import views

app_name = "rfc6349"

router = routers.SimpleRouter()
router.register(r"device", views.RfcDeviceView, basename="rfc-device")
router.register(r"ntc", views.AdminRfcTestsView, basename="rfc-tests")
urlpatterns = [
    path("result/", views.Rfc6349ResView.as_view(), name="result"),
    # path("device/", views.RfcDeviceView.as_view(), name="device")
    ]

urlpatterns += router.urls
