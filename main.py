import os
import re
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from bs4 import BeautifulSoup
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from connection import engine


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
                        print(currency_with_only_3_letters, amount_starts, event_time)
                        db.execute(text("insert into public.news (pair, stars, times) values (:pair, :stars, :times)"),
                                      {'pair': currency_with_only_3_letters, 'stars': amount_starts, 'times': event_time})
                        db.commit()
                        db.close()


def get_events(db):
    db.execute(text("truncate table public.news restart identity cascade"))
    db.commit()
    db.close()
    html = get_html_from_economic_calendar()
    extract_today_event_times(html=html, db=db)


Session = sessionmaker(bind=engine)
db = Session()

get_events(db)
