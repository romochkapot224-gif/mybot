import asyncio
import os
import threading
from flask import Flask, request, jsonify
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# --- НАСТРОЙКИ ---
TOKEN = '9179658337:AAG9Ia4fR0dZjvA7cVNX829brt48AfaOqhU'
CARD_NUMBER = "2200 3961 2634 2837"
ADMIN_ID = 8804452762 

# --- ССЫЛКИ НА КАРТИНКИ ---
IMG_START = "https://i.postimg.cc/5yDB5CZ1/58dfdbc021d1218e2a6dec03fd8d992c-e50d6344-285f-4836-9894-ed71d863032f-(1).png"
IMG_FAQ = "https://i.postimg.cc/66hTdnxM/edd5740c076ef1085147274e76aa9a51-82febf9d-67bf-46ad-8a5f-0d2ddf725540.jpg"

# --- БОТ ---
bot = Bot(token=TOKEN)
dp = Dispatcher()

class SteamStates(StatesGroup):
    waiting_for_amount = State()
    waiting_for_login = State()

class StarsStates(StatesGroup):
    waiting_for_username = State()

user_orders = {}

# --- ПОСТОЯННАЯ КЛАВИАТУРА СНИЗУ ---
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

# --- ГЛАВНОЕ МЕНЮ (СТАРТ) ---
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
        await message.answer_photo(
            photo=IMG_START,
            caption=welcome_text,
            reply_markup=get_main_reply_keyboard(),
            parse_mode="HTML"
        )
    except:
        await message.answer(welcome_text, reply_markup=get_main_reply_keyboard(), parse_mode="HTML")

# --- ОБРАБОТКА КНОПОК СНИЗУ (КАТАЛОГ) ---
@dp.message(lambda message: message.text == "🛒 Каталог")
async def catalog_reply(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔥 Brawl Stars", callback_data="brawl"), 
         InlineKeyboardButton(text="🎮 Steam", callback_data="steam")],
        [InlineKeyboardButton(text="🟥 Roblox", callback_data="roblox"), 
         InlineKeyboardButton(text="🔫 PUBG", callback_data="pubg")],
        [InlineKeyboardButton(text="⭐ Telegram Stars", callback_data="stars")]
    ])
    await message.answer("🛒 Выбери игру или сервис из каталога:", reply_markup=keyboard)

# --- ОБРАБОТКА КНОПОК СНИЗУ (FAQ) ---
@dp.message(lambda message: message.text == "❓ FAQ")
async def faq_reply(message: types.Message):
    faq_text = (
        "❓ <b>Частые вопросы (FAQ)</b>\n\n"
        "1️⃣ <b>Как оплатить?</b> Выбираете товар, вводите логин, переводите сумму и нажимаете «Я оплатил».\n\n"
        "2️⃣ <b>Сколько ждать?</b> Обычно 1–5 минут после оплаты.\n\n"
        "3️⃣ <b>Не пришло, что делать?</b> Напишите в поддержку с чеком, мы все решим."
    )
    try:
        await message.answer_photo(photo=IMG_FAQ, caption=faq_text, parse_mode="HTML")
    except:
        await message.answer(faq_text, parse_mode="HTML")

# --- ОБРАБОТКА КНОПОК СНИЗУ (ПОДДЕРЖКА) ---
@dp.message(lambda message: message.text == "🆘 Поддержка")
async def support_reply(message: types.Message):
    await message.answer(
        "🆘 <b>Поддержка PotapchikShop</b>\n\n"
        "Если у тебя возникли вопросы по оплате или заказу, напиши нам:\n"
        "👉 @Fatty_Jerry",
        parse_mode="HTML"
    )

