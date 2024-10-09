from flask import Flask, render_template, redirect, request, session, url_for, flash, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# MongoDB connection
app.config['MONGO_URI'] = "mongodb+srv://migospay:5gi9mrI7ICAE40Jj@cluster0.rp3pump.mongodb.net/techguard"
mongo = PyMongo(app)

# Schemas
admin_schema = mongo.db.admin
transactions_schema = mongo.db.transactions
orders_schema = mongo.db.orders
users_schema = mongo.db.users
songs_schema = mongo.db.songs
analytics_schema = mongo.db.albumAnalytics

# Admin User Creation
admin_user = {
    "username": "admin",
    "password": generate_password_hash("admin123@!!"),
    "role": "admin"
}

# Insert admin user if not exists
if admin_schema.find_one({"username": "admin"}) is None:
    admin_schema.insert_one(admin_user)

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin_user = admin_schema.find_one({'username': username})
        
        if admin_user and check_password_hash(admin_user['password'], password):
            session['admin'] = username
            return redirect('/dashboard')
        else:
            flash('Invalid credentials, please try again.', 'error')
            return redirect('/login')
    return render_template('login.html')

# Dashboard Route
@app.route('/dashboard')
def dashboard():
    if 'admin' not in session:
        return redirect('/login')

    total_songs = songs_schema.count()
    total_revenue = sum([order['total'] for order in orders_schema.find()])
    total_orders = orders_schema.count()

    # Paginated orders
    page = int(request.args.get('page', 1))
    per_page = 10
    orders = orders_schema.find().skip((page - 1) * per_page).limit(per_page)

    orders_with_customers = []
    for order in orders:
        # Fetch the customer email by querying the Users schema
        user = users_schema.find_one({"email": order['email']})
        order['customer_name'] = user['firstName'] + " " + user['lastName'] if user else 'Unknown'
        orders_with_customers.append(order)

    return render_template(
        'dashboard.html', 
        total_songs=total_songs,
        total_revenue=total_revenue,
        total_orders=total_orders,
        orders=orders_with_customers
    )

@app.route('/orders')
def orders():
    if 'admin' not in session:
        return redirect('/login')

    # Fetch all orders with customer details
    orders_data = orders_schema.find()
    orders_with_customers = []
    for order in orders_data:
        user = users_schema.find_one({"email": order['email']})
        order['customer_name'] = user['firstName'] + " " + user['lastName'] if user else 'Unknown'
        orders_with_customers.append(order)

    return render_template('orders.html', orders=orders_with_customers)


# Get Order Details (for Modal)
@app.route('/order/<id>', methods=['GET'])
def get_order(id):
    try:
        order = orders_schema.find_one({"_id": ObjectId(id)})
        if order:
            items = [{
                'id': str(item['_id']),
                'name': item['name'],
                'price': item['price'],
                'type': item['type']
            } for item in order['items']]

            return jsonify({
                "id": str(order['_id']),
                "customer_name": order['email'],
                "amount": order['total'],
                "status": order['paymentStatus'],
                "items": items
            })
        return jsonify({"error": "Order not found"}), 404
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

# Transactions Route
@app.route('/transactions')
def transactions():
    if 'admin' not in session:
        return redirect('/login')
    
    transactions_data = transactions_schema.find()
    return render_template('transactions.html', transactions=transactions_data)

# Get Transaction Details (for Modal)
@app.route('/transaction/<id>', methods=['GET'])
def get_transaction(id):
    transaction = transactions_schema.find_one({"_id": ObjectId(id)})
    if transaction:
        return jsonify({
            "id": str(transaction['_id']),
            "email": transaction['email'],
            "narration": transaction['narration'],
            "credit": transaction['credit'],
            "debit": transaction['debit'],
            "amount": transaction['amount'],
            "currency": transaction['currency'],
            "status": transaction['status'],
            "balance": transaction['balance']
        })
    return jsonify({"error": "Transaction not found"}), 404

# Approve or Decline Transaction
@app.route('/transaction/<id>/update', methods=['POST'])
def update_transaction(id):
    action = request.form.get('action')
    if action not in ['approve', 'decline']:
        return jsonify({"error": "Invalid action"}), 400
    
    # Update the transaction status
    transactions_schema.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"status": "approved" if action == 'approve' else 'declined'}}
    )
    return jsonify({"success": True})

@app.route('/analytics')
def analytics():
    if 'admin' not in session:
        return redirect('/login')

    analytics_data = analytics_schema.find()
    return render_template('analytics.html', analytics=analytics_data)

@app.route('/logout')
def logout():
    session.pop('user', None)  # Remove user session
    return redirect(url_for('login')) 

if __name__ == '__main__':
    # Make sure the app runs on 0.0.0.0 and listens on the specified port
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=True)
