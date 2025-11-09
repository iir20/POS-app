import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('pos_system.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            purchase_price REAL NOT NULL,
            sale_price REAL NOT NULL,
            stock_quantity INTEGER NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            total_due REAL DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            items_sold TEXT NOT NULL,
            total_amount REAL NOT NULL,
            timestamp TEXT NOT NULL,
            customer_id INTEGER,
            status TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            timestamp TEXT NOT NULL
        )
    ''')
    
    cursor.execute('SELECT COUNT(*) FROM products')
    if cursor.fetchone()[0] == 0:
        sample_products = [
            ('Rice 1kg', 40, 50, 100),
            ('Lentils 1kg', 80, 100, 50),
            ('Oil 1L', 120, 150, 30),
            ('Sugar 1kg', 45, 60, 80),
            ('Tea 200g', 80, 100, 40),
            ('Salt 1kg', 20, 25, 60),
            ('Flour 1kg', 35, 45, 70),
            ('Milk 1L', 50, 65, 25),
            ('Eggs (dozen)', 120, 140, 15),
            ('Bread', 30, 40, 45),
            ('Biscuits', 20, 30, 90),
            ('Soap', 25, 35, 55),
            ('Toothpaste', 80, 100, 20),
            ('Shampoo', 150, 180, 12),
            ('Detergent 500g', 60, 80, 35),
            ('Matches', 5, 8, 100),
            ('Candles', 10, 15, 60),
            ('Notebook', 25, 35, 40),
            ('Pen', 10, 15, 75),
            ('Chips', 20, 30, 50)
        ]
        cursor.executemany('INSERT INTO products (name, purchase_price, sale_price, stock_quantity) VALUES (?, ?, ?, ?)', sample_products)
    
    cursor.execute('SELECT COUNT(*) FROM customers')
    if cursor.fetchone()[0] == 0:
        sample_customers = [
            ('Karim Ahmed', '01711111111', 0),
            ('Fatima Begum', '01722222222', 0),
            ('Rahim Khan', '01733333333', 0),
            ('Ayesha Siddiqua', '01744444444', 0),
            ('Jamal Uddin', '01755555555', 0)
        ]
        cursor.executemany('INSERT INTO customers (name, phone, total_due) VALUES (?, ?, ?)', sample_customers)
    
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('pos_system.db')
    conn.row_factory = sqlite3.Row
    return conn

def update_stock(items_sold):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for item in items_sold:
        product_id = item['id']
        quantity = item['quantity']
        
        cursor.execute('UPDATE products SET stock_quantity = stock_quantity - ? WHERE id = ?', (quantity, product_id))
        
        cursor.execute('SELECT name, stock_quantity FROM products WHERE id = ?', (product_id,))
        product = cursor.fetchone()
        
        if product and product['stock_quantity'] < 5:
            print(f"⚠️ LOW STOCK ALERT: {product['name']} - Only {product['stock_quantity']} units left!")
    
    conn.commit()
    conn.close()
