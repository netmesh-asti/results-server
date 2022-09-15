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
    # path('android/list', views.ListAndroidResView.as_view(), name='list')
]
