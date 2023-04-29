import asyncio
import os
import re
import time

import aiohttp
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from connection import engine


async def insert_news(currency_with_only_3_letters, amount_starts, event_time):
    payload = {
        "pair": currency_with_only_3_letters,
        "stars": amount_starts,
        "hours": event_time
    }
    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(os.getenv('API_USER'), os.getenv('API_PASS'))
        headers = {'Authorization': auth.encode()}
        async with session.post('https://v1.investingbrazil.online/news/create', json=payload, headers=headers) as resp:
            if resp.status == 200:
                pass


def call_generate_filter():
    asyncio.run(generate_news_filter())


def call_insert_filter():
    asyncio.run(insert_news_filter())


def str_to_minutes(tempo_str):
    hora, minuto = map(int, tempo_str.split(':'))
    return hora * 60 + minuto


def minutes_to_str(minutos):
    hora = minutos // 60
    minuto = minutos % 60
    return f"{hora:02d}:{minuto:02d}"


async def filter_insert(pair, range_hours):
    payload = {
        "pair": str(pair),
        "range_hours": str(range_hours)
    }
    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(os.getenv('API_USER'), os.getenv('API_PASS'))
        headers = {'Authorization': auth.encode()}
        async with session.post('https://v1.investingbrazil.online/news/filter_news', json=payload,
                                headers=headers) as resp:
            if resp.status == 200:
                pass



range_hours_10 = {}
range_hours_20 = {}
hours_to_filter = {}


async def insert_news_filter():
    for par1 in range_hours_10:
        range_hours_10[par1] = list(set(range_hours_10[par1]))
    for par2 in range_hours_20:
        range_hours_20[par2] = list(set(range_hours_20[par2]))

    for k in range_hours_10:
        contador = 0
        horario = range_hours_10[k][contador]
        horario_minutos = str_to_minutes(horario)
        inicio = horario_minutos - 10
        fim = horario_minutos + 10

        if inicio < 0:
            inicio += 24 * 60

        if fim >= 24 * 60:
            fim -= 24 * 60

        if fim < inicio:
            fim += 24 * 60

        for minutos in range(inicio, fim + 1):
            if minutos >= 24 * 60:
                minutos -= 24 * 60
            if k not in hours_to_filter:
                hours_to_filter[k] = [minutes_to_str(minutos)]
            else:
                hours_to_filter[k].append(minutes_to_str(minutos))

        if contador < len(range_hours_10):
            contador += 1

    for k in range_hours_20:
        contador = 0
        horario = range_hours_20[k][contador]
        horario_minutos = str_to_minutes(horario)
        inicio = horario_minutos - 20
        fim = horario_minutos + 20

        if inicio < 0:
            inicio += 24 * 60

        if fim >= 24 * 60:
            fim -= 24 * 60

        if fim < inicio:
            fim += 24 * 60

        for minutos in range(inicio, fim + 1):
            if minutos >= 24 * 60:
                minutos -= 24 * 60
            if k not in hours_to_filter:
                hours_to_filter[k] = [minutes_to_str(minutos)]
            else:
                hours_to_filter[k].append(minutes_to_str(minutos))

        if contador < len(range_hours_20):
            contador += 1

    for l in hours_to_filter:
        await filter_insert(l, hours_to_filter[l])


def filter_news_dict(par, horario, estrelas, news_dicts):
    if estrelas == 1 and is_only_news_for_hour(news_dicts, horario, par):
        if par not in range_hours_10:
            range_hours_10[par] = [horario]
        else:
            range_hours_10[par].append(horario)
    elif estrelas == 1 and is_more_than_one_news_for_hour_and_stars(news_dicts, horario, par):
        if par not in range_hours_20:
            range_hours_20[par] = [horario]
        else:
            range_hours_20[par].append(horario)
    elif estrelas == 2 and is_only_news_for_hour(news_dicts, horario, par):
        if par not in range_hours_20:
            range_hours_20[par] = [horario]
        else:
            range_hours_20[par].append(horario)
    elif estrelas == 2 and is_more_than_one_news_for_hour(news_dicts, horario, par):
        if par not in range_hours_20:
            range_hours_20[par] = [horario]
        else:
            range_hours_20[par].append(horario)
    elif estrelas == 3 and is_only_news_for_hour(news_dicts, horario, par):
        if par not in range_hours_20:
            range_hours_20[par] = [horario]
        else:
            range_hours_20[par].append(horario)
    elif estrelas == 3 and is_more_than_one_news_for_hour(news_dicts, horario, par):
        if par not in range_hours_20:
            range_hours_20[par] = [horario]
        else:
            range_hours_20[par].append(horario)

    return range_hours_10, range_hours_20


