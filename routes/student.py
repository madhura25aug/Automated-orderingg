from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from routes.auth import login_required, role_required
from models import db
from models.user import User
from models.vendor import Vendor
from models.menu import MenuItem
from models.order import Order, OrderItem
from models.payment import Payment
from models.group_order import GroupOrder, GroupOrderMember
from models.prediction import SmartSwap
from models.eco_points import EcoTransaction
from services.crowd_prediction import get_canteen_crowd_status
from services.pickup_scheduler import calculate_pickup_slot
from services.smart_recommendations import get_cart_ai_recommendation

student_bp = Blueprint('student', __name__, url_prefix='/student')

@student_bp.route('/dashboard')
@login_required
@role_required('student')
def dashboard():
    user = User.query.get(session['user_id'])
    vendors = Vendor.query.all()
    crowd_data = get_canteen_crowd_status(vendors[0].id if vendors else None)
    
    active_order = Order.query.filter_by(user_id=user.id).filter(
        Order.status.in_(['PLACED', 'CONFIRMED', 'PREPARING', 'ALMOST_READY', 'READY'])
    ).order_by(Order.created_at.desc()).first()

    popular_items = MenuItem.query.filter_by(availability=True).order_by(MenuItem.popularity_score.desc()).limit(4).all()

    return render_template('student/dashboard.html',
                           user=user,
                           vendors=vendors,
                           crowd_data=crowd_data,
                           active_order=active_order,
                           popular_items=popular_items)

@student_bp.route('/vendors')
@login_required
def vendors():
    query = request.args.get('search', '').strip()
    if query:
        vendors_list = Vendor.query.filter(Vendor.name.ilike(f"%{query}%")).all()
    else:
        vendors_list = Vendor.query.all()

    crowd_info = get_canteen_crowd_status()['all_vendors_crowd']
    return render_template('student/vendors.html', vendors=vendors_list, crowd_info=crowd_info, search_query=query)

@student_bp.route('/vendors/<int:vendor_id>/menu')
@login_required
def menu(vendor_id):
    vendor = Vendor.query.get_or_404(vendor_id)
    category_filter = request.args.get('category', '').strip()
    search_query = request.args.get('search', '').strip()

    items_query = MenuItem.query.filter_by(vendor_id=vendor_id, availability=True)

    if category_filter and category_filter != 'All':
        items_query = items_query.filter_by(category=category_filter)
    if search_query:
        items_query = items_query.filter(MenuItem.name.ilike(f"%{search_query}%"))

    menu_items = items_query.all()
    categories = db.session.query(MenuItem.category).filter_by(vendor_id=vendor_id).distinct().all()
    categories = [c[0] for c in categories]

    return render_template('student/menu.html',
                           vendor=vendor,
                           menu_items=menu_items,
                           categories=categories,
                           selected_category=category_filter,
                           search_query=search_query)

@student_bp.route('/cart')
@login_required
def cart():
    # Session cart structure: {'vendor_id': X, 'items': {item_id: quantity}}
    cart_data = session.get('cart', {'vendor_id': None, 'items': {}})
    vendor = None
    cart_items = []
    total = 0.0
    item_ids_with_qty = {}

    if cart_data.get('vendor_id'):
        vendor = Vendor.query.get(cart_data['vendor_id'])
        for item_id_str, qty in cart_data.get('items', {}).items():
            item_id = int(item_id_str)
            menu_item = MenuItem.query.get(item_id)
            if menu_item:
                subtotal = menu_item.price * qty
                total += subtotal
                cart_items.append({
                    'item': menu_item,
                    'quantity': qty,
                    'subtotal': subtotal
                })
                item_ids_with_qty[item_id] = qty

    scheduler_res = calculate_pickup_slot(cart_data.get('vendor_id') or 1, item_ids_with_qty)
    ai_rec = get_cart_ai_recommendation(cart_items)

    return render_template('student/cart.html',
                           vendor=vendor,
                           cart_items=cart_items,
                           total=total,
                           scheduler=scheduler_res,
                           ai_rec=ai_rec)

@student_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart_data = session.get('cart', {'vendor_id': None, 'items': {}})
    if not cart_data.get('vendor_id') or not cart_data.get('items'):
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('student.vendors'))

    vendor = Vendor.query.get_or_404(cart_data['vendor_id'])
    
    # Calculate cart total
    cart_items = []
    total = 0.0
    item_ids_with_qty = {}
    for item_id_str, qty in cart_data.get('items', {}).items():
        item_id = int(item_id_str)
        menu_item = MenuItem.query.get(item_id)
        if menu_item:
            subtotal = menu_item.price * qty
            total += subtotal
            cart_items.append({'item': menu_item, 'quantity': qty, 'subtotal': subtotal})
            item_ids_with_qty[item_id] = qty

    custom_pickup = request.args.get('pickup_time')
    scheduler_res = calculate_pickup_slot(vendor.id, item_ids_with_qty, custom_pickup_time=custom_pickup)

    return render_template('student/checkout.html',
                           vendor=vendor,
                           cart_items=cart_items,
                           total=total,
                           scheduler=scheduler_res)

@student_bp.route('/orders')
@login_required
def orders():
    user_orders = Order.query.filter_by(user_id=session['user_id']).order_by(Order.created_at.desc()).all()
    return render_template('student/orders.html', orders=user_orders)

@student_bp.route('/tracking/<int:order_id>')
@login_required
def tracking(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != session['user_id'] and session.get('user_role') != 'admin':
        flash('Unauthorized to view this order tracking.', 'danger')
        return redirect(url_for('student.orders'))

    return render_template('student/tracking.html', order=order)

@student_bp.route('/group_order')
@login_required
def group_order():
    user_id = session['user_id']
    active_groups = GroupOrder.query.filter(GroupOrder.members.any(user_id=user_id)).all()
    return render_template('student/group_order.html', active_groups=active_groups)

@student_bp.route('/smartswap')
@login_required
def smartswap():
    my_swaps = SmartSwap.query.filter_by(owner_id=session['user_id']).all()
    available_swaps = SmartSwap.query.filter_by(status='AVAILABLE').filter(SmartSwap.owner_id != session['user_id']).all()
    return render_template('student/smartswap.html', my_swaps=my_swaps, available_swaps=available_swaps)

@student_bp.route('/eco_points')
@login_required
def eco_points():
    user = User.query.get(session['user_id'])
    transactions = EcoTransaction.query.filter_by(user_id=user.id).order_by(EcoTransaction.created_at.desc()).all()
    return render_template('student/eco_points.html', user=user, transactions=transactions)
