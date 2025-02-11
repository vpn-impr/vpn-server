from typing import TYPE_CHECKING

import brotli
from aiofiles.os import access
from aiogram import Router
from aiogram.enums.content_type import ContentType
from aiogram.filters import Command
from django.utils.regex_helper import contains

from bot.keyboards import servers_buttons, profile_payed_inline_keyboard, profile_not_payed_inline_keyboard, \
    available_cities_buttons, download_outline_inline_keyboard
from core.servers.utils import get_server_name_by_key, \
    get_can_change_location_by_key, get_access_key, get_available_countries, get_available_cities, change_user_city, \
    get_ssconf
from core.users.utils import get_user
from aiogram.types import Message, CallbackQuery, BufferedInputFile, InputMediaPhoto
from aiogram import F

from core.utils.datetimes import get_now
from PIL import Image, ImageDraw
from io import BytesIO
import aiohttp
from aiogram.types import FSInputFile
from aiogram import types

import re

from core.utils.myhome import aget_realty_data_by_id, download_image, apply_watermark, download_image_as_pil

router = Router()
router.message

WATERMARK_URL = 'https://storage.yandexcloud.net/s3r.aurora-estate.ge/locahost-other/RostomashviliHouse_60.png'


@router.message(Command(commands=["start"]))
async def handle_start_command(message: Message) -> None:
    if message.from_user is None:
        return

    user, is_new = await get_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )

    if is_new:
        await message.answer(
            'Добро пожаловать! 🚀\n\n'
            'Чтобы купить подписку - нажмите кнопку "Оформить подписку"\n'
            'В подписке вам доступны любые локации. Сменить локацию или найти данные для подключения можно через свой профиль'
        )
    else:
        await message.answer("Здравствуйте, вы уже зарегистрированы.")
    await handle_profile_command(message)

#Купить
@router.message(Command(commands=["buy"]))
async def handle_buy_command(message: Message) -> None:
    if message.from_user is None:
        return

    user, is_new = await get_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )

    await message.answer(
        'Тарифы\n\n'
        f'1 Месяц: 500 Рублей\n'
        f'3 Месяца: 1400 Рублей\n'
        f'6 Месяцев: 2700 Рублей\n'
        f'12 Месяцев: 5100 Рублей'
    )
    await message.answer(
        'Чтобы купить или продлить подписку скопируйте это сообщение и отправьте @greenvpnoutline_admin\n'
        f'Ваш ID: {user.id}'
    )

# Купить callback
@router.callback_query(lambda c: c.data and c.data == 'buy_action')
async def handle_buy_callback(callback: CallbackQuery) -> None:
    if callback.from_user is None:
        return

    user, is_new = await get_user(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username,
        first_name=callback.from_user.first_name,
        last_name=callback.from_user.last_name,
    )

    await callback.message.answer(
        'Тарифы\n\n'
        f'1 Месяц: 500 Рублей\n'
        f'3 Месяца: 1400 Рублей\n'
        f'6 Месяцев: 2700 Рублей\n'
        f'12 Месяцев: 5100 Рублей'
    )
    await callback.message.answer(
        'Чтобы купить или продлить подписку скопируйте это сообщение и отправьте @greenvpnoutline_admin\n'
        f'Ваш ID: {user.id}'
    )

