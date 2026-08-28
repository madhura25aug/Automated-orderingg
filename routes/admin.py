from flask import Blueprint, render_template, session, flash, redirect, url_for
from routes.auth import login_required, role_required
from models import db
from models.user import User
from models.vendor import Vendor
from models.order import Order
from services.waste_prediction import get_waste_analytics

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@login_required
@role_required('admin')
def dashboard():
    total_students = User.query.filter_by(role='student').count()
    total_vendors = Vendor.query.count()
    orders = Order.query.all()
    today_orders = len(orders)
    total_revenue = sum(o.total for o in orders if o.status in ['PICKED_UP', 'READY', 'ALMOST_READY', 'PREPARING', 'CONFIRMED', 'PLACED'])
    
    waste_summary = get_waste_analytics()

    vendors = Vendor.query.all()
    vendor_stats = []
    for v in vendors:
        v_orders = Order.query.filter_by(vendor_id=v.id).all()
        v_rev = sum(o.total for o in v_orders)
        vendor_stats.append({
            'vendor': v,
            'order_count': len(v_orders),
            'revenue': v_rev
        })

    return render_template('admin/dashboard.html',
                           total_students=total_students,
                           total_vendors=total_vendors,
                           today_orders=today_orders,
                           total_revenue=total_revenue,
                           waste_summary=waste_summary,
                           vendor_stats=vendor_stats)
