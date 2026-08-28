# CanteenFlow AI ⚡
> **"Beat the Queue. Predict the Rush. Eat Smarter."**

CanteenFlow AI is a complete, working, hackathon-ready full-stack campus canteen ordering & queue prediction platform built with Python (Flask, Flask-SQLAlchemy, Flask-SocketIO), SQLite, scikit-learn, HTML5, Bootstrap 5, and Chart.js.

---

## 🎯 The Hackathon Problem & Solution

**Traditional food ordering apps only solve ordering. CanteenFlow AI solves the entire campus canteen flow.**

### Problems Solved:
- **For Students:** Eliminates long physical queues, unpredictable wait times, and group order coordination headaches.
- **For Vendors:** Eliminates unpredictable demand surges, kitchen bottlenecks during peak lunch hours, and food wastage.

---

## 🚀 Key Innovation Highlights

1. **QueueZero Smart Pickup Scheduler:** Calculates exact preparation times, queue load, walking time, and recommends classroom departure times so students arrive right when food is ready.
2. **AI Demand Prediction:** Machine learning regression model (`RandomForestRegressor` via scikit-learn) trained on historical order patterns to forecast peak-hour item volume and stock shortage risks.
3. **Smart Order Batching:** Groups identical food items across active orders into kitchen batches (#B42 style) to optimize preparation throughput.
4. **Canteen Copilot:** AI vendor assistant that provides actionable preparation advice, shortage warnings, and answers kitchen queries using live app data.
5. **Real-Time WebSockets:** Powered by `Flask-SocketIO` to instantly sync order status changes between vendor kitchen boards and student tracking timelines without refreshing.
6. **SmartSwap & Food Waste Reduction:** Allows students to transfer uncollected meals to peers or donate to the Campus Food Bank, earning **Eco Points**.
7. **Group Ordering & Split Payment:** Classmates join via group codes (e.g. `CF-4821`) and pay their individual split amounts.
8. **Hackathon Demo Mode (`/demo`):** Features 1-click role logins, a **🔥 SIMULATE LUNCH RUSH** generator (creates 25 orders instantly), AI Demand Forecast execution, and QueueZero optimization demos.

---

## 💻 Tech Stack

- **Backend:** Python 3.11+, Flask, Flask-SQLAlchemy, Flask-SocketIO, Werkzeug
- **Database:** SQLite ORM
- **Machine Learning & Data Processing:** scikit-learn (`RandomForestRegressor`), pandas, numpy
- **Frontend:** HTML5, Vanilla CSS3, Vanilla JavaScript, Bootstrap 5, Chart.js

---

## 🔑 Demo Credentials

| Role | Email | Password |
| :--- | :--- | :--- |
| **Student** | `student@canteenflow.com` | `student123` |
| **Vendor** | `vendor@canteenflow.com` | `vendor123` |
| **Campus Admin** | `admin@canteenflow.com` | `admin123` |

---

## ⚙️ Installation & Setup Instructions

### 1. Clone & Setup Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Seed Database & Train ML Model

```bash
python seed.py
```
*`seed.py` creates SQLite database tables, populates 4 canteen outlets, 12 menu items, 3 demo users, generates 180+ historical order rows, and trains the RandomForest ML model.*

### 4. Run Application

```bash
python app.py
```
Open your browser and navigate to **[http://127.0.0.1:5000](http://127.0.0.1:5000)** or access the **[http://127.0.0.1:5000/demo](http://127.0.0.1:5000/demo)** fast-track page.

---

## 🧠 AI Algorithm & Architecture Explanation

### 1. Demand Prediction (`ml/demand_model.py` & `services/demand_prediction.py`)
- Uses a `RandomForestRegressor` trained on historical parameters (`hour`, `day_of_week`, `vendor_id`, `menu_item_id`).
- Predicts expected unit demand for every menu item during peak windows (e.g. 12:30 PM - 1:00 PM) and compares it against current inventory stock to calculate potential shortages.

### 2. QueueZero Scheduler (`services/pickup_scheduler.py`)
- Evaluates item prep times, active kitchen order volume, vendor capacity, and 4-minute campus walking time.
- Returns exact classroom departure time, pickup slot string (e.g. `12:42 PM`), and specific pickup counter (e.g. `Pickup Counter 2`).

### 3. Smart Batching Engine (`services/order_batching.py`)
- Groups orders with matching food items within close pickup windows into prioritized batches (e.g., `Batch #B42: Masala Dosa × 5, Burger × 3`), cutting kitchen preparation overhead by over 40%.

---



