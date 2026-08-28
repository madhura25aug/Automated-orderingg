from datetime import datetime
from models import db

class DemandPrediction(db.Model):
    __tablename__ = 'demand_predictions'

    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=False)
    time_slot = db.Column(db.String(50), nullable=False)  # e.g., "12:00 PM - 01:00 PM"
    predicted_demand = db.Column(db.Integer, nullable=False, default=10)
    confidence = db.Column(db.Float, default=0.88)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    menu_item = db.relationship('MenuItem')

    def to_dict(self):
        return {
            'id': self.id,
            'vendor_id': self.vendor_id,
            'menu_item_id': self.menu_item_id,
            'menu_item_name': self.menu_item.name if self.menu_item else 'Item',
            'time_slot': self.time_slot,
            'predicted_demand': self.predicted_demand,
            'confidence': self.confidence,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

class SmartSwap(db.Model):
    __tablename__ = 'smart_swaps'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    claimed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    status = db.Column(db.String(20), default='AVAILABLE')  # AVAILABLE, CLAIMED, EXPIRED
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    owner = db.relationship('User', foreign_keys=[owner_id])
    claimer = db.relationship('User', foreign_keys=[claimed_by])

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'order_number': self.order.order_number if self.order else None,
            'vendor_name': self.order.vendor.name if self.order and self.order.vendor else None,
            'items': [item.to_dict() for item in self.order.items] if self.order else [],
            'owner_id': self.owner_id,
            'owner_name': self.owner.name if self.owner else 'Student',
            'claimed_by': self.claimed_by,
            'claimed_by_name': self.claimer.name if self.claimer else None,
            'status': self.status,
            'pickup_time': self.order.pickup_time if self.order else None,
            'total': self.order.total if self.order else 0.0,
            'created_at': self.created_at.strftime('%H:%M:%S') if self.created_at else None
        }
