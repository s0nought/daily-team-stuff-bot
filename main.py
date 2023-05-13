import logging

logging.basicConfig(
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level = logging.INFO
)

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from modules.constants import (
    TELEGRAM_GROUP_ID,
    START_MESSAGE,
    HELP_MESSAGE,
    DAILY_JOB_INTERVAL_SEC,
    RELEASE_JOB_TIME_UTC,
    DSM_JOB_TIME_UTC,
    BIRTHDAY_JOB_TIME_UTC
)

from modules.secrets import (
    BOT_TOKEN,
    ADMIN_TELEGRAM_IDS
)

from modules.classes import (
    settings
)

from modules.utils import (
    is_friday,
    is_weekend,
    is_planning_day
)

def check_user(func):
    async def wrapper(*args):
        user_name = args[0].message.from_user.username

        if user_name not in settings.get_users():
            return

        await func(*args)

    return wrapper

def check_admin(func):
    async def wrapper(*args):
        user_id = str(args[0].message.from_user.id)

        if user_id not in ADMIN_TELEGRAM_IDS:
            return

        await func(*args)

    return wrapper

@check_user
async def bot_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = START_MESSAGE
    )

@check_user
async def bot_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = HELP_MESSAGE
    )

@check_user
async def bot_dsm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_name = settings.get_dsm_current()
    first_name = settings.get_first_name(user_name)

    await context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = f"Очередь DSM:\n{first_name}\n{user_name}"
    )

@check_user
async def bot_release(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_name = settings.get_release_current()
    first_name = settings.get_first_name(user_name)

    await context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = f"Очередь релизить:\n{first_name}\n{user_name}"
    )

@check_user
async def bot_onvacation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_name = update.message.from_user.username
    first_name = settings.get_first_name(user_name)

    settings.set_vacation_status(user_name, True)

    await context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = f"{first_name}, установлен статус \"В отпуске\""
    )

@check_user
async def bot_fromvacation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_name = update.message.from_user.username
    first_name = settings.get_first_name(user_name)

    settings.set_vacation_status(user_name, False)

    await context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = f"{first_name}, установлен статус \"Из отпуска\""
    )

@check_user
async def bot_vacationlist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = ", ".join(list(map(lambda x: settings.get_first_name(x), settings.get_vacation_list())))

    await context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = f"В отпуске: {text or '-'}"
    )

@check_admin
async def bot_save(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings.save()

    await context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = "Настройки сохранены."
    )

@check_admin
async def bot_addholiday(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    date = context.args[0] # %d.%m

    settings.add_holiday(date)

    await context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = f"Добавлен праздничный день: {date}"
    )

@check_admin
async def bot_removeholiday(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    date = context.args[0] # %d.%m

    settings.remove_holiday(date)

    await context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = f"Удалён праздничный день: {date}"
    )

@check_admin
async def bot_adduser(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_name = context.args[0] # str
    first_name = context.args[1] # str
    birthday = context.args[2] # %d.%m

    settings.update_user(user_name, first_name, birthday)

    await context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = f"Добавлен пользователь: {first_name} ({user_name})"
    )

    settings.generate_birthdays_map()

@check_admin
async def bot_removeuser(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_name = context.args[0] # str

    settings.remove_user(user_name)

    await context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = f"Удалён пользователь: {user_name}"
    )

@check_admin
async def bot_setvacation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_name = context.args[0] # str
    status = bool(int(context.args[1])) # 1|0

    first_name = settings.get_first_name(user_name)

    settings.set_vacation_status(user_name, status)

    on_vacation_text = "\"В отпуске\""
    from_vacation_text = "\"Из отпуска\""

    await context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = f"{first_name}, установлен статус {on_vacation_text if status else from_vacation_text}"
    )

async def daily_release(context: ContextTypes.DEFAULT_TYPE) -> None:
    settings.tick_release() # must tick every day

    if is_friday(): return
    if is_weekend(): return
    if settings.is_holiday(): return

    user_name = settings.get_release_current()
    first_name = settings.get_first_name(user_name)

    text = f"Очередь релизить:\n{first_name}\n"

    vacation_list = settings.get_vacation_list()

    if user_name in vacation_list:
        text += f"{user_name} (в отпуске)\n"

        subs = settings.get_release_order().remove(user_name)

        text += " ".join(map(lambda x: "@" + x, subs))
    else:
        text += f"@{user_name}"

    await context.bot.send_message(
        chat_id = TELEGRAM_GROUP_ID,
        text = text
    )

async def daily_dsm(context: ContextTypes.DEFAULT_TYPE) -> None:
    if is_planning_day(): return
    if is_weekend(): return
    if settings.is_holiday(): return

    settings.tick_dsm()

    user_name = settings.get_dsm_current()
    first_name = settings.get_first_name(user_name)

    text = f"Очередь DSM:\n{first_name}\n@{user_name}"

    await context.bot.send_message(
        chat_id = TELEGRAM_GROUP_ID,
        text = text
    )

async def daily_birthday(context: ContextTypes.DEFAULT_TYPE) -> None:
    birthday_boys = settings.get_birthday_boys()

    if len(birthday_boys) == 0: return

    text = "Поздравим с днём рождения!\n"
    text += ", ".join(map(lambda x: settings.get_first_name(x) + "@" + x, birthday_boys))

    await context.bot.send_message(
        chat_id = TELEGRAM_GROUP_ID,
        text = text
    )

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    start_handler = CommandHandler("start", bot_start)
    app.add_handler(start_handler)

    help_handler = CommandHandler("help", bot_help)
    app.add_handler(help_handler)

    dsm_handler = CommandHandler("dsm", bot_dsm)
    app.add_handler(dsm_handler)

    release_handler = CommandHandler("release", bot_release)
    app.add_handler(release_handler)

    onvacation_handler = CommandHandler("onvacation", bot_onvacation)
    app.add_handler(onvacation_handler)

    fromvacation_handler = CommandHandler("fromvacation", bot_fromvacation)
    app.add_handler(fromvacation_handler)

    vacationlist_handler = CommandHandler("vacationlist", bot_vacationlist)
    app.add_handler(vacationlist_handler)

    save_handler = CommandHandler("save", bot_save)
    app.add_handler(save_handler)

    addholiday_handler = CommandHandler("addholiday", bot_addholiday)
    app.add_handler(addholiday_handler)

    removeholiday_handler = CommandHandler("removeholiday", bot_removeholiday)
    app.add_handler(removeholiday_handler)

    adduser_handler = CommandHandler("adduser", bot_adduser)
    app.add_handler(adduser_handler)

    removeuser_handler = CommandHandler("removeuser", bot_removeuser)
    app.add_handler(removeuser_handler)

    setvacation_handler = CommandHandler("setvacation", bot_setvacation)
    app.add_handler(setvacation_handler)

    job_queue = app.job_queue

    job_release = job_queue.run_repeating(daily_release, DAILY_JOB_INTERVAL_SEC, first = RELEASE_JOB_TIME_UTC)
    job_dsm = job_queue.run_repeating(daily_dsm, DAILY_JOB_INTERVAL_SEC, first = DSM_JOB_TIME_UTC)
    job_birthday = job_queue.run_repeating(daily_birthday, DAILY_JOB_INTERVAL_SEC, first = BIRTHDAY_JOB_TIME_UTC)

    app.run_polling()
