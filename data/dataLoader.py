import pandas as pd
import requests
from io import BytesIO
import json
from datetime import datetime
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings()


schedule_excel = None
groups_names = None
groups_users_names = {}
call_schedule = {}
pinned_calls = {}

owner = 5329953695
admins = []

teachers = []
# teachers_schedule = {}


def load_schedule(url):
    global schedule_excel

    response = requests.get(url, verify=False)

    if response.status_code == 200:
        file_data = BytesIO(response.content)
        schedule_excel = pd.read_excel(file_data)
    else:
        print(f"Ошибка при загрузке файла: {response.status_code}")


def load_groups():
    global groups_names

    groups_names = list(schedule_excel.columns)[2:]


def load_groups_names():
    global groups_users_names

    with open('data/student_group_users.json', encoding='utf-8') as file:
        groups_users_names = json.loads(file.read())


def save_group_names():
    with open('data/student_group_users.json', mode='w', encoding='utf-8') as file:
        json.dump(groups_users_names, file, ensure_ascii=False, indent=2)


def load_groups_file():
    with open('data/student_groups.txt', mode='w', encoding='utf-8') as student_group_users_file:
        for group_name in groups_names:
            print(group_name, file=student_group_users_file)


def load_admins():
    global admins

    admins = []
    with open('data/admins_file.txt', mode='r', encoding='utf-8') as admins_file:
        for admin in admins_file.readlines():
            admins += [int(admin)]


def save_admins():
    with open('data/admins_file.txt', mode='w', encoding='utf-8') as admins_file:
        for admin in admins:
            print(admin, file=admins_file)


def is_admin(user_id):
    if user_id == owner:
        return True
    if user_id in admins:
        return True
    return False


def add_admin(user_id):
    global admins

    if user_id not in admins:
        admins += [user_id]
        save_admins()
        return True

    return False


def remove_admin(user_id):
    global admins

    if user_id in admins:
        admins.remove(user_id)
        save_admins()
        return True

    return False


def set_user_group(user_id, group_name):
    global groups_users_names

    if group_name in groups_users_names.keys() and user_id in groups_users_names[group_name]:
        return

    for k, v in groups_users_names.items():
        if user_id in v:
            groups_users_names[k].remove(user_id)
    if group_name not in groups_users_names.keys():
        groups_users_names[group_name] = []
    groups_users_names[group_name] += [user_id]

    save_group_names()


def get_user_group(user_id):
    for k, v in groups_users_names.items():
        if user_id in v:
            return k
    return 'неизв.'


def has_user_group(user_id):
    for k, v in groups_users_names.items():
        if user_id in v:
            return True
    return False


def get_day_indexes(day):
    if day == -1:
        return None

    start = -1
    end = -1
    for i in range(len(schedule_excel["День недели"])):
        if schedule_excel["День недели"][i] == day:
            start = i
        elif start != -1 and str(schedule_excel["День недели"][i]) != 'nan':
            end = i - 1
            break
    return start, end


days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]


def today():
    day = datetime.today().weekday()
    return -1 if day < 0 or day >= len(days) else days[day]


def tomorrow():
    day = datetime.today().weekday() + 1
    print(day)
    return -1 if day < 0 or day >= len(days) else days[day]


def time():
    now = datetime.today().time()
    return list(map(int, str(now).split(':')[0:2]))


def to_minutes(text): # 1.20 => 80
    hour, minute = text.split('.')
    return int(hour) * 60 + int(minute)


def get_nearest_call():  # (8:30, '1 пара', 3)
    day = 'Понедельник' if today() == 'Понедельник' else 'Будни+суббота'
    now = time()  # [23, 59]
    for k, v in call_schedule[day].items():
        for value in range(len(v)):
            minutes = to_minutes(v[value])
            now_minutes = now[0] * 60 + now[1]
            if minutes > now_minutes:
                return [v[value], k if value == 0 else f'Перемена после {k.split()[0]} пары', minutes - now_minutes]
    return None


def load_html():
    global call_schedule

    url = "https://oksei.ru/studentu/raspisanie_uchebnykh_zanyatij"
    response = requests.get(url, verify=False)
    response.encoding = 'utf-8'
    html = response.text
    soup = BeautifulSoup(html, "html.parser")

    table = soup.find("table")
    if not table:
        print("Таблица не найдена на странице.")
        return

    rows = table.find_all("tr")
    schedule = []

    for row in rows:
        cells = row.find_all(["td", "th"])
        schedule += [cell.text.strip() for cell in cells]

    schedule = list(filter(lambda x: not x.strip().startswith('перемена') and x != '', schedule[2:]))

    call_schedule = {'Понедельник': {}, 'Будни+суббота': {}}
    for i in range(len(schedule) - 1):
        if i % 2 == 0:
            temp = []
            for j in schedule[i + 1].split('-'):
                temp += list(map(lambda x: x.strip().strip('.'), j.split('–')))
            if i % 4 == 0:
                call_schedule['Понедельник'][schedule[i]] = (temp[0], temp[1])
            else:
                call_schedule['Будни+суббота'][schedule[i]] = (temp[0], temp[1])

    with open('data/call_schedule.json', mode='w', encoding='utf-8') as file:
        json.dump(call_schedule, file, ensure_ascii=False, indent=2)

    xml = soup.find("a", id="curr_rasp")
    url_xml = 'https://oksei.ru' + xml['href']
    load_schedule(url_xml)


def load_pinned_calls():
    global pinned_calls

    with open('data/pinned_calls.json', encoding='utf-8') as file:
        pinned_calls = json.loads(file.read())


def save_pinned_calls():
    with open('data/pinned_calls.json', mode='w', encoding='utf-8') as file:
        json.dump(pinned_calls, file, ensure_ascii=False, indent=2)


def add_pinned_call(*call):
    global pinned_calls
    for el in list(call):
        pinned_calls[el[0]] = el[1]
    save_pinned_calls()


load_html()
load_groups()
load_groups_names()
load_admins()
load_pinned_calls()
