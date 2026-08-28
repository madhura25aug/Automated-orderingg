import random
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, session
from models import db
from models.user import User
from models.vendor import Vendor
from models.menu import MenuItem
from models.order import Order, OrderItem
from models.prediction import SmartSwap, DemandPrediction
from models.group_order import GroupOrder, GroupOrderMember
from models.eco_points import EcoTransaction
from models.notification import Notification
from services.demand_prediction import get_hourly_forecast, get_item_forecast
from services.smart_recommendations import get_copilot_response
from services.crowd_prediction import get_canteen_crowd_status

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/cart/add', methods=['POST'])
def add_to_cart():
    data = request.json or {}
    item_id = data.get('item_id')
    quantity = int(data.get('quantity', 1))

    menu_item = MenuItem.query.get_or_404(item_id)
    cart = session.get('cart', {'vendor_id': menu_item.vendor_id, 'items': {}})

    if cart.get('vendor_id') and cart['vendor_id'] != menu_item.vendor_id:
        # Reset cart if items from a different vendor are added
        cart = {'vendor_id': menu_item.vendor_id, 'items': {}}

    cart['vendor_id'] = menu_item.vendor_id
    item_str = str(item_id)
    cart['items'][item_str] = cart['items'].get(item_str, 0) + quantity

    session['cart'] = cart
    session.modified = True

    total_count = sum(cart['items'].values())
    return jsonify({
        'success': True,
        'message': f"Added {menu_item.name} to cart!",
        'cart_count': total_count
    })

@api_bp.route('/cart/update', methods=['POST'])
def update_cart():
    data = request.json or {}
    item_id = str(data.get('item_id'))
    quantity = int(data.get('quantity', 1))

    cart = session.get('cart', {'vendor_id': None, 'items': {}})
    if quantity <= 0:
        cart['items'].pop(item_id, None)
    else:
        cart['items'][item_id] = quantity

    session['cart'] = cart
    session.modified = True
    return jsonify({'success': True, 'cart': cart})

@api_bp.route('/smartswap', methods=['GET', 'POST'])
def smartswap_api():
    if request.method == 'POST':
        data = request.json or {}
        order_id = data.get('order_id')
        order = Order.query.get_or_404(order_id)

        if order.user_id != session.get('user_id'):
            return jsonify({'error': 'Unauthorized'}), 403

        existing = SmartSwap.query.filter_by(order_id=order.id, status='AVAILABLE').first()
        if existing:
            return jsonify({'error': 'Order is already listed on SmartSwap!'}), 400

        order.status = 'SWAPPED'
        swap = SmartSwap(order_id=order.id, owner_id=session['user_id'], status='AVAILABLE')
        db.session.add(swap)

        # Award Eco points
        user = User.query.get(session['user_id'])
        user.eco_points += 15
        db.session.add(EcoTransaction(user_id=user.id, points=15, reason="Offered order on SmartSwap"))
        db.session.commit()

        return jsonify({'success': True, 'message': 'Order listed on SmartSwap marketplace (+15 Eco Points!)'})

    swaps = SmartSwap.query.filter_by(status='AVAILABLE').all()
    return jsonify({'swaps': [s.to_dict() for s in swaps]})

