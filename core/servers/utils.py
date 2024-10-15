from asyncio import Server

from django.conf import settings

from core.servers.models import Country, OutlineServer, OutlineServerKey, City
from core.users.models import TelegramUser
from asgiref.sync import sync_to_async
from django.db.models import Value
from django.db.models.functions import Concat

from core.utils.datetimes import get_now

from core.outline.utils import OutlineVPN


@sync_to_async
def get_available_countries():
    queryset = Country.objects.filter(
        city__city_outline_servers__active=True
    ).distinct()
    return queryset


@sync_to_async
def get_available_cities(id=None):
    queryset = City.objects.filter(
        city_outline_servers__active=True
    )
    queryset = queryset.annotate(
        dynamic_name=Concat(
            'name',
            Value(', '),
            'country__name',
            Value(' '),
            'country__emoji'
        )
    )
    if id:
        return queryset.filter(id=id).first()
    return queryset.distinct().order_by('country')


@sync_to_async
def get_server_name_by_key(key_id):
    if key_id is None:
        return 'Локация не выбрана'
    outline_server_key = OutlineServerKey.objects.get(id=key_id)
    queryset = OutlineServer.objects.filter(id=outline_server_key.server_id)
    queryset = queryset.annotate(
        dynamic_name=Concat(
            'city__name',
            Value(', '),
            'city__country__name',
            Value(' '),
            'city__country__emoji'
        )
    )
    dynamic_name = queryset.first().dynamic_name
    return dynamic_name

@sync_to_async
def get_can_change_location_by_key(key_id):
    if key_id is None:
        return True
    return True
    outline_server_key = OutlineServerKey.objects.get(id=key_id)
    seconds = (get_now() - outline_server_key.created_at).seconds
    if seconds > 60:
        return True
    return False


@sync_to_async
def get_access_key(key_id):
    if key_id is None:
        return None
    access_key = OutlineServerKey.objects.get(id=key_id).access_key
    return access_key

@sync_to_async
def create_new_server_key(server):
    client = OutlineVPN(
        api_url=server.api_url,
        cert_sha256=server.cert_sha_256
    )
    new_key = client.create_key()
    server_key = OutlineServerKey.objects.create(
        external_id=new_key.key_id,
        access_key=new_key.access_url,
        password=new_key.password,
        method=new_key.method,
        port=new_key.port,
        server=server
    )
    return server_key

@sync_to_async
def delete_server_key(server_key):
    client = OutlineVPN(
        api_url=server_key.server.api_url,
        cert_sha256=server_key.server.cert_sha_256
    )
    client.delete_key(server_key.external_id)
    server_key.delete()
    return True

@sync_to_async
def update(server_key):
    server_key.delete()
    return True

@sync_to_async
def outline_server_key_exists(user):
    if user.outline_server_key is None:
        return False
    return True

async def change_user_city(user, city):
    key_exists = await outline_server_key_exists(user)
    if key_exists:
        await delete_server_key(user.outline_server_key)
    if not user.subscription_active():
        return False, 'Подписка закончилась'
    server = await OutlineServer.objects.filter(city=city, active=True).afirst()
    if server is None:
        return False, 'Сервер не доступен. Попробуйте позже или выберете другой город.'
    outline_server_key = await create_new_server_key(server)
    await TelegramUser.objects.filter(id=user.id).aupdate(outline_server_key=outline_server_key)
    return True, outline_server_key

async def get_ssconf(server_key):
    return f'ssconf://{settings.DOMAIN}/config/?key={server_key.id} InterVPN'
