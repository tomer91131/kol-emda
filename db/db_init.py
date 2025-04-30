import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database connection details from environment variables
DATABASE_URL = os.getenv('DATABASE_URL')

# Connect to PostgreSQL
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# Create the articles table
create_table_query = """
CREATE TABLE IF NOT EXISTS articles (
    id SERIAL PRIMARY KEY,
    newsletter VARCHAR(255),
    author VARCHAR(255),
    datetime TIMESTAMP,
    url TEXT,
    title TEXT,
    description TEXT
);
"""

cursor.execute(create_table_query)
print("Table 'articles' created successfully.")

# Create the triplets table
create_triplets_table = """
CREATE TABLE IF NOT EXISTS triplets (
    id SERIAL PRIMARY KEY,
    article1_id INTEGER NOT NULL,
    article2_id INTEGER NOT NULL,
    article3_id INTEGER NOT NULL,
    score FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (article1_id) REFERENCES articles(id),
    FOREIGN KEY (article2_id) REFERENCES articles(id),
    FOREIGN KEY (article3_id) REFERENCES articles(id)
);
"""
cursor.execute(create_triplets_table)
conn.commit()

# Cleanup
cursor.close()
conn.close()
