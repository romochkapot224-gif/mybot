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

IMG_START = "https://i.postimg.cc/5yDB5CZ1/58dfdbc021d1218e2a6dec03fd8d992c-e50d6344-285f-4836-9894-ed71d863032f-(1).png"

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

# --- МЕНЮ ---
def get_main_reply_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛒 Каталог"), KeyboardButton(text="❓ FAQ")],
            [KeyboardButton(text="🆘 Поддержка")]
        ],
        resize_keyboard=True
    )

@dp.message(Command("start"))
async def start(message: types.Message):
    welcome_text = (
        "👋 <b>Добро пожаловать в PotapchikShop!</b>\n\n"
        "Мы — современный сервис по пополнению аккаунтов и покупке игровых ценностей.\n\n"
        "В нашем ассортименте:\n"
        "🎮 Steam | 🔥 Brawl Stars | 🟥 Roblox | 🔫 PUBG | ⭐ Telegram Stars\n\n"
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

@dp.message(lambda message: message.text == "❓ FAQ")
async def faq_reply(message: types.Message):
    await message.answer("❓ <b>Частые вопросы (FAQ)</b>\n\n1️⃣ <b>Как оплатить?</b> Выбираете товар, способ оплаты, переводите и жмете «Проверить».\n\n2️⃣ <b>Сколько ждать?</b> 1–5 минут.\n\n3️⃣ <b>Не пришло?</b> Напишите в поддержку с чеком.", parse_mode="HTML")

@dp.message(lambda message: message.text == "🆘 Поддержка")
async def support_reply(message: types.Message):
    await message.answer("🆘 <b>Поддержка PotapchikShop</b>\n\nНапиши нам:\n👉 @Fatty_Jerry", parse_mode="HTML")

# --- STEAM ---
@dp.callback_query(lambda c: c.data == "steam")
async def steam_menu(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💵 100₽", callback_data="steam_100"), InlineKeyboardButton(text="💵 200₽", callback_data="steam_200")],
        [InlineKeyboardButton(text="💵 500₽", callback_data="steam_500"), InlineKeyboardButton(text="💵 1000₽", callback_data="steam_1000")],
        [InlineKeyboardButton(text="✍️ Своя сумма", callback_data="steam_custom")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_catalog")]
    ])
    await callback.message.answer("Выбери сумму пополнения Steam:", reply_markup=keyboard)

@dp.callback_query(lambda c: c.data.startswith("steam_") and c.data != "steam_custom")
async def steam_amount_chosen(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete()
    amount = int(callback.data.split("_")[1])
    final_price = int(amount * 1.15)
    await state.update_data(steam_amount=amount, final_price=final_price)
    await callback.message.answer(f"Ты выбрал {amount}₽. К оплате: {final_price}₽.\nВведи логин Steam:")
    await state.set_state(SteamStates.waiting_for_login)

@dp.callback_query(lambda c: c.data == "steam_custom")
async def steam_custom(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer("Введи сумму пополнения (только цифры):")
    await state.set_state(SteamStates.waiting_for_amount)

@dp.message(SteamStates.waiting_for_amount)
async def process_custom_amount(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Введи только цифры.")
        return
    amount = int(message.text)
    final_price = int(amount * 1.15)
    await state.update_data(steam_amount=amount, final_price=final_price)
    await message.answer(f"Ты выбрал {amount}₽. К оплате: {final_price}₽.\nВведи логин Steam:")
    await state.set_state(SteamStates.waiting_for_login)

@dp.message(SteamStates.waiting_for_login)
async def process_login(message: types.Message, state: FSMContext):
    login = message.text.strip()
    data = await state.get_data()
    final_price = data.get('final_price')
    user_orders[message.from_user.id] = {"login": login, "price": final_price, "type": "Steam"}
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Карта", callback_data="pay_card")],
        [InlineKeyboardButton(text="🏦 СБП", callback_data="pay_sbp")]
    ])
    await message.answer(f"Отлично! Логин: {login}\nСумма к оплате: {final_price}₽.\n\nВыбери удобный способ оплаты:", reply_markup=keyboard)
    await state.clear()

# --- STARS ---
@dp.callback_query(lambda c: c.data == "stars")
async def stars_menu(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ 100 звезд", callback_data="stars_100"), InlineKeyboardButton(text="⭐ 200 звезд", callback_data="stars_200")],
        [InlineKeyboardButton(text="⭐ 500 звезд", callback_data="stars_500"), InlineKeyboardButton(text="⭐ 1000 звезд", callback_data="stars_1000")],
        [InlineKeyboardButton(text="✍️ Своё количество", callback_data="stars_custom")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_catalog")]
    ])
    await callback.message.answer("Выбери количество звезд:", reply_markup=keyboard)

@dp.callback_query(lambda c: c.data.startswith("stars_") and c.data != "stars_custom")
async def stars_amount_chosen(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete()
    stars_amount = int(callback.data.split("_")[1])
    final_price = int(stars_amount * STAR_PRICE * 1.15)
    await state.update_data(stars_amount=stars_amount, final_price=final_price)
    await callback.message.answer(f"Ты выбрал {stars_amount} звезд. К оплате: {final_price}₽.\nВведи юзернейм Telegram:")
    await state.set_state(StarsStates.waiting_for_username)

@dp.callback_query(lambda c: c.data == "stars_custom")
async def stars_custom(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer("Введи количество звезд (только цифры):")
    await state.set_state(StarsStates.waiting_for_custom_stars)

@dp.message(StarsStates.waiting_for_custom_stars)
async def process_custom_stars(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Введи только цифры.")
        return
    stars_amount = int(message.text)
    final_price = int(stars_amount * STAR_PRICE * 1.15)
    await state.update_data(stars_amount=stars_amount, final_price=final_price)
    await callback.message.answer(f"Ты выбрал {stars_amount} звезд. К оплате: {final_price}₽.\nВведи юзернейм Telegram:")
    await state.set_state(StarsStates.waiting_for_username)

@dp.message(StarsStates.waiting_for_username)
async def process_stars_username(message: types.Message, state: FSMContext):
    username = message.text.strip()
    data = await state.get_data()
    final_price = data.get('final_price')
    stars_amount = data.get('stars_amount')
    user_orders[message.from_user.id] = {"login": username, "price": final_price, "type": f"Telegram Stars ({stars_amount} шт.)"}
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Карта", callback_data="pay_card")],
        [InlineKeyboardButton(text="🏦 СБП", callback_data="pay_sbp")]
    ])
    await message.answer(f"Отлично! Получатель: {username}\nСумма к оплате: {final_price}₽.\n\nВыбери удобный способ оплаты:", reply_markup=keyboard)
    await state.clear()

# --- ВЫБОР СПОСОБА ---
@dp.callback_query(lambda c: c.data in ["pay_card", "pay_sbp"])
async def process_payment_method(callback: types.CallbackQuery):
    await callback.answer()
    order = user_orders.get(callback.from_user.id)
    
    if not order:
        await callback.message.answer("Ошибка: заказ не найден.")
        return

    method = callback.data
    await callback.message.delete() 

    check_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Проверить оплату", callback_data="check_payment")]
    ])

    if method == "pay_card":
        await callback.message.answer(f"💳 <b>Перевод на карту</b>\n\nСумма: <b>{order['price']}₽</b>\nКарта: <code>{CARD_NUMBER}</code>\n\nПосле перевода нажми:", reply_markup=check_keyboard, parse_mode="HTML")
    elif method == "pay_sbp":
        await callback.message.answer(f"🏦 <b>Оплата через СБП</b>\n\nСумма: <b>{order['price']}₽</b>\nНомер: <code>{SBP_PHONE}</code>\n\nПосле перевода нажми:", reply_markup=check_keyboard, parse_mode="HTML")

# --- ПРОВЕРКА ОПЛАТЫ ---
@dp.callback_query(lambda c: c.data == "check_payment")
async def check_payment(callback: types.CallbackQuery):
    await callback.answer()
    order = user_orders.get(callback.from_user.id)
    
    if not order:
        await callback.message.answer("Ошибка: заказ не найден.")
        return

    await callback.message.delete()
    await callback.message.answer("⏳ Запрос отправлен администратору. Ожидайте подтверждения...")
    
    admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить оплату", callback_data=f"admin_confirm_{callback.from_user.id}")],
        [InlineKeyboardButton(text="❌ Отклонить", callback_data=f"admin_reject_{callback.from_user.id}")]
    ])
    
    await bot.send_message(ADMIN_ID, f"💰 <b>ЗАПРОС НА ОПЛАТУ!</b>\n\nКлиент: {callback.from_user.first_name}\nТовар: {order.get('type', 'Steam')}\nЛогин/Ник: {order['login']}\nСумма: {order['price']}₽\n\nПроверь банк:", reply_markup=admin_keyboard, parse_mode="HTML")

