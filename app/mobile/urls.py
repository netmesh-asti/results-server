from django.urls import path
from rest_framework.routers import DefaultRouter

from mobile import views


app_name = 'mobile'

router = DefaultRouter()
router.register(
    r'ntc/result',
    views.AdminMobileTestsView,
    basename="speedtest"
)
router.register(
    r'ft/result',
    views.UserMobileTestsView,
    basename="user-tests"
)
router.register(
    r'device/manage',
    views.ManageMobileDeviceView,
    basename="mobile-device"
)


urlpatterns = [
    path('result/',
         views.MobileResultsView.as_view(),
         name='result'),
    # path('userntcresults/',
    #      views.SelfListNtcMobileTestsView.as_view(),
    #      name='userntcmobile'
    #      ),
    # path('userntcresultdetail/<test_id>',
    #      views.RetrieveUserMobileResultDetail.as_view(),
    #      name='userntcmobiledetail'
    #      ),
    path('ft/device/',
         views.ListUserMobileDevices.as_view(),
         name='mobiledevicelist'
         ),
    path('ft/device/<serial_number>',
         views.RetrieveUserMobileDeviceDetail.as_view(),
         name='mobiledevicedetail'
         ),

    path('result/datatable',
         views.MobileResultsList,
         name='mobileresultslist'
         ),
    path('result/csv',
         views.MobileResultCSV.as_view(),
         name='mobileresultcsv'
         ),
    path('result/speedtest/<str:name>',
         views.speedtest_performance_detail,
         name='speedtestperformancedetail'
         ),
    # path('android/list', views.ListAndroidResView.as_view(), name='list')
]

urlpatterns += router.urls
