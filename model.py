import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib
import os

class FlightPredictor:
    def __init__(self, df):
        """Initialize predictor with dataframe"""
        self.df = df.copy()
        self.delay_model = None
        self.satisfaction_model = None
        self.noshow_model = None
        self.label_encoders = {}
        
    def prepare_features(self, df, target_col=None):
        """Prepare features for ML models"""
        df = df.copy()
        
        # Select features
        categorical_cols = ['Airline', 'Departure_Airport', 'Arrival_Airport', 
                          'Gender', 'Income_Level', 'Travel_Purpose', 
                          'Seat_Class', 'Check_in_Method', 'Seat_Selected']
        
        numerical_cols = ['Flight_Duration_Minutes', 'Distance_Miles', 'Price_USD',
                         'Age', 'Bags_Checked', 'Booking_Days_In_Advance', 'Weather_Impact']
        
        # Encode categorical variables
        for col in categorical_cols:
            if col in df.columns:
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                    self.label_encoders[col].fit(df[col].astype(str))
                df[col] = self.label_encoders[col].transform(df[col].astype(str))
        
        # Select final features
        feature_cols = [col for col in categorical_cols + numerical_cols if col in df.columns]
        X = df[feature_cols]
        
        if target_col and target_col in df.columns:
            y = df[target_col]
            return X, y
        
        return X
    
    def train_models(self):
        """Train all prediction models"""
        print("Training delay prediction model...")
        self.train_delay_model()
        
        print("Training satisfaction prediction model...")
        self.train_satisfaction_model()
        
        print("Training no-show prediction model...")
        self.train_noshow_model()
        
        # Save models
        self.save_models()
        
    def train_delay_model(self):
        """Train delay prediction model"""
        # Filter delayed flights
        delayed_df = self.df[self.df['Flight_Status'] == 'Delayed'].copy()
        
        if len(delayed_df) < 100:
            print("Warning: Not enough delayed flights for training")
            return
        
        X, y = self.prepare_features(delayed_df, 'Delay_Minutes')
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.delay_model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
        self.delay_model.fit(X_train, y_train)
        
        score = self.delay_model.score(X_test, y_test)
        print(f"Delay model R² score: {score:.3f}")
    
    def train_satisfaction_model(self):
        """Train satisfaction prediction model"""
        X, y = self.prepare_features(self.df, 'Flight_Satisfaction_Score')
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.satisfaction_model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
        self.satisfaction_model.fit(X_train, y_train)
        
        score = self.satisfaction_model.score(X_test, y_test)
        print(f"Satisfaction model R² score: {score:.3f}")
    
    def train_noshow_model(self):
        """Train no-show prediction model"""
        X, y = self.prepare_features(self.df, 'No_Show')
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.noshow_model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
        self.noshow_model.fit(X_train, y_train)
        
        score = self.noshow_model.score(X_test, y_test)
        print(f"No-show model accuracy: {score:.3f}")
    
    def predict_delay(self, input_data):
        """Predict delay minutes for a flight"""
        if self.delay_model is None:
            return {"error": "Model not trained"}
        
        df_input = pd.DataFrame([input_data])
        X = self.prepare_features(df_input)
        
        prediction = self.delay_model.predict(X)[0]
        return {
            'predicted_delay_minutes': round(max(0, prediction), 1),
            'delay_category': 'Short' if prediction < 30 else 'Medium' if prediction < 60 else 'Long'
        }
    
    def predict_satisfaction(self, input_data):
        """Predict satisfaction score"""
        if self.satisfaction_model is None:
            return {"error": "Model not trained"}
        
        df_input = pd.DataFrame([input_data])
        X = self.prepare_features(df_input)
        
        prediction = self.satisfaction_model.predict(X)[0]
        return {
            'predicted_satisfaction': round(np.clip(prediction, 0, 10), 2),
            'satisfaction_level': 'Low' if prediction < 4 else 'Medium' if prediction < 7 else 'High'
        }
    
    def predict_noshow(self, input_data):
        """Predict no-show probability"""
        if self.noshow_model is None:
            return {"error": "Model not trained"}
        
        df_input = pd.DataFrame([input_data])
        X = self.prepare_features(df_input)
        
        prediction = self.noshow_model.predict(X)[0]
        probability = self.noshow_model.predict_proba(X)[0]
        
        return {
            'will_noshow': bool(prediction),
            'noshow_probability': round(probability[1] * 100, 2),
            'risk_level': 'Low' if probability[1] < 0.3 else 'Medium' if probability[1] < 0.6 else 'High'
        }
    
    def save_models(self):
        """Save trained models"""
        os.makedirs('models', exist_ok=True)
        
        if self.delay_model:
            joblib.dump(self.delay_model, 'models/delay_model.pkl')
        if self.satisfaction_model:
            joblib.dump(self.satisfaction_model, 'models/satisfaction_model.pkl')
        if self.noshow_model:
            joblib.dump(self.noshow_model, 'models/noshow_model.pkl')
        
        joblib.dump(self.label_encoders, 'models/label_encoders.pkl')
        print("Models saved successfully!")