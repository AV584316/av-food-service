from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os

# Initialize Flask App
app = Flask(__name__)
app.secret_key = "your_secret_key"

# Configure Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/orders.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Order Model
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    food_item = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    payment_mode = db.Column(db.String(50), nullable=False)
    order_status = db.Column(db.String(50), default="Pending")

    def __repr__(self):
        return f"Order {self.id}: {self.food_item} x {self.quantity} - {self.price} INR"

# Create Database Tables
with app.app_context():
    db.create_all()

# Homepage Route
@app.route('/')
def home():
    return render_template('index.html')

# Menu Route
@app.route('/menu')
def menu():
    food_items = [
        {'name': 'Aloo Paratha', 'price': 50},
        {'name': 'Paneer Paratha', 'price': 80},
        {'name': 'Mix Veg Sabji', 'price': 120},
        {'name': 'Dal Tadka', 'price': 100},
        {'name': 'Tandoori Roti', 'price': 20}
    ]
    return render_template('menu.html', food_items=food_items)

# Cart Feature
cart = []

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    food_item = request.form.get('food_item')
    price = int(request.form.get('price'))
    quantity = int(request.form.get('quantity'))

    cart.append({'food_item': food_item, 'price': price, 'quantity': quantity})
    return redirect(url_for('cart_page'))

@app.route('/cart')
def cart_page():
    total_price = sum(item['price'] * item['quantity'] for item in cart)
    return render_template('cart.html', cart=cart, total_price=total_price)

# Checkout Process
@app.route('/checkout', methods=['POST'])
def checkout():
    payment_mode = request.form.get('payment_mode')

    for item in cart:
        new_order = Order(
            food_item=item['food_item'],
            quantity=item['quantity'],
            price=item['price'] * item['quantity'],
            payment_mode=payment_mode
        )
        db.session.add(new_order)

    db.session.commit()
    cart.clear()

    return redirect(url_for('orders_page'))

# Order Tracking Page
@app.route('/orders')
def orders_page():
    all_orders = Order.query.all()
    return render_template('orders.html', orders=all_orders)

# Run Flask App
if __name__ == '__main__':
    app.run(debug=True)

