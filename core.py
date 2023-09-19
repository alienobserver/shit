from copy import deepcopy
from googletrans import Translator
from functools import partial
from dateutil.parser import parse
from datetime import datetime, timedelta
import pickle
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
import json
from rich.progress import Progress
import math
import utils

translator = Translator()
std_parse = partial(parse, dayfirst=True)

class ScrapeArmenPress():
    def __init__(self, num_pages=None, filename=None, categories=None):
        if not filename:
            filename = "shit.pkl"
        if not num_pages:
            num_pages = 40
        if not categories:
            categories = ['politics']

        self.num_pages = num_pages
        self.filename = filename
        self.url = 'https://armenpress.am/arm/news/politics/'
        self.categories = categories



    @staticmethod
    def get_40_x(x):
        if x % 40 == 0:
            return x

        else:
            return math.ceil(x / 40) * 40

    def extract_article_urls(self):
        with Progress() as progress:
            task = progress.add_task("[purple]Extracting URL\'s...", total=self.get_40_x(self.num_pages))
            driver = webdriver.Chrome()
            urls = set()

            # Navigate to the website
            driver.get(self.url)

            # Define the button to click (you may need to inspect the website's HTML to find the button's selector)
            button_selector = 'morenewsbydatecontainer'
            # Scroll down and click the button multiple times to load more news
            try:
                while len(urls) < self.num_pages:
                    element = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.ID, button_selector)))
                    button = driver.find_element(By.ID, button_selector)
                    actions = ActionChains(driver)
                    actions.move_to_element(button).click().perform()
                    # Get the page source with the loaded news
                    page_source = driver.page_source

                    # Parse the page source with BeautifulSoup
                    soup = BeautifulSoup(page_source, 'html.parser')

                    urls.update(soup.find_all('article', class_='newsbycatitem'))

                    progress.update(task, advance=40)

            except Exception as e:
                print(f"An error occurred: {str(e)}")

            # Close the web driver when you're done
            driver.quit()

            self.urls = urls

    def add_prefix(self, prefix=None):
        if not prefix:
            prefix = 'https://armenpress.am'

        links = set()
        for i in self.urls:
            if i is not None:
                a = i.find_all('a')
                for j in a:
                    links.add(prefix + j['href'])

        self.urls = links

    def get_data(self):
        self.extract_article_urls()
        self.add_prefix()

        data = []
        count = 0

        with Progress() as progress:
            task2 = progress.add_task("[purple]Scraping Data\'s...", total=len(self.urls))

            for url in self.urls:
                page = requests.get(url)
                soup = BeautifulSoup(page.text, 'html.parser')
                header = soup.find('h1', class_='opennewstitle').text
                body = soup.find('span', itemprop='articleBody').text
                date = soup.find('span', class_='datetime').text

                for key, value in utils.ARM_MONTHS.items():
                    date = date.lower().replace(key, value)

                date_changed = parse(date)

                data.append({'header': header, 'body': body, 'date' : date_changed, 'category' : 'politics', 'url' : url})
                count += 1

                progress.update(task2, advance=1)

            self.data = data

    def save(self):
        with open(self.filename, "wb") as outfile:
            pickle.dump(self.data, outfile)