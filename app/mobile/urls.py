from django.urls import path

from mobile import views


app_name = 'android'


urlpatterns = [
    path('android/store',
         views.CreateAndroidResView.as_view(),
         name='store'
         ),
    path('android/list', views.ListAndroidResView.as_view(), name='list')
]
