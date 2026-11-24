import asyncio
import hashlib
import hmac
import json
import os
import uuid

import aiohttp
from aiohttp import web
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from mystars_faas import MyStarsClient
from yookassa import Configuration, Payment

TOKEN = os.environ["BOT_TOKEN"]
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))
MYSTARS_API_KEY = os.environ.get("MYSTARS_API_KEY")
CRYPTOBOT_API_TOKEN = os.environ.get("CRYPTOBOT_API_TOKEN")
YOOKASSA_SHOP_ID = os.environ.get("YOOKASSA_SHOP_ID")
YOOKASSA_SECRET_KEY = os.environ.get("YOOKASSA_SECRET_KEY")
CARD_NUMBER = os.environ.get("CARD_NUMBER", "не задано")
SBP_PHONE = os.environ.get("SBP_PHONE", "не задано")
SUPPORT_USERNAME = os.environ.get("SUPPORT_USERNAME", "Fatty_Jerry")
WEBHOOK_HOST = os.environ.get("WEBHOOK_URL", "https://mybot-w3ie.onrender.com")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
ORDERS_FILE = os.environ.get("ORDERS_FILE", "orders.json")
MARKUP = 1.08

if YOOKASSA_SHOP_ID and YOOKASSA_SECRET_KEY:
    Configuration.account_id = YOOKASSA_SHOP_ID
    Configuration.secret_key = YOOKASSA_SECRET_KEY

IMG_START = "https://i.postimg.cc/5yDB5CZ1/58dfdbc021d1218e2a6dec03fd8d992c-e50d6344-285f-4836-9894-ed71d863032f-(1).png"
IMG_FAQ = "https://i.postimg.cc/66hTdnxM/edd5740c076ef1085147274e76aa9a51-82febf9d-67bf-46ad-8a5f-0d2ddf725540.jpg"
IMG_SUPPORT = "https://i.postimg.cc/zv2WzgJ7/62749612888563fa5dbfdf8de2ed074a-ed2c0b9b-7f01-4db5-a936-7addd32dd7ad-(1).jpg"
IMG_BRAWL = "https://i.postimg.cc/h42HmMCX/BS-Icon.webp"
IMG_STEAM = "https://i.postimg.cc/FzzCG5P9/9a558ccddb72eda578ab6150c2ed2110.png"
IMG_STARS = "https://i.postimg.cc/h43KnSR8/bf0290f4408d86d43307f23fb2577c86.jpg"
IMG_ROBLOX = "https://i.postimg.cc/0NfqBvCY/464853807c6f0421632c7ee19e2a9ec9afef7aa9.jpg"
IMG_PUBG = "https://i.postimg.cc/nrsbrDf3/5060874429f424d0a89c5ccd2b116abf.jpg"

