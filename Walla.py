from Newsletter import Newsletter
from bs4 import BeautifulSoup
from datetime import datetime
import re
import requests

class Walla(Newsletter):
    def extract_gregorian_date(self, text: str) -> list[str]:
        match = re.search(r"(\d{2})\.(\d{2})\.(\d{4})", text)
        if match:
            day, month, year = match.groups()
            return [day, month, year]
        return []
    
    def extract_news(self):

        if self.page:
            self.soup = BeautifulSoup(self.page.text, 'html.parser')
        else:
            return
        
        sections = self.soup.find_all('section', class_='css-3mskgx')
        for sec in sections:
            title = sec.find('h1', class_='breaking-item-title').getText()
            title = title[title.find('/')+1::]
            url = 'https://news.walla.co.il' + sec.find('a').attrs['href']
            try:
                description = sec.find('p', class_='article_speakable').getText()
            except:
                description = ""
            hour, minut  = map(int, sec.find('span', class_='red-time').text.split(':'))
            author = (sec.find('div', class_='writer-name-item'))
            article_page = requests.get(url)
            soup_for_date = BeautifulSoup(article_page.text, 'html.parser')
            date = soup_for_date.find('div', class_='header-titles').getText()
            date = self.extract_gregorian_date(date)
            time = datetime(int(date[2]),int(date[1]) , int(date[0]), hour, minut)
            if not author:
                author = sec.find('p', class_='content-provider-text')
            self.articles.append(self.Article(-1, "Walla", author.text, time, url, title, description))
