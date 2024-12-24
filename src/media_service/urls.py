"""
URL configuration for media_service project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView
from drf_spectacular.views import SpectacularRedocView, SpectacularSwaggerView

from src.media_service.service_settings import get_settings
service_settings = get_settings()

urlpatterns = [
    # path('api/', include("src.api.urls")),
    path('admin/', admin.site.urls),
]

if service_settings.ENVIRONMENT == 'dev':
    import debug_toolbar

    urlpatterns += [
        path('redoc', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
        path('docs', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
        path('schema', SpectacularAPIView.as_view(), name='schema'),

        path('__debug__/', include(debug_toolbar.urls)),
    ]