CATALOG = {
    "brawl": {
        "title": "Brawl Stars", "img": IMG_BRAWL,
        "caption": "🔥 <b>Brawl Stars</b>\n\nВыбери товар:",
        "items": [
            ("30", "💎 30 гемов - 109₽", "30 гемов", 109),
            ("80", "💎 80 гемов - 269₽", "80 гемов", 269),
            ("170", "💎 170 гемов - 549₽", "170 гемов", 549),
            ("360", "💎 360 гемов - 1099₽", "360 гемов", 1099),
            ("950", "💎 950 гемов - 2699₽", "950 гемов", 2699),
            ("2000", "💎 2000 гемов - 5499₽", "2000 гемов", 5499),
        ],
    },
    "steam": {
        "title": "Steam", "img": IMG_STEAM,
        "caption": "🎮 <b>Steam</b>\n\nВыбери сумму:",
        "items": [
            ("100", "💵 100₽", "100₽", 100),
            ("200", "💵 200₽", "200₽", 200),
            ("500", "💵 500₽", "500₽", 500),
            ("1000", "💵 1000₽", "1000₽", 1000),
            ("custom", "✍️ Своя сумма", None, None),
        ],
    },
    "roblox": {
        "title": "Roblox", "img": IMG_ROBLOX,
        "caption": "🟥 <b>Roblox</b>\n\nВыбери товар:",
        "items": [
            ("80", "🪙 80 Robux - 119₽", "80 Robux", 119),
            ("400", "🪙 400 Robux - 539₽", "400 Robux", 539),
            ("800", "🪙 800 Robux - 1080₽", "800 Robux", 1080),
            ("1200", "🪙 1200 Robux - 1290₽", "1200 Robux", 1290),
            ("1700", "🪙 1700 Robux - 2150₽", "1700 Robux", 2150),
            ("3150", "🪙 3150 Robux - 2990₽", "3150 Robux", 2990),
            ("4500", "🪙 4500 Robux - 5600₽", "4500 Robux", 5600),
            ("10000", "🪙 10000 Robux - 11390₽", "10000 Robux", 11390),
            ("22500", "🪙 22500 Robux - 22990₽", "22500 Robux", 22990),
        ],
    },
    "pubg": {
        "title": "PUBG Mobile", "img": IMG_PUBG,
        "caption": "🔫 <b>PUBG Mobile</b>\n\nВыбери товар:",
        "items": [
            ("60", "💵 60 UC - 99₽", "60 UC", 99),
            ("325", "💵 325 UC - 449₽", "325 UC", 449),
            ("660", "💵 660 UC - 899₽", "660 UC", 899),
            ("1800", "💵 1800 UC - 2290₽", "1800 UC", 2290),
            ("3850", "💵 3850 UC - 4490₽", "3850 UC", 4490),
            ("8100", "💵 8100 UC - 8990₽", "8100 UC", 8990),
        ],
    },
    "stars": {
        "title": "Telegram Stars", "img": IMG_STARS,
        "caption": "⭐ <b>Telegram Stars</b>\n\nВыбери количество:",
        "items": [
            ("100", "⭐ 100 звезд - 150₽", "100 звезд", 150),
            ("200", "⭐ 200 звезд - 300₽", "200 звезд", 300),
            ("500", "⭐ 500 звезд - 750₽", "500 звезд", 750),
            ("1000", "⭐ 1000 звезд - 1500₽", "1000 звезд", 1500),
        ],
    },
}

bot = Bot(token=TOKEN)
dp = Dispatcher()
client = MyStarsClient.production(MYSTARS_API_KEY) if MYSTARS_API_KEY else None


class BuyStates(StatesGroup):
    waiting_for_id = State()
    waiting_for_amount = State()


def load_orders():
    try:
        with open(ORDERS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_orders():
    with open(ORDERS_FILE, "w", encoding="utf-8") as f:
        json.dump(orders, f, ensure_ascii=False, indent=2)


orders = load_orders()


def main_reply_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛒 Каталог"), KeyboardButton(text="❓ FAQ")],
            [KeyboardButton(text="ℹ️ О нас"), KeyboardButton(text="🆘 Поддержка")],
        ],
        resize_keyboard=True,
    )


def catalog_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔥 Brawl Stars", callback_data="brawl"), InlineKeyboardButton(text="🎮 Steam", callback_data="steam")],
        [InlineKeyboardButton(text="🟥 Roblox", callback_data="roblox"), InlineKeyboardButton(text="🔫 PUBG", callback_data="pubg")],
        [InlineKeyboardButton(text="⭐ Telegram Stars", callback_data="stars")],
        [InlineKeyboardButton(text="🎬 AI Studio (Нейросети)", callback_data="ai_studio")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")],
    ])


def game_keyboard(game):
    items = CATALOG[game]["items"]
    rows = []
    for i in range(0, len(items), 2):
        row = []
        for key, text, _, _ in items[i:i + 2]:
            cb = "steam_custom" if key == "custom" else f"buy_{game}_{key}"
            row.append(InlineKeyboardButton(text=text, callback_data=cb))
        rows.append(row)
    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_catalog")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def safe_delete(message):
    try:
        await message.delete()
    except Exception:
        pass


async def send_card(message, img, text, markup=None):
    try:
        await message.answer_photo(photo=img, caption=text, reply_markup=markup, parse_mode="HTML")
    except Exception:
        await message.answer(text, reply_markup=markup, parse_mode="HTML")


async def get_user_order(callback, oid):
    order = orders.get(oid)
    if not order or order["user_id"] != callback.from_user.id:
        await callback.answer("Заказ не найден", show_alert=True)
        return None
    return order


async def mark_paid(oid, method):
    order = orders.get(oid)
    if not order or order["status"] != "new":
        return
    order["status"] = "paid"
    order["paid_via"] = method
    save_orders()
    await bot.send_message(order["user_id"], "✅ <b>Оплата получена!</b>\n\nМы приступаем к выполнению вашего заказа. Ожидайте.", parse_mode="HTML")
    await bot.send_message(
        ADMIN_ID,
        f"💰 <b>Оплачен заказ {oid}</b> ({method})\nТовар: {order['name']}\nЛогин/ID: {order['login']}\nСумма: {order['price']}₽",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏁 Выдать заказ", callback_data=f"admin_fulfil_{oid}")]
        ]),
        parse_mode="HTML",
    )


