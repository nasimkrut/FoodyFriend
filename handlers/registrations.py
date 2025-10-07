from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from db.crud import set_user_profile, get_user_by_telegram
from utils.calculations import calculate_macros

(
    ASK_NAME,
    ASK_WEIGHT,
    ASK_HEIGHT,
    ASK_AGE,
    ASK_GENDER,
    ASK_ACTIVITY,
    ASK_GOAL,
    COMPLETE,
) = range(8)

# Временное хранилище для регистрации (в памяти)
_registration_cache: dict[int, dict] = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id
    _registration_cache[tg_id] = {}
    await update.message.reply_text("Давай зарегистрируем профиль. Как тебя зовут?")
    return ASK_NAME

async def ask_weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id
    name = update.message.text.strip()
    _registration_cache[tg_id]["name"] = name
    await update.message.reply_text("Укажи, пожалуйста, свой вес в килограммах (например: 72.5)")
    return ASK_WEIGHT

async def ask_height(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id
    try:
        weight = float(update.message.text.replace(",", "."))
    except:
        await update.message.reply_text("Неправильный формат веса. Введи число, например: 72.5")
        return ASK_WEIGHT
    _registration_cache[tg_id]["weight"] = weight
    await update.message.reply_text("Укажи рост в сантиметрах (например: 178)")
    return ASK_HEIGHT

async def ask_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id
    try:
        height = float(update.message.text.replace(",", "."))
    except:
        await update.message.reply_text("Неправильный формат роста. Введи число, например: 178")
        return ASK_HEIGHT
    _registration_cache[tg_id]["height"] = height
    await update.message.reply_text("Сколько тебе лет? (пример: 30)")
    return ASK_AGE

async def ask_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id
    try:
        age = int(update.message.text.strip())
    except:
        await update.message.reply_text("Неправильный формат возраста. Введи целое число, например: 30")
        return ASK_AGE
    _registration_cache[tg_id]["age"] = age
    await update.message.reply_text("Пол? (male/female) — напиши 'male' или 'female'")
    return ASK_GENDER

async def ask_activity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id
    gender = update.message.text.strip().lower()
    if gender not in ("male", "female", "other", "m", "f"):
        await update.message.reply_text("Пожалуйста, напиши 'male' или 'female' (или 'other').")
        return ASK_GENDER
    _registration_cache[tg_id]["gender"] = "male" if gender.startswith("m") else "female" if gender.startswith("f") else "other"
    await update.message.reply_text(
        "Укажи уровень активности (примерные значения):\n"
        "1.2 — малоподвижный образ жизни\n"
        "1.375 — лёгкая активность\n"
        "1.55 — умеренная активность\n"
        "1.725 — активный образ жизни\n"
        "Напиши число (например: 1.55)"
    )
    return ASK_ACTIVITY

async def ask_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id
    try:
        activity = float(update.message.text.replace(",", "."))
    except:
        await update.message.reply_text("Неправильный формат. Введи число активности, например: 1.55")
        return ASK_ACTIVITY
    _registration_cache[tg_id]["activity"] = activity
    await update.message.reply_text("Какова твоя цель? Напиши: gain (набор), maintain (поддержание) или lose (похудение)")
    return ASK_GOAL

async def complete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id
    goal = update.message.text.strip().lower()
    if goal not in ("gain", "maintain", "lose"):
        await update.message.reply_text("Пожалуйста: gain, maintain или lose.")
        return ASK_GOAL

    _registration_cache[tg_id]["goal"] = goal

    data = _registration_cache.pop(tg_id)
    # Сохранение в БД
    user = await set_user_profile(tg_id, **data)
    # Вернём рассчитанные цели (они сохранены в user)
    text = (
        "Профиль сохранён!\n\n"
        f"Имя: {user.name}\n"
        f"Вес: {user.weight} кг\n"
        f"Рост: {user.height} см\n"
        f"Возраст: {user.age}\n"
        f"Пол: {user.gender}\n"
        f"Активность: {user.activity}\n"
        f"Цель: {user.goal}\n\n"
        f"Рассчитанные нормы:\n"
        f"Калории: {user.calorie_goal} ккал\n"
        f"Белки: {user.protein_goal} г\n"
        f"Жиры: {user.fat_goal} г\n"
        f"Углеводы: {user.carb_goal} г\n"
    )
    await update.message.reply_text(text)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id
    _registration_cache.pop(tg_id, None)
    await update.message.reply_text("Регистрация отменена.")
    return ConversationHandler.END

def build_handler():
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_weight)],
            ASK_WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_height)],
            ASK_HEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_age)],
            ASK_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_gender)],
            ASK_GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_activity)],
            ASK_ACTIVITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_goal)],
            ASK_GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, complete)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
        name="registration_conversation",
    )
    return conv
