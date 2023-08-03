# daily-team-stuff-bot

Telegram bot to automate standup and duty notifications.

NB: This bot requires Python 3.11 or newer to run!

## Features

- Standup
    - Choose standup master randomly.
    - Same member won't be a standup master twice in a row.
    - Each member will be a standup master at least once before the pool of candidates is cleared.
- Duty
    - Keep track of duty turns.
    - Find duty substitutes if needed.
- Notifications
    - Do not tag members on vacation.
    - Distinguish planning and standup meetings.
    - Do not send notifications on weekends and holidays.

## Commands

Free for all:
- `/start` - start bot

Members only:
- `/help` - display help message
- `/status` - standup and duty turns
- `/vacation` - members on vacation
- `/onvacation` - set state to active
- `/fromvacation` - set state to inactive

Admins only:
- `/export` - export bot's data
- `/import` - import bot's data

## Installation

### Clone repository

```shell
git clone https://github.com/s0nought/daily-team-stuff-bot.git ~/daily-team-stuff-bot
```

### Install dependencies

```shell
cd ~/daily-team-stuff-bot
pip3 install -r requirements.txt
```

## Configuration

### main.py

- `BOT_TOKEN` - bot's token
- `GROUP_ID` - group's ID (to send notifications to)
- `ADMIN_IDS` - admin IDs

### data.py

- `DATA_FILE_PATH` - full path to `data.json`

### data.json

|key|type|description|
|-|-|-|
|holidays|list[str]|list of holidays (format `%m.%d`)|
|members|list[str]|list of members (Telegram user names)|
|updateTurnsJobTimeUTC|str|when to execute update turns job (time, UTC)|
|notificationsJobTimeUTC|str|when to execute notifications job (time, UTC)|
|planning.intervalDays|int|interval between plannings in days|
|planning.nextDate|str|next planning date (%Y-%m-%d)|
|onVacation|list[str]|list of members on vacation|
|duty.engineers|list[str]|engineers that take duty|
|duty.schedule|dict|engineers' duty schedule|
|duty.turn|str|current duty turn|
|standup.turn|str|current turn (standup master)|
|standup.ban|list[str]|members who were standup masters recently|
