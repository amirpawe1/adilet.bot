import os
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7341098964
SUPPORT_USERNAME = "xe8oz"
CHANNEL_LINK = "https://t.me/+4KdL8SuRDuA4YjZi"

WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", os.getenv("RENDER_EXTERNAL_URL", ""))
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = WEBHOOK_HOST + WEBHOOK_PATH

logging.basicConfig(level=logging.INFO)

# 📦 Бот и Диспетчер
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

pending_users = {}

main_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="💳 Оплатить доступ", callback_data="pay")],
    [InlineKeyboardButton(text="ℹ Подробнее о канале", callback_data="about")],
    [InlineKeyboardButton(text="🆘 Поддержка", callback_data="support")]
])

back_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]
])

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Добро пожаловать в бот канала Адлета!\n\nВыберите действие ниже 👇",
        reply_markup=main_kb
    )

@dp.callback_query(F.data == "pay")
async def pay(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "💳 Тарифы:\n\n"
        "• 1 месяц — 4990₸\n"
        "• 6 месяцев — 19990₸\n"
        "• 12 месяцев — 44990₸\n\n"
        "После оплаты отправьте чек сюда 📎 (фото или файл).",
        reply_markup=back_kb
    )
    pending_users[callback.from_user.id] = True
    await callback.answer()

@dp.callback_query(F.data == "about")
async def about(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "⚽ Канал тренера Адлета — это:\n"
        "• Обучающий контент по футболу\n"
        "• Разбор тактик\n"
        "• Советы для игроков\n\n"
        "Подключайтесь и улучшайте игру!",
        reply_markup=back_kb
    )
    await callback.answer()

@dp.callback_query(F.data == "support")
async def support(callback: types.CallbackQuery):
    await callback.message.edit_text(
        f"✉ Поддержка: @{SUPPORT_USERNAME}",
        reply_markup=back_kb
    )
    await callback.answer()

@dp.callback_query(F.data == "back")
async def back(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "⬅️ Возврат в главное меню",
        reply_markup=main_kb
    )
    await callback.answer()

@dp.message(F.document | F.photo)
async def handle_files(message: types.Message):
    user_id = message.from_user.id
    if user_id in pending_users and pending_users[user_id]:
        # Пересылаем админу
        await message.forward(ADMIN_ID)
        await message.answer("✅ Чек отправлен на проверку админу.")
        # Уведомляем админа
        await bot.send_message(
            ADMIN_ID,
            f"📥 Новый чек от пользователя:\n"
            f"👤 {message.from_user.full_name}\n"
            f"🆔 ID: {message.from_user.id}\n\n"
            f"Чтобы подтвердить доступ:\n"
            f"/approve {message.from_user.id}\n\n"
            f"Чтобы отклонить:\n"
            f"/reject {message.from_user.id}"
        )
    else:
        await message.answer("⚠️ Сначала выберите 'Оплатить доступ', затем отправьте чек.")

@dp.message(Command("approve"))
async def approve(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        parts = message.text.split()
        if len(parts) == 2 and parts[1].isdigit():
            user_id = int(parts[1])
            await bot.send_message(
                user_id,
                f"✅ Оплата подтверждена! Вот ссылка на канал:\n{CHANNEL_LINK}"
            )
            await message.answer(f"✅ Доступ для пользователя {user_id} подтверждён.")
            if user_id in pending_users:
                del pending_users[user_id]
        else:
            await message.answer("⚠ Используй: /approve user_id")
    else:
        await message.answer("⛔ У тебя нет прав для этой команды.")

@dp.message(Command("reject"))
async def reject(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        parts = message.text.split()
        if len(parts) == 2 and parts[1].isdigit():
            user_id = int(parts[1])
            await bot.send_message(
                user_id,
                "❌ Оплата не подтверждена. Пожалуйста, проверьте реквизиты и попробуйте снова."
            )
            await message.answer(f"❌ Оплата пользователя {user_id} отклонена.")
            if user_id in pending_users:
                del pending_users[user_id]
        else:
            await message.answer("⚠ Используй: /reject user_id")
    else:
        await message.answer("⛔ У тебя нет прав для этой команды.")

async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(app):
    await bot.delete_webhook()
    await bot.session.close()

async def handle_health(request):
    return web.Response(text="I'm alive!")

def main():
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, dp.start_webhook)
    app.router.add_get("/", handle_health)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    port = int(os.getenv("PORT", "10000"))
    web.run_app(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
