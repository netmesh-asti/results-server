from django.urls import path

from user import views

app_name = 'user'

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('account/', views.ManageFieldUsersView.as_view(), name='account'),
    path('token/', views.CreateTokenView.as_view(), name='token'),

]