async def create_crypto_invoice(order):
    payload = {
        "currency_type": "fiat",
        "fiat": "RUB",
        "accepted_assets": "USDT",
        "amount": str(order["price"]),
        "description": f"Заказ {order['id']}",
        "payload": order["id"],
        "expires_in": 3600,
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://pay.crypt.bot/api/createInvoice",
            json=payload,
            headers={"Crypto-Pay-API-Token": CRYPTOBOT_API_TOKEN},
        ) as resp:
            data = await resp.json()
    if not data.get("ok"):
        print(f"CRYPTOBOT ERROR {order['id']}: {data}", flush=True)
        return None
    return data["result"]


def crypto_signature_ok(raw, signature):
    if not signature or not CRYPTOBOT_API_TOKEN:
        return False
    secret = hashlib.sha256(CRYPTOBOT_API_TOKEN.encode()).digest()
    expected = hmac.new(secret, raw, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


@dp.message(Command("start"))
async def start(message: types.Message):
    welcome_text = (
        "👋 <b>Добро пожаловать в наш магазин!</b>\n\n"
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
    await send_card(message, IMG_START, welcome_text, main_reply_keyboard())


@dp.message(F.text == "ℹ️ О нас")
async def about_us(message: types.Message):
    about_text = (
        "ℹ️ <b>О магазине</b>\n\n"
        "Добро пожаловать в наш магазин! Мы — команда энтузиастов, которая делает пополнение игровых аккаунтов максимально быстрым, удобным и безопасным.\n\n"
        "Почему выбирают нас?\n"
        "⚡ <b>Скорость:</b> Мы обрабатываем заказы в течение 1–5 минут.\n"
        "🛡 <b>Безопасность:</b> Работаем только через проверенные каналы, чтобы твой аккаунт не попал под бан.\n"
        "💎 <b>Выгодные цены:</b> Наши цены ниже официальных магазинов.\n"
        "🤝 <b>Поддержка:</b> Всегда на связи и готовы помочь с любым вопросом.\n\n"
        "Мы постоянно развиваемся и добавляем новые игры и сервисы. Спасибо, что выбираешь нас! 🚀"
    )
    await send_card(message, IMG_START, about_text)


@dp.message(F.text == "❓ FAQ")
async def faq_reply(message: types.Message):
    faq_text = (
        "❓ <b>Частые вопросы (FAQ)</b>\n\n"
        "1️⃣ <b>Как оплатить?</b> Выбираете товар, вводите логин, переводите сумму и нажимаете «Проверить».\n\n"
        "2️⃣ <b>Сколько ждать?</b> Обычно 1–5 минут после оплаты.\n\n"
        "3️⃣ <b>Не пришло, что делать?</b> Напишите в поддержку с чеком, мы все решим."
    )
    await send_card(message, IMG_FAQ, faq_text)


@dp.message(F.text == "🆘 Поддержка")
async def support_reply(message: types.Message):
    text = f"🆘 <b>Поддержка</b>\n\nЕсли у тебя возникли вопросы, напиши нам:\n👉 @{SUPPORT_USERNAME}"
    await send_card(message, IMG_SUPPORT, text)


@dp.message(F.text == "🛒 Каталог")
async def catalog_reply(message: types.Message):
    await message.answer("🛒 Выбери игру или сервис из каталога:", reply_markup=catalog_keyboard())


@dp.callback_query(F.data.in_(list(CATALOG)))
async def game_menu(callback: types.CallbackQuery):
    await callback.answer()
    await safe_delete(callback.message)
    game = CATALOG[callback.data]
    await send_card(callback.message, game["img"], game["caption"], game_keyboard(callback.data))


@dp.callback_query(F.data == "ai_studio")
async def ai_studio_menu(callback: types.CallbackQuery):
    await callback.answer()
    await safe_delete(callback.message)
    text = (
        "🎬 <b>AI Studio</b>\n\n"
        "Мы используем современные нейросети, чтобы создавать уникальный контент на заказ!\n\n"
        "Доступные услуги:\n"
        "🎥 <b>Оживление фото:</b> Сделаем видео из твоего фото (от 300₽).\n"
        "🎨 <b>Нейро-арт:</b> Сгенерируем аватарку или арт по твоему описанию (от 150₽).\n"
        "📝 <b>Тексты и сценарии:</b> Напишем крутой текст для канала или видео (от 200₽).\n\n"
        "👉 <b>Для заказа напиши нашему менеджеру:</b> @barmaf_khv\n"
        "Пришли свое фото или описание, и мы обсудим детали!"
    )
    await callback.message.answer(text, parse_mode="HTML")


@dp.callback_query(F.data == "back_to_catalog")
async def back_to_catalog(callback: types.CallbackQuery):
    await callback.answer()
    await safe_delete(callback.message)
    await callback.message.answer("🛒 Выбери игру или сервис из каталога:", reply_markup=catalog_keyboard())


@dp.callback_query(F.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    await callback.answer()
    await safe_delete(callback.message)
    await callback.message.answer("Главное меню:", reply_markup=main_reply_keyboard())


@dp.callback_query(F.data.startswith("buy_"))
async def item_chosen(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    _, game, key = callback.data.split("_")
    item = next((i for i in CATALOG[game]["items"] if i[0] == key), None)
    if not item:
        return
    _, _, name, price = item
    await safe_delete(callback.message)

    final_price = int(price * MARKUP)
    display_name = f"{CATALOG[game]['title']} ({name})"
    await state.update_data(name=display_name, price=final_price, game=game, stars=int(key) if game == "stars" else None)

    prompt = "Введи юзернейм Telegram (без @):" if game == "stars" else "Введи свой логин/ID:"
    await callback.message.answer(f"Ты выбрал {display_name}.\nК оплате: {final_price}₽.\n\n{prompt}")
    await state.set_state(BuyStates.waiting_for_id)


@dp.callback_query(F.data == "steam_custom")
async def steam_custom(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await safe_delete(callback.message)
    await callback.message.answer("Введи сумму пополнения Steam (только цифры):")
    await state.set_state(BuyStates.waiting_for_amount)


@dp.message(BuyStates.waiting_for_amount)
async def process_custom_amount(message: types.Message, state: FSMContext):
    if not message.text or not message.text.isdigit():
        await message.answer("❌ Введи только цифры.")
        return
    amount = int(message.text)
    final_price = int(amount * MARKUP)
    await state.update_data(name=f"Steam ({amount}₽)", price=final_price, game="steam", stars=None)
    await message.answer(f"Ты выбрал Steam {amount}₽. К оплате: {final_price}₽.\nВведи логин Steam:")
    await state.set_state(BuyStates.waiting_for_id)


@dp.message(BuyStates.waiting_for_id)
async def process_id(message: types.Message, state: FSMContext):
    if not message.text:
        await message.answer("Пожалуйста, отправь логин или ID текстовым сообщением.")
        return

    login = message.text.strip().lstrip("@")
    data = await state.get_data()
    game = data["game"]

    if game == "stars":
        msg = await message.answer("⏳ Проверяю юзернейм...")
        if not client:
            await msg.edit_text("❌ Ошибка: API-ключ MyStars не настроен.")
            return
        try:
            check = await asyncio.to_thread(client.check_recipient, login, type="stars")
        except Exception as e:
            print(f"MYSTARS CHECK ERROR {login}: {type(e).__name__}: {e}", flush=True)
            await msg.edit_text("❌ Ошибка проверки юзернейма. Попробуй позже.")
            return
        print(f"MYSTARS CHECK {login}: eligible={check.eligible} msg={check.telegram_message}", flush=True)
        if not check.eligible:
            await msg.edit_text(f"❌ {check.telegram_message}\nПроверь написание юзернейма.")
            return
        await safe_delete(msg)

    oid = uuid.uuid4().hex[:12]
    orders[oid] = {
        "id": oid,
        "user_id": message.from_user.id,
        "login": login,
        "name": data["name"],
        "price": data["price"],
        "game": game,
        "stars": data.get("stars"),
        "status": "new",
    }
    save_orders()
    await state.clear()

    buttons = []
    if CRYPTOBOT_API_TOKEN:
        buttons.append([InlineKeyboardButton(text="💎 Оплатить криптой (USDT)", callback_data=f"pay_crypto_{oid}")])
    if YOOKASSA_SHOP_ID and YOOKASSA_SECRET_KEY:
        buttons.append([InlineKeyboardButton(text="💳 Оплатить картой (Авто)", callback_data=f"pay_yookassa_{oid}")])
    buttons.append([InlineKeyboardButton(text="💳 Перевод на карту (Вручную)", callback_data=f"pay_card_{oid}")])
    buttons.append([InlineKeyboardButton(text="🏦 СБП (Вручную)", callback_data=f"pay_sbp_{oid}")])

    await message.answer(
        f"Отлично! Логин/ID: {login}\nСумма к оплате: {data['price']}₽.\n\nВыбери способ оплаты:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )


@dp.callback_query(F.data.startswith("pay_crypto_"))
async def pay_crypto(callback: types.CallbackQuery):
    await callback.answer()
    order = await get_user_order(callback, callback.data.removeprefix("pay_crypto_"))
    if not order:
        return
    await callback.message.answer("⏳ Создаю счет в CryptoBot...")
    invoice = await create_crypto_invoice(order)
    if not invoice:
        await callback.message.answer("❌ Ошибка при создании счета. Попробуй позже или выбери ручную оплату.")
        return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="💸 Оплатить криптой", url=invoice["bot_invoice_url"])]])
    await callback.message.answer(
        f"Сумма к оплате: <b>{order['price']}₽</b>\n\nНажми кнопку ниже. После оплаты заказ поставится в работу автоматически.",
        reply_markup=keyboard,
        parse_mode="HTML",
    )


@dp.callback_query(F.data.startswith("pay_yookassa_"))
async def pay_yookassa(callback: types.CallbackQuery):
    await callback.answer()
    order = await get_user_order(callback, callback.data.removeprefix("pay_yookassa_"))
    if not order:
        return
    await callback.message.answer("⏳ Создаю ссылку на оплату...")
    try:
        me = await bot.get_me()
        payment = await asyncio.to_thread(Payment.create, {
            "amount": {"value": f"{order['price']}.00", "currency": "RUB"},
            "confirmation": {"type": "redirect", "return_url": f"https://t.me/{me.username}"},
            "capture": True,
            "description": f"Заказ {order['id']}: {order['name']} для {order['login']}",
            "metadata": {"order_id": order["id"]},
        }, str(uuid.uuid4()))
    except Exception as e:
        print(f"YOOKASSA ERROR {order['id']}: {type(e).__name__}: {e}", flush=True)
        await callback.message.answer("❌ Ошибка при создании платежа. Выбери ручной способ.")
        return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="💸 Перейти к оплате", url=payment.confirmation.confirmation_url)]])
    await callback.message.answer(
        f"Сумма к оплате: <b>{order['price']}₽</b>\n\nНажми кнопку ниже, чтобы оплатить заказ:",
        reply_markup=keyboard,
        parse_mode="HTML",
    )


