from Newsletter import Newsletter
from datetime import timedelta
import json


class IsraelHayom(Newsletter):

    def extract_news(self):
        data = json.loads(self.page.text)
        articles = data["data"]["flashPosts"]
        for art in articles:
            author = art["writer"][0]["name"]
            publication_date = self.parse_iso_datetime(art["createDate"])
            publication_date = publication_date + timedelta(hours=3)
            url = 'https://www.israelhayom.co.il/' + art["url"]
            title = art["title"]
            description = art["body"]
            self.articles.append(self.Article(-1, "IsraelHayom", author, publication_date, url, title, description))
        