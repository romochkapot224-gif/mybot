import asyncio
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from mystars_faas import MyStarsClient

# --- НАСТРОЙКИ ---
# Берем данные из переменных окружения (настроено в Render)
TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", 0))
MYSTARS_API_KEY = os.environ.get("MYSTARS_API_KEY")

CARD_NUMBER = "2200 3961 2634 2837"
SBP_PHONE = "+7 (914) 547-56-71"

WEBHOOK_HOST = os.environ.get("WEBHOOK_URL", "https://mybot-w3ie.onrender.com")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# --- ССЫЛКИ НА КАРТИНКИ ---
IMG_START = "https://i.postimg.cc/5yDB5CZ1/58dfdbc021d1218e2a6dec03fd8d992c-e50d6344-285f-4836-9894-ed71d863032f-(1).png"
IMG_FAQ = "https://i.postimg.cc/66hTdnxM/edd5740c076ef1085147274e76aa9a51-82febf9d-67bf-46ad-8a5f-0d2ddf725540.jpg"
IMG_SUPPORT = "https://i.postimg.cc/zv2WzgJ7/62749612888563fa5dbfdf8de2ed074a-ed2c0b9b-7f01-4db5-a936-7addd32dd7ad-(1).jpg"

IMG_BRAWL = "https://i.postimg.cc/h42HmMCX/BS-Icon.webp"
IMG_STEAM = "https://i.postimg.cc/FzzCG5P9/9a558ccddb72eda578ab6150c2ed2110.png"
IMG_STARS = "https://i.postimg.cc/h43KnSR8/bf0290f4408d86d43307f23fb2577c86.jpg"
IMG_ROBLOX = "https://i.postimg.cc/0NfqBvCY/464853807c6f0421632c7ee19e2a9ec9afef7aa9.jpg"
IMG_PUBG = "https://i.postimg.cc/nrsbrDf3/5060874429f424d0a89c5ccd2b116abf.jpg"

bot = Bot(token=TOKEN)
dp = Dispatcher()
client = MyStarsClient.production(MYSTARS_API_KEY) if MYSTARS_API_KEY else None

class BuyStates(StatesGroup):
    waiting_for_id = State()
    waiting_for_amount = State()

user_orders = {}

def get_main_reply_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛒 Каталог"), KeyboardButton(text="❓ FAQ")],
            [KeyboardButton(text="ℹ️ О нас"), KeyboardButton(text="🆘 Поддержка")]
        ],
        resize_keyboard=True
    )

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
        "⭐ Telegram Stars\n"
        "🎬 AI Studio (услуги нейросетей)\n\n"
        "Приятных покупок! 🚀"
    )
    try:
        await message.answer_photo(photo=IMG_START, caption=welcome_text, reply_markup=get_main_reply_keyboard(), parse_mode="HTML")
    except Exception:
        await message.answer(welcome_text, reply_markup=get_main_reply_keyboard(), parse_mode="HTML")

@dp.message(lambda message: message.text == "ℹ️ О нас")
async def about_us(message: types.Message):
    about_text = (
        "ℹ️ <b>О магазине PotapchikShop</b>\n\n"
        "Добро пожаловать в наш магазин! Мы — команда энтузиастов, которая делает пополнение игровых аккаунтов максимально быстрым, удобным и безопасным.\n\n"
        "Почему выбирают нас?\n"
        "⚡ <b>Скорость:</b> Мы обрабатываем заказы в течение 1–5 минут.\n"
        "🛡 <b>Безопасность:</b> Работаем только через проверенные каналы, чтобы твой аккаунт не попал под бан.\n"
        "💎 <b>Выгодные цены:</b> Наши цены ниже официальных магазинов.\n"
        "🤝 <b>Поддержка:</b> Всегда на связи и готовы помочь с любым вопросом.\n\n"
        "Мы постоянно развиваемся и добавляем новые игры и сервисы. Спасибо, что выбираешь нас! 🚀"
    )
    try:
        await message.answer_photo(photo=IMG_START, caption=about_text, parse_mode="HTML")
    except Exception:
        await message.answer(about_text, parse_mode="HTML")

