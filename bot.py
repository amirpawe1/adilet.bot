import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
import time

API_TOKEN = os.getenv("8235029301:AAHtnMztthjduYDGIgxB47Q1OOfnaE8tO20")
ADMIN_ID = int(os.getenv("ADMIN_ID", "7341098964"))

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

user_last_action = {}
ANTI_SPAM_SECONDS = 2

main_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатить доступ", callback_data="pay")],
        [InlineKeyboardButton(text="📌 Подробнее о канале", callback_data="info")],
        [InlineKeyboardButton(text="🆘 Поддержка", callback_data="support")]
    ]
)

back_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back")]
    ]
)

pay_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="1 месяц — 4990₸", callback_data="pay_1m")],
        [InlineKeyboardButton(text="6 месяцев — 19990₸", callback_data="pay_6m")],
        [InlineKeyboardButton(text="12 месяцев — 44990₸", callback_data="pay_12m")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back")]
    ]
)

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    text = (
        "Приветствую! Это официальный бот Адилета Кудайбергена, который поможет узнать больше о закрытом канале База и вступить в него.\n\n"
        "Подписка ежемесячная 4990₸ или 9$, оплату принимаем через приложение Kaspi.kz\n\n"
        "Нажимай кнопку ниже:"
    )
    await message.answer(text, reply_markup=main_keyboard)

def check_spam(user_id):
    now = time.time()
    last = user_last_action.get(user_id, 0)
    if now - last < ANTI_SPAM_SECONDS:
        return True
    user_last_action[user_id] = now
    return False

@dp.callback_query()
async def handle_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if check_spam(user_id):
        await callback.answer("Слишком часто! Подожди пару секунд.", show_alert=True)
        return

    if callback.data == "pay":
        text = (
            "💳Стоимость подписки на канал\n"
            "1 месяц 4990₸\n"
            "6 месяцев 19.990₸\n"
            "12 месяцев 44.990₸\n\n"
            "Ниже есть кнопки, выбирай одну из тебе удобных и подключайся🔝"
        )
        await callback.message.edit_text(text, reply_markup=pay_keyboard)

    elif callback.data == "info":
        text = (
            "⚽ В закрытом канале тебя ждёт:\n\n"
            "— Уникальные материалы для развития футбольного мышления\n"
            "— Разборы матчей и тактические видео\n"
            "— Личные разговоры и ответы на вопросы\n"
            "— А может, именно ты станешь учеником на индивидуальных занятиях!\n\n"
            "Канал — это твой шанс выйти на новый уровень!"
        )
        await callback.message.edit_text(text, reply_markup=back_keyboard)

    elif callback.data == "support":
        text = "🆘 Поддержка: по всем вопросам пиши сюда 👉 @YourSupportUsername"
        await callback.message.edit_text(text, reply_markup=back_keyboard)

    elif callback.data == "back":
        await callback.message.edit_text(
            "Приветствую! Это официальный бот Адилета Кудайбергена, который поможет узнать больше о закрытом канале База и вступить в него.\n\n"
            "Подписка ежемесячная 4990₸ или 9$, оплату принимаем через приложение Kaspi.kz\n\n"
            "Нажимай кнопку ниже:",
            reply_markup=main_keyboard
        )

    elif callback.data in ["pay_1m", "pay_6m", "pay_12m"]:
        await callback.message.answer(
            "Отправь PDF-файл с чеком об оплате сюда, и администратор проверит его. ✅"
        )

    await callback.answer()

@dp.message(F.document)
async def handle_document(message: types.Message):
    if message.document.mime_type == "application/pdf":
        await bot.send_document(
            ADMIN_ID,
            message.document,
            caption=f"Чек от пользователя @{message.from_user.username or message.from_user.id}"
        )
        await message.answer("✅ Чек получен! Ожидай подтверждения доступа от администратора.")
    else:
        await message.answer("Пришли именно PDF файл чека!")

@dp.message(Command("approve"))
async def approve_user(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ У тебя нет прав для этой команды.")
        return
    await message.answer("✅ Доступ подтверждён. Пользователь может быть добавлен в канал.")

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
