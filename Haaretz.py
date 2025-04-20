from Newsletter import Newsletter
from bs4 import BeautifulSoup

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
