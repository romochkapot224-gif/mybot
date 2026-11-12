import asyncio
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

# --- НАСТРОЙКИ ---
TOKEN = '9179658337:AAG9Ia4fR0dZjvA7cVNX829brt48AfaOqhU'
CARD_NUMBER = "2200 3961 2634 2837"
SBP_PHONE = "+7 (914) 547-56-71"
ADMIN_ID = 8804452762 

WEBHOOK_HOST = os.environ.get("WEBHOOK_URL", "https://mybot-w3ie.onrender.com")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# --- ССЫЛКИ НА КАРТИНКИ ---
IMG_START = "https://i.postimg.cc/5yDB5CZ1/58dfdbc021d1218e2a6dec03fd8d992c-e50d6344-285f-4836-9894-ed71d863032f-(1).png"
# IMG_FAQ и IMG_SUPPORT убраны, чтобы не было рекламы

bot = Bot(token=TOKEN)
dp = Dispatcher()

class SteamStates(StatesGroup):
    waiting_for_amount = State()
    waiting_for_login = State()

class StarsStates(StatesGroup):
    waiting_for_custom_stars = State()
    waiting_for_username = State()

user_orders = {}
STAR_PRICE = 1.5 

def get_main_reply_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛒 Каталог"), KeyboardButton(text="❓ FAQ")],
            [KeyboardButton(text="🆘 Поддержка")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выбери раздел..."
    )
    return keyboard

@dp.message(Command("start"))
async def start(message: types.Message):
    welcome_text = (
        "👋 <b>Добро пожаловать в PotapchikShop!</b>\n\n"
        "Мы — современный сервис по пополнению аккаунтов и покупке игровых ценностей. "
        "Наша команда делает процесс покупки максимально быстрым, удобным и безопасным для каждого клиента.\n\n"
        "В нашем ассортименте всегда есть:\n"
        "🎮 Пополнение Steam (рубли)\n"
        "🔥 Гемы и Brawl Pass для Brawl Stars\n"
        "🟥 Robux для Roblox\n"
        "🔫 UC для PUBG Mobile\n"
        "⭐ Telegram Stars\n\n"
        "Мы ценим ваше время и доверие. Все заказы обрабатываются оперативно, а в случае любых вопросов наша поддержка всегда готова прийти на помощь.\n\n"
        "Приятных покупок! 🚀"
    )
    try:
        await message.answer_photo(photo=IMG_START, caption=welcome_text, reply_markup=get_main_reply_keyboard(), parse_mode="HTML")
    except:
        await message.answer(welcome_text, reply_markup=get_main_reply_keyboard(), parse_mode="HTML")

@dp.message(lambda message: message.text == "🛒 Каталог")
async def catalog_reply(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔥 Brawl Stars", callback_data="brawl"), InlineKeyboardButton(text="🎮 Steam", callback_data="steam")],
        [InlineKeyboardButton(text="🟥 Roblox", callback_data="roblox"), InlineKeyboardButton(text="🔫 PUBG", callback_data="pubg")],
        [InlineKeyboardButton(text="⭐ Telegram Stars", callback_data="stars")]
    ])
    await message.answer("🛒 Выбери игру или сервис из каталога:", reply_markup=keyboard)

# --- FAQ (БЕЗ КАРТИНКИ) ---
@dp.message(lambda message: message.text == "❓ FAQ")
async def faq_reply(message: types.Message):
    faq_text = (
        "❓ <b>Частые вопросы (FAQ)</b>\n\n"
        "1️⃣ <b>Как оплатить?</b> Выбираете товар, вводите логин, переводите сумму и нажимаете «Я оплатил».\n\n"
        "2️⃣ <b>Сколько ждать?</b> Обычно 1–5 минут после оплаты.\n\n"
        "3️⃣ <b>Не пришло, что делать?</b> Напишите в поддержку с чеком, мы все решим."
    )
    await message.answer(faq_text, parse_mode="HTML")

# --- ПОДДЕРЖКА (БЕЗ КАРТИНКИ) ---
@dp.message(lambda message: message.text == "🆘 Поддержка")
async def support_reply(message: types.Message):
    await message.answer(
        "🆘 <b>Поддержка PotapchikShop</b>\n\nЕсли у тебя возникли вопросы, напиши нам:\n👉 @Fatty_Jerry", 
        parse_mode="HTML"
    )

# ... (ОСТАЛЬНОЙ КОД С STEAM И STARS БЕЗ ИЗМЕНЕНИЙ) ...
# Пожалуйста, используй предыдущий код для Steam и Stars, я не буду его дублировать, чтобы не запутать.
# Вставь этот блок вместо старого FAQ и Поддержки.
