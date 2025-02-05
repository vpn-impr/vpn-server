import aiohttp
from PIL import Image, ImageDraw
from io import BytesIO
from aiogram.types import FSInputFile
import brotli

async def download_image(session: aiohttp.ClientSession, url: str) -> Image.Image:
    """Асинхронно загружает изображение по ссылке."""
    async with session.get(url) as response:
        image_bytes = await response.read()
        return Image.open(BytesIO(image_bytes))


async def download_image_as_pil(file_id: str, bot):
    # Получаем информацию о файле
    file = await bot.get_file(file_id)

    # Формируем URL для скачивания файла
    file_url = f"https://api.telegram.org/file/bot{bot.token}/{file.file_path}"

    # Скачиваем изображение через aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.get(file_url) as resp:
            file_content = await resp.read()

    # Преобразуем байты в изображение с помощью PIL
    bt = BytesIO(file_content)

    return bt

def apply_watermark(image, watermark: Image.Image) -> Image.Image:
    if isinstance(image, BytesIO):
        image = Image.open(image)

    position = (
        (image.width - watermark.width) // 2,
        (image.height - watermark.height) // 2,
    )

    image_with_watermark = image.copy()
    image_with_watermark.paste(watermark, position, watermark)
    return image_with_watermark

def get_realty_data_by_id(self, id):
    s = self.session
    response = s.get(f'https://api-statements.tnet.ge/v1/statements/{id}')
    # print(response.json())
    rdata = response.json()['data']['statement']
    images_links = []
    data = {
        'myhome_id': str(rdata['id'])
    }
    # get images
    # print(rdata['gallery'])
    for item in rdata['gallery']:
        link = item['image']['thumb']
        images_links.append(link)
    data['images_links'] = images_links
    # pprint(data)
    return data

async def aget_realty_data_by_id(id) -> dict:
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'x-website-key': 'myhome',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'referer': 'https://www.myhome.ge/',
        'priority': 'u=1, i',
        'origin': 'https://www.myhome.ge',
        'host': 'api-statements.tnet.ge',
        'locale': 'en',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,ru;q=0.7',
        'connection': 'keep-alive',
        'Cache-Control': 'no-cache'
    }
    session = aiohttp.ClientSession(headers=headers)
    url = f'https://api-statements.tnet.ge/v1/statements/{id}'

    async with session.get(url) as response:
        rdata = (await response.json())['data']['statement']
        images_links = [item['image']['thumb'] for item in rdata['gallery']]
        await session.close()
        return {
            'myhome_id': str(rdata['id']),
            'images_links': images_links
        }

