import os
import random
from datetime import datetime, timedelta
import pandas as pd
from app import create_app
from models import db
from models.user import User
from models.vendor import Vendor
from models.menu import MenuItem
from models.order import Order, OrderItem
from models.payment import Payment
from models.inventory import Inventory, WasteRecord
from models.eco_points import EcoTransaction
from models.notification import Notification
from services.demand_prediction import train_model

def seed_database():
    app = create_app()
    with app.app_context():
        print("Dropping existing tables and creating database schemas...")
        db.drop_all()
        db.create_all()

        print("Seeding demo user accounts...")
        # Demo Student
        student = User(name="Alex Rivers", email="student@canteenflow.com", role="student", eco_points=240)
        student.set_password("student123")

        # Additional Students for group order / SmartSwap demos
        s2 = User(name="Rahul Sharma", email="rahul@canteenflow.com", role="student", eco_points=110)
        s2.set_password("student123")
        s3 = User(name="Priya Patel", email="priya@canteenflow.com", role="student", eco_points=180)
        s3.set_password("student123")

        # Demo Vendor
        vendor_user = User(name="Central Canteen Manager", email="vendor@canteenflow.com", role="vendor")
        vendor_user.set_password("vendor123")

        # Demo Admin
        admin_user = User(name="Campus Admin", email="admin@canteenflow.com", role="admin")
        admin_user.set_password("admin123")

        db.session.add_all([student, s2, s3, vendor_user, admin_user])
        db.session.commit()

        print("Seeding canteen vendors...")
        v1 = Vendor(name="Central Canteen", location="Block A Ground Floor", description="Main campus cafeteria with wide variety of meals", average_prep_time=8, current_capacity=30)
        v2 = Vendor(name="South Indian Corner", location="Block B Food Court", description="Authentic dosas, idlis, and filter coffee", average_prep_time=6, current_capacity=20)
        v3 = Vendor(name="Burger Hub", location="Student Activity Center", description="Fresh gourmet burgers, rolls, and fries", average_prep_time=10, current_capacity=25)
        v4 = Vendor(name="Fresh Juice Station", location="Library Lawn", description="Refreshing natural juices and cold shakes", average_prep_time=4, current_capacity=15)

        db.session.add_all([v1, v2, v3, v4])
        db.session.commit()

        print("Seeding menu items...")
        menu_items_data = [
            # Central Canteen
            (v1.id, "Paneer Roll", "Spicy paneer stuffed in crispy wrap", "Rolls & Wraps", 70.0, 8, 40, 4.8),
            (v1.id, "Noodles", "Desi style stir-fry veg noodles", "Main Course", 75.0, 9, 35, 4.6),
            (v1.id, "Fried Rice", "Classic vegetable fried rice", "Main Course", 80.0, 9, 35, 4.5),
            (v1.id, "Sandwich", "Grilled vegetable & cheese sandwich", "Snacks", 65.0, 6, 8, 4.4),
            (v1.id, "Samosa", "Crispy potato samosa (2 pcs)", "Snacks", 20.0, 3, 60, 4.9),

            # South Indian Corner
            (v2.id, "Masala Dosa", "Crispy dosa with spiced potato masala", "South Indian", 60.0, 7, 50, 4.9),
            (v2.id, "Idli Vada", "Steamed idlis and crispy medu vada", "South Indian", 45.0, 5, 45, 4.7),

            # Burger Hub
            (v3.id, "Veg Burger", "Crispy veg patty burger with fresh lettuce", "Burgers", 80.0, 8, 30, 4.6),
            (v3.id, "Cheese Burger", "Double cheese loaded veg burger", "Burgers", 100.0, 10, 25, 4.8),

            # Fresh Juice Station
            (v4.id, "Lemon Juice", "Fresh squeezed mint lemon juice", "Beverages", 30.0, 3, 50, 4.8),
            (v4.id, "Mango Shake", "Thick mango shake with ice cream", "Beverages", 60.0, 5, 30, 4.9),
            (v4.id, "Cold Coffee", "Chilled whipped cold coffee", "Beverages", 70.0, 4, 35, 4.9)
        ]

        created_items = []
        for vendor_id, name, desc, category, price, prep_time, stock, pop in menu_items_data:
            item = MenuItem(
                vendor_id=vendor_id,
                name=name,
                description=desc,
                category=category,
                price=price,
                prep_time=prep_time,
                stock=stock,
                popularity_score=pop,
                availability=True
            )
            db.session.add(item)
            created_items.append(item)

        db.session.commit()

        # Seed Inventories
        for item in created_items:
            db.session.add(Inventory(vendor_id=item.vendor_id, menu_item_id=item.id, quantity=item.stock))

        print("Generating 180+ historical orders for ML model training...")
        now = datetime.utcnow()
        all_students = [student, s2, s3]

        for i in range(180):
            # Pick past date within 14 days
            days_ago = random.randint(0, 14)
            # Peak hours: 12-14 lunch, 17-18 evening snack
            hour = random.choices([11, 12, 13, 14, 15, 16, 17, 18], weights=[10, 35, 30, 15, 5, 5, 10, 5])[0]
            minute = random.randint(0, 59)
            order_dt = now - timedelta(days=days_ago)
            order_dt = order_dt.replace(hour=hour, minute=minute)

            u = random.choice(all_students)
            item = random.choice(created_items)
            qty = random.randint(1, 3)

            ord_obj = Order(
                user_id=u.id,
                vendor_id=item.vendor_id,
                order_number=f"CF-{1000 + i}",
                status='PICKED_UP' if days_ago > 0 else random.choice(['PREPARING', 'READY', 'PICKED_UP']),
                total=item.price * qty,
                pickup_time=order_dt.strftime('%I:%M %p'),
                pickup_counter=f"Counter {(i % 3) + 1}",
                pickup_token=f"TK-{1000 + i}",
                created_at=order_dt
            )
            db.session.add(ord_obj)
            db.session.flush()

            oi = OrderItem(
                order_id=ord_obj.id,
                menu_item_id=item.id,
                quantity=qty,
                price=item.price
            )
            db.session.add(oi)

            # Payment
            pm = Payment(order_id=ord_obj.id, user_id=u.id, amount=item.price * qty, method='UPI', status='SUCCESS', created_at=order_dt)
            db.session.add(pm)

        print("Seeding food waste records & eco transactions...")
        w1 = WasteRecord(vendor_id=v1.id, menu_item_id=created_items[3].id, quantity_wasted=3, reason="Over-preparation")
        w2 = WasteRecord(vendor_id=v1.id, menu_item_id=created_items[0].id, quantity_wasted=2, reason="Cancelled order")
        db.session.add_all([w1, w2])

        db.session.add_all([
            EcoTransaction(user_id=student.id, points=20, reason="Donated meal to Campus Food Bank"),
            EcoTransaction(user_id=student.id, points=15, reason="Offered order on SmartSwap"),
            EcoTransaction(user_id=student.id, points=10, reason="Chose recommended QueueZero slot")
        ])

        db.session.commit()

        print("Training AI Demand Prediction Model (RandomForest)...")
        train_success = train_model()
        print(f"ML Model training completed! Success: {train_success}")

        print("\n[SUCCESS] Seed database successfully completed! Ready for hackathon demo.")

if __name__ == '__main__':
    seed_database()
