import logging

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from data import bot_data as BD
from data import (
    is_friday,
    is_weekend,
)

logging.basicConfig(
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level = logging.INFO
)

BOT_TOKEN = r""
GROUP_ID = r""
ADMIN_IDS = [""]

DAILY_JOB_INTERVAL_SEC = 60 * 60 * 24

START_MESSAGE = "start"

HELP_MESSAGE = "help"

def check_member(func):
    """Decorator. Check user name is a member."""

    async def wrapper(*args):
        user_name = args[0].message.from_user.username

        if not BD.is_member(user_name):
            return

        await func(*args)

    return wrapper

def check_admin(func):
    """Decorator. Check user ID is an admin ID."""

    async def wrapper(*args):
        user_id = str(args[0].message.from_user.id)

        if user_id not in ADMIN_IDS:
            return

        await func(*args)

    return wrapper

async def _start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/start - return start message."""

    await context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = START_MESSAGE
    )

@check_member
async def _help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/help - return help message."""

    await context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = HELP_MESSAGE
    )

@check_admin
async def _export(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/export - return bot's data."""

    await context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = BD._export()
    )

@check_admin
async def _import(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/import - import bot's data from a string."""

    BD._import(context.args[0])
    BD._save()

    await _export(update, context)

@check_member
async def _holidays(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/holidays - return list of holidays."""

    await context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = "\n".join(BD.get_holidays())
    )

@check_member
async def _members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/members - return members list."""

    await context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = "\n".join(BD.get_members())
    )

@check_member
async def _vacation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/vacation - return list of members on vacation."""

    await context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = "\n".join(BD.get_on_vacation())
    )

@check_member
async def _standup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/standup - return standup turn."""

    await context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = BD.get_standup_turn()
    )

@check_member
async def _duty(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/duty - return duty turn."""

    await context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = BD.get_duty_turn()
    )

@check_member
async def _onvacation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/onvacation - set vacation state to 1 (active)."""

    BD.set_vacation_state(update.message.from_user.username, 1)
    BD._save()

    await _vacation(update, context)

@check_member
async def _fromvacation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/fromvacation - set vacation state to 0 (inactive)."""

    BD.set_vacation_state(update.message.from_user.username, 0)
    BD._save()

    await _vacation(update, context)

async def _update_turns_job() -> None:
    """Repeating job that updates duty and standup turns."""

    BD.tick_duty_turn() # must tick every day

    if not BD.is_holiday() and \
        not BD.is_planning_day() and \
        not is_weekend():
        BD.tick_standup_turn() # only tich when needed

    BD._save()

async def _notifications_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Repeating job that sends notifications to the group."""

    if BD.is_planning_day():
        meeting_type = "Planning"
    else:
        meeting_type = "Standup"

    standup_turn = BD.get_standup_turn()
    duty_turn = BD.get_duty_turn()

    text = f"{meeting_type}"

    if meeting_type == "Standup":
        text += f"\n\nStandup: @{standup_turn}"

    if not BD.is_on_vacation(duty_turn):
        text += f"\n\nDuty: @{duty_turn}"
    else:
        subs = "@" + " @".join(BD.get_duty_substitutes(duty_turn))
        text += f"\n\nDuty: {duty_turn}\n{subs}"

    if not BD.is_holiday() and \
        not is_weekend():
        await context.bot.send_message(
            chat_id = GROUP_ID,
            text = text
        )

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    start_handler = CommandHandler("start", _start)
    app.add_handler(start_handler)

    help_handler = CommandHandler("help", _help)
    app.add_handler(help_handler)

    export_handler = CommandHandler("export", _export)
    app.add_handler(export_handler)

    import_handler = CommandHandler("import", _import)
    app.add_handler(import_handler)

    holidays_handler = CommandHandler("holidays", _holidays)
    app.add_handler(holidays_handler)

    members_handler = CommandHandler("members", _members)
    app.add_handler(members_handler)

    vacation_handler = CommandHandler("vacation", _vacation)
    app.add_handler(vacation_handler)

    standup_handler = CommandHandler("standup", _standup)
    app.add_handler(standup_handler)

    duty_handler = CommandHandler("duty", _duty)
    app.add_handler(duty_handler)

    onvacation_handler = CommandHandler("onvacation", _onvacation)
    app.add_handler(onvacation_handler)

    fromvacation_handler = CommandHandler("fromvacation", _fromvacation)
    app.add_handler(fromvacation_handler)

    job_queue = app.job_queue

    update_turns_job = job_queue.run_repeating(_update_turns_job, DAILY_JOB_INTERVAL_SEC, first = BD.get_update_turns_job_time_utc())
    notifications_job = job_queue.run_repeating(_notifications_job, DAILY_JOB_INTERVAL_SEC, first = BD.get_notifications_job_time_utc())

    app.run_polling()
