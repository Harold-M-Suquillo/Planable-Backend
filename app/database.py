import psycopg2
from psycopg2.extras import RealDictCursor
import time


class Database:
    conn = None
    cursor = None

    def connect(hostI, databaseI, userI, passwordI):
        while True:
            try: 
                Database.conn = psycopg2.connect(host=hostI, database=databaseI, user=userI, password=passwordI, cursor_factory=RealDictCursor)
                Database.cursor = Database.conn.cursor()
                break

            except Exception as error:
                print("Failed to connect: ", error)
                time.sleep(2)
    
    def disconnect():
        Database.cursor.close()
        Database.conn.close()