@dp.message(lambda message: message.text == "❓ FAQ")
async def faq_reply(message: types.Message):
    faq_text = (
        "❓ <b>Частые вопросы (FAQ)</b>\n\n"
        "1️⃣ <b>Как оплатить?</b> Выбираете товар, вводите логин, переводите сумму и нажимаете «Проверить».\n\n"
        "2️⃣ <b>Сколько ждать?</b> Обычно 1–5 минут после оплаты.\n\n"
        "3️⃣ <b>Не пришло, что делать?</b> Напишите в поддержку с чеком, мы все решим."
    )
    try:
        await message.answer_photo(photo=IMG_FAQ, caption=faq_text, parse_mode="HTML")
    except Exception:
        await message.answer(faq_text, parse_mode="HTML")

@dp.message(lambda message: message.text == "🆘 Поддержка")
async def support_reply(message: types.Message):
    try:
        await message.answer_photo(photo=IMG_SUPPORT, caption="🆘 <b>Поддержка PotapchikShop</b>\n\nЕсли у тебя возникли вопросы, напиши нам:\n👉 @Fatty_Jerry", parse_mode="HTML")
    except Exception:
        await message.answer("🆘 <b>Поддержка PotapchikShop</b>\n\nЕсли у тебя возникли вопросы, напиши нам:\n👉 @Fatty_Jerry", parse_mode="HTML")

# --- КАТАЛОГ ---
@dp.message(lambda message: message.text == "🛒 Каталог")
async def catalog_reply(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔥 Brawl Stars", callback_data="brawl"), InlineKeyboardButton(text="🎮 Steam", callback_data="steam")],
        [InlineKeyboardButton(text="🟥 Roblox", callback_data="roblox"), InlineKeyboardButton(text="🔫 PUBG", callback_data="pubg")],
        [InlineKeyboardButton(text="⭐ Telegram Stars", callback_data="stars")],
        [InlineKeyboardButton(text="🎬 AI Studio (Нейросети)", callback_data="ai_studio")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
    ])
    await message.answer("🛒 Выбери игру или сервис из каталога:", reply_markup=keyboard)

# --- МЕНЮ ИГР ---
@dp.callback_query(lambda c: c.data == "brawl")
async def brawl_menu(callback: types.CallbackQuery):
    await callback.answer()
    try:
        await callback.message.delete()
    except Exception:
        pass
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 100 гемов - 150₽", callback_data="buy_brawl_100")],
        [InlineKeyboardButton(text="💎 500 гемов - 700₽", callback_data="buy_brawl_500")],
        [InlineKeyboardButton(text="🎫 Brawl Pass - 350₽", callback_data="buy_brawl_pass")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_catalog")]
    ])
    try:
        await callback.message.answer_photo(photo=IMG_BRAWL, caption="🔥 <b>Brawl Stars</b>\n\nВыбери товар:", reply_markup=keyboard, parse_mode="HTML")
    except Exception:
        await callback.message.answer("🔥 <b>Brawl Stars</b>\n\nВыбери товар:", reply_markup=keyboard, parse_mode="HTML")

@dp.callback_query(lambda c: c.data == "steam")
async def steam_menu(callback: types.CallbackQuery):
    await callback.answer()
    try:
        await callback.message.delete()
    except Exception:
        pass
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💵 100₽", callback_data="buy_steam_100"), InlineKeyboardButton(text="💵 200₽", callback_data="buy_steam_200")],
        [InlineKeyboardButton(text="💵 500₽", callback_data="buy_steam_500"), InlineKeyboardButton(text="💵 1000₽", callback_data="buy_steam_1000")],
        [InlineKeyboardButton(text="✍️ Своя сумма", callback_data="steam_custom")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_catalog")]
    ])
    try:
        await callback.message.answer_photo(photo=IMG_STEAM, caption="🎮 <b>Steam</b>\n\nВыбери сумму:", reply_markup=keyboard, parse_mode="HTML")
    except Exception:
        await callback.message.answer("🎮 <b>Steam</b>\n\nВыбери сумму:", reply_markup=keyboard, parse_mode="HTML")

@dp.callback_query(lambda c: c.data == "roblox")
async def roblox_menu(callback: types.CallbackQuery):
    await callback.answer()
    try:
        await callback.message.delete()
    except Exception:
        pass
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🪙 100 Robux - 120₽", callback_data="buy_roblox_100")],
        [InlineKeyboardButton(text="🪙 500 Robux - 550₽", callback_data="buy_roblox_500")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_catalog")]
    ])
    try:
        await callback.message.answer_photo(photo=IMG_ROBLOX, caption="🟥 <b>Roblox</b>\n\nВыбери товар:", reply_markup=keyboard, parse_mode="HTML")
    except Exception:
        await callback.message.answer("🟥 <b>Roblox</b>\n\nВыбери товар:", reply_markup=keyboard, parse_mode="HTML")

