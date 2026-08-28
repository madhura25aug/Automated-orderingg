from models import db

class Vendor(db.Model):
    __tablename__ = 'vendors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='OPEN')  # 'OPEN', 'BUSY', 'CLOSED'
    average_prep_time = db.Column(db.Integer, default=10) # in minutes
    current_capacity = db.Column(db.Integer, default=25)

    # Relationships
    menu_items = db.relationship('MenuItem', backref='vendor', lazy=True, cascade="all, delete-orphan")
    orders = db.relationship('Order', backref='vendor', lazy=True)
    inventories = db.relationship('Inventory', backref='vendor', lazy=True)
    waste_records = db.relationship('WasteRecord', backref='vendor', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'location': self.location,
            'description': self.description,
            'status': self.status,
            'average_prep_time': self.average_prep_time,
            'current_capacity': self.current_capacity
        }
