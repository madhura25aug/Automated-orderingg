from datetime import datetime
from models import db

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)
    order_number = db.Column(db.String(20), unique=True, nullable=False)
    status = db.Column(db.String(30), default='PLACED') # PLACED, CONFIRMED, PREPARING, ALMOST_READY, READY, PICKED_UP, CANCELLED, DONATED, SWAPPED
    total = db.Column(db.Float, nullable=False, default=0.0)
    pickup_time = db.Column(db.String(50), nullable=True) # Recommended or chosen pickup time (e.g. 12:45 PM)
    pickup_counter = db.Column(db.String(50), default='Counter 1')
    pickup_token = db.Column(db.String(20), nullable=True) # e.g. TK-8492 for quick counter collection
    estimated_ready_time = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade="all, delete-orphan")
    payment = db.relationship('Payment', backref='order', uselist=False, lazy=True)
    smart_swaps = db.relationship('SmartSwap', backref='order', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else 'Student',
            'vendor_id': self.vendor_id,
            'vendor_name': self.vendor.name if self.vendor else 'Vendor',
            'order_number': self.order_number,
            'status': self.status,
            'total': self.total,
            'pickup_time': self.pickup_time,
            'pickup_counter': self.pickup_counter,
            'pickup_token': self.pickup_token,
            'estimated_ready_time': self.estimated_ready_time.strftime('%I:%M %p') if self.estimated_ready_time else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'items': [item.to_dict() for item in self.items]
        }

class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'menu_item_id': self.menu_item_id,
            'menu_item_name': self.menu_item.name if self.menu_item else 'Food Item',
            'quantity': self.quantity,
            'price': self.price,
            'subtotal': self.price * self.quantity
        }