@dp.callback_query(lambda c: c.data == "pubg")
async def pubg_menu(callback: types.CallbackQuery):
    await callback.answer()
    try:
        await callback.message.delete()
    except Exception:
        pass
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💵 60 UC - 90₽", callback_data="buy_pubg_60")],
        [InlineKeyboardButton(text="💵 325 UC - 450₽", callback_data="buy_pubg_325")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_catalog")]
    ])
    try:
        await callback.message.answer_photo(photo=IMG_PUBG, caption="🔫 <b>PUBG Mobile</b>\n\nВыбери товар:", reply_markup=keyboard, parse_mode="HTML")
    except Exception:
        await callback.message.answer("🔫 <b>PUBG Mobile</b>\n\nВыбери товар:", reply_markup=keyboard, parse_mode="HTML")

@dp.callback_query(lambda c: c.data == "stars")
async def stars_menu(callback: types.CallbackQuery):
    await callback.answer()
    try:
        await callback.message.delete()
    except Exception:
        pass
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ 100 звезд - 150₽", callback_data="buy_stars_100"), InlineKeyboardButton(text="⭐ 200 звезд - 300₽", callback_data="buy_stars_200")],
        [InlineKeyboardButton(text="⭐ 500 звезд - 750₽", callback_data="buy_stars_500"), InlineKeyboardButton(text="⭐ 1000 звезд - 1500₽", callback_data="buy_stars_1000")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_catalog")]
    ])
    try:
        await callback.message.answer_photo(photo=IMG_STARS, caption="⭐ <b>Telegram Stars</b>\n\nВыбери количество:", reply_markup=keyboard, parse_mode="HTML")
    except Exception:
        await callback.message.answer("⭐ <b>Telegram Stars</b>\n\nВыбери количество:", reply_markup=keyboard, parse_mode="HTML")

# --- AI STUDIO ---
@dp.callback_query(lambda c: c.data == "ai_studio")
async def ai_studio_menu(callback: types.CallbackQuery):
    await callback.answer()
    try:
        await callback.message.delete()
    except Exception:
        pass
    
    text = (
        "🎬 <b>AI Studio PotapchikShop</b>\n\n"
        "Мы используем современные нейросети, чтобы создавать уникальный контент на заказ!\n\n"
        "Доступные услуги:\n"
        "🎥 <b>Оживление фото:</b> Сделаем видео из твоего фото (от 300₽).\n"
        "🎨 <b>Нейро-арт:</b> Сгенерируем аватарку или арт по твоему описанию (от 150₽).\n"
        "📝 <b>Тексты и сценарии:</b> Напишем крутой текст для канала или видео (от 200₽).\n\n"
        "👉 <b>Для заказа напиши нашему менеджеру:</b> @barmaf_khv\n"
        "Пришли свое фото или описание, и мы обсудим детали!"
    )
    await callback.message.answer(text, parse_mode="HTML")

