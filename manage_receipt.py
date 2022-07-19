import re
import regex
import datetime
from datetime import datetime


def find_receipt(data, word, sort_by, order_by):
    if '\\' in word:
        word = list(word)
        word.insert(word.index('\\'), '\\')
        word = ''.join(word)

    new_data = {}
    for i in data.keys():
        res = regex.search(word, data[i]['full_text'], re.IGNORECASE)
        if res:
            new_data[i] = {}
            new_data[i] |= data[i]

    return sort_receipt(new_data, sort_by, order_by)

def sort_receipt(data, sort_by, order_by):
    if order_by == 'Ascending':
        reverse = False
    else:
        reverse = True

    if sort_by == 'Upload Date':
        new_data = sorted(data.items(), key=lambda x:datetime.strptime(x[0], '%d-%m-%Y_%H-%M-%S'), reverse=reverse)
    elif sort_by == 'Receipt date':
        new_data = sorted(data.items(), key=compare_date, reverse=reverse)
    else:
        new_data = sorted(data.items(), key=compare_total, reverse=reverse)

    return dict(new_data)

def compare_date(data):
    date = data[1]['date'].split('/')
    temp = date[0]
    date[0] = date[2]
    date[2] = temp
    return ''.join(date)

def compare_total(data):
    total = final_total(data[1]['prices'], data[1]['price_text'])
    return float(total)

def final_total(prices, price_text):
    total = -1
    for i in range(len(prices)):
        total_word_found = regex.search('Total', price_text[i], re.IGNORECASE)
        if total_word_found and float(prices[i]) > float(total):
            total = prices[i]

    if total == -1:
        total = max(prices)

    return total