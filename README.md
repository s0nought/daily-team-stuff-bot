# daily-team-stuff-bot

Telegram bot to automate daily scrum team stuff written in Python and means to install it.

## Features

- pick random DSM host
- notify whose turn to release it is
- notify if it is someone's birthday today

## Installation

1. Clone this repository to a local directory
    ```
    git clone https://github.com/s0nought/daily-team-stuff-bot.git ~/daily-team-stuff-bot
    ```

1. Install required Python modules
    ```
    cd ~/daily-team-stuff-bot
    pip install -r requirements.txt
    ```

## Configuration

Notes:
- It is assumed you have created a new Telegram bot via [@BotFather](https://t.me/BotFather) already.
- There is no need to rename *.example files manually.

### data/settings.json.example

- `holidays` - list of holidays (format: %d.%m)
- `users` - list of users
- `dsm` - DSM related data
    - `hosts` - list of users who already hosted DSM
    - `current` - whose turn to host DSM it is
- `release` - release schedule related data
    - `order` - release schedule
    - `current` - whose turn to release it is

### modules/secrets.py.example

- `BOT_TOKEN` - access token received from [@BotFather](https://t.me/BotFather)
- `ADMIN_TELEGRAM_IDS` - Telegram user IDs list (can be retrieved from [@userinfobot](https://t.me/userinfobot))

### modules/constants.py.example

- `TELEGRAM_GROUP_ID` - Telegram group ID (group this bot will be added to)
- `RELEASE_JOB_TIME_UTC` - when to notify whose turn to release it is
- `DSM_JOB_TIME_UTC` - when to pick random DSM host
- `BIRTHDAY_JOB_TIME_UTC` - when to notify if it is someone's birthday today
- `SETTINGS_FILE_PATH` - full path to `data/settings.json`
- `START_MESSAGE` - message this bot returns on `/start` command
- `HELP_MESSAGE` - message this bot returns on `/help` command

### BotFather

To let this bot interact within the group you need to configure it via [@BotFather](https://t.me/BotFather)
- `/setjoingroups` - Enable
- `/setprivacy` - Enable
- `/setcommands` - List of commands

### Run setup scripts

```
chmod +x setup1.sh
chmod +x setup2.sh
./setup1.sh
sudo ./setup2.sh
```

setup1.sh will do the following:
- Rename *.example files.
- Create run_bot.sh
- Create run_restart.sh
- Create `<bot name>` systemd service in the working directory
- Schedule a cron job to restart bot daily (just in case, y'know)

setup2.sh will do the following:
- Create `<bot name>` systemd service in /etc/systemd/system directory
- Enable and start `<bot name>` systemd service

### Add this bot to your group

Just like you would normally.

## Commands list

User commands:
- `/start` - begins the interaction with the user
- `/help` - returns a help message
- `/dsm` - returns info about the current DSM host
- `/release` - returns info about the current release engineer
- `/onvacation` - sets user's `is_on_vacation` to true
- `/fromvacation` - sets user's `is_on_vacation` to false
- `/vacationlist` - returns a list of users on vacation

Admin Commands:
- `/save` - writes bot's current settings to disk
- `/addholiday <date>` - adds `date` (format: %d.%m) to the holidays list
- `/removeholiday <date>` - removes `date` (format: %d.%m) from the holidays list
- `/adduser <user name> <first name> <birthday date>` - adds a new user to the users list
- `/removeuser <user name>` - removes `user name` from the users list
- `/setvacation <user name> <status>` - sets `is_on_vacation` as `<status>` (1|0) for the specified `<user name>`

## To Do

<input type="checkbox"> Add unit tests.  
<input type="checkbox"> There is no validation of parameters passed to admin commands.  
