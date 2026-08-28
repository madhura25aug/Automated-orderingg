from datetime import datetime, timedelta
from models.order import Order
from models.vendor import Vendor
from models.menu import MenuItem

def calculate_pickup_slot(vendor_id, item_ids_with_qty, walk_time_mins=4, custom_pickup_time=None):
    """
    QueueZero Smart Pickup Scheduler
    Calculates exact preparation time, queue delay, estimated ready time, recommended classroom departure time, and pickup counter.
    """
    vendor = Vendor.query.get(vendor_id)
    if not vendor:
        prep_time_mins = 10
    else:
        # Find maximum preparation time among items ordered plus slight multiplier for quantities
        max_prep = 0
        total_items_count = 0
        for item_id, qty in item_ids_with_qty.items():
            menu_item = MenuItem.query.get(item_id)
            if menu_item:
                max_prep = max(max_prep, menu_item.prep_time)
                total_items_count += qty
        
        prep_time_mins = max_prep + max(0, total_items_count - 1) * 2

    # Active active orders ahead in vendor queue
    active_orders_count = Order.query.filter_by(vendor_id=vendor_id).filter(
        Order.status.in_(['PLACED', 'CONFIRMED', 'PREPARING'])
    ).count()

    # Queue delay calculation: each order ahead adds approx 2 mins of queue latency
    queue_delay_mins = int(active_orders_count * 1.5)
    total_wait_mins = prep_time_mins + queue_delay_mins

    now = datetime.now()

    if custom_pickup_time:
        try:
            # Parse custom requested time e.g. "12:45 PM"
            parsed_time = datetime.strptime(custom_pickup_time, "%H:%M")
            pickup_dt = now.replace(hour=parsed_time.hour, minute=parsed_time.minute, second=0)
            if pickup_dt < now:
                pickup_dt += timedelta(days=1)
            estimated_ready_dt = pickup_dt
        except Exception:
            estimated_ready_dt = now + timedelta(minutes=total_wait_mins)
            pickup_dt = estimated_ready_dt
    else:
        estimated_ready_dt = now + timedelta(minutes=total_wait_mins)
        pickup_dt = estimated_ready_dt

    # Classroom departure time = Ready time minus walking time
    leave_classroom_dt = estimated_ready_dt - timedelta(minutes=walk_time_mins)
    if leave_classroom_dt < now:
        leave_classroom_dt = now

    # Counter assignment based on order hash / load balancing
    counter_num = (active_orders_count % 3) + 1
    pickup_counter = f"Pickup Counter {counter_num}"

    return {
        'prep_time_mins': prep_time_mins,
        'active_queue_count': active_orders_count,
        'queue_delay_mins': queue_delay_mins,
        'total_wait_mins': total_wait_mins,
        'leave_classroom_time': leave_classroom_dt.strftime('%I:%M %p'),
        'estimated_ready_time': estimated_ready_dt.strftime('%I:%M %p'),
        'estimated_ready_dt': estimated_ready_dt,
        'pickup_slot_str': pickup_dt.strftime('%I:%M %p'),
        'pickup_counter': pickup_counter,
        'walking_time_mins': walk_time_mins
    }
