import json
from datetime import datetime, date, time, timezone
import random

DATA_FILE_PATH = "data.json"

def get_date() -> str:
    """Return current date."""

    return date.today()

def get_datetime_utc() -> datetime:
    """Return current datetime (UTC)."""

    return datetime.now(timezone.utc)

def get_weekday_iso() -> int:
    """Return day of the week (ISO)."""

    return date.isoweekday(get_datetime_utc())

def is_friday() -> bool:
    """Return True if today is Friday, False otherwise."""

    return True if get_weekday_iso() == 5 else False

def is_weekend() -> bool:
    """Return True if today is a weekend, False otherwise."""

    return True if get_weekday_iso() > 5 else False

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

    def get_first_planning_datetime_utc(self) -> datetime:
        """Return first planning datetime (UTC)."""

        return datetime.fromisoformat(self.data.get("firstPlanningDatetimeUTC", "2023-01-30T00:00:01Z"))

    def is_planning_day(self, dt: datetime = get_datetime_utc()) -> bool:
        """Return True if given datetime is a planning day, False otherwise."""

        x = (dt - self.get_first_planning_datetime_utc()).days
        return True if x % 14 == 0 else False

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

    def get_duty_order(self) -> list[str]:
        """Return duty order."""

        return self.data["duty"].get("order", [""])

    def get_duty_turn_code(self) -> str:
        """Return duty turn code."""

        return self.data["duty"].get("turnCode", "N/A")

    def set_duty_turn_code(self, code: str) -> None:
        """Set duty turn code."""

        self.data["duty"]["turnCode"] = code
        return

    def get_duty_turn(self) -> str:
        """Return duty turn."""

        return self.data["duty"]["turnMap"].get(self.get_duty_turn_code(), "N/A")

    def tick_duty_turn(self) -> None:
        """Calculate and set duty turn code."""

        code = ""

        for dt_str in self.get_duty_order():
            code += str((get_datetime_utc() - datetime.fromisoformat(dt_str)).days % 3)

        self.set_duty_turn_code(code)
        return

    def get_duty_substitutes(self, user_name: str) -> list[str]:
        """Return duty substitutes (when user name is on vacation)."""

        all = list(self.data["duty"]["turnMap"].values())
        return all.remove(user_name)

bot_data = BotData()
