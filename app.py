from flask import Flask, render_template, redirect, request, session, url_for, flash, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import os
import datetime
import requests

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
albums_schema = mongo.db.albums
album_analytics_schema = mongo.db.AlbumAnalytics
single_analytics_schema = mongo.db.SingleAnalytics
location_analytics_schema = mongo.db.Location
monthly_analytics_schema = mongo.db.MonthlyAnalytics
promotions_schema = mongo.db.promotions  # Collection for promotions
releases_schema = mongo.db.releases      # Collection for releases

# Admin User Creation
admin_user = {
    u"username": u"admin",
    u"password": generate_password_hash(u"admin123@!!"),
    u"role": u"admin"
}

# Insert admin user if not exists
if admin_schema.find_one({u"username": u"admin"}) is None:
    admin_schema.insert_one(admin_user)

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin_user = admin_schema.find_one({u'username': username})
        
        if admin_user and check_password_hash(admin_user[u'password'], password):
            session['admin'] = username
            return redirect('/dashboard')
        else:
            flash(u'Invalid credentials, please try again.', 'error')
            return redirect('/login')
    return render_template('login.html')

# Dashboard Route
# Dashboard Route
@app.route('/dashboard', methods=['GET'])
def dashboard():
    
    total_songs = songs_schema.count()
    total_revenue = sum([order['total'] for order in orders_schema.find()])
    total_orders = orders_schema.count()
    
    # Pagination logic
    current_page = int(request.args.get('page', 1))
    orders_per_page = 10
    total_orders = orders_schema.count_documents({})
    total_pages = (total_orders + orders_per_page - 1) // orders_per_page

    # Fetch the orders for the current page
    orders = list(orders_schema.find().skip((current_page - 1) * orders_per_page).limit(orders_per_page))
    
    orders_with_customers = []  # Initialize the list after fetching orders
    for order in orders:
        user = users_schema.find_one({"email": order['email']})
        order['customer_name'] = user['firstName'] + " " + user['lastName'] if user else 'Unknown'
        orders_with_customers.append(order)

    # Render dashboard with order data
    return render_template('dashboard.html', orders=orders_with_customers, total_pages=total_pages, current_page=current_page, total_songs=total_songs, total_revenue=total_revenue, total_orders=total_orders)

# Orders Route
@app.route('/orders')
def orders():
    if 'admin' not in session:
        return redirect('/login')

    # Fetch all orders with customer details
    orders_data = orders_schema.find()
    orders_with_customers = []
    
    for order in orders_data:
        # Get the corresponding user details based on the email
        user = users_schema.find_one({u"email": order[u'email']})
        order[u'customer_name'] = user[u'firstName'] + u" " + user[u'lastName'] if user else u'Unknown'

        # Ensure the order_id is included
        order[u'order_id'] = str(order[u'_id'])  # Convert the ObjectId to a string for easier handling in HTML

        orders_with_customers.append(order)

    # Pass the modified orders data with customer details to the template
    return render_template('orders.html', orders=orders_with_customers)


# Transactions Route
@app.route('/transactions')
def transactions():
    if 'admin' not in session:
        return redirect('/login')

    transactions = transactions_schema.find()
    return render_template('transactions.html', transactions=transactions)

