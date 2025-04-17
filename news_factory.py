from bs4 import BeautifulSoup
import requests
import os
from datetime import datetime
from abc import ABC, abstractmethod
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time


class Newsletter(ABC):
    class Article:
        def __init__(self, id, news_letter, author, publication_date, url, title, description):
            self.id = id
            self.news_letter = news_letter
            self.author = author
            self.publication_date = publication_date
            self.url = url
            self.title = title
            self.description = description

        def __str__(self):
            return f"""newsletter:{self.news_letter}, author:{self.author}, publication_date:{self.publication_date}\n 
                    url: {self.url}\n\n
                    title: {self.title}\n\n
                    description:\n {self.description}\n"""

    def __init__(self, url, filename):
        self.articles = []
        self.url = url
        self.filename = filename

        try:
            self.page = requests.get(self.url, timeout=5)
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error: {e.response.status_code} {e.response.reason}")
        except requests.exceptions.ConnectionError:
            print("Connection failed. Check your network or the URL.")
        except requests.exceptions.Timeout:
            print("Request timed out.")
        except requests.exceptions.RequestException as e:
            print(f"Unexpected error: {e}")

    
    def dump_to_file(self):
        try:
            os.remove(self.filename)
        except FileNotFoundError:
            print(f"removing {self.filename} failed")
        try:
            fd = open(self.filename, 'w')
            strlist = ''
            for art in self.articles:
                strlist += art.__str__()
            fd.write(strlist)
            fd.close()
        except OSError:
            print(f"failed to open {self.filename}")

    def parse_datetime(self, date_string):
        # Parsing the string to a datetime object
        return datetime.strptime(date_string, "%a, %d %b %Y %H:%M:%S %z")
    
    def parse_iso_datetime(self, iso_str: str) -> datetime:
        return datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%S.%fZ")

    @abstractmethod
    def extract_news():
        pass
    
    def __str__(self):
        s = ''
        for art in self.articles:
            s += art.__str__()
        return s
    

class Haaretz(Newsletter):

    def extract_news(self):
        if self.page:
            self.soup = BeautifulSoup(self.page.text, 'xml')
        else:
            return
        items = self.soup.find_all('item')
        for item in items:
            self.articles.append(self.Article(id=-1,
                                              news_letter='Haaretz',
                                              author=item.find('dc:creator').getText(), 
                                              publication_date=self.parse_datetime(item.find('pubDate').getText()),
                                              url=item.find('link').getText(),
                                              title=item.find('title').getText(),
                                              description=item.find('description').getText()))

class Ynet(Newsletter):
    def extract_news(self):

        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)
        driver.get(self.url)
        time.sleep(2)
        AccordionSections = driver.find_elements(By.CLASS_NAME, "AccordionSection")
        for section in AccordionSections:
            try:
                # Scroll to the element (optional but helps sometimes)
                driver.execute_script("arguments[0].scrollIntoView();", section)
                button = section.find_element(By.CLASS_NAME, "title")
                # Click to expand the section
                button.click()
                time.sleep(0.5)  # wait for content to load after click

                # Parse updated HTML with BeautifulSoup
                soup = BeautifulSoup(driver.page_source, "html.parser")

                # Get the itemBody inside the currently opened section
                date = section.find_element(By.CLASS_NAME, "DateDisplay").get_attribute('datetime')
                url = 'https://www.ynet.co.il/news/article/' + section.get_attribute('id')
                title = section.text
                indx = title[::-1].find('\n')
                author = title[-indx::]
                description = section.find_element(By.CLASS_NAME, "itemBody").text
                self.articles.append(self.Article(-1,"Ynet", author, self.parse_datetime(date), url, title, description))

            except Exception as e:
                continue
    
        driver.quit()
        
            

class Walla(Newsletter):
    def extract_news(self):

        if self.page:
            self.soup = BeautifulSoup(self.page.text, 'html.parser')
        else:
            return
        
        sections = self.soup.find_all('section', class_='css-3mskgx')
        for sec in sections:
            title = sec.find('h1', class_='breaking-item-title').getText()
            title = title[title.find('/')+1::]
            url = 'https://news.walla.co.il/' + sec.find('a').attrs['href']
            description = sec.find('p', class_='article_speakable').text
            author = (sec.find('div', class_='writer-name-item'))
            hour, minut  = map(int, sec.find('span', class_='red-time').text.split(':'))
            now = datetime.now()
            time = datetime(now.year, now.month, now.day, hour, minut)
            if not author:
                author = sec.find('p', class_='content-provider-text')
            self.articles.append(self.Article(-1, "Walla", author.text, time, url, title, description))


class Israelhayom(Newsletter):

    def extract_news(self):
        data = json.loads(self.page.text)
        articles = data["data"]["flashPosts"]
        for art in articles:
            author = art["writer"][0]["name"]
            publication_date = self.parse_iso_datetime(art["createDate"])
            url = 'https://www.israelhayom.co.il/' + art["url"]
            title = art["title"]
            description = art["body"]
            self.articles.append(self.Article(-1, "IsraelHayom", author, publication_date, url, title, description))
        
            
class NewsFactory:
    @staticmethod
    def create_newsletter(news_letter_name: str, filename: str) -> Newsletter:
        newsletter_dict = {
            "Haaretz": Haaretz,
            "Ynet": Ynet,
            "Walla": Walla,
            "IsraelHayom": Israelhayom
        }
        urls = {"Haaretz": "https://www.haaretz.co.il/srv/rss---feedly",
            "Ynet": "https://www.ynet.co.il/news/category/184",
            "Walla": "https://news.walla.co.il/breaking",
            "IsraelHayom": "https://www.israelhayom.co.il/flash-posts-manage-api/flash_post_data?from=0&size=20&viewScope=newsflash"
        }
        return newsletter_dict[news_letter_name](urls[news_letter_name], filename)