# --- ОБРАБОТКА ВЫБОРА ТОВАРА ---
@dp.callback_query(lambda c: c.data.startswith("buy_") and "custom" not in c.data)
async def item_chosen(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    try:
        await callback.message.delete()
    except Exception:
        pass
    
    parts = callback.data.split("_")
    game = parts[1]
    item = parts[2]
    
    prices = {
        "brawl": {"100": 150, "500": 700, "pass": 350},
        "steam": {"100": 100, "200": 200, "500": 500, "1000": 1000},
        "roblox": {"100": 120, "500": 550},
        "pubg": {"60": 90, "325": 450},
        "stars": {"100": 150, "200": 300, "500": 750, "1000": 1500}
    }
    
    base_price = prices.get(game, {}).get(item, 0)
    if base_price == 0: return
        
    final_price = int(base_price * 1.15)
    names = {"brawl": "Brawl Stars", "steam": "Steam", "roblox": "Roblox", "pubg": "PUBG", "stars": "Telegram Stars"}
    item_names = {"100": "100", "500": "500", "pass": "Brawl Pass", "200": "200", "1000": "1000", "60": "60 UC", "325": "325 UC"}
    
    display_name = f"{names[game]} ({item_names.get(item, item)})"
    
    if game == "stars":
        await state.update_data(item_name=display_name, final_price=final_price, game=game, stars_amount=int(item))
    else:
        await state.update_data(item_name=display_name, final_price=final_price, game=game)
    
    if game == "stars":
        await callback.message.answer(f"Ты выбрал {display_name}.\nК оплате: {final_price}₽.\n\nВведи юзернейм Telegram (без @):")
    else:
        await callback.message.answer(f"Ты выбрал {display_name}.\nК оплате: {final_price}₽.\n\nВведи свой логин/ID:")
    
    await state.set_state(BuyStates.waiting_for_id)

@dp.callback_query(lambda c: c.data == "steam_custom")
async def steam_custom(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer("Введи сумму пополнения Steam (только цифры):")
    await state.set_state(BuyStates.waiting_for_amount)

@dp.message(BuyStates.waiting_for_amount)
async def process_custom_amount(message: types.Message, state: FSMContext):
    if not message.text or not message.text.isdigit():
        await message.answer("❌ Введи только цифры.")
        return
    amount = int(message.text)
    final_price = int(amount * 1.15)
    await state.update_data(item_name=f"Steam {amount}₽", final_price=final_price, game="steam")
    await message.answer(f"Ты выбрал Steam {amount}₽. К оплате: {final_price}₽.\nВведи логин Steam:")
    await state.set_state(BuyStates.waiting_for_id)

@dp.message(BuyStates.waiting_for_id)
async def process_id(message: types.Message, state: FSMContext):
    if not message.text:
        await message.answer("Пожалуйста, отправь свой логин или ID текстовым сообщением.")
        return

    user_id_input = message.text.strip().replace("@", "")
    data = await state.get_data()
    final_price = data.get('final_price')
    item_name = data.get('item_name')
    game = data.get('game')
    stars_amount = data.get('stars_amount')
    
    if game == "stars":
        msg = await message.answer("⏳ Проверяю юзернейм и создаю заказ...")
        if not client:
            await msg.edit_text("❌ Ошибка: API-ключ MyStars не настроен.")
            return
        try:
            # Оборачиваем синхронные запросы в to_thread, чтобы бот не зависал
            check = await asyncio.to_thread(client.check_recipient, user_id_input, type="stars")
            if not check.eligible:
                await msg.edit_text(f"❌ Ошибка: {check.telegram_message}\nПроверь написание юзернейма.")
                return
            
            order = await asyncio.to_thread(client.create_order, type="stars", recipient=user_id_input, quantity=stars_amount, payment_currency="TON")
            user_orders[message.from_user.id] = {"login": user_id_input, "price": final_price, "type": item_name, "mystars_order_id": order.id}
            await msg.delete()
        except Exception as e:
            await msg.edit_text(f"❌ Ошибка при создании заказа. Попробуйте позже.")
            return
    else:
        user_orders[message.from_user.id] = {"login": user_id_input, "price": final_price, "type": item_name}
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Карта", callback_data="pay_card")],
        [InlineKeyboardButton(text="🏦 СБП", callback_data="pay_sbp")]
    ])
    await message.answer(f"Отлично! Логин/ID: {user_id_input}\nСумма к оплате: {final_price}₽.\n\nВыбери способ оплаты:", reply_markup=keyboard)
    await state.clear()

# --- ОПЛАТА ---
@dp.callback_query(lambda c: c.data in ["pay_card", "pay_sbp"])
async def process_payment_method(callback: types.CallbackQuery):
    await callback.answer()
    order = user_orders.get(callback.from_user.id)
    if not order: return

    method = callback.data
    try:
        await callback.message.delete() 
    except Exception:
        pass

    check_keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔄 Проверить оплату", callback_data="check_payment")]])

    if method == "pay_card":
        await callback.message.answer(f"💳 <b>Перевод на карту</b>\n\nСумма: <b>{order['price']}₽</b>\nКарта: <code>{CARD_NUMBER}</code>\n\nПосле перевода нажми:", reply_markup=check_keyboard, parse_mode="HTML")
    elif method == "pay_sbp":
        await callback.message.answer(f"🏦 <b>Оплата через СБП</b>\n\nСумма: <b>{order['price']}₽</b>\nНомер: <code>{SBP_PHONE}</code>\n\nПосле перевода нажми:", reply_markup=check_keyboard, parse_mode="HTML")

