import mysql.connector
import os
import pandas as pd
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
    # interval will be adjusted according to the data
    query = f"""
        SELECT HOUR(FROM_UNIXTIME(created)) AS order_hour,
        COUNT(*) AS order_count
        FROM fct_orders
        WHERE place_id = {merchant_id} AND created >= UNIX_TIMESTAMP(DATE_SUB(NOW(), INTERVAL 1000 DAY))
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
    happy_hour = 3 # default value
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
        T1.`email`
    FROM dim_users AS T1
    INNER JOIN dim_accounts AS T2 ON T1.`id` = T2.`user_id`
    WHERE MONTH(FROM_UNIXTIME(T1.`date_of_birth`)) = MONTH(CURDATE())
    AND DAY(FROM_UNIXTIME(T1.`date_of_birth`)) = DAY(CURDATE())
      AND T1.`date_of_birth` IS NOT NULL
      AND T1.`email_valid` = 1
      AND T2.`place_id` = {merchant_id}
    LIMIT {limit};
    """
    return run_sql(query)

def get_products_by_merchant_id(merchant_id: int):
    conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME
    )
    cursor = conn.cursor()
    query = f'''
        SELECT menu_items.title AS 'product'
        FROM (
            SELECT id , title, place_id
            FROM LLDeloitteAIHackathon.dim_sections  
            WHERE place_id = %s AND type = 'Normal'
        ) sections
        LEFT JOIN LLDeloitteAIHackathon.dim_menu_items menu_items
        ON menu_items.section_id  = sections.id 
        WHERE menu_items.title IS NOT NULL;
    '''
    parameter = (merchant_id, )
    cursor.execute(query, parameter)
    results = cursor.fetchall()
    products = []
    for row in results:
        products.append(row[0])
    cursor.close()
    conn.close()
    return products

def get_best_selling_products_by_merchant_id(merchant_id: int):
    conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME
    )
    cursor = conn.cursor(dictionary=True)
    query = f'''
        SELECT sections.title AS category, menu_items.title AS 'product', menu_items.purchases,  menu_items.price
        FROM (
            SELECT id , title, place_id
            FROM LLDeloitteAIHackathon.dim_sections  
            WHERE place_id = %s AND type = 'Normal'
        ) sections
        LEFT JOIN LLDeloitteAIHackathon.dim_menu_items menu_items
        ON menu_items.section_id  = sections.id 
        WHERE menu_items.title IS NOT NULL
        ORDER BY menu_items.purchases DESC 
        LIMIT 1;
        '''
    parameter = (merchant_id, )
    cursor.execute(query, parameter)
    results = cursor.fetchall()
    products = []
    for row in results:
        products.append(row)
    return products

def get_least_selling_products_by_merchant_id(merchant_id: int):
    conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME
    )
    cursor = conn.cursor(dictionary=True)
    query = f'''
        SELECT sections.title AS category, menu_items.title AS 'product', menu_items.purchases,  menu_items.price
        FROM (
            SELECT id , title, place_id
            FROM LLDeloitteAIHackathon.dim_sections  
            WHERE place_id = %s AND type = 'Normal'
        ) sections
        LEFT JOIN LLDeloitteAIHackathon.dim_menu_items menu_items
        ON menu_items.section_id  = sections.id 
        WHERE menu_items.title IS NOT NULL
        ORDER BY menu_items.purchases ASC 
        LIMIT 1;
        '''
    parameter = (merchant_id, )
    cursor.execute(query, parameter)
    results = cursor.fetchall()
    products = []
    for row in results:
        products.append(row)
    return products

def get_loyal_customers_by_merchant_id(merchant_id: int):
    conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME
    )
    cursor = conn.cursor(dictionary=True)
    query = f'''
        SELECT user_id, count(*) AS orders_number, SUM(fo.total_amount) AS total_spent
        FROM LLDeloitteAIHackathon.fct_orders fo 
        WHERE fo.place_id = %s
        AND status = 'Closed'
        AND user_id != 0
        GROUP BY user_id
        ORDER BY orders_number DESC, total_spent DESC
        LIMIT 5;
    '''
    parameter = (merchant_id, )
    cursor.execute(query, parameter)
    results = cursor.fetchall()
    users = []
    for row in results:
        users.append(row['user_id'])
    return users

def get_loyal_users_order_history(merchant_id):
    conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME
    )
    cursor = conn.cursor(dictionary=True)
    loyal_users = get_loyal_customers_by_merchant_id(merchant_id)
    placeholders = ', '.join(['%s'] * len(loyal_users))
    query = f'''
        SELECT user_id, title, price, quantity, DATE_FORMAT(FROM_UNIXTIME(created), '%Y-%m-%d') AS purchase_date, item_id 
        FROM LLDeloitteAIHackathon.fct_order_items oi
        WHERE user_id  in ({placeholders});
    '''
    cursor.execute(query, loyal_users)
    rows = cursor.fetchall()
    purchase_data = {
            'customer_id' : [],
            'item_id': [],
            'item_name': [],
            'purchase_date': [],
            'quantity': [],
            'price': []
    }
    for row in rows:
        purchase_data['customer_id'].append(row['user_id'])
        purchase_data['item_id'].append(row['item_id'])
        purchase_data['item_name'].append(row['title'])
        purchase_data['purchase_date'].append(row['purchase_date'])
        purchase_data['quantity'].append(row['quantity'])
        purchase_data['price'].append(row['price'])

    purchase_df = pd.DataFrame(purchase_data)
    purchase_df['purchase_date'] = pd.to_datetime(purchase_df['purchase_date'])
    return purchase_df

def get_users_emails(users_id):
    conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME
    )
    cursor = conn.cursor(dictionary=True)
    placeholders = ', '.join(['%s'] * len(users_id))
    query = f'''
        SELECT user_id, email
        FROM LLDeloitteAIHackathon.dim_users
        WHERE user_id in ({placeholders})
        AND email IS NOT NULL;
    '''
    cursor.execute(query, users_id)
    users_emails = {}
    rows = cursor.fetchall()
    for row in rows:
        users_emails[row['user_id']] = row['email'] 
    return users_emails
