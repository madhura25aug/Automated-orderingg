from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from routes.auth import login_required, role_required
from models import db
from models.vendor import Vendor
from models.order import Order
from models.menu import MenuItem
from models.inventory import Inventory, WasteRecord
from services.order_batching import generate_smart_batches
from services.demand_prediction import get_hourly_forecast, get_item_forecast
from services.waste_prediction import get_waste_analytics

vendor_bp = Blueprint('vendor', __name__, url_prefix='/vendor')

def get_current_vendor():
    # If user is vendor, map or default to vendor_id 1 (Central Canteen)
    return Vendor.query.first()

@vendor_bp.route('/dashboard')
@login_required
@role_required('vendor')
def dashboard():
    vendor = get_current_vendor()
    if not vendor:
        flash('No vendor profile found.', 'danger')
        return redirect(url_for('landing'))

    today_orders = Order.query.filter_by(vendor_id=vendor.id).all()
    active_orders = [o for o in today_orders if o.status in ['PLACED', 'CONFIRMED', 'PREPARING', 'ALMOST_READY', 'READY']]
    revenue = sum(o.total for o in today_orders if o.status in ['PICKED_UP', 'READY', 'ALMOST_READY', 'PREPARING', 'CONFIRMED', 'PLACED'])

    return render_template('vendor/dashboard.html',
                           vendor=vendor,
                           today_count=len(today_orders),
                           active_count=len(active_orders),
                           revenue=revenue,
                           avg_prep=vendor.average_prep_time,
                           recent_orders=today_orders[:6])

@vendor_bp.route('/live_orders')
@login_required
@role_required('vendor')
def live_orders():
    vendor = get_current_vendor()
    orders = Order.query.filter_by(vendor_id=vendor.id).order_by(Order.created_at.desc()).all()
    
    kanban = {
        'PLACED': [o for o in orders if o.status == 'PLACED'],
        'PREPARING': [o for o in orders if o.status in ['CONFIRMED', 'PREPARING']],
        'ALMOST_READY': [o for o in orders if o.status == 'ALMOST_READY'],
        'READY': [o for o in orders if o.status == 'READY'],
        'COMPLETED': [o for o in orders if o.status == 'PICKED_UP']
    }

    return render_template('vendor/live_orders.html', vendor=vendor, kanban=kanban)

@vendor_bp.route('/batches')
@login_required
@role_required('vendor')
def batches():
    vendor = get_current_vendor()
    smart_batches = generate_smart_batches(vendor.id)
    return render_template('vendor/batches.html', vendor=vendor, batches=smart_batches)

@vendor_bp.route('/demand')
@login_required
@role_required('vendor')
def demand():
    vendor = get_current_vendor()
    hourly_forecasts = get_hourly_forecast(vendor.id)
    item_forecasts = get_item_forecast(vendor.id)
    return render_template('vendor/demand.html', vendor=vendor, hourly_forecasts=hourly_forecasts, item_forecasts=item_forecasts)

@vendor_bp.route('/inventory')
@login_required
@role_required('vendor')
def inventory():
    vendor = get_current_vendor()
    items = MenuItem.query.filter_by(vendor_id=vendor.id).all()
    forecasts = {f['menu_item_id']: f for f in get_item_forecast(vendor.id)}
    return render_template('vendor/inventory.html', vendor=vendor, items=items, forecasts=forecasts)

@vendor_bp.route('/waste')
@login_required
@role_required('vendor')
def waste():
    vendor = get_current_vendor()
    analytics = get_waste_analytics(vendor.id)
    return render_template('vendor/waste.html', vendor=vendor, analytics=analytics)

@vendor_bp.route('/analytics')
@login_required
@role_required('vendor')
def analytics():
    vendor = get_current_vendor()
    return render_template('vendor/analytics.html', vendor=vendor)

@vendor_bp.route('/copilot')
@login_required
@role_required('vendor')
def copilot():
    vendor = get_current_vendor()
    return render_template('vendor/copilot.html', vendor=vendor)
