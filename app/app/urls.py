from django.contrib import admin
from django.urls import path
from django.urls import include
from drf_spectacular.views import (
        SpectacularAPIView,
        SpectacularSwaggerView,
        )

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='api-schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(
        url_name='api-schema'),
        name='api-docs'),
    path('api/user/', include('user.urls')),
    path('api/mobile/', include('mobile.urls')),
    path('api/rfc6349/', include('rfc6349.urls')),
    path('api/server/', include('server.urls')),
]

# urlpatterns += [path('api-auth/', include('rest_framework.urls')), ]
