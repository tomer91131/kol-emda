import mysql.connector
import subprocess


def start_mysql():
    try:
        subprocess.run(["mysql.server", "start"], check=True)
        print("MySQL started.")
    except subprocess.CalledProcessError as e:
        print("Failed to start MySQL:", e)

def stop_mysql():
    try:
        subprocess.run(["mysql.server", "stop"], check=True)
        print("MySQL stopped.")
    except subprocess.CalledProcessError as e:
        print("Failed to stop MySQL:", e)

start_mysql()

# Configuration - replace these with your MySQL server info
config = {
    "host": "localhost",
    "user": "admin",
    "password": "viva123",
}

# Database and table info
DB_NAME = "kol_emda"
TABLE_NAME = "articles"

# Connect to MySQL Server
conn = mysql.connector.connect(**config)
cursor = conn.cursor()

# Step 1: Create the database
cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
cursor.execute(f"USE {DB_NAME}")

# Step 2: Create the articles table
create_table_query = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    id INT AUTO_INCREMENT PRIMARY KEY,
    newsletter VARCHAR(255),
    author VARCHAR(255),
    datetime DATETIME,
    url TEXT,
    title TEXT,
    description TEXT
);
"""

cursor.execute(create_table_query)
print(f"Table '{TABLE_NAME}' created successfully in database '{DB_NAME}'.")

# Cleanup
cursor.close()
conn.close()
stop_mysql()
