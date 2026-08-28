from models import db

class MenuItem(db.Model):
    __tablename__ = 'menu_items'

    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=False, default='Main')
    price = db.Column(db.Float, nullable=False)
    prep_time = db.Column(db.Integer, default=8)  # in minutes
    stock = db.Column(db.Integer, default=50)
    availability = db.Column(db.Boolean, default=True)
    popularity_score = db.Column(db.Float, default=4.5)

    order_items = db.relationship('OrderItem', backref='menu_item', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'vendor_id': self.vendor_id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'price': self.price,
            'prep_time': self.prep_time,
            'stock': self.stock,
            'availability': self.availability,
            'popularity_score': self.popularity_score
        }
