from flask import Flask, render_template
import pandas as pd
from sqlalchemy import create_engine

# Replace these variables with your actual database credentials
DB_TYPE = 'mysql'
DB_DRIVER = 'pymysql'
DB_USER = 'root'
DB_PASS = 'R1a2m3$%^'
DB_HOST = 'localhost'
DB_PORT = '3306'
DB_NAME = 'traveldb'

# Create the Flask application
app = Flask(__name__, template_folder='D:\\Python_Intern_project\\template')

# Create the database engine
DATABASE_URL = f"{DB_TYPE}+{DB_DRIVER}://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

def execute_query(query, exclude_india_total=False):
    """Executes the given SQL query and returns the result as a DataFrame."""
    df = pd.read_sql(query, engine)
    if exclude_india_total:
        df = df[df['City'] != 'India Total']
    return df

def exclude_last_row(df):
    """Excludes the last row from the given DataFrame."""
    return df.iloc[:-1].copy()

def calculate_rate(numerator, denominator):
    """Calculates the rate as a percentage."""
    return (numerator / denominator) * 100 if denominator > 0 else 0

# Route to render the dashboard template
@app.route('/')
def dashboard():
    # Define queries
    queries = {
        "Total Bookings Canceled by Customers": "SELECT `Bookings`, `User Cancellation Rate` FROM `All-time Table-All Cities`;",
        "Average Distance per Trip (km)": "SELECT `Average Distance per Trip (km)` FROM `All-time Table-All Cities`;",
        "Average Fare per Trip": "SELECT `Average Fare per Trip` FROM `All-time Table-All Cities`;",
        "Top Two Locations by Trip Count": "SELECT `City`, `Completed Trips` FROM `All-time Table-All Cities`;",
        "Total Unique Trips excluding the last cell": "SELECT `Completed Trips` FROM `All-time Table-All Cities`;",
        "Total Searches excluding the last cell": "SELECT `Searches` FROM `All-time Table-All Cities`;",
        "Total Searches that got an estimate": "SELECT `Searches which got estimate` FROM `All-time Table-All Cities`;",
        "Total Searches for quotes": "SELECT `Searches for Quotes` FROM `All-time Table-All Cities`;",
        "Total Searches that resulted in quotes": "SELECT `Searches which got Quotes` FROM `All-time Table-All Cities`;",
        "Total Distance Traveled": "SELECT `Distance Travelled (km)` FROM `All-time Table-All Cities`;",
        "Rate of Estimates to Searches for Quotes": "SELECT `Searches which got estimate`, `Searches for Quotes` FROM `All-time Table-All Cities`;",
        "Quote Acceptance Rate": "SELECT `Searches`, `Searches which got Quotes` FROM `All-time Table-All Cities`;",
        "City with the highest total fare": "SELECT `City`, `Drivers' Earnings` FROM `All-time Table-All Cities`;",
        "City with the highest number of cancellations": "SELECT `City`, `Cancelled Bookings` FROM `All-time Table-All Cities`;",
        "City with the highest number of completed trips": "SELECT `City`, `Completed Trips` FROM `All-time Table-All Cities`;",
        "Duration with highest trip count and total fare": "SELECT `Time`, `Completed Trips`, `Drivers' Earnings` FROM `all-time trip trends-all cities`;",
        "Booking Cancellation Rate": "SELECT `City`, `Bookings`, `Cancelled Bookings` FROM `All-time Table-All Cities`;",
        "Total Completed Trips": "SELECT `Completed Trips` FROM `All-time Table-All Cities`;",
        "Total Drivers' Earnings": "SELECT `Drivers' Earnings` FROM `All-time Table-All Cities`;"
    }
    
    results = {}
    
    # Execute each query and store the results
    for description, query in queries.items():
        exclude_india_total = description in [
            "City with the highest total fare",
            "City with the highest number of cancellations",
            "City with the highest number of completed trips",
            "Top Two Locations by Trip Count"
        ]
        df = exclude_last_row(execute_query(query, exclude_india_total=exclude_india_total))
        
        if description in ["Rate of Estimates to Searches for Quotes", "Quote Acceptance Rate"]:
            if not df.empty:
                num = df.iloc[:, 0].sum()
                denom = df.iloc[:, 1].sum()
                rate = calculate_rate(num, denom)
            else:
                rate = 0
            results[description] = f"{rate:.2f}%"
        
        elif description == "Total Distance Traveled":
            total_distance = df.iloc[:, 0].sum() if not df.empty else 0
            results[description] = f"{total_distance}"
        
        elif description in ["City with the highest total fare", "City with the highest number of cancellations", "City with the highest number of completed trips"]:
            if not df.empty:
                col_name = df.columns[1]
                df[col_name] = pd.to_numeric(df[col_name], errors='coerce')
                max_city = df.groupby('City')[col_name].sum().idxmax()
                max_value = df.groupby('City')[col_name].sum().max()
            else:
                max_city = None
                max_value = 0
            results[description] = f"{max_city} with {max_value}"
        
        elif description == "Duration with highest trip count and total fare":
            if not df.empty:
                df['Completed Trips'] = pd.to_numeric(df['Completed Trips'], errors='coerce')
                df['Drivers\' Earnings'] = pd.to_numeric(df['Drivers\' Earnings'], errors='coerce')
                grouped = df.groupby('Time').agg({
                    'Completed Trips': 'sum',
                    'Drivers\' Earnings': 'sum'
                }).reset_index()
                duration_highest_trip = grouped.loc[grouped['Completed Trips'].idxmax()]
                duration_highest_fare = grouped.loc[grouped['Drivers\' Earnings'].idxmax()]
                results["Duration with highest trip count"] = f"{duration_highest_trip}"
                results["Duration with highest total fare"] = f"{duration_highest_fare}"
            else:
                results["Duration with highest trip count"] = "No data found"
                results["Duration with highest total fare"] = "No data found"
        
        elif description == "Booking Cancellation Rate":
            if not df.empty:
                df['Bookings'] = pd.to_numeric(df['Bookings'], errors='coerce')
                df['Cancelled Bookings'] = pd.to_numeric(df['Cancelled Bookings'], errors='coerce')
                if df['Bookings'].sum() > 0:
                    cancellation_rate = (df['Cancelled Bookings'].sum() / df['Bookings'].sum()) * 100
                else:
                    cancellation_rate = 0
                results[description] = f"{cancellation_rate:.2f}%"
            else:
                results[description] = "No data found"
        
        else:
            result = df.iloc[:, 0].sum() if not df.empty else 0
            results[description] = f"{result}"
    
    top_locations_query = "SELECT `City`, `Completed Trips` FROM `All-time Table-All Cities` ORDER BY `Completed Trips` DESC;"
    top_locations = execute_query(top_locations_query, exclude_india_total=True)
    results['top_locations'] = {
        'labels': top_locations['City'][:2].tolist(),
        'data': top_locations['Completed Trips'][:2].tolist()
    }
    
    return render_template('dashboard.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)
