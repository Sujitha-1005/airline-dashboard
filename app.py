from flask import Flask, render_template, jsonify, request
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
from data_processor import DataProcessor
from model import FlightPredictor

app = Flask(__name__)

# Initialize data processor and predictor
data_processor = DataProcessor('data/flights_data.csv')
predictor = FlightPredictor(data_processor.df)

@app.route('/')
def index():
    """Main dashboard page"""
    stats = data_processor.get_summary_stats()
    return render_template('index.html', stats=stats)

@app.route('/analytics')
def analytics():
    """Analytics page"""
    return render_template('analytics.html')

@app.route('/predictions')
def predictions():
    """Predictions page"""
    return render_template('predictions.html')

@app.route('/api/kpi-data')
def kpi_data():
    """Get KPI metrics"""
    stats = data_processor.get_summary_stats()
    return jsonify(stats)

@app.route('/api/airline-performance')
def airline_performance():
    """Get airline performance metrics"""
    df = data_processor.df
    
    airline_stats = df.groupby('Airline').agg({
        'Flight_Satisfaction_Score': 'mean',
        'Delay_Minutes': 'mean',
        'Price_USD': 'mean',
        'Flight_ID': 'count'
    }).reset_index()
    
    airline_stats.columns = ['Airline', 'Avg_Satisfaction', 'Avg_Delay', 'Avg_Price', 'Total_Flights']
    
    return jsonify(airline_stats.to_dict('records'))

@app.route('/api/delay-distribution')
def delay_distribution():
    """Get delay distribution data"""
    df = data_processor.df
    delays = df[df['Flight_Status'] == 'Delayed']['Delay_Minutes'].value_counts().sort_index()
    
    return jsonify({
        'delay_minutes': delays.index.tolist(),
        'count': delays.values.tolist()
    })

@app.route('/api/route-analysis')
def route_analysis():
    """Get popular routes"""
    df = data_processor.df
    
    routes = df.groupby(['Departure_Airport', 'Arrival_Airport']).agg({
        'Flight_ID': 'count',
        'Price_USD': 'mean',
        'Delay_Minutes': 'mean'
    }).reset_index()
    
    routes = routes.sort_values('Flight_ID', ascending=False).head(10)
    routes['Route'] = routes['Departure_Airport'] + ' → ' + routes['Arrival_Airport']
    
    return jsonify(routes.to_dict('records'))

@app.route('/api/time-series')
def time_series():
    """Get time series data"""
    df = data_processor.df.copy()
    df['Departure_Time'] = pd.to_datetime(df['Departure_Time'])
    df['Date'] = df['Departure_Time'].dt.date
    
    daily_stats = df.groupby('Date').agg({
        'Flight_ID': 'count',
        'Delay_Minutes': 'mean',
        'Flight_Satisfaction_Score': 'mean'
    }).reset_index()
    
    daily_stats['Date'] = daily_stats['Date'].astype(str)
    
    return jsonify(daily_stats.to_dict('records'))

@app.route('/api/satisfaction-factors')
def satisfaction_factors():
    """Analyze factors affecting satisfaction"""
    df = data_processor.df
    
    factors = {
        'seat_class': df.groupby('Seat_Class')['Flight_Satisfaction_Score'].mean().to_dict(),
        'check_in': df.groupby('Check_in_Method')['Flight_Satisfaction_Score'].mean().to_dict(),
        'travel_purpose': df.groupby('Travel_Purpose')['Flight_Satisfaction_Score'].mean().to_dict()
    }
    
    return jsonify(factors)

@app.route('/api/predict-delay', methods=['POST'])
def predict_delay():
    """Predict flight delay"""
    data = request.json
    
    # Add default values for all required features
    default_data = {
        'Airline': data.get('Airline', 'Delta'),
        'Departure_Airport': data.get('Departure_Airport', 'JFK'),
        'Arrival_Airport': data.get('Arrival_Airport', 'LAX'),
        'Gender': 'Male',
        'Income_Level': 'Medium',
        'Travel_Purpose': 'Business',
        'Seat_Class': 'Economy',
        'Check_in_Method': 'Online',
        'Seat_Selected': 'Window',
        'Flight_Duration_Minutes': int(data.get('Flight_Duration_Minutes', 180)),
        'Distance_Miles': int(data.get('Distance_Miles', 1000)),
        'Price_USD': float(data.get('Price_USD', 250)),
        'Age': 35,
        'Bags_Checked': 1,
        'Booking_Days_In_Advance': 30,
        'Weather_Impact': int(data.get('Weather_Impact', 0))
    }
    
    try:
        prediction = predictor.predict_delay(default_data)
        return jsonify({
            'success': True,
            'prediction': prediction
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/predict-satisfaction', methods=['POST'])
def predict_satisfaction():
    """Predict satisfaction score"""
    data = request.json
    
    # Add default values for all required features
    default_data = {
        'Airline': data.get('Airline', 'Delta'),
        'Departure_Airport': 'JFK',
        'Arrival_Airport': 'LAX',
        'Gender': 'Male',
        'Income_Level': data.get('Income_Level', 'Medium'),
        'Travel_Purpose': data.get('Travel_Purpose', 'Business'),
        'Seat_Class': data.get('Seat_Class', 'Economy'),
        'Check_in_Method': data.get('Check_in_Method', 'Online'),
        'Seat_Selected': 'Window',
        'Flight_Duration_Minutes': int(data.get('Flight_Duration_Minutes', 180)),
        'Distance_Miles': 1000,
        'Price_USD': float(data.get('Price_USD', 250)),
        'Age': 35,
        'Bags_Checked': 1,
        'Booking_Days_In_Advance': 30,
        'Weather_Impact': 0
    }
    
    try:
        prediction = predictor.predict_satisfaction(default_data)
        return jsonify({
            'success': True,
            'prediction': prediction
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/predict-noshow', methods=['POST'])
def predict_noshow():
    """Predict no-show probability"""
    data = request.json
    
    # Add default values for all required features
    default_data = {
        'Airline': 'Delta',
        'Departure_Airport': 'JFK',
        'Arrival_Airport': 'LAX',
        'Gender': 'Male',
        'Income_Level': data.get('Income_Level', 'Medium'),
        'Travel_Purpose': data.get('Travel_Purpose', 'Business'),
        'Seat_Class': data.get('Seat_Class', 'Economy'),
        'Check_in_Method': 'Online',
        'Seat_Selected': 'Window',
        'Flight_Duration_Minutes': 180,
        'Distance_Miles': 1000,
        'Price_USD': float(data.get('Price_USD', 250)),
        'Age': int(data.get('Age', 35)),
        'Bags_Checked': 1,
        'Booking_Days_In_Advance': int(data.get('Booking_Days_In_Advance', 30)),
        'Weather_Impact': 0
    }
    
    try:
        prediction = predictor.predict_noshow(default_data)
        return jsonify({
            'success': True,
            'prediction': prediction
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/revenue-analysis')
def revenue_analysis():
    """Revenue analysis by various factors"""
    df = data_processor.df
    
    revenue_by_airline = df.groupby('Airline')['Price_USD'].sum().to_dict()
    revenue_by_class = df.groupby('Seat_Class')['Price_USD'].sum().to_dict()
    
    return jsonify({
        'by_airline': revenue_by_airline,
        'by_class': revenue_by_class
    })

if __name__ == '__main__':
    print("🚀 Starting Airline Performance Dashboard...")
    print("📊 Loading data and training models...")
    predictor.train_models()
    print("✅ Models trained successfully!")
    print("🌐 Dashboard running at: http://localhost:5000")
    app.run(debug=True, port=5000)