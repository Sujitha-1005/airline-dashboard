import pandas as pd
import numpy as np

class DataProcessor:
    def __init__(self, csv_path):
        """Initialize and load data"""
        self.df = pd.read_csv(csv_path)
        self.clean_data()
        
    def clean_data(self):
        """Clean and prepare data"""
        # Handle negative values
        self.df['Flight_Duration_Minutes'] = self.df['Flight_Duration_Minutes'].abs()
        self.df['Distance_Miles'] = self.df['Distance_Miles'].abs()
        
        # Convert datetime
        self.df['Departure_Time'] = pd.to_datetime(self.df['Departure_Time'])
        
        # Fill missing Frequent Flyer Status
        self.df['Frequent_Flyer_Status'] = self.df['Frequent_Flyer_Status'].fillna('None')
        
        # Remove duplicates
        self.df.drop_duplicates(subset=['Passenger_ID'], inplace=True)
        
    def get_summary_stats(self):
        """Get summary statistics for dashboard"""
        df = self.df
        
        total_flights = len(df)
        on_time_rate = (df['Flight_Status'] == 'On-time').sum() / total_flights * 100
        avg_delay = df[df['Flight_Status'] == 'Delayed']['Delay_Minutes'].mean()
        avg_satisfaction = df['Flight_Satisfaction_Score'].mean()
        total_revenue = df['Price_USD'].sum()
        cancellation_rate = (df['Flight_Status'] == 'Cancelled').sum() / total_flights * 100
        no_show_rate = df['No_Show'].sum() / total_flights * 100
        
        # Customer demographics
        avg_age = df['Age'].mean()
        male_ratio = (df['Gender'] == 'Male').sum() / total_flights * 100
        
        # Flight metrics
        avg_duration = df['Flight_Duration_Minutes'].mean()
        avg_distance = df['Distance_Miles'].mean()
        avg_price = df['Price_USD'].mean()
        
        # Most popular airline
        most_popular_airline = df['Airline'].value_counts().index[0]
        
        return {
            'total_flights': int(total_flights),
            'on_time_rate': round(on_time_rate, 2),
            'avg_delay': round(avg_delay, 2) if not pd.isna(avg_delay) else 0,
            'avg_satisfaction': round(avg_satisfaction, 2),
            'total_revenue': round(total_revenue, 2),
            'cancellation_rate': round(cancellation_rate, 2),
            'no_show_rate': round(no_show_rate, 2),
            'avg_age': round(avg_age, 1),
            'male_ratio': round(male_ratio, 1),
            'avg_duration': round(avg_duration, 1),
            'avg_distance': round(avg_distance, 1),
            'avg_price': round(avg_price, 2),
            'most_popular_airline': most_popular_airline
        }
    
    def get_airline_comparison(self):
        """Compare airlines performance"""
        return self.df.groupby('Airline').agg({
            'Flight_Satisfaction_Score': 'mean',
            'Delay_Minutes': 'mean',
            'Price_USD': 'mean',
            'Flight_ID': 'count'
        }).reset_index()
    
    def get_route_analysis(self):
        """Analyze popular routes"""
        routes = self.df.groupby(['Departure_Airport', 'Arrival_Airport']).agg({
            'Flight_ID': 'count',
            'Price_USD': 'mean',
            'Delay_Minutes': 'mean',
            'Flight_Satisfaction_Score': 'mean'
        }).reset_index()
        
        routes = routes.sort_values('Flight_ID', ascending=False)
        return routes.head(15)
    
    def get_temporal_trends(self):
        """Get temporal trends"""
        df = self.df.copy()
        df['Month'] = df['Departure_Time'].dt.month
        df['Hour'] = df['Departure_Time'].dt.hour
        df['DayOfWeek'] = df['Departure_Time'].dt.dayofweek
        
        return {
            'by_month': df.groupby('Month').size().to_dict(),
            'by_hour': df.groupby('Hour').size().to_dict(),
            'by_day': df.groupby('DayOfWeek').size().to_dict()
        }
    
    def get_customer_segments(self):
        """Analyze customer segments"""
        segments = self.df.groupby(['Income_Level', 'Travel_Purpose']).agg({
            'Flight_ID': 'count',
            'Price_USD': 'mean',
            'Flight_Satisfaction_Score': 'mean'
        }).reset_index()
        
        return segments