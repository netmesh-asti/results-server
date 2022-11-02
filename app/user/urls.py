from django.urls import path
from rest_framework import routers

from user import views

router = routers.SimpleRouter()

app_name = 'user'
router.register(
    r'manage',
    views.ManageFieldUsersView,
    basename='user')

urlpatterns = [
    # path('', views.ListUsersView.as_view(), name='users'),
    # path('create/', views.CreateUserView.as_view(), name='create'),
    path('profile/', views.UserProfileView.as_view(), name='my-profile'),
    path('token/', views.AuthTokenView.as_view(), name='token'),
    path('geo/csv/<str:csv_id>', views.csv1, name='csv1'),
]

urlpatterns += router.urls
