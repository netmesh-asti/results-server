from django.urls import path
from nro import views

app_name = "nro"

urlpatterns = [
    path("office/", views.NroOfficeView.as_view(), name="office-detail" )
]
