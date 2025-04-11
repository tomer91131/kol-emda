from bs4 import BeautifulSoup
import requests
import os
from datetime import datetime
from abc import ABC, abstractmethod

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
                    description:\n {self.description}"""

    def __init__(self, url, filename, parser_method):
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

        if self.page:
            self.soup = BeautifulSoup(self.page.text, parser_method)
    
    def dump_to_file(self):
        try:
            os.remove(self.filename)
        except FileNotFoundError:
            print(f"removing {self.filename} failed")
        try:
            fd = open(self.filename, 'w')
            fd.write(self.soup.text)
            fd.close()
        except OSError:
            print(f"failed to open {self.filename}")

    def parse_datetime(self, date_string):
        # Parsing the string to a datetime object
        return datetime.strptime(date_string, "%a, %d %b %Y %H:%M:%S %z")

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
        items = self.soup.find_all('item')
        for item in items:
            self.articles.append(self.article(id=-1,
                                              news_letter='Haaretz',
                                              author=item.find('dc:creator').getText(), 
                                              publication_date=self.parse_datetime(item.find('pubDate').getText()),
                                              url=item.find('link').getText(),
                                              title=item.find('title').getText(),
                                              description=item.find('description').getText()))

class Ynet(Newsletter):
    def extract_news():
        items = self.soup.find_all('div', class_="AccordionSection")
        for item in items:
            

class Walla(Newsletter):
    def extract_news():
        pass

class Channel14(Newsletter):
    def extract_news():
        pass

class Israelhayom(Newsletter):
    def extract_news():
        pass

class Kan11(Newsletter):
    def extract_news():
        pass
            
class NewsFactory:
    @staticmethod
    def create_newsletter(news_letter_name: str, url: str, filename: str, parser_method='xml') -> Newsletter:
        newsletter_dict = {
            "Haaretz": Haaretz,
            "Ynet": Ynet,
            "Walla": Walla,
            "Channel14": Channel14,
            "IsraelHayom": Israelhayom,
            "Kan11": Kan11
        }
        return newsletter_dict[news_letter_name](url, filename, parser_method)






