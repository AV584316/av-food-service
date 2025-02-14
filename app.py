from flask import Flask, render_template_string, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import os

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "supersecretkey"  # Required for session storage

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
    quantity = db.Column(db.Integer, nullable=False)
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
            <form action="/add_to_cart" method="POST">
                <input type="hidden" name="food_item" value="{{ item.name }}">
                <input type="hidden" name="price" value="{{ item.price }}">
                <label for="quantity">Quantity:</label>
                <input type="number" name="quantity" value="1" min="1" required>
                <button type="submit">Add to Cart</button>
            </form>
        </li>
        {% endfor %}
    </ul>
    <p><a href="/cart">🛒 View Cart</a></p>
    <p><a href="/">Go Back</a></p>
</body>
</html>
"""

TEMPLATE_CART = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Shopping Cart</title>
</head>
<body>
    <h1>🛒 Your Cart</h1>
    {% if cart %}
    <table border="1">
        <tr>
            <th>Food Item</th>
            <th>Quantity</th>
            <th>Price (₹)</th>
        </tr>
        {% for item in cart %}
        <tr>
            <td>{{ item.food_item }}</td>
            <td>{{ item.quantity }}</td>
            <td>₹{{ item.total_price }}</td>
        </tr>
        {% endfor %}
    </table>
    <p><strong>Total Price: ₹{{ total_price }}</strong></p>
    <form action="/checkout" method="POST">
        <label for="payment_mode">Payment Mode:</label>
        <select name="payment_mode" required>
            <option value="UPI">UPI</option>
            <option value="Cash on Delivery">Cash on Delivery</option>
        </select>
        <button type="submit">Proceed to Checkout</button>
    </form>
    {% else %}
    <p>Your cart is empty.</p>
    {% endif %}
    <p><a href="/menu">← Back to Menu</a></p>
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
            <th>Quantity</th>
            <th>Price (₹)</th>
            <th>Payment Mode</th>
        </tr>
        {% for order in orders %}
        <tr>
            <td>{{ order.id }}</td>
            <td>{{ order.food_item }}</td>
            <td>{{ order.quantity }}</td>
            <td>₹{{ order.price }}</td>
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

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    food_item = request.form.get('food_item')
    quantity = int(request.form.get('quantity'))
    price = int(request.form.get('price'))

    if "cart" not in session:
        session["cart"] = []

    session["cart"].append({"food_item": food_item, "quantity": quantity, "total_price": quantity * price})
    session.modified = True

    return redirect('/cart')

@app.route('/cart')
def cart():
    cart_items = session.get("cart", [])
    total_price = sum(item["total_price"] for item in cart_items)
    return render_template_string(TEMPLATE_CART, cart=cart_items, total_price=total_price)

@app.route('/checkout', methods=['POST'])
def checkout():
    payment_mode = request.form.get("payment_mode")
    for item in session.get("cart", []):
        new_order = Order(food_item=item["food_item"], quantity=item["quantity"], price=item["total_price"], payment_mode=payment_mode)
        db.session.add(new_order)
    db.session.commit()
    session.pop("cart", None)
    return redirect('/orders')

@app.route('/orders')
def orders():
    all_orders = Order.query.all()
    return render_template_string(TEMPLATE_ORDERS, orders=all_orders)

if __name__ == '__main__':
    app.run(debug=True)

