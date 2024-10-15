from rest_framework.response import Response
from core.servers.models import OutlineServerKey
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView

class GetConfigByKeyViewSet(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request):
        try:
            key = request.query_params.get("key")
            server_key = OutlineServerKey.objects.filter(id=key).first()
            data = {
                "status": True,
                "server": server_key.server.host,
                "server_port": server_key.port,
                "password": server_key.password,
                "method": server_key.method
            }
            return Response(data)
        except:
            return Response({"status": False})