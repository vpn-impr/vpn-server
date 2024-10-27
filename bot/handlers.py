from typing import TYPE_CHECKING

from aiofiles.os import access
from aiogram import Router
from aiogram.filters import Command
from django.utils.regex_helper import contains

from bot.keyboards import servers_buttons, profile_payed_inline_keyboard, profile_not_payed_inline_keyboard, \
    available_cities_buttons, download_outline_inline_keyboard
from core.servers.utils import get_server_name_by_key, \
    get_can_change_location_by_key, get_access_key, get_available_countries, get_available_cities, change_user_city, \
    get_ssconf
from core.users.utils import get_user
from aiogram.types import Message, CallbackQuery
from aiogram import F

from core.utils.datetimes import get_now

router = Router()
router.message


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
        f'1 Месяц: 500'
        f'3 Месяца: 1400'
        f'6 Месяцев: 2700'
        f'12 Месяцев: 5100'
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
        f'1 Месяц: 500\n'
        f'3 Месяца: 1400\n'
        f'6 Месяцев: 2700\n'
        f'12 Месяцев: 5100'
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
        '<b>Как настроить Dance VPN</b>\n\n'
        'Green VPN настраивается буквально в два-три клика.\n\n'
        'Нужно скачать приложение Outline, оно есть на любой системе (Android, iOS, Windows, MacOS).\n'
        'Ссылки для скачивания мы прикрепили внизу этого сообщения.\n\n'
        'После этого мы пришлём ссылку, в которой содержится уникальный ключ. Если Outline уже установлен, то при переходе по ссылке, ключ применится автоматически и VPN заработает).\n\n'
        'Если что-то в процессе не получится или у останутся вопросы, в любое время можно написать админу @greenvpnoutline_admin .\n\n',
        reply_markup=reply_markup
    )