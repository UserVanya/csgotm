import urllib.parse
from bs4 import BeautifulSoup
import datetime
import requests
import sys
import PySimpleGUI as sg
import webbrowser
cur_moment = datetime.datetime(2099, 1, 1, 0)

def open_link(cite, name):
    if cite == 'CSGOTM':
        webbrowser.open('https://market.csgo.com/?search=' + name.replace(' ', '%20'))
    else:
        webbrowser.open('https://steamcommunity.com/market/search?appid=730&q=' + name.replace(' ', '+'))

def get_diff(new_items, previous_items):
    items_to_return = new_items.copy()
    for prev_item in previous_items:
        for new_item in items_to_return:
            if prev_item[0] == new_item[0] and prev_item[1] == new_item[1]:
                items_to_return.remove(new_item)
    return items_to_return


def get_items_no_adds(items):
    items_no_adds = []
    for item in items:
        new_name = item[0]
        if item[0] == None:
            print(items.index(item))
        if "(" in item[0]:
            new_name = new_name[:new_name.find("(") - 1]
        if '★' in new_name:
            new_name = new_name[new_name.find(" ") + 1:]
        if 'StatTrak' in new_name:
            new_name = new_name[new_name.find(" ") + 1:]
        items_no_adds.append([new_name, item[1], item[2]])
    return items_no_adds


def get_best(items, amount, cost_gap=(0, 1000000000),
             time_gap=(datetime.datetime(1, 1, 1), cur_moment),
             buys_gap=(0, 99), name_part=None):
    stats = {}
    print(len(items))
    for item in items:
        new_name = item[0]
        if time_gap[0] < item[2] < time_gap[1] and cost_gap[0] < item[1] < cost_gap[1]:
            if new_name not in stats.keys():
                stats[new_name] = [0, 0]
            stats[new_name][0] += 1
            stats[new_name][1] += item[1]
    stats_list = list(stats.items())
    stats_list.sort(key=lambda x: x[1][1])
    stats_list = [el for el in stats_list if buys_gap[0] < el[1][0] < buys_gap[1]]
    if name_part is not None and name_part is not '':
        stats_list = [el for el in stats_list if name_part.lower() in el[0].lower()]
    stats_list = stats_list[-amount:]
    return list(reversed(stats_list))


def scan_new_items():
    new_items = []
    try:
        r = requests.get('https://market.csgo.com/history')
        b = BeautifulSoup(r.text, 'html.parser')
        h3 = b.find("h3", text='Последние покупки:')
        for item in h3.next.next.next.find_all("a", class_='item'):
            name = item.find('div', class_='name').text
            price = float(item.find('div', class_='price').text[:-1].replace(" ", ""))
            info = item.find('div', class_='info').text[:-1]
            moment = datetime.datetime.now()
            number = int(info[:info.find(" ")].replace('\n', '0'))
            if 'минут' in info:
                moment += datetime.timedelta(minutes=number)
            else:
                moment += datetime.timedelta(seconds=number)
            new_items.append((name, price, moment))
    except:
        print(sys.exc_info())
    return new_items


def choose_beginning_time(start_time, current_time_string):
    current_time = start_time if current_time_string == 'начала работы программы' else \
        datetime.datetime.strptime(current_time_string, '%d %B, %Y %Hh')
    hours = ["0" + str(i) for i in range(0, 10)] + [str(i) for i in range(10, 25)]
    layout = [[sg.Text('C:'),
               sg.In(key='date', visible=True, disabled=True, size=(20, 20),
                     default_text=current_time.strftime('%d %B, %Y')),
               sg.CalendarButton('Дата', format='%d %B, %Y', target='date'),
               sg.InputCombo(hours, current_time.hour, size=(3, 20), key='start_hour'),
               sg.Text('часов'),
               sg.Button('Начала работы программы'), sg.Button('Сохранить'), sg.Button('Отмена')]]
    window = sg.Window('Выбор момента начала:', layout)
    event = None
    while event is None:
        event, values = window.read()
        if event in (None, 'Exit', 'Отмена'):
            window.close()
            if current_time == start_time:
                return start_time, 'начала работы программы'
            return current_time, current_time_string
        if event == 'Сохранить':
            window.close()
            date_string = f'{values["date"]} {values["start_hour"]}h'
            date = datetime.datetime.strptime(date_string, '%d %B, %Y %Hh')
            if date == start_time:
                return date, 'начала работы программы'
            return date, date_string
        if event == 'Начала работы программы':
            window.close()
            return start_time, 'начала работы программы'


def choose_ending_time(current_time_string):
    current_time = cur_moment if current_time_string == 'текущего момента' else \
        datetime.datetime.strptime(current_time_string, '%d %B, %Y %Hh')
    hours = ["0" + str(i) for i in range(0, 10)] + [str(i) for i in range(10, 25)]
    layout = [[sg.Text('До:'),
               sg.In(key='date', visible=True, disabled=True, size=(20, 20),
                     default_text=current_time.strftime('%d %B, %Y')),
               sg.CalendarButton('Дата', format='%d %B, %Y', target='date'),
               sg.InputCombo(hours, current_time.hour, key='end_hour', size=(3, 20)),
               sg.Text('часов'),
               sg.Button('Текущего момента'), sg.Button('Сохранить'), sg.Button('Отмена')]]
    window = sg.Window('Выбор момента окончания:', layout)
    event = None
    while event is None:
        event, values = window.read()
        if event in (None, 'Exit', 'Отмена'):
            window.close()
            if current_time == cur_moment:
                return current_time, 'текущего момента'
            return current_time, current_time.strftime('%d %B, %Y %Hh')
        if event == 'Сохранить':
            window.close()
            date_string = f'{values["date"]} {values["end_hour"]}h'
            date = datetime.datetime.strptime(date_string, '%d %B, %Y %Hh')
            if date == cur_moment:
                return date, 'текущего момента'
            return date, date_string
        if event == 'Текущего момента':
            window.close()
            return cur_moment, 'текущего момента'


def get_usd_cost():
    address = 'http://www.cbr.ru/scripts/XML_daily.asp'
    r = requests.get(address)
    start = r.text.find('<Valute ID="R01235">')
    length = len('<Valute ID="R01235">')
    value_start = r.text.find('<Value>', start + length) + len('<Value>')
    value_end = r.text.find('</Value>', start + length)
    r = float(r.text[value_start:value_end].replace(',', '.'))
    return r


def get_steam_item_info(name):
    try:
        address = 'https://steamcommunity.com/market/search?appid=730&q='
        data = f'{name.replace("★ ", "").replace("| ", "").replace(" ", "+")}'
        data = urllib.parse.quote(data)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 OPR/82.0.4227.50',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': address
        }
        r = requests.get(address + data, headers=headers)
        b = BeautifulSoup(r.text, 'html.parser')
        cost_part = b.find('div', class_='market_listing_row market_recent_listing_row market_listing_searchresult')
        cost = cost_part.find('span', class_="normal_price").next.next.next.next.text
        name = cost_part.get('data-hash-name')
        cost = float(cost.replace('$', '').replace(' USD', '').replace(',', '')) * get_usd_cost()
        amount = int(cost_part.find('span', class_="market_listing_num_listings_qty").text)
        return name, cost, amount
    except:
        print(sys.exc_info())
        return '', 0, 0


def get_last_items(total_items):
    last = len(total_items)
    total_items.sort(key=lambda x: x[2])
    for el in total_items:
        if (datetime.datetime.now() - el[2]).total_seconds() > 900:
            last = total_items.index(el)
            break
    return total_items[:last].copy()