@dp.callback_query(lambda c: c.data == "check_payment")
async def check_payment(callback: types.CallbackQuery):
    await callback.answer()
    order = user_orders.get(callback.from_user.id)
    if not order: return

    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer("⏳ Запрос отправлен администратору. Ожидайте подтверждения...")
    
    admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить оплату", callback_data=f"admin_confirm_{callback.from_user.id}")],
        [InlineKeyboardButton(text="❌ Отклонить", callback_data=f"admin_reject_{callback.from_user.id}")]
    ])
    mystars_info = f"\nMyStars Order ID: {order.get('mystars_order_id')}" if order.get('mystars_order_id') else ""
    await bot.send_message(ADMIN_ID, f"💰 <b>ЗАПРОС НА ОПЛАТУ!</b>\n\nКлиент: {callback.from_user.first_name}\nТовар: {order.get('type', 'Steam')}\nЛогин/Ник: {order['login']}\nСумма: {order['price']}₽{mystars_info}\n\nПроверь банк:", reply_markup=admin_keyboard, parse_mode="HTML")

@dp.callback_query(lambda c: c.data.startswith("admin_confirm"))
async def admin_confirm(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID: return
    user_id = int(callback.data.split("_")[2])
    await bot.send_message(user_id, "✅ <b>Оплата получена!</b>\n\nМы приступаем к выполнению вашего заказа. Ожидайте.", parse_mode="HTML")
    complete_keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🏁 Заказ выполнен", callback_data=f"admin_complete_{user_id}")]])
    
    try:
        await callback.message.edit_text("✅ Ты подтвердил оплату. Нажми кнопку ниже, когда выдашь товар.", reply_markup=complete_keyboard)
    except Exception:
        pass

@dp.callback_query(lambda c: c.data.startswith("admin_reject"))
async def admin_reject(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID: return
    user_id = int(callback.data.split("_")[2])
    await bot.send_message(user_id, "❌ <b>Оплата не найдена.</b>\nНапиши в поддержку @Fatty_Jerry.", parse_mode="HTML")
    
    if user_id in user_orders:
        del user_orders[user_id]
        
    try:
        await callback.message.edit_text("❌ Отклонено.")
    except Exception:
        pass

@dp.callback_query(lambda c: c.data.startswith("admin_complete"))
async def admin_complete(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID: return
    user_id = int(callback.data.split("_")[2])
    await bot.send_message(user_id, "🏁 <b>Заказ успешно выполнен!</b>\n\nСпасибо, что выбрали PotapchikShop!", parse_mode="HTML")
    
    if user_id in user_orders:
        del user_orders[user_id]

    try:
        await callback.message.edit_text("🏁 Заказ завершен. Клиент уведомлен.")
    except Exception:
        pass

@dp.callback_query(lambda c: c.data == "back_to_catalog")
async def back_to_catalog(callback: types.CallbackQuery):
    await callback.answer()
    try:
        await callback.message.delete()
    except Exception:
        pass
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔥 Brawl Stars", callback_data="brawl"), InlineKeyboardButton(text="🎮 Steam", callback_data="steam")],
        [InlineKeyboardButton(text="🟥 Roblox", callback_data="roblox"), InlineKeyboardButton(text="🔫 PUBG", callback_data="pubg")],
        [InlineKeyboardButton(text="⭐ Telegram Stars", callback_data="stars")],
        [InlineKeyboardButton(text="🎬 AI Studio (Нейросети)", callback_data="ai_studio")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
    ])
    await callback.message.answer("🛒 Выбери игру или сервис из каталога:", reply_markup=keyboard)

# --- ОБРАБОТКА ПИНГА ДЛЯ RENDER ---
async def handle_ping(request):
    return web.Response(text="OK")

# --- ВЕБХУК ---
async def on_startup(app: web.Application):
    # drop_pending_updates=False, чтобы не терять сообщения, пока бот "спал" на Render
    await bot.delete_webhook(drop_pending_updates=False)
    await bot.set_webhook(WEBHOOK_URL)

def main():
    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    
    # Добавляем путь для Cron-Job пинга
    app.router.add_get('/ping', handle_ping)
    
    app.on_startup.append(on_startup)
    port = int(os.environ.get("PORT", 10000))
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
