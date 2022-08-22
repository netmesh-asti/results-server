from django.urls import path

from user import views

app_name = 'user'

urlpatterns = [
    path('', views.ListUsersView.as_view(), name='users'),
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('myprofile/', views.ManageUserView.as_view(), name='my-profile'),
    path('manage/', views.ManageFieldUsersView.as_view(),
         name='manage-account'),
    path('token/', views.AuthTokenView.as_view(), name='token')
]
