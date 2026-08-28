from datetime import datetime, timedelta
import random
from flask import Blueprint, request, jsonify, session
from models import db
from models.order import Order, OrderItem
from models.payment import Payment
from models.menu import MenuItem
from models.user import User
from models.notification import Notification
from services.pickup_scheduler import calculate_pickup_slot

orders_bp = Blueprint('orders', __name__, url_prefix='/api/orders')

def emit_socket_event(event_name, data):
    try:
        from app import socketio
        socketio.emit(event_name, data)
    except Exception as e:
        print(f"SocketIO emit warning: {e}")

@orders_bp.route('', methods=['POST'])
def create_order():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json or {}
    items_data = data.get('items', []) # [{'menu_item_id': 1, 'quantity': 2}, ...]
    vendor_id = data.get('vendor_id')
    pickup_time = data.get('pickup_time')
    payment_method = data.get('payment_method', 'UPI')

    if not items_data or not vendor_id:
        return jsonify({'error': 'Invalid order items or vendor'}), 400

    order_num = f"CF-{random.randint(1000, 9999)}"
    item_ids_with_qty = {item['menu_item_id']: item['quantity'] for item in items_data}
    scheduler_res = calculate_pickup_slot(vendor_id, item_ids_with_qty, custom_pickup_time=pickup_time)

    total_amount = 0.0
    order_items_to_add = []

    for item in items_data:
        m_item = MenuItem.query.get(item['menu_item_id'])
        if not m_item or not m_item.availability:
            return jsonify({'error': f"Item {item.get('menu_item_id')} is unavailable."}), 400
        
        qty = item['quantity']
        subtotal = m_item.price * qty
        total_amount += subtotal

        # Stock deduction
        if m_item.stock >= qty:
            m_item.stock -= qty
        
        order_items_to_add.append(OrderItem(
            menu_item_id=m_item.id,
            quantity=qty,
            price=m_item.price
        ))

    token_code = f"TK-{random.randint(1000, 9999)}"
    new_order = Order(
        user_id=session['user_id'],
        vendor_id=vendor_id,
        order_number=order_num,
        status='PLACED',
        total=total_amount,
        pickup_time=scheduler_res['pickup_slot_str'],
        pickup_counter=scheduler_res['pickup_counter'],
        pickup_token=token_code,
        estimated_ready_time=scheduler_res['estimated_ready_dt']
    )

    db.session.add(new_order)
    db.session.flush()

    for oi in order_items_to_add:
        oi.order_id = new_order.id
        db.session.add(oi)

    # Simulated Payment
    payment = Payment(
        order_id=new_order.id,
        user_id=session['user_id'],
        amount=total_amount,
        method=payment_method,
        status='SUCCESS'
    )
    db.session.add(payment)

    # Notification
    notif = Notification(
        user_id=session['user_id'],
        message=f"Order {order_num} (Token: {token_code}) placed! Ready at {scheduler_res['estimated_ready_time']}.",
        notification_type="order_placed"
    )
    db.session.add(notif)
    db.session.commit()

    # Clear Session Cart
    session.pop('cart', None)

    # WebSocket Real-Time Broadcast
    emit_socket_event('new_order', {
        'order_id': new_order.id,
        'order_number': order_num,
        'vendor_id': vendor_id,
        'status': new_order.status,
        'total': total_amount,
        'pickup_token': token_code,
        'user_name': session.get('user_name', 'Student')
    })

    return jsonify({
        'success': True,
        'message': 'Order placed successfully!',
        'order_id': new_order.id,
        'order_number': order_num,
        'pickup_time': new_order.pickup_time,
        'pickup_counter': new_order.pickup_counter,
        'pickup_token': token_code
    })

@orders_bp.route('/<int:order_id>/status', methods=['PUT'])
def update_status(order_id):
    order = Order.query.get_or_404(order_id)
    data = request.json or {}
    new_status = data.get('status')

    valid_statuses = ['PLACED', 'CONFIRMED', 'PREPARING', 'ALMOST_READY', 'READY', 'PICKED_UP', 'CANCELLED']
    if new_status not in valid_statuses:
        return jsonify({'error': 'Invalid status'}), 400

    order.status = new_status
    
    # Notify Student
    notif = Notification(
        user_id=order.user_id,
        message=f"Your order #{order.order_number} is now {new_status.replace('_', ' ')}!",
        notification_type="status_change"
    )
    db.session.add(notif)
    db.session.commit()

    # Emit WebSocket update
    emit_socket_event('order_status_update', {
        'order_id': order.id,
        'order_number': order.order_number,
        'user_id': order.user_id,
        'status': new_status,
        'updated_at': datetime.utcnow().strftime('%H:%M:%S')
    })

    return jsonify({'success': True, 'order_id': order.id, 'status': new_status})
