from django.urls import path
from rest_framework.routers import DefaultRouter

from mobile import views


app_name = 'mobile'

router = DefaultRouter()
router.register(
    r'ntc/list-result',
    views.ListNtcMobileTestsView,
    basename="ntc")

urlpatterns = [
    path('result/',
         views.AndroidResultsView.as_view(),
         name='result'
         ),
    # path('ntcresults/',
    #      views.ListNtcMobileTestsView.as_view(),
    #      name='ntcmobile'
    #      ),
    # path('android/list', views.ListAndroidResView.as_view(), name='list')
]

urlpatterns += router.urls
