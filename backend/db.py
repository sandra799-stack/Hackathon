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

def run_sql(query: str):
    conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows

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

def get_birthdays_last_month_by_merchant(merchant_id: int, limit: int = 5):
    query = f"""
    SELECT 
        T1.`first_name`,
        T1.`last_name`,
        T1.`email_valid`,
        T1.`email`,
        T2.`place_id` AS merchant_id
    FROM dim_users AS T1
    INNER JOIN dim_accounts AS T2 ON T1.`id` = T2.`user_id`
    WHERE MONTH(FROM_UNIXTIME(T1.`date_of_birth`)) = MONTH(CURDATE() - INTERVAL 1 MONTH)
      AND T1.`date_of_birth` IS NOT NULL
      AND T1.`email_valid` = 1
      AND T2.`place_id` = {merchant_id}
    LIMIT {limit};
    """
    return run_sql(query)