def is_only_news_for_hour(news_dicts, horario, par):
    count = 0
    for news_dict in news_dicts:
        if news_dict['hours'] == horario and news_dict['pair'] == par:
            count += 1
            if count > 1:
                return False
    return True


def is_more_than_one_news_for_hour(news_dicts, horario, par):
    count = 0
    for news_dict in news_dicts:
        if news_dict['hours'] == horario and news_dict['pair'] == par and news_dict['stars'] >= 2:
            count += 1
    return count > 1


def is_more_than_one_news_for_hour_and_stars(news_dicts, horario, par):
    count = 0
    for news_dict in news_dicts:
        if news_dict['hours'] == horario and news_dict['pair'] == par and news_dict['stars'] == 1:
            count += 1
    return count > 1


async def generate_news_filter():
    async with aiohttp.ClientSession() as session:
        auth = aiohttp.BasicAuth(os.getenv('API_USER'), os.getenv('API_PASS'))
        headers = {'Authorization': auth.encode()}
        async with session.get('https://v1.investingbrazil.online/news/get_news', headers=headers) as resp:
            if resp.status == 200:
                r = await resp.json()
                for news_dict in r:
                    par = news_dict['pair']
                    horario = news_dict['hours']
                    estrelas = news_dict['stars']
                    filter_news_dict(par, horario, estrelas, r)



def get_html_from_economic_calendar():
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode
    chrome_options.add_argument("--disable-gpu")  # Disable GPU usage
    chrome_options.add_argument("--no-sandbox")  # Disable the sandbox
    chrome_options.add_argument("--disable-dev-shm-usage")  # Disable shared memory usage
    chrome_options.page_load_strategy = 'eager'
    executable_path = '/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome'

    # Set up the Chrome service
    chrome_service = ChromeService(executable_path=executable_path)
    browser = webdriver.Chrome(service=chrome_service, options=chrome_options)
    url = 'https://br.investing.com/economic-calendar/'
    browser.get(url)
    # btn = browser.find_element(By.XPATH, '//*[@id="timeFrame_yesterday"]')
    # btn.click()
    # time.sleep(2)
    html = browser.page_source
    return html


def extract_today_event_times(html, db):
    soup = BeautifulSoup(html.encode('utf-8'), 'html.parser')
    table = soup.find("table", {"id": "economicCalendarData"})

    trs = table.find_all('tr')
    # trs=trs[2:]

    for tr in trs:
        tds = tr.find_all('td')
        if len(tds) < 2:
            continue
        column_of_currency_name = 1
        currency = tds[column_of_currency_name].text

        currency_with_only_3_letters = re.sub('.*([A-Z]{3}).*', '\\1', currency)

        stars = tr.find_all(attrs={'class': 'grayFullBullishIcon'})
        amount_starts = len(stars)
        has_at_least_1_star = amount_starts > 0

        if has_at_least_1_star:
            for td in tds:
                if re.search('\d+:\d+', td.text):
                    event_time = td.text
                    if currency_with_only_3_letters:
                        asyncio.run(insert_news(currency_with_only_3_letters, amount_starts, event_time))


def get_events(db):
    db.execute(text("truncate table public.news restart identity cascade"))
    db.commit()
    db.close()
    db.execute(text("truncate table public.filter_news restart identity cascade"))
    db.commit()
    db.close()
    html = get_html_from_economic_calendar()
    extract_today_event_times(html=html, db=db)
    call_generate_filter()
    call_insert_filter()


Session = sessionmaker(bind=engine)
db = Session()

get_events(db)
