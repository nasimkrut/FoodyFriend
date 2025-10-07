import logging
import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler
from config import TELEGRAM_TOKEN
from handlers.registrations import build_handler, cancel
from db.base import init_db
from db.crud import get_user_by_telegram

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def profile_command(update, context):
    tg_id = update.effective_user.id
    user = await get_user_by_telegram(tg_id)
    if not user:
        await update.message.reply_text("Профиль не найден. Запусти /start чтобы зарегистрироваться.")
        return
    text = (
        f"Профиль:\n\n"
        f"Имя: {user.name}\n"
        f"Вес: {user.weight} кг\n"
        f"Рост: {user.height} см\n"
        f"Возраст: {user.age}\n"
        f"Пол: {user.gender}\n"
        f"Активность: {user.activity}\n"
        f"Цель: {user.goal}\n\n"
        f"Калории: {user.calorie_goal} ккал\n"
        f"Белки: {user.protein_goal} г\n"
        f"Жиры: {user.fat_goal} г\n"
        f"Углеводы: {user.carb_goal} г\n"
    )
    await update.message.reply_text(text)


async def help_command(update, context):
    await update.message.reply_text("/start — регистрация\n/profile — показать профиль\n/cancel — отменить ввод")


async def main():
    if not TELEGRAM_TOKEN:
        raise RuntimeError("TELEGRAM_TOKEN not set in env")

    await init_db()

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Handlers
    app.add_handler(build_handler())
    app.add_handler(CommandHandler("profile", profile_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("cancel", cancel))

    logger.info("Bot started")

    # Запуск polling вручную
    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    # Ждём событий без закрытия loop
    await asyncio.Event().wait()  # Блокировка, бот работает постоянно


if __name__ == "__main__":
    asyncio.run(main())