@app.route('/order/<string:order_id>', methods=['GET'])
def get_order(order_id):
    try:
        # Fetch the order using the correct orders collection
        order = orders_schema.find_one({'_id': ObjectId(order_id)})
        
        if order:
            # Ensure the keys you access exist in the order object
            order_data = {
                'order_id': str(order['_id']),
                'user_email': order.get('email', 'N/A'),  # Use .get to avoid KeyError
                'amount': order.get('total', 0),
                'status': order.get('status', 'Unknown'),
                'order_date': order.get('order_date', 'N/A'),  # Ensure this field exists
                # Add other necessary fields here
            }
            # If you expect a structure with items, wrap order_data in an 'items' key
            return jsonify({'items': [order_data]}), 200  # Note the use of a list for items
        else:
            return jsonify({'error': 'Order not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Function to get JWT token
def get_jwt_token():
    login_url = "https://soundmuve-backend-zrap.onrender.com/api/auth/sign-in"
    payload = {
        u"email": u"latham01@yopmail.com",
        u"password": u"EmekaIwuagwu87**"
    }
    response = requests.post(login_url, json=payload)

    if response.status_code == 200:
        return response.json().get(u'token')  # Adjust based on the actual structure of the response
    else:
        flash(u'Failed to authenticate with the external API.', 'error')
        return None


def get_all_releases(page=1, items_per_page=5):
    """Fetch paginated releases from songs and albums collections."""
    skip = (page - 1) * items_per_page
    releases = []

    # Fetch songs
    songs = list(songs_schema.find().skip(skip).limit(items_per_page))
    for song in songs:
        releases.append({
            'id': str(song['_id']),
            'title': song['song_title'],
            'creative_name': song.get('creative_name', 'Unknown'),
            'type': 'single',
            'status': song.get('status', 'Unknown'),
        })

    # Fetch albums
    albums = list(albums_schema.find().skip(skip).limit(items_per_page))
    for album in albums:
        releases.append({
            'id': str(album['_id']),
            'title': album['album_title'],
            'artist_name': album.get('artist_name', 'Unknown'),
            'type': 'album',
            'status': album.get('status', 'Unknown'),
        })

    # Calculate total releases count
    total_releases = songs_schema.count_documents({}) + albums_schema.count_documents({})
    
    # Return the combined releases and total releases
    return releases, total_releases


# Releases Route
@app.route('/releases', methods=['GET'])
def releases():
    page = int(request.args.get('page', 1))  # Get the current page number from the query string
    items_per_page = 10  # Set the number of items per page

    # Fetch paginated releases and total releases
    releases, total_releases = get_all_releases(page, items_per_page)

    # Calculate total pages
    total_pages = (total_releases + items_per_page - 1) // items_per_page  # Ceiling division

    print("Releases:", releases)  # Debug line
    print("Total Releases:", total_releases)  # Debug line

    # Check if the request is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  
        return jsonify({
            'releases': releases,
            'totalPages': total_pages,
            'totalReleases': total_releases,
        })

    return render_template('releases.html', releases=releases, total_releases=total_releases, current_page=page, total_pages=total_pages)



# Analytics Route
@app.route('/analytics')
def analytics():
    if 'admin' not in session:
        return redirect('/login')
    
    # You can add your logic for analytics here
    return render_template('analytics.html')

@app.route('/release_details/<release_id>', methods=['GET'])
def release_details(release_id):
    # Find the release by ID in both albums and songs
    album = albums_schema.find_one({'_id': ObjectId(release_id)})
    song = songs_schema.find_one({'_id': ObjectId(release_id)})

    if album:
        return jsonify({
            'id': str(album['_id']),
            'title': album['album_title'],
            'artist_name': album.get('artist_name', 'Unknown'),
            'type': 'album',
            'status': album.get('status', 'Unknown'),
        })
    elif song:
        return jsonify({
            'id': str(song['_id']),
            'title': song['song_title'],
            'creative_name': song.get('creative_name', 'Unknown'),
            'type': 'single',
            'status': song.get('status', 'Unknown'),
        })
    else:
        return jsonify({'error': 'Release not found'}), 404


# Route to handle approval submissions
@app.route('/submit_approval/<release_id>', methods=['POST'])
def submit_approval(release_id):
    approval_status = request.json.get('status')
    
    # Check if the release_id belongs to an album or a song
    album = albums_schema.find_one({'_id': ObjectId(release_id)})
    song = songs_schema.find_one({'_id': ObjectId(release_id)})

    if album:
        # Update the status of the album
        albums_schema.update_one({'_id': ObjectId(release_id)}, {'$set': {'status': approval_status}})
    elif song:
        # Update the status of the song
        songs_schema.update_one({'_id': ObjectId(release_id)}, {'$set': {'status': approval_status}})
    else:
        # Return an error if neither album nor song is found
        return jsonify({'error': 'Release not found'}), 404

    # Flash a success message and return a JSON response
    flash('Release status updated successfully.', 'success')
    return jsonify({'status': 'success'})


@app.route('/transaction/<transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    transaction = transactions_schema.find_one({'_id': ObjectId(transaction_id)})
    if transaction:
        # Extract necessary fields (make sure they match your schema)
        response = {
            'userName': transaction['email'],
            'amount': transaction['amount'],
            'status': transaction['status'],
            'narration': transaction['narration']  # Adjust based on your schema
        }
        return jsonify(response)
    return jsonify({'error': 'Transaction not found'}), 404

@app.route('/transaction/<transaction_id>/update', methods=['POST'])
def update_transaction(transaction_id):
    data = request.get_json()
    action = data.get('action')

    # Validate the action
    if action not in ['approve', 'decline']:
        return jsonify({'error': 'Invalid action'}), 400

    # Update the transaction status based on the action
    new_status = 'completed' if action == 'approve' else 'declined'

    # Find and update the transaction
    result = transactions_schema.update_one(
        {'_id': ObjectId(transaction_id)},
        {'$set': {'status': new_status}}
    )

    if result.modified_count == 1:
        return jsonify({'success': True})
    return jsonify({'error': 'Transaction not found or not updated'}), 404


# Logout Route
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
