import os
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7341098964
SUPPORT_USERNAME = "xe8oz"
CHANNEL_LINK = "https://t.me/+4KdL8SuRDuA4YjZi"

WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", os.getenv("RENDER_EXTERNAL_URL", ""))
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = WEBHOOK_HOST + WEBHOOK_PATH

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def main_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="💳 Оплатить доступ", callback_data="pay")
    builder.button(text="ℹ Подробнее о канале", callback_data="about")
    builder.button(text="🆘 Поддержка", callback_data="support")
    builder.adjust(1)
    return builder.as_markup()

def pay_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="1 месяц — 5000₸", callback_data="pay_1m")
    builder.button(text="3 месяца — 12000₸", callback_data="pay_3m")
    builder.button(text="⬅️ Назад", callback_data="back")
    builder.adjust(1)
    return builder.as_markup()

def support_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="✉ Написать поддержку", url=f"https://t.me/{SUPPORT_USERNAME}")
    builder.button(text="⬅️ Назад", callback_data="back")
    builder.adjust(1)
    return builder.as_markup()

def about_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Назад", callback_data="back")
    return builder.as_markup()

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "👋 Привет! Добро пожаловать в бот канала Адлета!\n\n"
        "Здесь ты можешь получить доступ к закрытому контенту ⚽",
        reply_markup=main_menu()
    )

@dp.callback_query(F.data == "pay")
async def pay_section(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "💳 Выберите тариф:\n\n"
        "• 1 месяц — 5000₸\n"
        "• 3 месяца — 12000₸\n\n"
        "После оплаты отправьте чек сюда 📎",
        reply_markup=pay_menu()
    )
    await callback.answer()

@dp.callback_query(F.data == "about")
async def about_section(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "⚽ Канал тренера Адлета — это:\n"
        "• Обучающий контент по футболу\n"
        "• Разбор тактик\n"
        "• Советы для игроков\n\n"
        "Присоединяйтесь и улучшайте игру! 💪",
        reply_markup=about_menu()
    )
    await callback.answer()

@dp.callback_query(F.data == "support")
async def support_section(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "✉ Поддержка доступна по кнопке ниже 👇",
        reply_markup=support_menu()
    )
    await callback.answer()

@dp.callback_query(F.data == "back")
async def go_back(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "⬅️ Главное меню:",
        reply_markup=main_menu()
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("pay_"))
async def fake_payment(callback: types.CallbackQuery):
    if callback.data == "pay_1m":
        text = "✅ Вы выбрали тариф: 1 месяц — 5000₸"
    else:
        text = "✅ Вы выбрали тариф: 3 месяца — 12000₸"
    await callback.message.edit_text(
        f"{text}\n\nОтправьте чек сюда 📎",
        reply_markup=about_menu()
    )
    await callback.answer()

@dp.message(F.document | F.photo)
async def handle_payment_proof(message: types.Message):
    await message.forward(ADMIN_ID)
    await message.answer("✅ Чек отправлен администратору. Ожидайте подтверждения.")

@dp.message(F.document | F.photo)
async def handle_files(message: types.Message):
    if ADMIN_ID:
        await message.forward(ADMIN_ID)
        await bot.send_message(ADMIN_ID, f"💡 Новый чек от пользователя ID: {message.from_user.id}\n"
                                         f"Чтобы выдать доступ, используй команду:\n"
                                         f"/approve {message.from_user.id}")
        await message.answer("✅ Чек отправлен на проверку админу.")
    else:
        await message.answer("⚠️ ADMIN_ID не задан. Сообщи админу!")

@dp.message(Command("approve"))
async def approve(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        parts = message.text.split()
        if len(parts) == 2 and parts[1].isdigit():
            user_id = int(parts[1])
            try:
                await bot.send_message(user_id, f"✅ Доступ подтверждён! Вот ссылка на канал:\n{CHANNEL_LINK}")
                await message.answer(f"✅ Доступ выдан пользователю {user_id}")
            except Exception as e:
                await message.answer(f"⚠️ Ошибка при отправке пользователю {user_id}: {e}")
        else:
            await message.answer("❌ Используй формат: /approve user_id")
    else:
        await message.answer("⛔ У тебя нет прав для этой команды.")

def main():
    app = web.Application()
    app.router.add_get("/", health)
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    port = int(os.getenv("PORT", "10000"))
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()

