import logging
from django.contrib import admin
from django.urls import include, path

from core.servers.views import GetConfigByKeyViewSet

logger = logging.getLogger(__name__)


urlpatterns = [
    path("admin/", admin.site.urls),
    path('config/', GetConfigByKeyViewSet.as_view())
]

#urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
