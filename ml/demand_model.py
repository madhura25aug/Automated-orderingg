import os
import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'demand_rf_model.pkl')

class DemandModelManager:
    def __init__(self):
        self.model = None
        self.load_model()

    def train(self, data_df):
        """
        Train RandomForestRegressor on historical order dataset.
        Columns required in data_df: ['hour', 'day_of_week', 'vendor_id', 'menu_item_id', 'quantity']
        """
        if data_df.empty:
            return False

        X = data_df[['hour', 'day_of_week', 'vendor_id', 'menu_item_id']]
        y = data_df['quantity']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        self.model = RandomForestRegressor(n_estimators=50, random_state=42)
        self.model.fit(X_train, y_train)

        # Save trained model
        with open(MODEL_PATH, 'wb') as f:
            pickle.dump(self.model, f)
        return True

    def load_model(self):
        if os.path.exists(MODEL_PATH):
            try:
                with open(MODEL_PATH, 'rb') as f:
                    self.model = pickle.load(f)
            except Exception:
                self.model = None

    def predict(self, hour, day_of_week, vendor_id, menu_item_id):
        if self.model is None:
            # Fallback estimation if model not yet trained
            base = 12 if 12 <= hour <= 14 else 5
            return max(1, base + (menu_item_id % 3) * 2)

        try:
            features = pd.DataFrame([{
                'hour': hour,
                'day_of_week': day_of_week,
                'vendor_id': vendor_id,
                'menu_item_id': menu_item_id
            }])[['hour', 'day_of_week', 'vendor_id', 'menu_item_id']]
            pred = self.model.predict(features)[0]
            return max(1, int(round(pred)))
        except Exception:
            base = 12 if 12 <= hour <= 14 else 5
            return max(1, base + (menu_item_id % 3) * 2)

demand_ml_manager = DemandModelManager()