# Профиль
@router.message(Command(commands=["profile"]))
async def handle_profile_command(message: Message) -> None:
    if message.from_user is None:
        return

    user, is_new = await get_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )

    subscription_text = 'Подписка: Неактивна\n'
    server_text = None
    reply_markup = await profile_not_payed_inline_keyboard()
    can_change_location = True

    if user.subscription_expire_datetime and user.subscription_expire_datetime > get_now():
        time_remaining = user.subscription_expire_datetime - get_now()

        # Разбиваем разницу на дни, часы, минуты и секунды
        days = time_remaining.days
        hours, remainder = divmod(time_remaining.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        # Формируем текст с оставшимся временем
        subscription_text = f'Подписка: Активна\nДо конца подписки: {days}д {hours}ч {minutes}м'

        server_text = await get_server_name_by_key(user.outline_server_key_id)
        can_change_location = await get_can_change_location_by_key(user.outline_server_key_id)
        reply_markup = await profile_payed_inline_keyboard(can_change_location, user.outline_server_key_id)

    result_text = f'<b>Мой профиль</b>\n\n' + f'{subscription_text}\n'
    if server_text:
        result_text = result_text + f'Локация: {server_text}\n'
    if not can_change_location:
        result_text = result_text + f'\n<i>Смена локации не доступна. Менять локацию можно 1 раз в минуту.</i>\n'

    await message.answer(result_text, reply_markup=reply_markup)

# Скопировать ключ доступа
@router.callback_query(lambda c: c.data and c.data.startswith('get_access_key'))
async def handle_get_access_key_callback(callback: CallbackQuery) -> None:
    if callback.from_user is None:
        return

    user, is_new = await get_user(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username,
        first_name=callback.from_user.first_name,
        last_name=callback.from_user.last_name,
    )

    access_key = await get_access_key(user.outline_server_key_id)
    if access_key is None:
        text = 'Ключ не найден'
    else:
        text = 'Ваш ключ:'
    await callback.message.answer(text)
    if access_key:
        await callback.message.answer(f'{await get_ssconf(access_key)}')


# Города
@router.message(Command(commands=["cities"]))
async def handle_cities_command(message: Message) -> None:
    if message.from_user is None:
        return

    user, is_new = await get_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )

    cities = await get_available_cities()

    if not user.subscription_active():
        text = 'Список достпуных городов в подписке:\n'
        async for city in cities:
            text += f'{city.dynamic_name}\n'
        await message.answer(text)
    else:
        reply_markup = await available_cities_buttons(cities)
        await message.answer('Смена локации. Выберите город:', reply_markup=reply_markup)

@router.callback_query(lambda c: c.data and c.data == 'cities')
async def handle_cities_callback(callback: CallbackQuery) -> None:
    if callback.from_user is None:
        return

    user, is_new = await get_user(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username,
        first_name=callback.from_user.first_name,
        last_name=callback.from_user.last_name,
    )

    cities = await get_available_cities()

    if not user.subscription_active():
        text = 'Список достпуных городов в подписке:\n'
        async for city in cities:
            text += f'{city.dynamic_name}\n'
        await callback.message.answer(text)
    else:
        reply_markup = await available_cities_buttons(cities)
        await callback.message.answer('Смена локации. Выберите город:', reply_markup=reply_markup)

@router.callback_query(lambda c: c.data and c.data.startswith('get_city_'))
async def handle_get_city_callback(callback: CallbackQuery) -> None:
    if callback.from_user is None:
        return

    user, is_new = await get_user(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username,
        first_name=callback.from_user.first_name,
        last_name=callback.from_user.last_name,
    )

    city = await get_available_cities(callback.data.split('get_city_')[-1])
    if city is None:
        await callback.message.answer('Данный город больше не доступен. Попробуйте позже или выберете другой.')

    status, _ = await change_user_city(user, city)
    if status:
        await callback.message.answer(f'Локация успешно изменена.\nНовая локация: {city.dynamic_name}.\nВ следующем сообщении ваш новый ключ.')
        await callback.message.answer(f'{await get_ssconf(_)}')
        await callback.message.edit_reply_markup(reply_markup=None)
    else:
        await callback.message.answer(f'Не удалось сменить локацию: {_}')




# Как настроить
@router.message(Command(commands=["setup"]))
async def handle_setup_command(message: Message) -> None:
    if message.from_user is None:
        return

    user, is_new = await get_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )

    reply_markup = await download_outline_inline_keyboard()

    await message.answer(
        '<b>Как настроить GreenVPN</b>\n\n'
        'GreenVPN настраивается буквально в два-три клика.\n\n'
        'Нужно скачать приложение Outline, оно есть на любой системе (Android, iOS, Windows, MacOS).\n'
        'Ссылки для скачивания мы прикрепили внизу этого сообщения.\n\n'
        'После этого мы пришлём ссылку, в которой содержится уникальный ключ. Если Outline уже установлен, то при переходе по ссылке, ключ применится автоматически и VPN заработает).\n\n'
        'Если что-то в процессе не получится или у останутся вопросы, в любое время можно написать админу @greenvpnoutline_admin .\n\n',
        reply_markup=reply_markup
    )

