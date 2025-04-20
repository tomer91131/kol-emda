from Newsletter import Newsletter
from bs4 import BeautifulSoup
from datetime import datetime

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
