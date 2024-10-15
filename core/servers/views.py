from django.http import JsonResponse
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
            # Преобразуем данные ответа в строку для хеширования
            content_str = str(data).encode('utf-8')

            # Создаем хеш для ETag
            etag = hashlib.md5(content_str).hexdigest()

            # Проверяем, отправлял ли клиент заголовок If-None-Match
            if_none_match = request.headers.get('If-None-Match')

            if if_none_match == etag:
                # Возвращаем 304 Not Modified, если ETag совпадает
                return Response(status=304)

            # Возвращаем ответ с ETag
            response = Response(data)
            response['ETag'] = etag
            return Response(data)
        except:
            return Response({"status": False})