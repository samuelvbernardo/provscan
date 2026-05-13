from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from omr.views import serve_protected_media

from .router.api import api_urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "api/",
        include(
            (api_urls, "myproject.router.api.api_urls"),
            namespace="api",
        ),
    ),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    # Mídia protegida por JWT — substitui a exposição pública de /media/
    path("api/media/<path:path>", serve_protected_media, name="protected-media"),
]

# Em desenvolvimento serve mídia localmente (sem autenticação, apenas para conveniência)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
