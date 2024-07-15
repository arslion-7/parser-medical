import sqlite3
from sqlite3 import Error

class DatabaseManager:
    def __init__(self, db_file):
        """Initialize the DatabaseManager with a database file."""
        self.db_file = db_file
        self.conn = self.create_connection()

    def create_connection(self):
        """Create a database connection to the SQLite database."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
            print(f"Connection to {self.db_file} established.")
        except Error as e:
            print(f"Error: {e}")
        return conn

    def create_table(self):
        create_table_sql = """
          CREATE TABLE IF NOT EXISTS posts (
              id INTEGER PRIMARY KEY,
              url TEXT,
              title TEXT,
              content TEXT,
              date TEXT
          );
          """
        try:
            c = self.conn.cursor()
            c.execute(create_table_sql)
            print("Table created successfully.")
        except Error as e:
            print(f"Error: {e}")

    def insert_data(self, data):
        insert_sql = "INSERT INTO posts (url, title, content, date) VALUES (?, ?, ?, ?)"
        try:
            c = self.conn.cursor()
            c.execute(insert_sql, data)
            self.conn.commit()
            print("Data inserted successfully.")
        except Error as e:
            print(f"Error: {e}")

    def close_connection(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            print("Connection closed.")
