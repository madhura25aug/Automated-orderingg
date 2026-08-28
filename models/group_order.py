from datetime import datetime
from models import db

class GroupOrder(db.Model):
    __tablename__ = 'group_orders'

    id = db.Column(db.Integer, primary_key=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    group_code = db.Column(db.String(20), unique=True, nullable=False)
    status = db.Column(db.String(20), default='ACTIVE') # ACTIVE, COMPLETED, CANCELLED
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    members = db.relationship('GroupOrderMember', backref='group_order', lazy=True, cascade="all, delete-orphan")
    creator = db.relationship('User', foreign_keys=[creator_id])

    def to_dict(self):
        return {
            'id': self.id,
            'creator_id': self.creator_id,
            'creator_name': self.creator.name if self.creator else 'Creator',
            'group_code': self.group_code,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'members': [m.to_dict() for m in self.members]
        }

class GroupOrderMember(db.Model):
    __tablename__ = 'group_order_members'

    id = db.Column(db.Integer, primary_key=True)
    group_order_id = db.Column(db.Integer, db.ForeignKey('group_orders.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='PENDING') # PENDING, PAID

    user = db.relationship('User', foreign_keys=[user_id])

    def to_dict(self):
        return {
            'id': self.id,
            'group_order_id': self.group_order_id,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else 'Member',
            'amount': self.amount,
            'status': self.status
        }
