from datetime import datetime
from models.vendor import Vendor
from models.order import Order

def get_canteen_crowd_status(vendor_id=None):
    """
    Evaluates current queue size and capacity to determine crowd status.
    Returns crowd level, estimated wait minutes, and faster alternate vendor recommendation.
    """
    vendors = Vendor.query.all()
    crowd_info = {}

    for v in vendors:
        active_count = Order.query.filter_by(vendor_id=v.id).filter(
            Order.status.in_(['PLACED', 'CONFIRMED', 'PREPARING'])
        ).count()

        # Calculation
        ratio = active_count / max(1, v.current_capacity)
        if ratio < 0.25:
            level = "LOW 🟢"
            level_code = "LOW"
            badge_class = "success"
            wait_mins = max(3, active_count * 2)
        elif ratio < 0.55:
            level = "MODERATE ⚡"
            level_code = "MODERATE"
            badge_class = "warning"
            wait_mins = 6 + active_count * 2
        elif ratio < 0.8:
            level = "BUSY 🟠"
            level_code = "BUSY"
            badge_class = "orange"
            wait_mins = 12 + active_count * 2
        else:
            level = "VERY BUSY 🔴"
            level_code = "VERY BUSY"
            badge_class = "danger"
            wait_mins = 18 + active_count * 2

        crowd_info[v.id] = {
            'vendor_id': v.id,
            'vendor_name': v.name,
            'active_orders': active_count,
            'level': level,
            'level_code': level_code,
            'badge_class': badge_class,
            'wait_mins': wait_mins
        }

    target_vendor_id = vendor_id or (vendors[0].id if vendors else 1)
    current_data = crowd_info.get(target_vendor_id, {
        'level': 'LOW 🟢', 'level_code': 'LOW', 'badge_class': 'success', 'wait_mins': 4
    })

    # Find faster vendor option
    faster_recommendation = None
    min_wait_vendor = min(crowd_info.values(), key=lambda x: x['wait_mins']) if crowd_info else None
    
    if min_wait_vendor and min_wait_vendor['vendor_id'] != target_vendor_id:
        diff = current_data['wait_mins'] - min_wait_vendor['wait_mins']
        if diff >= 3:
            faster_recommendation = {
                'vendor_id': min_wait_vendor['vendor_id'],
                'vendor_name': min_wait_vendor['vendor_name'],
                'wait_mins': min_wait_vendor['wait_mins'],
                'time_saved_mins': diff,
                'message': f"{min_wait_vendor['vendor_name']} is currently {diff} minutes faster."
            }

    return {
        'current_vendor_crowd': current_data,
        'all_vendors_crowd': crowd_info,
        'ai_recommendation': faster_recommendation
    }
