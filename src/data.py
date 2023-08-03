import json
from datetime import datetime, date, time, timezone, timedelta
import random

DATA_FILE_PATH = "/home/s0nought/daily-team-stuff-bot/data.json"

def get_datetime_utc() -> datetime:
    """Return current datetime (UTC)."""

    return datetime.now(timezone.utc)

def get_date() -> str:
    """Return current date (UTC)."""

    return get_datetime_utc().date()

def get_weekday_iso() -> int:
    """Return day of the week (ISO)."""

    return date.isoweekday(get_datetime_utc())

def is_friday() -> bool:
    """Return True if today is Friday, False otherwise."""

    return True if get_weekday_iso() == 5 else False

def is_weekend() -> bool:
    """Return True if today is a weekend, False otherwise."""

    return True if get_weekday_iso() > 5 else False

def convert_to_date(d: str) -> date:
    """Convert ISO format date string to date object."""

    return date.fromisoformat(d)

class BotData:
    """
    Bot's data.
    """

    def __init__(self):
        with open(DATA_FILE_PATH, mode = "rt", encoding = "UTF-8") as f:
            self.data = json.load(f)

    def _save(self) -> None:
        """Write bot's data to the data file."""

        with open(DATA_FILE_PATH, mode = "wt", encoding = "UTF-8") as f:
            json.dump(self.data, f, indent = 4)

    def _export(self) -> str:
        """Export bot's data."""

        return json.dumps(self.data, indent = 4)

    def _import(self, obj: str) -> None:
        """Import bot's data."""

        self.data = json.loads(obj)
        return

    def get_holidays(self) -> list[str]:
        """Return list of holidays."""

        return self.data.get("holidays", [""])

    def is_holiday(self, d: date = get_date()) -> bool:
        """Return True if given date is a holiday, False otherwise."""

        return True if d.strftime(r"%m.%d") in self.get_holidays() else False

    def get_members(self) -> list[str]:
        """Return members list."""

        return self.data.get("members", [""])

    def is_member(self, user_name: str) -> bool:
        """Return True if user name is in the list of members, False otherwise."""

        return True if user_name in self.get_members() else False

    def get_on_vacation(self) -> list[str]:
        """Return list of members on vacation."""

        return self.data.get("onVacation", [""])

    def is_on_vacation(self, user_name: str) -> bool:
        """Return True if member is on vacation, False otherwise."""

        return True if user_name in self.get_on_vacation() else False

    def set_vacation_state(self, user_name: str, state: int) -> None:
        """Set vacation state."""

        if state == 0:
            try:
                self.data["onVacation"].remove(user_name)
            except ValueError as ex:
                print(ex)
        elif state == 1:
            self.data["onVacation"].append(user_name)
        else:
            raise ValueError(f"State {state} is unsupported.")

    def get_update_turns_job_time_utc(self) -> time:
        """Return update turns job time (UTC)."""

        return time.fromisoformat(self.data.get("updateTurnsJobTimeUTC", "00:13:37Z"))

    def get_notifications_job_time_utc(self) -> time:
        """Return notifications job time (UTC)."""

        return time.fromisoformat(self.data.get("notificationsJobTimeUTC", "06:00:00Z"))

    def get_next_planning_day_date(self) -> date:
        """Return next planning day date."""

        return date.fromisoformat(self.data["planning"].get("nextDate", "2023-08-14"))

    def set_next_planning_day_date(self, date: str) -> None:
        """Set next planning day date."""

        self.data["planning"]["nextDate"] = date
        return

    def get_planning_interval_days(self) -> int:
        """Get planning interval days."""

        return self.data["planning"].get("intervalDays", 14)

    def tick_next_planning_day_date(self) -> None:
        """Calculate and set next planning day date."""

        interval_days = self.get_planning_interval_days()
        cur_date = get_date()

        while cur_date > self.get_next_planning_day_date():
            next_date = self.get_next_planning_day_date() + timedelta(days = interval_days)
            self.set_next_planning_day_date(next_date.strftime(r"%Y-%m-%d"))

    def is_planning_day(self, d: date = get_date()) -> bool:
        """Return True if given datetime is a planning day, False otherwise."""

        return True if d == self.get_next_planning_day_date() else False

    def get_standup_turn(self) -> str:
        """Return standup turn."""

        return self.data["standup"].get("turn", "N/A")

    def set_standup_turn(self, user_name: str) -> None:
        """Set standup turn."""

        self.data["standup"]["turn"] = user_name
        return

    def get_standup_ban(self) -> list[str]:
        """Return standup ban list."""

        return self.data["standup"].get("ban", [""])

    def add_to_standup_ban(self, user_name: str) -> None:
        """Add user name to standup ban list."""

        self.data["standup"]["ban"].append(user_name)
        return

    def clear_standup_ban(self) -> None:
        """Clear standup ban list."""

        self.data["standup"]["ban"].clear()
        return

    def tick_standup_turn(self) -> None:
        """Choose and set next standup turn randomly."""

        candidates = set(self.get_members()) # all
        candidates.difference_update(set(self.get_standup_ban())) # subtract standup ban
        candidates.difference_update(set(self.get_on_vacation())) # subtract on vacation

        if len(candidates) == 0: # everyone has taken a turn
            self.clear_standup_ban()
            return self.tick_standup_turn()

        l = list(candidates)
        turn = random.choice(l)

        if turn == self.get_standup_turn(): # same person won't take a turn twice in a row
            return self.tick_standup_turn()

        self.set_standup_turn(turn)
        self.add_to_standup_ban(turn)
        return

    def get_duty_engineers(self) -> list[str]:
        """Return duty engineers."""

        return self.data["duty"].get("engineers", [""])

    def get_duty_substitutes(self, user_name: str) -> list[str]:
        """Return available duty substitutes for the given user_name."""

        candidates = set(self.get_duty_engineers()) # all
        candidates.difference_update(set(self.get_on_vacation())) # subtract on vacation
        candidates.difference_update(set([user_name])) # subtract the given user_name

        return candidates if len(candidates) > 0 else ["N/A"]

    def get_current_duty_turn(self) -> str:
        """Get current duty turn."""

        return self.data["duty"].get("turn", "N/A")

    def set_current_duty_turn(self, user_name: str) -> None:
        """Set current duty turn."""

        self.data["duty"]["turn"] = user_name
        return

    def get_next_duty_date(self, user_name: str) -> date:
        """Get next duty date for the given user_name."""

        return convert_to_date(self.data["duty"]["schedule"][user_name]["nextDate"])

    def set_next_duty_date(self, user_name: str, date: str) -> None:
        """Set next duty date for the given user_name as date."""

        self.data["duty"]["schedule"][user_name] = date
        return

    def update_duty_schedule(self) -> None:
        """Update duty schedule."""

        cur_date = get_date()

        for user_name, duty_data in self.data["duty"]["schedule"]:
            repeat_every_days = duty_data["repeatEveryDays"]

            while cur_date > self.get_next_duty_date(user_name):
                next_date = self.get_next_duty_date(user_name) + timedelta(days = repeat_every_days)
                self.set_next_duty_date(user_name, next_date.strftime(r"%Y-%m-%d"))

        return

    def tick_duty_turn(self) -> None:
        """Calculate and set next duty turn."""

        cur_date = get_date().strftime(r"%Y-%m-%d")

        for user_name, duty_data in self.data["duty"]["schedule"]:
            if duty_data["nextDate"] == cur_date:
                self.set_current_duty_turn(user_name)

        return

bot_data = BotData()
