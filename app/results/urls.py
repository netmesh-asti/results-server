from django.urls import path

from results import views


app_name = 'results'


urlpatterns = [
    path('android/create',
         views.CreateAndroidResView.as_view(),
         name='create'
         ),
    path('android/list', views.ListAndroidResView.as_view(), name='list')
]
