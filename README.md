# daily-team-stuff-bot

Telegram bot to automate standup and duty notifications.

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

### data.json

|key|type|description|
|-|-|-|
|holidays|list[str]|list of holidays (format `%m.%d`)|
|members|list[str]|list of members (Telegram user names)|
|updateTurnsJobTimeUTC|str|when to execute update turns job (time, UTC)|
|notificationsJobTimeUTC|str|when to execute notifications job (time, UTC)|
|firstPlanningDatetimeUTC|str|date of the first planning (datetime, UTC)|
|onVacation|list[str]|list of members on vacation|
|duty.order|list[str]|duty order (datetime, UTC)|
|duty.turnMap|dict|turn codes and corresponding user names|
|duty.turnCode|str|current turn code (duty engineer)|
|standup.turn|str|current turn (standup master)|
|standup.ban|list[str]|members who were standup masters recently|

Notes:

Planning takes place every 14 days.

## Duty

This feature is implemented with the following assumptions:
- There are 3 duty engineers.
- They change every day.
- We are aware of 3 sequential dates in the past (each date being someone's duty date).
- Turn codes are generated beforehand and stored in the turns map.

How it works:
1. Get timedelta in days between current date and the first known duty date.
1. Divide that number by 3 and get the remainder of the operation (N mod 3).
1. Repeat with the second and the third duty dates.
1. Combine all the remainders in a string (that becomes the turn code).
1. Use the turn code to get a member from the turns map.

Example:

order
```python
[
    "2023-07-01T00:00:01Z", # user_name_5's duty
    "2023-07-02T00:00:01Z", # user_name_6's duty
    "2023-07-03T00:00:01Z" # user_name_7's duty
]
```

map
```python
{
    "021": "user_name_5",
    "102": "user_name_6",
    "210": "user_name_7"
}
```

Today is 10th of July (dt1).
```
(dt1 - order[0]).days % 3 -> 9 % 3 -> 0
(dt1 - order[1]).days % 3 -> 8 % 3 -> 2
(dt1 - order[2]).days % 3 -> 7 % 3 -> 1
```
Today is 11th of July (dt2).
```
(dt2 - order[0]).days % 3 -> 10 % 3 -> 1
(dt2 - order[1]).days % 3 -> 9 % 3 -> 0
(dt2 - order[2]).days % 3 -> 8 % 3 -> 2
```
Today is 12th of July (dt3).
```
(dt3 - order[0]).days % 3 -> 11 % 3 -> 2
(dt3 - order[1]).days % 3 -> 10 % 3 -> 1
(dt3 - order[2]).days % 3 -> 9 % 3 -> 0
```
<...>

Today is 15th of July (dt4).
```
(dt4 - order[0]).days % 3 -> 14 % 3 -> 2
(dt4 - order[1]).days % 3 -> 13 % 3 -> 1
(dt4 - order[2]).days % 3 -> 12 % 3 -> 0
```

Today is 16th of July (dt5).
```
(dt5 - order[0]).days % 3 -> 15 % 3 -> 0
(dt5 - order[1]).days % 3 -> 14 % 3 -> 2
(dt5 - order[2]).days % 3 -> 13 % 3 -> 1
```

etc.

Turn codes
- 10th of July - `021`
- 11th of July - `102`
- 12th of July - `210`
- <...>
- 15th of July - `210`
- 16th of July - `021`
- etc.

map.get("210") -> user_name_7
