from typing import List, Tuple
from datetime import datetime, timedelta
import psycopg2
from news_factory import NewsFactory
from itertools import combinations
from Newsletter import Newsletter
import os
from dotenv import load_dotenv

def update_database():
    news_stand: List[Newsletter] = NewsFactory.create_newsletter("all", '')
    for paper in news_stand:
        paper.extract_news()
        # paper.dump_to_file()
        paper.insert_articles()

hebrew_stopwords = { "דיווח", "לגבי", "הכל", " ", "חדשות"
    "של", "על", "עם", "זה", "זו", "זאת", "הוא", "היא", "הם", "הן", "את",
    "אני", "אתה", "את", "אנחנו", "אתם", "אתן", "יש", "אין", "כן", "לא",
    "כל", "כמו", "אם", "כי", "או", "אבל", "גם", "רק", "עוד", "כבר", "אז",
    "כאשר", "אשר", "מה", "מי", "איפה", "מתי", "למה", "איך", "היכן", "זמן",
    "עד", "תוך", "לפני", "אחרי", "מאז", "היה", "הייתה", "היו", "יכול", "יכולה",
    "יכולים", "צריך", "צריכה", "צריכים", "נמצא", "נמצאת", "נמצאים", "נמצאות",
    "כדי", "בעד", "נגד", "לכן", "למרות", "בגלל", "בין", "אחד", "אחת", "שני", "שתי",
    "שלושה", "שלוש", "ארבעה", "ארבע"
}

def normalize_title(title: str) -> List[str]:
    title = title.replace('.:,;"`/', '')
    words = title.split()
    clean_set = set()
    for word in words:
        if word not in hebrew_stopwords:
            clean_set.add(word)
    return list(clean_set)

def score_similarity(title1: Tuple, title2: Tuple) -> int:
    overlap = len(set(normalize_title(title1[5])) & set(normalize_title(title2[5])))
    score = overlap / min(len(normalize_title(title1[5])), len(normalize_title(title2[5])))
    timedif = title1[3] - title2[3]
    if abs(timedif) < timedelta(minutes=30):
        score *= 4
    elif abs(timedif) < timedelta(minutes=60):
        score *= 3
    elif abs(timedif) < timedelta(minutes=120):
        score *= 2
    return score

def pull_titles(newsletter):
    load_dotenv()
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    query = """
    SELECT * FROM articles
        WHERE newsletter = %s
        AND datetime >= NOW() - INTERVAL '12 hours'
        ORDER BY datetime DESC;
    """
    
    cursor.execute(query, (newsletter,))
    sqlres = cursor.fetchall()

    cursor.close()
    conn.close()
    return sqlres

def insert_triplets(triplets : List[Tuple]):
    load_dotenv()
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    for triplet in triplets:
        if triplet[3] >= 2:
            query = """INSERT INTO triplets (article1_id, article2_id, article3_id, score)
                        VALUES (%s, %s, %s, %s)
                        """
            cursor.execute(query, (triplet[0][0], triplet[1][0], triplet[2][0], triplet[3]))
    
    conn.commit()
    cursor.close()
    conn.close()

def match_titles() -> list[tuple]:
    titles1 = pull_titles('Haaretz')
    titles2 = pull_titles('Ynet')
    titles3 = pull_titles('IsraelHayom')
    titles4 = pull_titles('Walla')

    l1, l2, l3, l4 = titles1, titles2, titles3, titles4
    all_vs_all_scores = {}
    all_titles : List[Tuple] = l1 + l2 + l3 + l4

    for i in range(len(all_titles)):
        for j in range(i):
            title1, title2 = all_titles[i], all_titles[j]
            score = score_similarity(title1, title2)
            if title1[1] == title2[1]: #if the same newsletter : give it a bad score
                score = 0
            # store it twice for easy access
            all_vs_all_scores[(title1, title2)] = score
            all_vs_all_scores[(title2, title1)] = score

    def triplets_score(indices) -> int:
        i, j, k = indices
        title1, title2, title3 = all_titles[i], all_titles[j], all_titles[k]
        # title1, title2, title3 = indices
        score1, score2, score3 = all_vs_all_scores[(title1, title2)], all_vs_all_scores[(title2, title3)], all_vs_all_scores[(title1,title3)]
        score = (score1 + score2 + score3) * min(score1, score2, score3)
        return score

    # Generate all possible triplets from all_titles
    all_triplets = list(combinations(range(len(all_titles)), 3))

    # Sort the triplets based on their score using triplets_score
    sorted_triplets = sorted(all_triplets, key=triplets_score, reverse=True)

    used_items = set()

    top_triplets = []
    for indices in sorted_triplets:
        if all_titles[indices[0]] in used_items or all_titles[indices[1]] in used_items or all_titles[indices[2]] in used_items:
            continue
        else:
            used_items.add(all_titles[indices[0]])
            used_items.add(all_titles[indices[1]])
            used_items.add(all_titles[indices[2]])
            top_triplets.append((all_titles[indices[0]], all_titles[indices[1]], all_titles[indices[2]], triplets_score(indices)))
            # print(f"triplets score = {triplets_score(indices)}")
            # print(f"newsletters: {all_titles[indices[0]][1]}, {all_titles[indices[1]][1]}, {all_titles[indices[2]][1]}")
            # print(f"first title: {all_titles[indices[0]][5]},\n second title: {all_titles[indices[1]][5]},\n third title: {all_titles[indices[2]][5]} \n\n")
    insert_triplets(top_triplets)

if __name__ == '__main__':
    update_database()
    match_titles()