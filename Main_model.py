#Main_model.py
import psycopg2
import pandas as pd
from event_impact import predict_event_impact

# Database connection parameters
DB_CONFIG = {
    "dbname": "turbo",
    "user": "postgres",
    "password": "vaish123",
    "host": "localhost",
    "port": "5432"
}

# SQL query to fetch sales data with weekly aggregation
QUERY = """
SELECT 
    oi.product_id,
    SUM(oi.quantity) AS total_quantity
FROM orderitem oi
JOIN "order" o ON oi.order_id = o.order_id
WHERE o.delivery_date IS NOT NULL
GROUP BY oi.product_id
ORDER BY oi.product_id;
"""

# Connect to PostgreSQL and fetch data
try:
    conn = psycopg2.connect(**DB_CONFIG)
    df = pd.read_sql_query(QUERY, conn)
    conn.close()
except Exception as e:
    print(f"Error connecting to the database: {e}")
    exit()

# Ensure product_id is an integer
df["product_id"] = df["product_id"].astype(int)

# Calculate average weekly sales per product
avg_weekly_sales = df.copy()
avg_weekly_sales["avg_weekly_sales"] = avg_weekly_sales["total_quantity"] / 52  # Assuming 52 weeks in a year

def determine_base_quantity(sales):
    if sales > 1000:
        return sales * 1.5
    elif sales > 500:
        return sales * 1.3
    else:
        return sales * 1.1

avg_weekly_sales["base_quantity"] = avg_weekly_sales["avg_weekly_sales"].apply(determine_base_quantity)

# Get event impact predictions
impact_dict = predict_event_impact()
impact_df = pd.DataFrame(list(impact_dict.items()), columns=['l2_catg', 'predicted_impact_percentage'])

# Adjust stock based on impact
def adjust_stock(base_quantity, impact_percentage):
    adjustment = base_quantity * (impact_percentage / 100)
    return base_quantity + adjustment, adjustment

# Assume each product belongs to an l2_catg
avg_weekly_sales["l2_catg"] = "default_category"  # Modify as per actual mapping

# Merge impact with base quantities
final_df = avg_weekly_sales.merge(impact_df, on='l2_catg', how='left').fillna({'predicted_impact_percentage': 0})
final_df["final_quantity"], final_df["event_impact"] = zip(*final_df.apply(
    lambda row: adjust_stock(row["base_quantity"], row["predicted_impact_percentage"]), axis=1
))

# Prepare final DataFrame for database insertion
forecast_df = final_df[["product_id", "final_quantity", "event_impact"]].copy()

# Ensure correct data types before inserting
forecast_df["product_id"] = forecast_df["product_id"].astype(int)
forecast_df["final_quantity"] = forecast_df["final_quantity"].astype(float)
forecast_df["event_impact"] = forecast_df["event_impact"].astype(float)

# Insert into PostgreSQL
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS forecast (
            product_id INT PRIMARY KEY,
            final_quantity FLOAT,
            event_impact FLOAT
        )
    """)
    conn.commit()
    
    # Insert or update records
    for _, row in forecast_df.iterrows():
        cursor.execute("""
            INSERT INTO forecast (product_id, final_quantity, event_impact)
            VALUES (%s, %s, %s)
            ON CONFLICT (product_id) DO UPDATE 
            SET final_quantity = EXCLUDED.final_quantity, 
                event_impact = EXCLUDED.event_impact;
        """, (row.product_id, row.final_quantity, row.event_impact))
    
    conn.commit()
    conn.close()
    print("Forecast table updated successfully!")
except Exception as e:
    print(f"Error updating forecast table: {e}")
