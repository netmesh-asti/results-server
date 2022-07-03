from django.urls import path, include
from user import views

app_name = 'user'

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('me/', views.ManageUserView.as_view(), name='me'),
    path('account/', views.ManageFieldUsersView.as_view(), name='account'),
    path('token/', views.CreateTokenView.as_view(), name='token')
]
