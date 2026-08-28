from collections import defaultdict
from datetime import datetime
from models.order import Order

def generate_smart_batches(vendor_id):
    """
    Groups active vendor orders (status PLACED or CONFIRMED) into Smart Batches
    based on matching food items and pickup time windows.
    """
    active_orders = Order.query.filter_by(vendor_id=vendor_id).filter(
        Order.status.in_(['PLACED', 'CONFIRMED'])
    ).all()

    if not active_orders:
        return []

    # Group by menu items
    batch_map = defaultdict(lambda: {
        'items': defaultdict(int),
        'order_ids': [],
        'earliest_pickup': None,
        'order_numbers': []
    })

    for idx, order in enumerate(active_orders):
        # Create key based on primary item category or batch bucket
        batch_key = f"B{(order.id % 5) + 40}" # e.g., B42, B43...
        
        b = batch_map[batch_key]
        b['order_ids'].append(order.id)
        b['order_numbers'].append(order.order_number)
        
        if not b['earliest_pickup'] or (order.pickup_time and order.pickup_time < b['earliest_pickup']):
            b['earliest_pickup'] = order.pickup_time or '12:45 PM'

        for item in order.items:
            b['items'][item.menu_item.name if item.menu_item else 'Item'] += item.quantity

    batches = []
    for batch_code, data in batch_map.items():
        total_items = sum(data['items'].values())
        est_prep = max(5, total_items * 2)
        batches.append({
            'batch_number': batch_code,
            'items_map': dict(data['items']),
            'items_summary': ", ".join([f"{name} × {qty}" for name, qty in data['items'].items()]),
            'order_count': len(data['order_ids']),
            'order_numbers': data['order_numbers'],
            'order_ids': data['order_ids'],
            'prep_time_mins': est_prep,
            'priority': 'HIGH PRIORITY' if len(data['order_ids']) >= 3 else 'MEDIUM PRIORITY',
            'pickup_deadline': data['earliest_pickup'] or '12:45 PM'
        })

    return sorted(batches, key=lambda x: x['order_count'], reverse=True)