@dp.callback_query(F.data.startswith(("pay_card_", "pay_sbp_")))
async def pay_manual(callback: types.CallbackQuery):
    await callback.answer()
    _, kind, oid = callback.data.split("_")
    order = await get_user_order(callback, oid)
    if not order:
        return
    await safe_delete(callback.message)
    check_keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔄 Проверить оплату", callback_data=f"check_{oid}")]])
    if kind == "card":
        text = f"💳 <b>Перевод на карту</b>\n\nСумма: <b>{order['price']}₽</b>\nКарта: <code>{CARD_NUMBER}</code>\n\nПосле перевода нажми:"
    else:
        text = f"🏦 <b>Оплата через СБП</b>\n\nСумма: <b>{order['price']}₽</b>\nНомер: <code>{SBP_PHONE}</code>\n\nПосле перевода нажми:"
    await callback.message.answer(text, reply_markup=check_keyboard, parse_mode="HTML")


@dp.callback_query(F.data.startswith("check_"))
async def check_payment(callback: types.CallbackQuery):
    await callback.answer()
    oid = callback.data.removeprefix("check_")
    order = await get_user_order(callback, oid)
    if not order:
        return
    await safe_delete(callback.message)
    await callback.message.answer("⏳ Запрос отправлен администратору. Ожидайте подтверждения...")
    admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить оплату", callback_data=f"admin_confirm_{oid}")],
        [InlineKeyboardButton(text="❌ Отклонить", callback_data=f"admin_reject_{oid}")],
    ])
    await bot.send_message(
        ADMIN_ID,
        f"💰 <b>ЗАПРОС НА ОПЛАТУ (ВРУЧНУЮ)!</b>\n\nКлиент: {callback.from_user.first_name}\nТовар: {order['name']}\nЛогин/ID: {order['login']}\nСумма: {order['price']}₽\n\nПроверь банк:",
        reply_markup=admin_keyboard,
        parse_mode="HTML",
    )


