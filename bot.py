import os
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

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

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💳 Оплатить доступ")],
        [KeyboardButton(text="ℹ Подробнее о канале")],
        [KeyboardButton(text="🆘 Поддержка")]
    ],
    resize_keyboard=True
)

back_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⬅️ Назад")]
    ],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Добро пожаловать в бот канала Адлета!\n\nВыберите действие ниже 👇",
        reply_markup=main_kb
    )

@dp.message(F.text == "💳 Оплатить доступ")
async def pay(message: types.Message):
    await message.answer(
        "💳 Тарифы:\n\n• 1 месяц — 5000 тг\n• 3 месяца — 12000 тг\n\nПосле оплаты отправьте чек сюда 📎",
        reply_markup=back_kb
    )

@dp.message(F.text == "ℹ Подробнее о канале")
async def about(message: types.Message):
    await message.answer(
        "⚽ Канал тренера Адлета — это:\n• Обучающий контент по футболу\n• Разбор тактик\n• Советы для игроков\n\nПодключайтесь и улучшайте игру!",
        reply_markup=back_kb
    )

@dp.message(F.text == "🆘 Поддержка")
async def support(message: types.Message):
    await message.answer(
        f"✉ Поддержка: @{SUPPORT_USERNAME}",
        reply_markup=back_kb
    )

@dp.message(F.text == "⬅️ Назад")
async def back(message: types.Message):
    await message.answer("⬅️ Возврат в главное меню", reply_markup=main_kb)

@dp.message(F.document | F.photo)
async def handle_files(message: types.Message):
    if ADMIN_ID:
        await message.forward(ADMIN_ID)
        await message.answer("✅ Чек отправлен на проверку админу.")
    else:
        await message.answer("⚠️ ADMIN_ID не задан. Сообщи админу!")

@dp.message(Command("approve"))
async def approve(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer(f"✅ Доступ подтверждён! Вот ссылка на канал:\n{CHANNEL_LINK}")
    else:
        await message.answer("⛔ У тебя нет прав для этой команды.")

async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(app):
    await bot.delete_webhook()
    await bot.session.close()

async def handle_health(request):
    return web.Response(text="I'm alive!")

async def webhook_handler(request):
    data = await request.json()
    update = types.Update(**data)
    await dp.feed_update(bot, update)
    return web.Response()

async def main():
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, webhook_handler)
    app.router.add_get("/", handle_health)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    port = int(os.getenv("PORT", "10000"))
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
