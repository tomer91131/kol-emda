import psycopg2
from datetime import datetime
import random
import os
from dotenv import load_dotenv

class NewsModel:
    def __init__(self):
        load_dotenv()
        self.DATABASE_URL = os.getenv('DATABASE_URL')

    def get_connection(self):
        return psycopg2.connect(self.DATABASE_URL)

    def _randomize_articles(self, articles):
        """Randomize the order of articles in a triplet"""
        articles_copy = articles.copy()
        random.shuffle(articles_copy)
        return articles_copy

    def get_recent_triplets(self, limit=5):
        """Get the most recent triplets of news articles for the game"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT t.id, 
                   a1.title as title1, a1.newsletter as source1,
                   a2.title as title2, a2.newsletter as source2,
                   a3.title as title3, a3.newsletter as source3,
                   t.created_at
            FROM triplets t
            JOIN articles a1 ON t.article1_id = a1.id
            JOIN articles a2 ON t.article2_id = a2.id
            JOIN articles a3 ON t.article3_id = a3.id
            ORDER BY t.created_at DESC
            LIMIT %s
        """, (limit,))
        
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        
        triplets = []
        for result in results:
            # Create articles array
            articles = [
                {'title': result['title1'], 'source': result['source1']},
                {'title': result['title2'], 'source': result['source2']},
                {'title': result['title3'], 'source': result['source3']}
            ]
            
            # Randomize the order
            randomized_articles = self._randomize_articles(articles)
            
            triplets.append({
                'id': result['id'],
                'created_at': result['created_at'],
                'articles': randomized_articles
            })
        return triplets

    def get_triplets_for_display(self, limit=10):
        """Get triplets for display in the news comparison tab"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT t.id,
                   a1.title as title1, a1.newsletter as source1, a1.datetime as date1, a1.url as url1,
                   a2.title as title2, a2.newsletter as source2, a2.datetime as date2, a2.url as url2,
                   a3.title as title3, a3.newsletter as source3, a3.datetime as date3, a3.url as url3
            FROM triplets t
            JOIN articles a1 ON t.article1_id = a1.id
            JOIN articles a2 ON t.article2_id = a2.id
            JOIN articles a3 ON t.article3_id = a3.id
            ORDER BY t.created_at DESC
            LIMIT %s
        """, (limit,))
        
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        
        triplets = []
        for row in results:
            # Create articles array
            articles = [
                {
                    'title': row['title1'],
                    'source': row['source1'],
                    'datetime': row['date1'],
                    'url': row['url1']
                },
                {
                    'title': row['title2'],
                    'source': row['source2'],
                    'datetime': row['date2'],
                    'url': row['url2']
                },
                {
                    'title': row['title3'],
                    'source': row['source3'],
                    'datetime': row['date3'],
                    'url': row['url3']
                }
            ]
            
            # Randomize the order
            randomized_articles = self._randomize_articles(articles)
            
            triplet = {
                'id': row['id'],
                'articles': randomized_articles
            }
            
            # Sort articles by source (Haaretz -> Ynet -> Walla -> Israel Hayom)
            source_order = {'Haaretz': 0, 'Ynet': 1, 'Walla': 2, 'Israel Hayom': 3}
            triplet['articles'].sort(key=lambda x: source_order.get(x['source'], 999))
            triplets.append(triplet)
            
        return triplets 