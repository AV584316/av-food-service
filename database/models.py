from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    food_item = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    payment_mode = db.Column(db.String(50), nullable=False)
    order_status = db.Column(db.String(50), default="Pending")

    def __repr__(self):
        return f"Order {self.id}: {self.food_item} x {self.quantity} - {self.price} INR"
