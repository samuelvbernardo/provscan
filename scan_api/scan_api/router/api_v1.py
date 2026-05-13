from django.conf.urls import include
from django.urls import path

from accounts.api.v1 import router as accounts_router
from core.api.v1 import router as core_router
from omr.api.v1 import router as omr_router

api_v1_urls = [
    path("", include((accounts_router.urlpatterns, "accounts"), namespace="accounts")),
    path("", include((core_router.urlpatterns, "core"), namespace="core")),
    path("", include((omr_router.urlpatterns, "omr"), namespace="omr")),
]