@dp.callback_query(F.data.startswith("admin_confirm_"))
async def admin_confirm(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа", show_alert=True)
        return
    await callback.answer()
    await mark_paid(callback.data.removeprefix("admin_confirm_"), "вручную")
    await safe_delete(callback.message)


@dp.callback_query(F.data.startswith("admin_reject_"))
async def admin_reject(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа", show_alert=True)
        return
    await callback.answer()
    oid = callback.data.removeprefix("admin_reject_")
    order = orders.get(oid)
    if order and order["status"] == "new":
        order["status"] = "rejected"
        save_orders()
        await bot.send_message(order["user_id"], f"❌ <b>Оплата не найдена.</b>\nНапиши в поддержку @{SUPPORT_USERNAME}.", parse_mode="HTML")
    await safe_delete(callback.message)


@dp.callback_query(F.data.startswith("admin_fulfil_"))
async def admin_fulfil(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа", show_alert=True)
        return
    await callback.answer()
    oid = callback.data.removeprefix("admin_fulfil_")
    order = orders.get(oid)
    if not order or order["status"] != "paid":
        await callback.message.answer("Заказ не найден или уже выполнен.")
        return

    if order["game"] == "stars":
        if not client:
            await callback.message.answer("❌ API-ключ MyStars не настроен.")
            return
        try:
            mystars_order = await asyncio.to_thread(
                client.create_order, type="stars", recipient=order["login"], quantity=order["stars"], payment_currency="ton"
            )
        except Exception as e:
            print(f"MYSTARS ORDER ERROR {oid}: {type(e).__name__}: {e}", flush=True)
            await callback.message.answer(f"❌ MyStars не создал заказ: {type(e).__name__}: {e}")
            return
        print(f"MYSTARS ORDER OK {oid}: {mystars_order}", flush=True)
        order["mystars_order"] = str(mystars_order)
        save_orders()
        await callback.message.answer(f"MyStars заказ создан:\n{mystars_order}\n\nЕсли MyStars просит оплату, оплати его в @my_stars_tg_bot.")

    await callback.message.answer(
        f"Проверь выдачу заказа {oid} ({order['name']}, {order['login']}). Когда выдача готова, нажми:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✅ Выдано, сообщить клиенту", callback_data=f"admin_done_{oid}")]]),
    )