# --- STEAM ---
@dp.callback_query(lambda c: c.data == "steam")
async def steam_menu(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💵 100₽", callback_data="steam_100"),
         InlineKeyboardButton(text="💵 200₽", callback_data="steam_200")],
        [InlineKeyboardButton(text="💵 500₽", callback_data="steam_500"),
         InlineKeyboardButton(text="💵 1000₽", callback_data="steam_1000")],
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
        [InlineKeyboardButton(text="✅ Я оплатил", callback_data="user_paid")]
    ])
    await message.answer(f"Переведи {final_price}₽ на карту:\n{CARD_NUMBER}\n\nПосле перевода нажми:", reply_markup=keyboard)
    await state.clear()

# --- TELEGRAM STARS ---
@dp.callback_query(lambda c: c.data == "stars")
async def stars_menu(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer("⭐ Введи свой юзернейм в Telegram (кому подарить звезды):")
    await state.set_state(StarsStates.waiting_for_username)

@dp.message(StarsStates.waiting_for_username)
async def process_stars_username(message: types.Message, state: FSMContext):
    username = message.text.strip()
    final_price = 150 
    user_orders[message.from_user.id] = {"login": username, "price": final_price, "type": "Telegram Stars"}
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Я оплатил", callback_data="user_paid")]
    ])
    await message.answer(f"Звезды для: {username}\nК оплате: {final_price}₽\n\nПереведи на карту:\n{CARD_NUMBER}\n\nПосле перевода нажми:", reply_markup=keyboard)
    await state.clear()

# --- ПОДТВЕРЖДЕНИЕ ОПЛАТЫ ---
@dp.callback_query(lambda c: c.data == "user_paid")
async def user_paid(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_text("⏳ Проверяем оплату...")
    
    order = user_orders.get(callback.from_user.id)
    if order:
        admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"admin_confirm_{callback.from_user.id}")],
            [InlineKeyboardButton(text="❌ Отклонить", callback_data=f"admin_reject_{callback.from_user.id}")]
        ])
        order_type = order.get('type', 'Steam')
        await bot.send_message(ADMIN_ID, f"💰 ОПЛАТА!\nКлиент: {callback.from_user.first_name}\nТовар: {order_type}\nЛогин/Ник: {order['login']}\nСумма: {order['price']}₽", reply_markup=admin_keyboard)

@dp.callback_query(lambda c: c.data.startswith("admin_"))
async def admin_action(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет прав.", show_alert=True)
        return
    parts = callback.data.split("_")
    action, user_id = parts[1], int(parts[2])
    if action == "confirm":
        await bot.send_message(user_id, "✅ Оплата прошла! Заказ выполнен.")
        await callback.message.edit_text("✅ Подтверждено.")
    else:
        await bot.send_message(user_id, "❌ Оплата не найдена. Напиши в поддержку.")
        await callback.message.edit_text("❌ Отклонено.")

# --- НАЗАД В КАТАЛОГ ---
@dp.callback_query(lambda c: c.data == "back_to_catalog")
async def back_to_catalog(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔥 Brawl Stars", callback_data="brawl"), 
         InlineKeyboardButton(text="🎮 Steam", callback_data="steam")],
        [InlineKeyboardButton(text="🟥 Roblox", callback_data="roblox"), 
         InlineKeyboardButton(text="🔫 PUBG", callback_data="pubg")],
        [InlineKeyboardButton(text="⭐ Telegram Stars", callback_data="stars")]
    ])
    await callback.message.answer("🛒 Выбери игру или сервис из каталога:", reply_markup=keyboard)

# --- ОСТАЛЬНЫЕ ИГРЫ ---
@dp.callback_query(lambda c: c.data in ["brawl", "roblox", "pubg"])
async def other_games(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer("Этот раздел в разработке. Скоро добавим!")

# --- FLASK СЕРВЕР ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running"

@app.route('/webhook', methods=['POST'])
def webhook():
    return jsonify({"status": "success"}), 200

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, use_reloader=False)

async def main():
    print("Bot is starting...")
    threading.Thread(target=run_flask, daemon=True).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