@api_bp.route('/smartswap/<int:swap_id>/claim', methods=['POST'])
def claim_smartswap(swap_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    swap = SmartSwap.query.get_or_404(swap_id)
    if swap.status != 'AVAILABLE':
        return jsonify({'error': 'This order has already been claimed!'}), 400
    if swap.owner_id == session['user_id']:
        return jsonify({'error': 'You cannot claim your own SmartSwap order.'}), 400

    swap.status = 'CLAIMED'
    swap.claimed_by = session['user_id']
    
    # Transfer order ownership
    order = Order.query.get(swap.order_id)
    order.user_id = session['user_id']
    order.status = 'CONFIRMED'

    # Award Eco points to claimer
    claimer = User.query.get(session['user_id'])
    claimer.eco_points += 10
    db.session.add(EcoTransaction(user_id=claimer.id, points=10, reason="Claimed SmartSwap order"))
    db.session.commit()

    return jsonify({'success': True, 'message': f"Successfully claimed order #{order.order_number}! (+10 Eco Points)"})

@api_bp.route('/orders/<int:order_id>/donate', methods=['POST'])
def donate_order(order_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    order = Order.query.get_or_404(order_id)
    if order.user_id != session['user_id']:
        return jsonify({'error': 'Unauthorized'}), 403

    order.status = 'DONATED'
    user = User.query.get(session['user_id'])
    user.eco_points += 20
    db.session.add(EcoTransaction(user_id=user.id, points=20, reason="Donated meal to Campus Food Bank"))
    db.session.commit()

    return jsonify({'success': True, 'message': 'Thank you for your generosity! Your order was donated and you earned +20 Eco Points 🌱'})

@api_bp.route('/group/create', methods=['POST'])
def create_group():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    code = f"CF-{random.randint(1000, 9999)}"
    group = GroupOrder(creator_id=session['user_id'], group_code=code)
    db.session.add(group)
    db.session.flush()

    member = GroupOrderMember(group_order_id=group.id, user_id=session['user_id'], amount=0.0, status='PAID')
    db.session.add(member)
    db.session.commit()

    return jsonify({'success': True, 'group_code': code, 'group_id': group.id})

@api_bp.route('/group/join', methods=['POST'])
def join_group():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json or {}
    code = data.get('group_code', '').strip().upper()
    group = GroupOrder.query.filter_by(group_code=code, status='ACTIVE').first()

    if not group:
        return jsonify({'error': 'Invalid or inactive group code.'}), 404

    existing = GroupOrderMember.query.filter_by(group_order_id=group.id, user_id=session['user_id']).first()
    if not existing:
        member = GroupOrderMember(group_order_id=group.id, user_id=session['user_id'], amount=60.0, status='PENDING')
        db.session.add(member)
        db.session.commit()

    return jsonify({'success': True, 'message': f"Joined group {group.group_code}!", 'group': group.to_dict()})

@api_bp.route('/copilot/chat', methods=['POST'])
def copilot_chat():
    data = request.json or {}
    question = data.get('question', '')
    res = get_copilot_response(question)
    return jsonify(res)

@api_bp.route('/demo/forecast', methods=['GET', 'POST'])
def demo_forecast():
    vendor_id = 1
    hourly = get_hourly_forecast(vendor_id)
    items = get_item_forecast(vendor_id)
    
    return jsonify({
        'time_slot': '12:30 PM - 01:00 PM',
        'expected_orders': 145,
        'demand_level': 'HIGH 🔥',
        'recommendations': [
            {'item': 'Masala Dosa', 'qty': 42},
            {'item': 'Veg Burger', 'qty': 30},
            {'item': 'Sandwich', 'qty': 26},
            {'item': 'Lemon Juice', 'qty': 35}
        ],
        'alert': {
            'shortage_item': 'Sandwich',
            'current_stock': 8,
            'predicted_demand': 26,
            'potential_shortage': 18,
            'recommendation': 'Prepare 18 additional sandwiches.'
        }
    })

@api_bp.route('/demo/optimize', methods=['GET', 'POST'])
def demo_optimize():
    return jsonify({
        'before_optimization_mins': 14,
        'after_optimization_mins': 5,
        'reduction_pct': 72,
        'message': '72% reduction in estimated queue time achieved via QueueZero slot staggering!'
    })

@api_bp.route('/demo/rush', methods=['POST'])
def simulate_lunch_rush():
    """
    🔥 LUNCH RUSH SIMULATOR
    Generates 25 realistic incoming canteen orders, updates vendor workload,
    and returns high-demand crowd state.
    """
    users = User.query.filter_by(role='student').all()
    if not users:
        student_user = User(name='Demo Student', email='student@canteenflow.com', role='student')
        student_user.set_password('student123')
        db.session.add(student_user)
        db.session.commit()
        users = [student_user]

    vendors = Vendor.query.all()
    vendor = vendors[0] if vendors else Vendor(name='Central Canteen', location='Block A', average_prep_time=12)

    menu_items = MenuItem.query.filter_by(vendor_id=vendor.id).all()
    if not menu_items:
        m1 = MenuItem(vendor_id=vendor.id, name='Masala Dosa', category='Main', price=60.0, prep_time=7)
        db.session.add(m1)
        db.session.commit()
        menu_items = [m1]

    created_orders = []
    for i in range(25):
        u = random.choice(users)
        item = random.choice(menu_items)
        qty = random.randint(1, 3)
        order_num = f"CF-{random.randint(2000, 9999)}"
        token_code = f"TK-{random.randint(1000, 9999)}"
        
        ord_obj = Order(
            user_id=u.id,
            vendor_id=vendor.id,
            order_number=order_num,
            status=random.choice(['PLACED', 'CONFIRMED', 'PREPARING']),
            total=item.price * qty,
            pickup_time="12:45 PM",
            pickup_counter=f"Counter {(i % 3) + 1}",
            pickup_token=token_code,
            estimated_ready_time=datetime.utcnow() + timedelta(minutes=15)
        )
        db.session.add(ord_obj)
        db.session.flush()

        oi = OrderItem(order_id=ord_obj.id, menu_item_id=item.id, quantity=qty, price=item.price)
        db.session.add(oi)
        created_orders.append(order_num)

    db.session.commit()

    try:
        from app import socketio
        socketio.emit('crowd_update', {
            'level': 'VERY BUSY 🔴',
            'wait_mins': 18,
            'active_orders': len(created_orders)
        })
    except Exception:
        pass

    return jsonify({
        'success': True,
        'orders_generated': len(created_orders),
        'crowd_level': 'VERY BUSY 🔴',
        'estimated_wait_mins': 18,
        'message': f"🔥 Simulated Lunch Rush! Created {len(created_orders)} live orders. Crowd level is now VERY BUSY 🔴."
    })

@api_bp.route('/batches/create', methods=['POST'])
def trigger_batch_creation():
    from services.order_batching import generate_smart_batches
    vendor_id = request.json.get('vendor_id', 1) if request.json else 1
    batches = generate_smart_batches(vendor_id)

    try:
        from app import socketio
        socketio.emit('batch_created', {
            'vendor_id': vendor_id,
            'count': len(batches),
            'timestamp': datetime.utcnow().strftime('%H:%M:%S')
        })
    except Exception:
        pass

    return jsonify({
        'success': True,
        'count': len(batches),
        'batches': batches,
        'message': f"Created {len(batches)} Smart Kitchen Order Batches!"
    })

@api_bp.route('/batches/start', methods=['POST'])
def start_batch_cooking():
    data = request.json or {}
    batch_num = data.get('batch_number', 'B42')
    order_ids = data.get('order_ids', [])

    if order_ids:
        orders = Order.query.filter(Order.id.in_(order_ids)).all()
        for o in orders:
            if o.status in ['PLACED', 'CONFIRMED']:
                o.status = 'PREPARING'
        db.session.commit()

    try:
        from app import socketio
        socketio.emit('order_status_update', {
            'status': 'PREPARING',
            'message': f"Batch #{batch_num} cooking started!"
        })
    except Exception:
        pass

    return jsonify({
        'success': True,
        'message': f"Batch #{batch_num} sent to kitchen grill! Orders set to PREPARING."
    })
