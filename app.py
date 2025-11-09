from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from database import init_db, get_db_connection
from datetime import datetime
import json
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')
CORS(app)

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/due-list')
def due_list():
    return render_template('due_list.html')

@app.route('/expenses')
def expenses():
    return render_template('expenses.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/inventory')
def inventory():
    return render_template('inventory.html')

@app.route('/api/products', methods=['GET'])
def get_products():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products ORDER BY name').fetchall()
    conn.close()
    
    products_list = []
    for product in products:
        products_list.append({
            'id': product['id'],
            'name': product['name'],
            'purchase_price': product['purchase_price'],
            'sale_price': product['sale_price'],
            'stock_quantity': product['stock_quantity']
        })
    
    return jsonify(products_list)

@app.route('/api/add_product', methods=['POST'])
def add_product():
    data = request.json
    
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400
    
    name = data.get('name', '').strip()
    purchase_price = data.get('purchase_price', 0)
    sale_price = data.get('sale_price', 0)
    stock_quantity = data.get('stock_quantity', 0)
    
    if not name:
        return jsonify({'success': False, 'message': 'Product name is required'}), 400
    
    try:
        purchase_price = float(purchase_price)
        sale_price = float(sale_price)
        stock_quantity = int(stock_quantity)
        
        if purchase_price < 0:
            return jsonify({'success': False, 'message': 'Purchase price cannot be negative'}), 400
        if sale_price < 0:
            return jsonify({'success': False, 'message': 'Sale price cannot be negative'}), 400
        if stock_quantity < 0:
            return jsonify({'success': False, 'message': 'Stock quantity cannot be negative'}), 400
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Invalid price or quantity values'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO products (name, purchase_price, sale_price, stock_quantity) VALUES (?, ?, ?, ?)',
            (name, purchase_price, sale_price, stock_quantity)
        )
        conn.commit()
        product_id = cursor.lastrowid
        conn.close()
        
        return jsonify({'success': True, 'id': product_id, 'message': 'Product added successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500

@app.route('/api/update_product/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.json
    
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400
    
    name = data.get('name', '').strip()
    purchase_price = data.get('purchase_price')
    sale_price = data.get('sale_price')
    stock_quantity = data.get('stock_quantity')
    
    if not name:
        return jsonify({'success': False, 'message': 'Product name is required'}), 400
    
    try:
        purchase_price = float(purchase_price)
        sale_price = float(sale_price)
        stock_quantity = int(stock_quantity)
        
        if purchase_price < 0:
            return jsonify({'success': False, 'message': 'Purchase price cannot be negative'}), 400
        if sale_price < 0:
            return jsonify({'success': False, 'message': 'Sale price cannot be negative'}), 400
        if stock_quantity < 0:
            return jsonify({'success': False, 'message': 'Stock quantity cannot be negative'}), 400
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Invalid price or quantity values'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM products WHERE id = ?', (product_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'message': 'Product not found'}), 404
        
        cursor.execute(
            'UPDATE products SET name = ?, purchase_price = ?, sale_price = ?, stock_quantity = ? WHERE id = ?',
            (name, purchase_price, sale_price, stock_quantity, product_id)
        )
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Product updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500

@app.route('/api/add_sale', methods=['POST'])
def add_sale():
    data = request.json
    
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400
    
    items_sold = data.get('items', [])
    total_amount = data.get('total_amount', 0)
    status = data.get('status', 'cash')
    customer_id = data.get('customer_id')
    
    if not items_sold:
        return jsonify({'success': False, 'message': 'No items in cart'}), 400
    
    if total_amount <= 0:
        return jsonify({'success': False, 'message': 'Invalid total amount'}), 400
    
    if status == 'due' and not customer_id:
        return jsonify({'success': False, 'message': 'Customer ID required for due sales'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        for item in items_sold:
            if not isinstance(item.get('id'), int) or not isinstance(item.get('quantity'), int):
                conn.close()
                return jsonify({'success': False, 'message': 'Invalid item data'}), 400
            
            if item.get('quantity', 0) <= 0:
                conn.close()
                return jsonify({'success': False, 'message': f'Invalid quantity for item'}), 400
            
            product = cursor.execute('SELECT stock_quantity, name FROM products WHERE id = ?', (item['id'],)).fetchone()
            
            if not product:
                conn.close()
                return jsonify({'success': False, 'message': f'Product with ID {item["id"]} not found'}), 400
            
            if product['stock_quantity'] < item['quantity']:
                conn.close()
                return jsonify({'success': False, 'message': f'Insufficient stock for {product["name"]}. Available: {product["stock_quantity"]}'}), 400
        
        if status == 'due':
            customer = cursor.execute('SELECT id FROM customers WHERE id = ?', (customer_id,)).fetchone()
            if not customer:
                conn.close()
                return jsonify({'success': False, 'message': 'Customer not found'}), 400
        
        timestamp = datetime.now().isoformat()
        items_json = json.dumps(items_sold)
        
        cursor.execute(
            'INSERT INTO sales (items_sold, total_amount, timestamp, customer_id, status) VALUES (?, ?, ?, ?, ?)',
            (items_json, total_amount, timestamp, customer_id, status)
        )
        
        if status == 'due':
            cursor.execute(
                'UPDATE customers SET total_due = total_due + ? WHERE id = ?',
                (total_amount, customer_id)
            )
        
        for item in items_sold:
            cursor.execute('UPDATE products SET stock_quantity = stock_quantity - ? WHERE id = ?', (item['quantity'], item['id']))
            
            updated_product = cursor.execute('SELECT name, stock_quantity FROM products WHERE id = ?', (item['id'],)).fetchone()
            
            if updated_product and updated_product['stock_quantity'] < 5:
                print(f"⚠️ LOW STOCK ALERT: {updated_product['name']} - Only {updated_product['stock_quantity']} units left!")
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Sale recorded successfully'})
    
    except Exception as e:
        conn.rollback()
        conn.close()
        print(f"Error in add_sale: {str(e)}")
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500

@app.route('/api/customers', methods=['GET'])
def get_customers():
    conn = get_db_connection()
    customers = conn.execute('SELECT * FROM customers ORDER BY name').fetchall()
    conn.close()
    
    customers_list = []
    for customer in customers:
        customers_list.append({
            'id': customer['id'],
            'name': customer['name'],
            'phone': customer['phone'],
            'total_due': customer['total_due']
        })
    
    return jsonify(customers_list)

@app.route('/api/add_customer', methods=['POST'])
def add_customer():
    data = request.json
    
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400
    
    name = data.get('name', '').strip()
    phone = data.get('phone', '').strip()
    
    if not name:
        return jsonify({'success': False, 'message': 'Customer name is required'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO customers (name, phone, total_due) VALUES (?, ?, 0)', (name, phone))
        conn.commit()
        customer_id = cursor.lastrowid
        conn.close()
        
        return jsonify({'success': True, 'id': customer_id})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500

@app.route('/api/add_expense', methods=['POST'])
def add_expense():
    data = request.json
    
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400
    
    category = data.get('category', '').strip()
    amount = data.get('amount', 0)
    description = data.get('description', '').strip()
    
    if not category:
        return jsonify({'success': False, 'message': 'Category is required'}), 400
    
    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({'success': False, 'message': 'Amount must be greater than 0'}), 400
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Invalid amount'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        timestamp = datetime.now().isoformat()
        cursor.execute(
            'INSERT INTO expenses (category, amount, description, timestamp) VALUES (?, ?, ?, ?)',
            (category, amount, description, timestamp)
        )
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Expense recorded successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500

@app.route('/api/expenses', methods=['GET'])
def get_expenses():
    conn = get_db_connection()
    expenses = conn.execute('SELECT * FROM expenses ORDER BY timestamp DESC').fetchall()
    conn.close()
    
    expenses_list = []
    for expense in expenses:
        expenses_list.append({
            'id': expense['id'],
            'category': expense['category'],
            'amount': expense['amount'],
            'description': expense['description'],
            'timestamp': expense['timestamp']
        })
    
    return jsonify(expenses_list)

@app.route('/api/dashboard_data', methods=['GET'])
def get_dashboard_data():
    conn = get_db_connection()
    
    today = datetime.now().date().isoformat()
    
    total_sales_today = conn.execute(
        "SELECT COALESCE(SUM(total_amount), 0) as total FROM sales WHERE date(timestamp) = ?",
        (today,)
    ).fetchone()['total']
    
    total_expenses_today = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) as total FROM expenses WHERE date(timestamp) = ?",
        (today,)
    ).fetchone()['total']
    
    total_due = conn.execute(
        "SELECT COALESCE(SUM(total_due), 0) as total FROM customers"
    ).fetchone()['total']
    
    low_stock_products = conn.execute(
        "SELECT * FROM products WHERE stock_quantity < 5 ORDER BY stock_quantity ASC"
    ).fetchall()
    
    conn.close()
    
    low_stock_list = []
    for product in low_stock_products:
        low_stock_list.append({
            'id': product['id'],
            'name': product['name'],
            'stock_quantity': product['stock_quantity']
        })
    
    return jsonify({
        'total_sales_today': total_sales_today,
        'total_expenses_today': total_expenses_today,
        'total_due': total_due,
        'low_stock_products': low_stock_list
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
