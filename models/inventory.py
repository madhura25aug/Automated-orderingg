from datetime import datetime
from models import db

class Inventory(db.Model):
    __tablename__ = 'inventories'

    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=False)
    quantity = db.Column(db.Integer, default=50)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    menu_item = db.relationship('MenuItem', backref='inventories')

    def to_dict(self):
        return {
            'id': self.id,
            'vendor_id': self.vendor_id,
            'menu_item_id': self.menu_item_id,
            'menu_item_name': self.menu_item.name if self.menu_item else 'Item',
            'quantity': self.quantity,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

class WasteRecord(db.Model):
    __tablename__ = 'waste_records'

    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=False)
    quantity_wasted = db.Column(db.Integer, nullable=False, default=0)
    date = db.Column(db.Date, default=datetime.utcnow().date)
    reason = db.Column(db.String(100), default='Over-preparation')

    menu_item = db.relationship('MenuItem')

    def to_dict(self):
        return {
            'id': self.id,
            'vendor_id': self.vendor_id,
            'menu_item_id': self.menu_item_id,
            'menu_item_name': self.menu_item.name if self.menu_item else 'Item',
            'quantity_wasted': self.quantity_wasted,
            'date': self.date.strftime('%Y-%m-%d') if self.date else None,
            'reason': self.reason
        }
