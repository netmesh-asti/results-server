from django.contrib import admin
from django.urls import path
from django.urls import include
from drf_spectacular.views import (
        SpectacularAPIView,
        SpectacularSwaggerView,
        )

urlpatterns = [
    path('portal/admin/', admin.site.urls),
    path('portal/api/schema/', SpectacularAPIView.as_view(), name='api-schema'),
    path('portal/api/docs/', SpectacularSwaggerView.as_view(
        url_name='api-schema'),
        name='api-docs'),
    path('portal/api/user/', include('user.urls')),
    path('portal/api/mobile/', include('mobile.urls')),
    path('portal/api/rfc6349/', include('rfc6349.urls')),
    path('portal/api/server/', include('server.urls')),
    path('portal/api/accounts/', include('django.contrib.auth.urls')),
    path('portal/api/nro/', include('nro.urls'))
]

# urlpatterns += [path('api-auth/', include('rest_framework.urls')), ]
