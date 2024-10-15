from django.http import JsonResponse
from outline_api.prometheus import headers
from rest_framework.response import Response
from core.servers.models import OutlineServerKey
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from django.http import JsonResponse
import hashlib
import logging

logger = logging.getLogger(__name__)

class GetConfigByKeyViewSet(APIView):

    def get(self, request):
        try:
            key = request.query_params.get("key")
            server_key = OutlineServerKey.objects.filter(id=key).first()
            data = {
                "server": server_key.server.host,
                "server_port": int(server_key.port),
                "password": server_key.password,
                "method": server_key.method
            }
            return JsonResponse(data, status=200)
        except:
            return JsonResponse({"status": False}, status=200)