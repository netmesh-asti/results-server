from django.urls import path

from mobile import views


app_name = 'mobile'


urlpatterns = [
    path('result/',
         views.CreateAndroidResView.as_view(),
         name='result'
         ),
    path('ntcresults/',
         views.ListNtcMobileTestsView.as_view(),
         name='ntcmobile'
         ),
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
