from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from django.views.static import serve


async def servers_buttons(servers):
    keyboard = InlineKeyboardBuilder()
    async for server in servers:
        keyboard.add(InlineKeyboardButton(text=server.dynamic_name, callback_data=f"server_info_{server.id}"))
    return keyboard.adjust(1).as_markup()

async def profile_payed_inline_keyboard(change_location=False, outline_server_key_id=None):
    keyboard = InlineKeyboardBuilder()
    change_server_text = 'Сменить локацию'
    pay_button_text = 'Продлить подписку'
    get_access_key_button_text = 'Скопировать ключ доступа'

    if outline_server_key_id:
        keyboard.add(InlineKeyboardButton(text=get_access_key_button_text, callback_data="get_access_key"))
    if change_location:
        keyboard.add(InlineKeyboardButton(text=change_server_text, callback_data="cities"))
    keyboard.add(InlineKeyboardButton(text=pay_button_text, callback_data="buy_action"))
    return keyboard.adjust(1).as_markup()

async def profile_not_payed_inline_keyboard():
    keyboard = InlineKeyboardBuilder()
    pay_button_text = 'Оформить подписку'
    keyboard.add(InlineKeyboardButton(text=pay_button_text, callback_data=f"buy_action"))
    return keyboard.adjust(1).as_markup()

async def available_cities_buttons(cities):
    keyboard = InlineKeyboardBuilder()
    async for city in cities:
        keyboard.add(InlineKeyboardButton(text=f'{city.dynamic_name}', callback_data=f"get_city_{city.id}"))
    return keyboard.adjust(1).as_markup()

async def download_outline_inline_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Скачать для iPhone', url='https://apps.apple.com/us/app/outline-app/id1356177741'))
    keyboard.add(InlineKeyboardButton(text='Скачать для MacOS', url='https://apps.apple.com/us/app/outline-app/id1356178125'))
    keyboard.add(InlineKeyboardButton(text='Скачать для Android', url='https://play.google.com/store/apps/details?id=org.outline.android.client'))
    keyboard.add(InlineKeyboardButton(text='Скачать для Android (.apk)', url='https://s3.amazonaws.com/outline-releases/client/android/stable/Outline-Client.apk'))
    keyboard.add(InlineKeyboardButton(text='Скачать для Windows', url='https://s3.amazonaws.com/outline-releases/client/windows/stable/Outline-Client.exe'))
    return keyboard.adjust(2).as_markup()