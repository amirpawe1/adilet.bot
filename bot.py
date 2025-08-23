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

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

main_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатить доступ", callback_data="pay")],
        [InlineKeyboardButton(text="ℹ Подробнее о канале", callback_data="about")],
        [InlineKeyboardButton(text="🆘 Поддержка", callback_data="support")]
    ]
)

back_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]
    ]
)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Приветствую! Это официальный бот Адилета Кудайбергена, который поможет узнать больше о закрытом канале База и вступить в него." 
        "подписка ежемесячная 4990₸ или 9$, оплату принимаем через приложение Kaspi.kz"
        "Нажимай кнопку ниже:\n\nВыберите действие ниже 👇",
        reply_markup=main_kb
    )

@dp.callback_query(F.data == "pay")
async def pay(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Реквезиты: +77777777777"
        "💳 Тарифы:\n\n"
        "• 1 месяц — 4990₸\n"
        "• 6 месяцев — 19990₸\n"
        "• 12 месяцев — 44990₸\n\n"
        "После оплаты отправьте чек сюда 📎",
        reply_markup=back_kb
    )
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
    if ADMIN_ID:
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"approve:{message.from_user.id}")],
                [InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject:{message.from_user.id}")]
            ]
        )
        await message.forward(ADMIN_ID)
        await bot.send_message(
            ADMIN_ID,
            f"📎 Новый чек от @{message.from_user.username or message.from_user.id}",
            reply_markup=kb
        )
        await message.answer("✅ Чек отправлен на проверку админу.")
    else:
        await message.answer("⚠️ ADMIN_ID не задан.")

@dp.callback_query(F.data.startswith("approve"))
async def approve(callback: types.CallbackQuery):
    if callback.from_user.id == ADMIN_ID:
        user_id = int(callback.data.split(":")[1])
        await bot.send_message(user_id, f"✅ Доступ подтверждён! Вот ссылка на канал:\n{CHANNEL_LINK}")
        await callback.message.edit_text("✅ Пользователь получил доступ!")
    else:
        await callback.answer("⛔ Нет прав", show_alert=True)

@dp.callback_query(F.data.startswith("reject"))
async def reject(callback: types.CallbackQuery):
    if callback.from_user.id == ADMIN_ID:
        user_id = int(callback.data.split(":")[1])
        await bot.send_message(user_id, "❌ Ваш чек отклонён. Попробуйте снова или обратитесь в поддержку.")
        await callback.message.edit_text("❌ Пользователю отказано в доступе.")
    else:
        await callback.answer("⛔ Нет прав", show_alert=True)

async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(app):
    await bot.delete_webhook()
    await bot.session.close()

async def handle_webhook(request):
    data = await request.json()
    update = types.Update(**data)
    await dp.feed_update(bot, update)
    return web.Response()

async def handle_health(request):
    return web.Response(text="I'm alive!")

def main():
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, handle_webhook)
    app.router.add_get("/", handle_health)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    port = int(os.getenv("PORT", "10000"))
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