# --- АДМИН ПОДТВЕРЖДАЕТ ---
@dp.callback_query(lambda c: c.data.startswith("admin_confirm"))
async def admin_confirm(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID: return
    user_id = int(callback.data.split("_")[2])
    
    # Сообщение клиенту
    await bot.send_message(user_id, "✅ <b>Оплата получена!</b>\n\nМы приступаем к выполнению вашего заказа. Ожидайте.", parse_mode="HTML")
    
    # Кнопка "Заказ выполнен" для админа
    complete_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏁 Заказ выполнен", callback_data=f"admin_complete_{user_id}")]
    ])
    await callback.message.edit_text("✅ Ты подтвердил оплату. Нажми кнопку ниже, когда выдашь товар.", reply_markup=complete_keyboard)

# --- АДМИН ОТКЛОНЯЕТ ---
@dp.callback_query(lambda c: c.data.startswith("admin_reject"))
async def admin_reject(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID: return
    user_id = int(callback.data.split("_")[2])
    await bot.send_message(user_id, "❌ <b>Оплата не найдена.</b>\nНапиши в поддержку @Fatty_Jerry.", parse_mode="HTML")
    await callback.message.edit_text("❌ Отклонено.")

# --- АДМИН ЗАВЕРШАЕТ ЗАКАЗ ---
@dp.callback_query(lambda c: c.data.startswith("admin_complete"))
async def admin_complete(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID: return
    user_id = int(callback.data.split("_")[2])
    await bot.send_message(user_id, "🏁 <b>Заказ успешно выполнен!</b>\n\nСпасибо, что выбрали PotapchikShop. Будем рады видеть вас снова! 🎮", parse_mode="HTML")
    await callback.message.edit_text("🏁 Заказ завершен. Клиент уведомлен.")

@dp.callback_query(lambda c: c.data == "back_to_catalog")
async def back_to_catalog(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔥 Brawl Stars", callback_data="brawl"), InlineKeyboardButton(text="🎮 Steam", callback_data="steam")],
        [InlineKeyboardButton(text="🟥 Roblox", callback_data="roblox"), InlineKeyboardButton(text="🔫 PUBG", callback_data="pubg")],
        [InlineKeyboardButton(text="⭐ Telegram Stars", callback_data="stars")]
    ])
    await callback.message.answer("🛒 Выбери игру или сервис из каталога:", reply_markup=keyboard)

@dp.callback_query(lambda c: c.data in ["brawl", "roblox", "pubg"])
async def other_games(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer("Этот раздел в разработке. Скоро добавим!")

# --- ВЕБХУК ---
async def on_startup(app: web.Application):
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(WEBHOOK_URL)

def main():
    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    app.on_startup.append(on_startup)
    
    port = int(os.environ.get("PORT", 10000))
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
