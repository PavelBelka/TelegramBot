import datetime, re
import pytz

from app.utils.exceptions import IncorrectlySetCommandKeys, TimeInFuture

categories_output = ('Прочее', 'Питание', 'Проезд', 'Квартплата', 'Медицина', 'Зарплата')
categories = ("Common", "Food", "Transport", "Utilities","Medicine", "Salary")
regs = (r'(Оплата|Покупка|Доход|Расход)', r'(?<=c|с)\d+(?=\s+)', r'(Прочее|Питание|Проезд|Квартплата|Медицина|Зарплата)',
            r'(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0-2])\.([0-9]{4})', r'(([01][0-9])|(2[0-3])):[0-5][0-9]:[0-5][0-9]$')

time_regs = r'(минута|час|день|неделя|месяц|год)'

def regexp_insert_record(text, posix_date: datetime.datetime):
    command = list()
    local = pytz.timezone("Europe/Moscow")
    type_cat = None
    for reg in regs:
        found = re.search(reg, text, re.M | re.I)
        if found:
            command.append(found.group())
        else:
            command.append(None)
    if command[0] is not None and command[1] is not None:
        if command[0].lower() == "оплата" or command[0].lower() == "расход" or command[0].lower() == "покупка":
            come = False
        elif command[0].lower() == "доход":
            come = True
        else:
            come = False
        if command[2] is not None:
            for name in categories_output:
                if command[2].lower() == name.lower():
                    type_cat = categories[categories_output.index(name)]
        else:
            type_cat = categories[0]
        #reserve_date = datetime.datetime.utcfromtimestamp(int(posix_date))
        local_dt = local.localize(posix_date, is_dst=None)
        utc_date = local_dt.astimezone(pytz.utc)
        reserve_date = utc_date.replace(tzinfo=None)
        if command[3] is not None:
            date_d = datetime.datetime.strptime(command[3], '%d.%m.%Y')
            if date_d > datetime.datetime.combine(reserve_date.date(), datetime.time.min):
                raise TimeInFuture
        else:
            date_d = datetime.datetime.combine(reserve_date.date(), datetime.time.min)

        if command[4] is not None:
            time_d = datetime.datetime.strptime(command[4], '%H:%M:%S')
        else:
            time_d = datetime.datetime.combine(datetime.date.min, reserve_date.time())
        if command[3] is None and command[4] is None:
            result_date = reserve_date
            print("reserve_date: ", result_date)
        else:
            result_date = datetime.datetime.combine(date_d.date(), time_d.time())
            print("result_date: ", result_date)
        ammo = command[1]
        del command
        return come, type_cat, result_date, ammo
    else:
        raise IncorrectlySetCommandKeys

def regexp_check_number(number):
    found = re.search(r'\d+', number, re.M | re.I)
    if found:
        return found.group()
    else:
        return None

def regexp_search_time(text, time, current_time):
    if text.lower() == 'минута':
        delta_t = datetime.timedelta(minutes= int(time))
    elif text.lower() == 'час':
        delta_t = datetime.timedelta(hours= int(time))
    elif text.lower() == 'день':
        delta_t = datetime.timedelta(days= int(time))
    elif text.lower() == 'неделя':
        delta_t = datetime.timedelta(days= 7 * int(time))
    elif text.lower() == 'месяц':
        delta_t = datetime.timedelta(days= 30 * int(time))
    elif text.lower() == 'год':
        delta_t = datetime.timedelta(days= 360 * int(time))
    else:
        delta_t = 0
    past_time = current_time - delta_t
    return past_time

def regexp_check_time_unit(text):
    found = re.search(time_regs, text, re.M | re.I)
    if found:
        return found.group()
    else:
        return None

def generate_output_string(data):
    type_cat = None
    str_d=""
    for item in data:
        if item[2]:
            operate = "Доход"
        else:
            operate = "Расход"
        if item[3] is not None:
            for obj in categories:
                if item[3] == obj:
                    type_cat = categories_output[categories.index(obj)]
        else:
            type_cat = "прочее"
        str_d += f"{item[0]}. {operate} c{item[4]} {type_cat} {item[1].strftime('%d.%m.%Y %H:%M:%S')}\n"
    return str_d