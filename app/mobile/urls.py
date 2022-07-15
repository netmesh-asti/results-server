from django.urls import path

from mobile import views


app_name = 'mobile'


urlpatterns = [
    path('result/',
         views.CreateAndroidResView.as_view(),
         name='result'
         ),
    # path('android/list', views.ListAndroidResView.as_view(), name='list')
]
