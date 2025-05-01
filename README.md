# **AI Dark Store Management for Q-Com**

## Project Overview
This project is an AI-driven dark store management system designed to optimize inventory forecasting and stock management for Q-Com. It leverages historical sales data, event impacts, and machine learning models to predict demand fluctuations and adjust stock quantities accordingly.

## Technologies Used
- Python 3
- PostgreSQL
- Pandas
- scikit-learn (RandomForestRegressor)
- psycopg2 (PostgreSQL database adapter for Python)

## Database Schema Overview
The project uses a PostgreSQL database with the following key tables:

- **users**: Stores user information.
- **agent**: Stores delivery agent information.
- **L1Catg, L2Catg, L3Catg**: Hierarchical product category tables.
- **product**: Product details including category, price, description, brand, and rating.
- **stock**: Current stock quantities per product.
- **forecast**: Forecasted stock quantities per product.
- **cart, cartItem**: Shopping cart and cart items for users.
- **order, orderitem**: Order details and associated items.
- **eventcongif, weathercongif**: Configuration tables for event and weather impacts on demand.

## Key Scripts

### `event_impact.py`
- Connects to the PostgreSQL database to fetch historical sales and event data.
- Trains a RandomForestRegressor model to predict the impact of upcoming events on product category sales.
- Returns predicted impact percentages by product category.

### `Main_model.py`
- Connects to the PostgreSQL database to fetch aggregated sales data.
- Calculates average weekly sales and determines base stock quantities.
- Uses predictions from `event_impact.py` to adjust stock quantities based on event impacts.
- Updates the `forecast` table in the database with the final stock quantity forecasts.

## Setup and Usage

1. **Database Setup**
   - Ensure PostgreSQL is installed and running.
   - Create a database named `turbo`.
   - Execute the `schema.sql` script to create the necessary tables and schema.
   - Populate the database with relevant data for products, orders, events, etc.

2. **Python Environment**
   - Install required Python packages:
     ```
     pip install pandas psycopg2-binary scikit-learn numpy
     ```
   
3. **Running the Forecast**
   - Run `Main_model.py` to generate stock forecasts adjusted for event impacts:
     ```
     python Main_model.py
     ```
   - The script will update the `forecast` table in the database with the latest predictions.

## Notes
- Database connection parameters are hardcoded in the scripts; update them as needed for your environment.
- The event impact prediction model uses historical sales and event data to train and predict demand changes.
- The system assumes 52 weeks in a year for weekly sales calculations.

## License
This project is provided as-is without any warranty. Use at your own risk.
