from flask import Flask, jsonify, render_template, request, redirect, url_for
import os
import pymysql
from datetime import datetime

app = Flask(__name__)

DB_HOST = os.getenv("DB_HOST", "db")
DB_USER = os.getenv("DB_USER", "pos_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "StrongPassword123")
DB_NAME = os.getenv("DB_NAME", "pos_db")

def get_db_connection():
    connection = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection

def initialize_database():
    """Initialize the database with the required tables."""
    conn = get_db_connection()
    with conn.cursor() as cursor:
        # Create the products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE
            )
        """)

        # Create the purchases table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS purchases (
                id INT AUTO_INCREMENT PRIMARY KEY,
                product_id INT NOT NULL,
                purchase_date DATETIME NOT NULL,
                purchase_price DECIMAL(10, 2) NOT NULL,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)

        # Create the sales table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INT AUTO_INCREMENT PRIMARY KEY,
                product_id INT NOT NULL,
                quantity INT NOT NULL,
                selling_price DECIMAL(10, 2) NOT NULL,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)

        # Add a demo product if the products table is empty
        cursor.execute("SELECT COUNT(*) AS count FROM products")
        product_count = cursor.fetchone()['count']
        if product_count == 0:
            cursor.execute("INSERT INTO products (name) VALUES ('Demo Product')")

        # Add a demo sale if the sales table is empty
        cursor.execute("SELECT COUNT(*) AS count FROM sales")
        sale_count = cursor.fetchone()['count']
        if sale_count == 0:
            cursor.execute("SELECT id FROM products WHERE name = 'Demo Product'")
            demo_product_id = cursor.fetchone()['id']
            cursor.execute("""
                INSERT INTO sales (product_id, quantity, selling_price)
                VALUES (%s, %s, %s)
            """, (demo_product_id, 2, 19.99))

        conn.commit()
    conn.close()

@app.route('/')
def home():
    """Render the home page with products, purchases, and sales tables."""
    conn = get_db_connection()
    with conn.cursor() as cursor:
        # Fetch products
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()

        # Fetch purchases
        cursor.execute("""
            SELECT purchases.id, products.name AS product_name, purchases.purchase_date, purchases.purchase_price
            FROM purchases
            JOIN products ON purchases.product_id = products.id
        """)
        purchases = cursor.fetchall()

        # Fetch sales
        cursor.execute("""
            SELECT sales.id, products.name AS product_name, sales.quantity, sales.selling_price
            FROM sales
            JOIN products ON sales.product_id = products.id
        """)
        sales = cursor.fetchall()

    conn.close()
    return render_template('index.html', products=products, purchases=purchases, sales=sales)

@app.route('/add_sale', methods=['POST'])
def add_sale():
    """Add a sale to the database."""
    product_id = request.form['product_id']
    quantity = request.form['quantity']
    selling_price = request.form['selling_price']
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO sales (product_id, quantity, selling_price)
            VALUES (%s, %s, %s)
        """, (product_id, quantity, selling_price))
        conn.commit()
    conn.close()
    return redirect(url_for('home'))

if __name__ == '__main__':
    initialize_database()
    app.run(host='0.0.0.0', port=5000, debug=True)
