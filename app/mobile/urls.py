from django.urls import path

from mobile import views


app_name = 'android'


urlpatterns = [
    path('android/',
         views.CreateAndroidResView.as_view(),
         name='result'
         ),
    # path('android/list', views.ListAndroidResView.as_view(), name='list')
]