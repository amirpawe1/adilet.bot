import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio
import os

API_TOKEN = os.getenv("8235029301:AAHtnMztthjduYDGIgxB47Q1OOfnaE8tO20")
ADMIN_ID = int(os.getenv("ADMIN_ID", "7341098964"))

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_cmd(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатить доступ", callback_data="pay")],
        [InlineKeyboardButton(text="ℹ Подробнее о канале", callback_data="about")],
        [InlineKeyboardButton(text="🛠 Поддержка", callback_data="support")]
    ])
    await message.answer(
        "Приветствую! Это официальный бот Адилета Кудайбергена, который поможет узнать больше о закрытом канале База и вступить в него.\n\n"
        "Подписка ежемесячная: 4990₸ или 9$\n"
        "Оплату принимаем через приложение Kaspi.kz\n\n"
        "Нажимай кнопку ниже:",
        reply_markup=kb
    )

@dp.callback_query(F.data == "pay")
async def pay_handler(callback: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1 месяц - 4990₸", callback_data="pay_1m")],
        [InlineKeyboardButton(text="6 месяцев - 19.990₸", callback_data="pay_6m")],
        [InlineKeyboardButton(text="12 месяцев - 44.990₸", callback_data="pay_12m")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back")]
    ])
    await callback.message.edit_text(
        "💳Стоимость подписки на канал\n"
        "1 месяц — 4990₸\n"
        "6 месяцев — 19.990₸\n"
        "12 месяцев — 44.990₸\n\n"
        "Ниже есть кнопки, выбирай одну из удобных и подключайся 🔝",
        reply_markup=kb
    )

@dp.callback_query(F.data == "about")
async def about_handler(callback: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back")]
    ])
    await callback.message.edit_text(
        "⚽ В закрытом канале ты найдёшь:\n"
        "- Разбор футбольных матчей и тренировок\n"
        "- Советы для развития мышления футболиста\n"
        "- Видео и аналитика\n"
        "- Возможность стать учеником индивидуально 🔥",
        reply_markup=kb
    )

@dp.callback_query(F.data == "support")
async def support_handler(callback: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back")]
    ])
    await callback.message.edit_text(
        "👨‍💻 Поддержка: напишите сюда @yourusername",
        reply_markup=kb
    )

@dp.callback_query(F.data == "back")
async def back_handler(callback: CallbackQuery):
    await start_cmd(callback.message)

@dp.message(F.document | F.photo)
async def receive_file(message: Message):
    if str(message.from_user.id) == str(ADMIN_ID):
        return  # админ не должен сам себе кидать
    await bot.send_message(
        ADMIN_ID,
        f"📩 Новый чек от @{message.from_user.username or message.from_user.id}"
    )
    if message.document:
        await message.document.copy_to(ADMIN_ID)
    elif message.photo:
        await message.photo[-1].copy_to(ADMIN_ID)
    await message.answer("✅ Чек отправлен! Ожидайте подтверждения.")

@dp.message(Command("approve"))
async def approve(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.reply("✅ Доступ подтвержден. Пользователь добавлен в канал.")
    else:
        await message.reply("❌ У вас нет прав для этой команды.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
