from Walla import Walla
from Ynet import Ynet
from Haaretz import Haaretz
from IsraelHayom import IsraelHayom
from Newsletter import Newsletter




            
class NewsFactory:
    @staticmethod
    def create_newsletter(news_letter_name: str, filename: str) -> Newsletter:
        newsletter_dict = {
            "Haaretz": Haaretz,
            "Ynet": Ynet,
            "Walla": Walla,
            "IsraelHayom": IsraelHayom
        }
        urls = {"Haaretz": "https://www.haaretz.co.il/srv/rss---feedly",
            "Ynet": "https://www.ynet.co.il/Integration/StoryRss1854.xml",
            "Walla": "https://news.walla.co.il/breaking",
            "IsraelHayom": "https://www.israelhayom.co.il/flash-posts-manage-api/flash_post_data?from=0&size=20&viewScope=newsflash"
        }
        if news_letter_name == "all":
            stand = []
            for key in newsletter_dict:
                stand.append(newsletter_dict[key](urls[key], key+'.txt'))
            return stand
        return newsletter_dict[news_letter_name](urls[news_letter_name], filename)







