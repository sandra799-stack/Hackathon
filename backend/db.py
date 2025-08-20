import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()

# MySQL connection details
DB_HOST = os.getenv("DB_HOST") 
DB_PORT = os.getenv("DB_PORT")             
DB_USER = os.getenv("DB_USER") 
DB_PASS = os.getenv("DB_PASS") 
DB_NAME = os.getenv("DB_NAME")

def get_connection():
    try:
        # Connect to MySQL through the SSH tunnel
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME
        )

        cursor = conn.cursor()
        return cursor

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def get_hour_with_least_orders(merchant_id):
    query = f"""
        SELECT HOUR(FROM_UNIXTIME(created)) AS order_hour,
        COUNT(*) AS order_count
        FROM fct_orders
        WHERE place_id = {merchant_id} AND created >= UNIX_TIMESTAMP(DATE_SUB(NOW(), INTERVAL 7 DAY))
        group by order_hour
        order by order_count ASC
        limit 1
    """
    conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME
        )

    cursor = conn.cursor()
    if cursor is None:
        return
    cursor.execute(query)
    for row in cursor.fetchall():
        happy_hour = row[0]
    return happy_hour

def notify_user():
    pass

def get_users_email_by_merchant_id(merchant_id):
    users_email = []
    query = f'''
        SELECT email
        FROM (  SELECT user_id
                FROM fct_orders  
                WHERE place_id = {merchant_id}
            ) orders
        INNER JOIN dim_users users
        ON users.user_id  = orders.user_id
    '''
    conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME
        )

    cursor = conn.cursor()
    if cursor is None:
        return
    cursor.execute(query)
    for row in cursor.fetchall():
        users_email.append(row[0])

    return users_email