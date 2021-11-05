import datetime

from app.utils.regexp import categories, categories_output

def calculate_amount(data, time: datetime.datetime, number, unit):
    amount = {categories[0]: 0, categories[1]: 0, categories[2]: 0, categories[3]: 0, categories[4]: 0,
              'total_expense': 0, 'total_income': 0, 'balance': 0}
    str_d=""
    for item in data:
        if item[2]:
            sum_operate = item[4]
            amount['total_income'] += sum_operate
        else:
            sum_operate = -item[4]
            amount['total_expense'] += sum_operate
        if item[3] is not None:
            amount[item[3]] += sum_operate
        else:
            amount[categories[0]] += sum_operate
        amount['balance'] += sum_operate
    str_d += f'''Информация по балансу за {time.strftime('%d.%m.%Y %H:%M:%S')}
================================\n
За {number} {unit}:
Доходы составили: {amount['total_income']}
Расходы составили:{amount['total_expense']},
Из них:
- {categories_output[1]}: {amount[categories[1]]}
- {categories_output[2]}: {amount[categories[2]]}
- {categories_output[3]}: {amount[categories[3]]}
- {categories_output[4]}: {amount[categories[4]]}
- {categories_output[0]}: {amount[categories[0]]}\n
===============================
Баланс: {amount['balance']}
'''
    return str_d