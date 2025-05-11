from Newsletter import Newsletter
from bs4 import BeautifulSoup
import requests

class Ynet(Newsletter):
    # def strip(self, s: str) -> str: 
    #     return s.strip('[]CDAT ')
    
    def extract_news(self):
        soup = BeautifulSoup(self.page.text, 'xml')
        items = soup.find_all('item')

        for item in items:
            try:
                url = item.find('link').text
                title = item.find('title').text
                publication_date = self.parse_datetime(item.find('pubDate').text)
                newpage = requests.get(url)
                newsoup = BeautifulSoup(newpage.text, 'html.parser')
                author = newsoup.find('div', class_='authors').getText()
                author = author.replace('|','')
                description = newsoup.find('span', attrs={"data-text": "true"}).text
                self.articles.append(self.Article(-1, 'Ynet', author, publication_date, url, title, description))
            except Exception as e:
                print("skipping article because of error: ", e)
