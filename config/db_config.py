import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

load_dotenv()

class DBConfig:
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = int(os.getenv('DB_PORT', '3306'))
        self.user = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASSWORD')
        self.database = os.getenv('DB_NAME')

    def get_connection(self):
        try:
            if not self.user or not self.database or self.password is None:
                raise ValueError('Missing DB credentials in .env. Check .env.example and copy from .env.example to .env')
            conn = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                connection_timeout=5
            )
            return conn
        except Error as e:
            raise ConnectionError(f'MySQL connection error: {e}')
        except ValueError as e:
            raise ValueError(f'Configuration error: {e}')

    def test_connection(self):
        try:
            conn = self.get_connection()
            if conn.is_connected():
                conn.close()
                return True, 'Connection successful'
            return False, 'Connection failed'
        except Exception as e:
            return False, str(e)

def get_db_config():
    return DBConfig()
