import random
from calendar import Calendar

from .constants import (
    SETTINGS_FILE_PATH
)

from .utils import (
    load_json,
    dump_json,
    get_datetime,
    format_datetime,
    get_current_date
)

class Settings:
    def __init__(self):
        self.data = load_json(SETTINGS_FILE_PATH)
        self.holidays = self.data["holidays"]
        self.users = self.data["users"]
        self.birthdays = dict()
        self.dsm = self.data["dsm"]
        self.release = self.data["release"]

        self.generate_birthdays_map()

    def save(self) -> None:
        dump_json(self.data, SETTINGS_FILE_PATH)

    # holidays

    def is_holiday(self) -> bool:
        return True if get_current_date() in self.holidays else False

    def add_holiday(self, date: str) -> None:
        if date not in self.holidays:
            self.holidays.append(date)
            self.save()

    def remove_holiday(self, date: str) -> None:
        if date in self.holidays:
            self.holidays.remove(date)
            self.save()

    # users

    def get_users(self) -> list[str]:
        return list(self.users.keys())

    def is_user(self, user_name: str) -> bool:
        return True if user_name in self.get_users() else False

    def get_first_name(self, user_name: str) -> str:
        x = self.users.get(user_name)

        return x["first_name"] if x else "-"

    def update_user(self, user_name: str, first_name: str, birthday: str, is_team_member: bool) -> None:
        user_data = {
            "first_name": first_name,
            "birthday": birthday,
            "is_on_vacation": False,
            "is_team_member": is_team_member
        }

        self.users.update({user_name: user_data})
        self.save()
        self.generate_birthdays_map()

    def remove_user(self, user_name: str) -> None:
        if self.is_user(user_name):
            self.users.pop(user_name)
            self.save()
            self.generate_birthdays_map()

    # team members

    def get_team_members(self) -> list[str]:
        result = list()

        for user_name, user_data in self.users.items():
            if user_data.get("is_team_member"):
                result.append(user_name)

        return result

    def is_team_member(self, user_name: str) -> bool:
        return True if user_name in self.get_team_members() else False

    # birthdays

    def generate_birthdays_map(self) -> None:
        self.birthdays.clear()

        for user_name, user_data in self.users.items():
            birthday_date = user_data.get("birthday")

            x = self.birthdays.get(birthday_date)

            if x == None:
                self.birthdays.update({birthday_date: [user_name]})
            else:
                self.birthdays.update({birthday_date: x + [user_name]})

    def get_birthday_boys(self) -> list[str]:
        x = self.birthdays.get(get_current_date())

        return x if x else []

    # vacation

    def get_vacation_list(self) -> list[str]:
        result = list()

        for user_name, user_data in self.users.items():
            if user_data.get("is_on_vacation"):
                result.append(user_name)

        return result

    def set_vacation_status(self, user_name: str, status: bool) -> None:
        user_data = self.users.get(user_name)
        user_data.update({"is_on_vacation": status})

        self.users.update({user_name: user_data})
        self.save()

    # dsm

    def get_dsm_hosts(self) -> list[str]:
        return self.dsm.get("hosts")

    def set_dsm_hosts(self, hosts: list[str]) -> None:
        self.dsm.update({"hosts": hosts})
        self.save()

    def append_dsm_host(self, user_name: str) -> None:
        self.set_dsm_hosts(self.get_dsm_hosts() + [user_name])

    def get_dsm_current(self) -> str:
        return self.dsm.get("current")

    def set_dsm_current(self, user_name: str) -> None:
        self.dsm.update({"current": user_name})
        self.save()

    def tick_dsm(self) -> None:
        candidates = set(self.get_team_members())
        candidates.difference_update(set(self.get_dsm_hosts())) # already hosted
        candidates.difference_update(set(self.get_vacation_list())) # on vacation

        candidates_list = list(candidates)

        if len(candidates_list) == 0:
            self.set_dsm_hosts([])
            return self.tick_dsm()

        host = random.choice(candidates_list)

        self.append_dsm_host(host)
        self.set_dsm_current(host)

    # release

    def get_release_order(self) -> list[str]:
        return self.release.get("order")

    def set_release_order(self, order: list[str]) -> None:
        self.release.update({"order": order})
        self.save()

    def get_release_current(self) -> str:
        date = get_current_date()
        return self.release["schedule"].get(date, "N/A")

    def set_release_schedule(self, schedule: dict[str, str]) -> None:
        self.release.update({"schedule" : schedule})
        self.save()

    def generate_release_schedule_month(self, start_index: int = 0) -> None:
        order = self.get_release_order()
        order_len = len(order)
        cur_dt = get_datetime()
        cur_date = cur_dt.date()
        cal = Calendar()
        schedule = dict()
        i = start_index

        for dt in cal.itermonthdates(cur_dt.year, cur_dt.month):
            if dt < cur_date:
                continue

            date = format_datetime(dt, r"%d.%m")

            schedule.update({date : order[i]})
            i += 1

            if i >= order_len:
                i = 0

        self.set_release_schedule(schedule)

settings = Settings()
