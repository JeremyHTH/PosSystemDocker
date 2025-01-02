from flask import Flask, jsonify, render_template, request, redirect, url_for
import os
import pymysql
from datetime import datetime, timedelta

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
                purchase_date DATE NOT NULL,
                purchase_price DECIMAL(10, 2) NOT NULL,
                quantity INT NOT NULL,
                entry_date DATE NOT NULL, 
                entry_time TIME NOT NULL, 
                processed BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)

        # Create the sales table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INT AUTO_INCREMENT PRIMARY KEY,
                product_id INT NOT NULL,
                sales_date DATE NOT NULL,
                selling_price DECIMAL(10, 2) NOT NULL,
                quantity INT NOT NULL,
                entry_date DATE NOT NULL, 
                entry_time TIME NOT NULL, 
                processed BOOLEAN DEFAULT FALSE,
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
                INSERT INTO sales (product_id, quantity, selling_price, sales_date, entry_date, entry_time)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (demo_product_id, 2, 19.99, datetime.now(), datetime.now().date(), datetime.now().time()))

        conn.commit()
    conn.close()

@app.route('/')
def home():
    """Render the home page with products, purchases, and sales tables."""
    conn = get_db_connection()
    with conn.cursor() as cursor:
        # Fetch products
        cursor.execute("SELECT * FROM products ORDER BY products.id")
        products = cursor.fetchall()

        # Fetch purchases
        cursor.execute("""
            SELECT purchases.id, products.name AS product_name, purchases.purchase_date, purchases.purchase_price, purchases.quantity, purchases.entry_date, purchases.entry_time,  purchases.processed
            FROM purchases
            JOIN products ON purchases.product_id = products.id
            ORDER BY purchases.purchase_date
        """)
        purchases = cursor.fetchall()
 
        # Fetch sales
        cursor.execute("""
            SELECT sales.id, products.name AS product_name, sales.sales_date, sales.quantity, sales.selling_price, sales.entry_date, sales.entry_time, sales.processed
            FROM sales
            JOIN products ON sales.product_id = products.id
            ORDER BY sales.sales_date
        """)
        sales = cursor.fetchall()

    conn.close()
    
    return render_template('Home.html', products=products, purchases=purchases, sales=sales)

@app.route('/add_product', methods=['POST'])
def add_product():
    """Add a product to the database."""
    name = request.form['name']  # Fetch the product name from the form
    conn = get_db_connection()
    with conn.cursor() as cursor:
        try:
            cursor.execute("INSERT INTO products (name) VALUES (%s)", (name,))
            conn.commit()
        except pymysql.MySQLError as e:
            return f"Error: {e}", 400  # Handle errors gracefully
    conn.close()
    return redirect(url_for('home'))

@app.route('/add_purchase', methods=['POST'])
def add_purchase():
    """Add a purchase to the database."""
    try:
        product_id = int(request.form['purchase_product_id'])  # Get Product ID from the form
        purchase_price = float(request.form['purchase_price'])  # Get Purchase Price
        purchase_date = request.form['purchase_date']  # Get Purchase Date
        quantity = int(request.form['purchase_quantity'])
        processed = request.form.get('processed') == 'on' 
        
        entry_datetime = datetime.now()
        entry_date = entry_datetime.date()
        entry_time = entry_datetime.time()

        print(product_id, purchase_price)
        # Ensure product_id is non-negative
        if product_id < 0:
            return "Error: Product ID must be non-negative.", 400

        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO purchases (product_id, purchase_date, purchase_price, quantity, entry_date, entry_time, processed)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (product_id, purchase_date, purchase_price, quantity, entry_date, entry_time, processed))
            conn.commit()
        conn.close()
        return redirect(url_for('home'))
    except Exception as e:
        return f"Error: {str(e)}", 400  # Handle unexpected errors gracefully


@app.route('/add_sale', methods=['POST'])
def add_sale():
    """Add a sale to the database."""
    try:
        product_id = int(request.form['sale_product_id'])  # Product ID
        quantity = int(request.form['sale_quantity'])  # Quantity
        selling_price = float(request.form['selling_price'])  # Selling Price
        sales_date = request.form['sales_date']  # Sales Date
        processed = request.form.get('processed') == 'on' 

        entry_datetime = datetime.now()
        entry_date = entry_datetime.date()
        entry_time = entry_datetime.time()

        # Validate input
        if product_id < 0 or quantity < 0:
            return "Error: Product ID and Quantity must be non-negative.", 400

        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO sales (product_id, quantity, selling_price, sales_date, entry_date, entry_time, processed)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (product_id, quantity, selling_price, sales_date, entry_date, entry_time, processed))
            conn.commit()
        conn.close()
        return redirect(url_for('home'))
    except Exception as e:
        return f"Error: {str(e)}", 400
    
@app.route('/update_processed', methods=['POST'])
def update_processed():
    data = request.json
    record_type = data['type']
    record_id = data['id']
    processed_status = data['processed']
    print(record_type, record_id, processed_status)

    table = 'purchases' if record_type == 'purchase' else 'sales'

    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute(f"""
            UPDATE {table}
            SET processed = %s
            WHERE id = %s
        """, (processed_status, record_id)) 
        conn.commit()
    conn.close()
    return jsonify({'message': 'Processed status updated successfully'})

@app.route('/Debug', methods=['POST', 'GET'])
def Debug():
    def serialize_data(data):
        """
        Converts non-serializable fields like timedelta to strings.
        """
        for record in data:
            for key, value in record.items():
                if isinstance(value, timedelta):
                    record[key] = str(value)  # Convert timedelta to string
        return data

    results = {}
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM products")
        results['products'] = cursor.fetchall()  # Add products to the results

        cursor.execute("SELECT * FROM purchases")
        purchases = cursor.fetchall()
        results['purchases'] = serialize_data(purchases)  # Serialize purchases

        cursor.execute("SELECT * FROM sales")
        sales = cursor.fetchall()
        results['sales'] = serialize_data(sales)  # Serialize sales

    conn.close()
    return jsonify(results)  # Return the consolidated results as JSON
if __name__ == '__main__':
    initialize_database()
    app.run(host='0.0.0.0', port=5000, debug=True)
