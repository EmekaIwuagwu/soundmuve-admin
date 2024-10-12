from flask import Flask, render_template, redirect, request, session, url_for, flash, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import os
import datetime
import requests  # Import requests for making HTTP requests

app = Flask(__name__)
app.secret_key = os.urandom(24)

# MongoDB connection
app.config['MONGO_URI'] = "mongodb+srv://migospay:5gi9mrI7ICAE40Jj@cluster0.rp3pump.mongodb.net/techguard?retryWrites=true&w=majority"
mongo = PyMongo(app)

# Schemas (Collections)
admin_schema = mongo.db.admin
transactions_schema = mongo.db.transactions
orders_schema = mongo.db.orders
users_schema = mongo.db.users
songs_schema = mongo.db.songs
album_analytics_schema = mongo.db.AlbumAnalytics
single_analytics_schema = mongo.db.SingleAnalytics
location_analytics_schema = mongo.db.Location
monthly_analytics_schema = mongo.db.MonthlyAnalytics

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
        user = users_schema.find_one({"email": order['email']})
        order['customer_name'] = user['firstName'] + " " + user['lastName'] if user else 'Unknown'
        orders_with_customers.append(order)

    # Calculate total pages
    total_pages = (total_orders + per_page - 1) // per_page  # Ceiling division

    return render_template(
        'dashboard.html', 
        total_songs=total_songs,
        total_revenue=total_revenue,
        total_orders=total_orders,
        orders=orders_with_customers,
        current_page=page,
        total_pages=total_pages
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

# Function to get JWT token
def get_jwt_token():
    login_url = "https://soundmuve-backend-zrap.onrender.com/api/auth/sign-in"
    payload = {
        "email": "latham01@yopmail.com",
        "password": "EmekaIwuagwu87**"
    }
    response = requests.post(login_url, json=payload)

    if response.status_code == 200:
        return response.json().get('token')  # Adjust based on the actual structure of the response
    else:
        flash('Failed to authenticate with the external API.', 'error')
        return None

# Add Single Analytics
@app.route('/add_single_analytics', methods=['POST'])
def add_single_analytics():
    if request.method == 'POST':
        # Extract data from form
        email = request.form['email']
        singles_id = request.form['singles_id']
        single_name = request.form['single_name']
        single_sold = int(request.form['single_sold'])
        stream_apple = int(request.form['stream_apple'])
        stream_spotify = int(request.form['stream_spotify'])
        revenue_apple = float(request.form['revenue_apple'])
        revenue_spotify = float(request.form['revenue_spotify'])
        streamTime_apple = int(request.form['streamTime_apple'])
        streamTime_spotify = int(request.form['streamTime_spotify'])

        # Prepare the data for the HTTP request
        data = {
            "email": email,
            "singles_id": singles_id,
            "single_name": single_name,
            "single_sold": single_sold,
            "stream": {
                "apple": stream_apple,
                "spotify": stream_spotify
            },
            "revenue": {
                "apple": revenue_apple,
                "spotify": revenue_spotify
            },
            "streamTime": {
                "apple": streamTime_apple,
                "spotify": streamTime_spotify
            },
            "created_at": datetime.datetime.utcnow().isoformat()  # Using isoformat for date
        }

        # Get JWT token
        token = get_jwt_token()
        if token is None:
            return redirect('/analytics')

        # Make the HTTP request to the external API
        response = requests.post(
            "https://soundmuve-backend-zrap.onrender.com/api/analyticsManager/single-analytics",
            json=data,
            headers={"Authorization": "Bearer {}".format(token)}  # Use Bearer token for authentication
        )

        # Check if the request was successful
        if response.status_code == 201:  # HTTP 201 Created
            flash('Single analytics added successfully!', 'success')
        else:
            flash('Failed to add single analytics. Error: {}'.format(response.text), 'error')
        
        return redirect('/analytics')

# Add Album Analytics
@app.route('/add_album_analytics', methods=['POST'])
def add_album_analytics():
    if request.method == 'POST':
        # Extract data from form
        email = request.form['email']
        album_name = request.form['album_name']
        song_title = request.form['song_title']
        album_id = request.form['album_id']
        album_sold = int(request.form['album_sold'])
        stream_apple = int(request.form['stream_apple'])
        stream_spotify = int(request.form['stream_spotify'])
        revenue_apple = float(request.form['revenue_apple'])
        revenue_spotify = float(request.form['revenue_spotify'])
        streamTime_apple = int(request.form['streamTime_apple'])
        streamTime_spotify = int(request.form['streamTime_spotify'])

        # Prepare the data for the HTTP request
        data = {
            "email": email,
            "album_name": album_name,
            "song_title": song_title,
            "album_id": album_id,
            "album_sold": album_sold,
            "stream": {
                "apple": stream_apple,
                "spotify": stream_spotify
            },
            "revenue": {
                "apple": revenue_apple,
                "spotify": revenue_spotify
            },
            "streamTime": {
                "apple": streamTime_apple,
                "spotify": streamTime_spotify
            },
            "created_at": datetime.datetime.utcnow().isoformat()  # Using isoformat for date
        }

        # Get JWT token
        token = get_jwt_token()
        if token is None:
            return redirect('/analytics')

        # Make the HTTP request to the external API
        response = requests.post(
            "https://soundmuve-backend-zrap.onrender.com/api/analyticsManager/album-analytics",
            json=data,
            headers={"Authorization": "Bearer {}".format(token)}  # Use Bearer token for authentication
        )

        # Check if the request was successful
        if response.status_code == 201:  # HTTP 201 Created
            flash('Album analytics added successfully!', 'success')
        else:
            flash('Failed to add album analytics. Error: {}'.format(response.text), 'error')
        
        return redirect('/analytics')

# Add Location Analytics
@app.route('/add_location_analytics', methods=['POST'])
def add_location_analytics():
    if request.method == 'POST':
        data = {
            "email": request.form['email'],
            "location": request.form['location'],
            "album_sold": int(request.form['album_sold']),
            "single_sold": int(request.form['single_sold']),
            "streams": int(request.form['streams']),
            "total": float(request.form['total']),
            "created_at": datetime.datetime.utcnow().isoformat()  # Using isoformat for date
        }

        try:
            result = mongo.db.Location.insert_one(data)
            if result.inserted_id:
                flash('Location analytics added successfully!', 'success')
            else:
                flash('Failed to add location analytics. Please try again.', 'error')
        except Exception as e:
            flash('Error occurred: {}'.format(str(e)), 'error')

        return redirect('/analytics')

# Add Monthly Analytics
@app.route('/add_monthly_analytics', methods=['POST'])
def add_monthly_analytics():
    if request.method == 'POST':
        data = {
            "email": request.form['email'],
            "sales_period": request.form['sales_period'],
            "album_sold": int(request.form['album_sold']),
            "single_sold": int(request.form['single_sold']),
            "streams": int(request.form['streams']),
            "total": float(request.form['total']),
            "created_at": datetime.datetime.utcnow().isoformat()  # Using isoformat for date
        }

        try:
            result = mongo.db.MonthlyAnalytics.insert_one(data)
            if result.inserted_id:
                flash('Monthly analytics added successfully!', 'success')
            else:
                flash('Failed to add monthly analytics. Please try again.', 'error')
        except Exception as e:
            flash('Error occurred: {}'.format(str(e)), 'error')

        return redirect('/analytics')

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

# Analytics Route
@app.route('/analytics')
def analytics():
    if 'admin' not in session:
        return redirect('/login')

    analytics_data = {
        "album": mongo.db.AlbumAnalytics.find(),
        "single": mongo.db.SingleAnalytics.find(),
        "location": mongo.db.Location.find(),
        "monthly": mongo.db.MonthlyAnalytics.find()
    }
    return render_template('analytics.html', analytics=analytics_data)

@app.route('/logout')
def logout():
    session.pop('user', None)  # Remove user session
    return redirect(url_for('login')) 

if __name__ == '__main__':
    # Make sure the app runs on 0.0.0.0 and listens on the specified port
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=True)
