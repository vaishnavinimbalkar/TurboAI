# event_impact.py
import psycopg2
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from contextlib import closing

# Database connection parameters
DEFAULT_DB_CONFIG = {
    "dbname": "turbo",
    "user": "postgres",
    "password": "vaish123",
    "host": "localhost",
    "port": "5432"
}

def get_db_connection(db_config):
    """Create and return a database connection."""
    return psycopg2.connect(**db_config)

def execute_query(query, conn, params=None):
    """Execute SQL query and return results as DataFrame."""
    return pd.read_sql_query(query, conn, params=params)

def predict_event_impact(db_config=None, prediction_days=7):
    """
    Predict the impact of events on product categories for the specified number of days.
    
    Args:
        db_config (dict): Database connection parameters
        prediction_days (int): Number of days to predict for
        
    Returns:
        dict: Dictionary with l2_catg as keys and predicted impact as values
    """
    # Use default DB config if none provided
    if db_config is None:
        db_config = DEFAULT_DB_CONFIG
    
    # Connect to PostgreSQL
    try:
        with closing(get_db_connection(db_config)) as conn:
            # Get historical data for model training
            TRAINING_QUERY = """
            SELECT e.event_type, p.l2_catg, SUM(oi.quantity) AS total_sales, 
                   DATE_PART('year', o.delivery_date) AS sales_year
            FROM orderitem oi
            JOIN "order" o ON oi.order_id = o.order_id
            JOIN product p ON oi.product_id = p.product_id
            JOIN event e ON o.delivery_date = e.date
            WHERE o.delivery_date IS NOT NULL
            GROUP BY e.event_type, p.l2_catg, sales_year
            ORDER BY sales_year, e.event_type, p.l2_catg;
            """
            
            df = execute_query(TRAINING_QUERY, conn)
            
            # Get upcoming events for next n days
            today = datetime.now()
            end_date = today + timedelta(days=prediction_days)
            UPCOMING_EVENTS_QUERY = """
            SELECT date, event_type
            FROM event
            WHERE date >= %s AND date <= %s
            ORDER BY date;
            """
            
            upcoming_events = execute_query(
                UPCOMING_EVENTS_QUERY, 
                conn, 
                params=(today.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
            )
            
            # Get product categories
            CATEGORIES_QUERY = """
            SELECT DISTINCT l2_catg FROM product;
            """
            categories = execute_query(CATEGORIES_QUERY, conn)
    
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return {}
    
    # Check if we have data to work with
    if df.empty:
        print("No historical data found.")
        return {}
    
    if upcoming_events.empty:
        print(f"No upcoming events in the next {prediction_days} days.")
        return {}
    
    if categories.empty:
        print("No product categories found.")
        return {}
    
    # Pivot the data to compute percentage change year-over-year
    print("Preparing data for modeling...")
    df_pivot = df.pivot_table(index=['event_type', 'l2_catg'], columns='sales_year', values='total_sales', fill_value=0)
    df_pivot = df_pivot.pct_change(axis=1) * 100  # Convert to percentage change
    df_pivot = df_pivot.dropna(axis=1)  # Drop NaN values (if missing data)
    df_pivot.reset_index(inplace=True)
    
    # Rename target column (last available year)
    target_col = df_pivot.columns[-1]
    df_pivot.rename(columns={target_col: 'percentage_change'}, inplace=True)
    
    # Train the model
    print("Training model...")
    X = pd.get_dummies(df_pivot[['event_type', 'l2_catg']])
    y = df_pivot['percentage_change']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
   
    
    # Store all feature names
    all_features = X.columns
    model_features = model.feature_names_in_
    
    # Function to predict percentage change
    def predict_impact(event_type, l2_catg):
        # Create a dataframe with all features set to 0
        input_data = pd.DataFrame(0, index=[0], columns=all_features)
        
        # Safely set the event type and category features
        event_col = f'event_type_{event_type}'
        catg_col = f'l2_catg_{l2_catg}'
        
        if event_col in all_features:
            input_data[event_col] = 1
        if catg_col in all_features:
            input_data[catg_col] = 1
            
        # Only use the columns that the model was trained on
        input_data = input_data[model_features]
        
        return model.predict(input_data)[0]
    
    # Generate predictions for the next n days
    print(f"Generating predictions for next {prediction_days} days...")
    
    # Get today's event type
    today_events = upcoming_events[upcoming_events['date'] == today.replace(hour=0, minute=0, second=0, microsecond=0).date()]
    
    if today_events.empty:
        print("No events found for today.")
        return {}
    
    today_event_type = today_events.iloc[0]['event_type']
    print(f"Today's event type: {today_event_type}")
    
    # Create dictionary with category as key and predicted impact as value
    impact_dict = {}
    
    for _, category_row in categories.iterrows():
        category = category_row['l2_catg']
        try:
            impact = predict_impact(today_event_type, category)
            impact_dict[category] = impact
        except Exception as e:
            print(f"Error predicting for {category}: {e}")
            impact_dict[category] = 0.0  # Default to no impact on error
    
    return impact_dict

# If this script is run directly, execute the function and show results
if __name__ == "__main__":
    impact_dict = predict_event_impact()
    
    if impact_dict:
        print("\nPredicted Category Impacts:")
        print("=" * 40)
        print(f"{'Category':<20} {'Predicted Impact':<20}")
        print("-" * 40)
        
        for category, impact in sorted(impact_dict.items(), key=lambda x: x[1], reverse=True):
            print(f"{category:<20} {impact:>6.2f}%")
    else:
        print("No impact predictions generated.")