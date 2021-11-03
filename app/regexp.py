import datetime, re
from app.exceptions import IncorrectlySetCommandKeys

categories = ("Common", "Food", "Transport", "Utilities", "Salary")
regs = (r'(Оплата|Покупка|Доход|Расход)', r'(?<=с:)\d+', r'(Общее|Еда|Транспорт|Бытовые|Зарплата)',
            r'(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0-2])\.([0-9]{4})', r'(([01][0-9])|(2[0-3])):[0-5][0-9]:[0-5][0-9]$')
command = list()

def regexp_insert_record(text):
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
        if command[1].lower() == "общее":
            type_cat = categories[0]
        elif command[1].lower() == "еда":
            type_cat = categories[1]
        elif command[1].lower() == "транспорт":
            type_cat = categories[2]
        elif command[1].lower() == "бытовые":
            type_cat = categories[3]
        elif command[1].lower() == "зарплата":
            type_cat = categories[4]
        else:
            type_cat = categories[0]
        posix_date = 1635878220
        reserve_date = datetime.datetime.utcfromtimestamp(posix_date)
        if command[3] is not None:
            date = datetime.datetime.strptime(command[3], '%d.%m.%Y')
        else:
            date = datetime.datetime.combine(reserve_date.date(), datetime.time.min)

        if command[4] is not None:
            time_d = datetime.datetime.strptime(command[4], '%H:%M:%S')
        else:
            time_d = datetime.datetime.combine(datetime.date.min, reserve_date.time())
        if command[3] is None and command[4] is None:
            result_date = reserve_date
            print("reserve_date: ", result_date)
        else:
            result_date = datetime.datetime.combine(date.date(), time_d.time())
            print("result_date: ", result_date)
        return come, type_cat, result_date, command[1]
    else:
        raise IncorrectlySetCommandKeys