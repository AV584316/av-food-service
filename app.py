from flask import Flask, render_template_string, request, redirect
from flask_sqlalchemy import SQLAlchemy
import os

# Initialize Flask app
app = Flask(__name__)

# Configure database (SQLite)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'orders.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Define Order model
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    food_item = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    payment_mode = db.Column(db.String(50), nullable=False)

# Create database tables
with app.app_context():
    db.create_all()

# Food Menu (List of Available Dishes)
MENU_ITEMS = [
    {"name": "Paratha", "price": 50},
    {"name": "Sabji", "price": 70},
    {"name": "Roti", "price": 30},
    {"name": "Dal Tadka", "price": 80},
    {"name": "Paneer Butter Masala", "price": 120},
    {"name": "Biryani", "price": 150},
]

# HTML Templates (Rendered in Python)
TEMPLATE_HOME = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AV Food Service</title>
</head>
<body>
    <h1>🍽️ Welcome to AV Food Service</h1>
    <p><a href="/menu">View Menu</a> | <a href="/orders">View Orders</a></p>
</body>
</html>
"""

TEMPLATE_MENU = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Our Menu - AV Food Service</title>
</head>
<body>
    <h1>🍽️ Our Menu</h1>
    <ul>
        {% for item in menu %}
        <li>
            <strong>{{ item.name }}</strong> - ₹{{ item.price }}
            <form action="/order" method="POST">
                <input type="hidden" name="food_item" value="{{ item.name }}">
                <input type="hidden" name="price" value="{{ item.price }}">
                <label for="payment_mode">Payment Mode:</label>
                <select name="payment_mode" required>
                    <option value="UPI">UPI</option>
                    <option value="Cash on Delivery">Cash on Delivery</option>
                </select>
                <button type="submit">Order Now</button>
            </form>
        </li>
        {% endfor %}
    </ul>
    <p><a href="/">Go Back</a></p>
</body>
</html>
"""

TEMPLATE_ORDERS = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Orders - AV Food Service</title>
</head>
<body>
    <h1>📦 Orders</h1>
    {% if orders %}
    <table border="1">
        <tr>
            <th>ID</th>
            <th>Food Item</th>
            <th>Price (₹)</th>
            <th>Payment Mode</th>
        </tr>
        {% for order in orders %}
        <tr>
            <td>{{ order.id }}</td>
            <td>{{ order.food_item }}</td>
            <td>{{ order.price }}</td>
            <td>{{ order.payment_mode }}</td>
        </tr>
        {% endfor %}
    </table>
    {% else %}
    <p>No orders yet.</p>
    {% endif %}
    <p><a href="/">Go Back</a></p>
</body>
</html>
"""

# Routes
@app.route('/')
def home():
    return render_template_string(TEMPLATE_HOME)

@app.route('/menu')
def menu():
    return render_template_string(TEMPLATE_MENU, menu=MENU_ITEMS)

@app.route('/order', methods=['POST'])
def order():
    food_item = request.form.get('food_item')
    price = request.form.get('price')
    payment_mode = request.form.get('payment_mode')

    if food_item and price and payment_mode:
        new_order = Order(food_item=food_item, price=int(price), payment_mode=payment_mode)
        db.session.add(new_order)
        db.session.commit()

    return redirect('/orders')

@app.route('/orders')
def orders():
    all_orders = Order.query.all()
    return render_template_string(TEMPLATE_ORDERS, orders=all_orders)

# Run Flask App
if __name__ == '__main__':
    app.run(debug=True)
