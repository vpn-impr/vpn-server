from django.http import JsonResponse
from rest_framework.response import Response
from core.servers.models import OutlineServerKey
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from django.http import HttpResponse
import logging
import json

logger = logging.getLogger(__name__)

class GetConfigByKeyViewSet(APIView):
    renderer_classes = [JSONRenderer]

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
            # Преобразуем данные в JSON-строку с отступами
            json_data = json.dumps(data, indent=4)

            # Создаем HTTP-ответ с типом содержимого 'application/json'
            response = HttpResponse(json_data, content_type='application/json')

            # Добавляем заголовок для предложения файла к скачиванию
            response['Content-Disposition'] = 'attachment; filename="data.json"'
            return response
        except:
            return Response({"status": False})