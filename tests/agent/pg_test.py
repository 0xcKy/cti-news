import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

cur = None
conn = None

def get_table_info():
    result = ""
    try:
        with psycopg.connect(
            host = os.getenv('HOSTNAME'),
            dbname = os.getenv('DATABASE_NAME'),
            user = os.getenv('USER_NAME'),
            password = os.getenv('PASSWORD_TEXT'),
            port = os.getenv('PORT_ID')) as conn:
        
            with conn.cursor() as cur:
                
                table = os.getenv('TABLE_NAME')
                cur.execute(f'SELECT * FROM {table}')
                table_info = cur.fetchall()
                for i in table_info:
                    result = result + (f"ID: {str(i[0])}\nSource: {i[1]}\nTitle: {i[2]}\nURL: {i[3]}\nPublished @: {i[4]}\nCollected @: {i[6]}\nContent: {i[5]}\n\n")
            return(result)
    except Exception as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
