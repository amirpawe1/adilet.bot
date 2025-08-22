import os
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💳 Оплатить")],
        [KeyboardButton(text="ℹ Подробнее о канале")],
        [KeyboardButton(text="🆘 Поддержка")],
    ],
    resize_keyboard=True
)

@dp.message(commands=["start"])
async def start_handler(message: types.Message):
    await message.answer(
        "👋 Привет! Я бот канала Адлета.\n"
        "Здесь ты можешь оплатить доступ, узнать подробнее о канале или связаться с поддержкой.",
        reply_markup=menu
    )

async def echo_handler(message: types.Message):
    if message.text == "💳 Оплатить":
        await message.answer("💳 Оплата временно в разработке. Скоро добавим!")
    elif message.text == "ℹ Подробнее о канале":
        await message.answer("📢 Канал посвящён футболу и обучающему контенту.")
    elif message.text == "🆘 Поддержка":
        await message.answer("✉ Для связи с поддержкой напиши: @адлет_support")
    else:
        await message.answer("Я тебя не понял 🤔. Используй кнопки ниже.", reply_markup=menu)

async def on_startup(app: web.Application):
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(app: web.Application):
    await bot.delete_webhook()
    await bot.session.close()

def main():
    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    port = int(os.getenv("PORT", 8080))
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
