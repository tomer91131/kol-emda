import requests
import os
from datetime import datetime
from abc import ABC, abstractmethod
import psycopg2
from dotenv import load_dotenv

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
    
    def insert_articles(self):
        load_dotenv()
        DATABASE_URL = os.getenv('DATABASE_URL')
        
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        for art in self.articles:
            query = """INSERT INTO articles (newsletter, author, datetime, url, title, description)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (url) DO UPDATE
                        SET title = EXCLUDED.title,
                            description = EXCLUDED.description,
                            datetime = EXCLUDED.datetime,
                            author = EXCLUDED.author;"""
            cursor.execute(query, (art.news_letter, art.author, art.publication_date, art.url, art.title, art.description))
        
        conn.commit()
        cursor.close()
        conn.close()

    def __str__(self):
        s = ''
        for art in self.articles:
            s += art.__str__()
        return s
    