# Обработчик для получения фото
@router.message(F.photo)
async def handle_images(message: Message) -> None:
    if message.from_user is None:
        return
    # Загружаем водяной знак
    outputs = []
    async with aiohttp.ClientSession() as session:
        watermark = await download_image(session, WATERMARK_URL)

        # Список для хранения обработанных изображений
        image_buffers = []
        # Проверяем, если это одиночное изображение
        if message.photo:
            #print(message.photo)
            photo = message.photo[-1]  # Берем самое качественное фото
            # Получаем ID файла фотографии
            file_id = photo.file_id
            file = await download_image_as_pil(file_id, message.bot)
            try:
                image_with_watermark = apply_watermark(file, watermark)
                file.close()

                # Сохраняем изображение с водяным знаком в байтовый поток
                output = BytesIO()
                image_with_watermark.save(output, format="JPEG")
                output.seek(0)

                image_buffers.append(
                    types.InputMediaPhoto(
                        media=BufferedInputFile(output.getvalue(), filename="image_with_watermark.jpg"))
                )
                outputs.append(output)

            except Exception as e:
                await message.answer(f"Ошибка при обработке изображения: {str(e)}")

        # Если есть обработанные изображения, отправляем их обратно
        if image_buffers:
            batch_size = 10  # Отправляем не более 10 изображений за раз
            for i in range(0, len(image_buffers), batch_size):
                media_group = image_buffers[i:i + batch_size]
                await message.answer_media_group(media_group)
    for output in outputs:
        output.close()


# Выгрузка фото с myhome.ge
@router.message()
async def handle_myhome_get_image_command(message: Message) -> None:
    if message.from_user is None:
        return

    text = message.text.lower()

    if 'myhome.ge' in text:

        for i in text.split(' '):
            if 'myhome.ge' in i:
                link = i

        little = False
        need_orig = False
        need_add_to_db = False
        if ' мал' in text:
            little = True
        if ' ориг' in text:
            need_orig = True
        if ' добав' in text:
            need_add_to_db = True

        pattern = r"https?://(?:www\.)?myhome\.ge/(?:[a-z]{2}/)?pr/(\d+)/"
        match = re.match(pattern, link)
        mid = match.group(1) if match else None
        if mid is None:
            await message.answer(f"Не понимаю вас")
            return

        data = await aget_realty_data_by_id(mid)
        outputs = []

        async with aiohttp.ClientSession() as session:
            # Загружаем водяной знак
            watermark = await download_image(session, WATERMARK_URL)

            image_buffers = []
            for i, image_url in enumerate(data["images_links"]):
                try:
                    image = await download_image(session, image_url)
                    if not need_orig:
                        image_with_watermark = apply_watermark(image, watermark, little)
                    else:
                        image_with_watermark = image

                    # Сохраняем изображение в буфер
                    output = BytesIO()
                    image_with_watermark.save(output, format="JPEG")
                    output.seek(0)

                    image_buffers.append(
                        InputMediaPhoto(media=BufferedInputFile(output.getvalue(), filename=f"image_{i + 1}.jpg"))
                    )
                    outputs.append(output)
                    image.close()
                except Exception as e:
                    await message.answer(f"Ошибка при обработке изображения: {str(e)}")

            # Отправляем изображения группами по 10 файлов
            batch_size = 10
            for i in range(0, len(image_buffers), batch_size):
                media_group = []
                for file in image_buffers[i:i + batch_size]:
                    media_group.append(file)
                await message.answer_media_group(media_group)
        for output in outputs:
            output.close()
        if need_add_to_db:
            await message.answer("Добавляем в систему")
            url_aur = 'https://api.rem.auora-estate.ge/v1/pre_approve_by_myhome/approve/'
            headers = {'Authorization': 'Token f4254f25dde331cac97959872d614eaaef7ca2a2'}
            try:
                async with session.post(url_aur, headers=headers, data={'myhome_id': str(mid)}) as response:
                    if response.ok:
                        await message.answer("Запрос на одобрение отправлен.")
                    else:
                        error_text = await response.text()
                        await message.answer(f"Ошибка: {error_text}")
            except Exception as e:
                await message.answer(f"Ошибка запроса: {str(e)}")
    else:
        await message.answer(f"Не понимаю вас")