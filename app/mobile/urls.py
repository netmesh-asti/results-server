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
         name='result'),
    path('userntcresults/',
         views.SelfListNtcMobileTestsView.as_view(),
         name='userntcmobile'
         ),
    path('userntcresultdetail/<test_id>',
         views.RetrieveUserMobileResultDetail.as_view(),
         name='userntcmobiledetail'
         ),
    path('mobiledevicelist/',
         views.ListUserMobileDevices.as_view(),
         name='mobiledevicelist'
         ),
    path('mobiledevicedetail/<serial_number>',
         views.RetrieveUserMobileDeviceDetail.as_view(),
         name='mobiledevicedetail'
         ),
    # path('android/list', views.ListAndroidResView.as_view(), name='list')
]

urlpatterns += router.urls