@dp.callback_query(F.data.startswith("admin_done_"))
async def admin_done(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа", show_alert=True)
        return
    await callback.answer()
    oid = callback.data.removeprefix("admin_done_")
    order = orders.get(oid)
    if not order or order["status"] != "paid":
        await callback.message.answer("Заказ не найден или уже выполнен.")
        return
    order["status"] = "fulfilled"
    save_orders()
    await bot.send_message(order["user_id"], "🏁 <b>Заказ успешно выполнен!</b>\n\nСпасибо, что выбрали нас!", parse_mode="HTML")
    await safe_delete(callback.message)


async def handle_ping(request):
    return web.Response(text="OK")


async def handle_yookassa_webhook(request):
    try:
        data = await request.json()
        if data.get("event") == "payment.succeeded":
            payment = await asyncio.to_thread(Payment.find_one, data["object"]["id"])
            if payment.status == "succeeded":
                await mark_paid(payment.metadata.get("order_id"), "онлайн")
    except Exception as e:
        print(f"YOOKASSA WEBHOOK ERROR: {type(e).__name__}: {e}", flush=True)
    return web.Response(text="OK")


async def handle_crypto_webhook(request):
    raw = await request.read()
    if not crypto_signature_ok(raw, request.headers.get("crypto-pay-api-signature")):
        return web.Response(status=403, text="bad signature")
    try:
        data = json.loads(raw)
        if data.get("update_type") == "invoice_paid":
            await mark_paid(data["payload"]["payload"], "криптой")
    except Exception as e:
        print(f"CRYPTO WEBHOOK ERROR: {type(e).__name__}: {e}", flush=True)
    return web.Response(text="OK")


async def on_startup(app: web.Application):
    await bot.delete_webhook(drop_pending_updates=False)
    await bot.set_webhook(WEBHOOK_URL)


def main():
    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    app.router.add_get("/ping", handle_ping)
    app.router.add_post("/yookassa_webhook", handle_yookassa_webhook)
    app.router.add_post("/crypto_webhook", handle_crypto_webhook)
    app.on_startup.append(on_startup)
    web.run_app(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))


if __name__ == "__main__":
    main()
