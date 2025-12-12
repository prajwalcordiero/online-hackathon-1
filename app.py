import pandas as pd
from flask import Flask, render_template

app = Flask(__name__)
DATA_FILE = 'retail_data.csv'

# --- Utility Functions ---

def load_data():
    """Loads and returns the raw sales data."""
    try:
        df = pd.read_csv(DATA_FILE)
        return df, None
    except FileNotFoundError:
        return None, f"Error: Data file '{DATA_FILE}' not found."
    except Exception as e:
        return None, f"An unexpected error occurred: {e}"

def get_retail_insights(df):
    """
    Simulates demand forecasting and dynamic pricing logic 
    and returns the insights DataFrame.
    """
    if df is None:
        return None
        
    # 1. Simulate Demand Forecasting (Simple Average)
    avg_sales = df.groupby(['Product_ID', 'Store_ID', 'Region'])['Daily_Sales_Units'].mean().reset_index()
    avg_sales.rename(columns={'Daily_Sales_Units': 'Inventory_Forecast_Units'}, inplace=True)

    # 2. Get latest prices
    latest_prices = df.drop_duplicates(subset=['Product_ID', 'Store_ID'], keep='last')[
        ['Product_ID', 'Store_ID', 'Base_Price', 'Competitor_Price']
    ]
    insights_df = pd.merge(avg_sales, latest_prices, on=['Product_ID', 'Store_ID'], how='left')

    # 3. Simulate Dynamic Pricing Logic
    def suggest_dynamic_price(row):
        base_price = row['Base_Price']
        forecast = row['Inventory_Forecast_Units']
        
        if forecast > 70:
            new_price = base_price * 1.05
            action = "↑ Increase Price (High Demand/Low Stock Risk)"
        elif forecast < 40:
            new_price = base_price * 0.90
            action = "↓ Decrease Price (Low Demand/Overstock Risk)"
        else:
            new_price = base_price 
            action = "— Hold Price (Stable Demand)"
        
        return round(new_price, 2), action

    insights_df[['Suggested_Price', 'Pricing_Action']] = insights_df.apply(
        lambda row: pd.Series(suggest_dynamic_price(row)), axis=1
    )
    
    return insights_df


# --- Flask Routes ---

@app.route('/')
def index():
    df, error = load_data()
    message = error if error else "Data fetched and insights generated successfully."
    insights_html = None
    
    if df is not None:
        insights_df = get_retail_insights(df)
        if insights_df is not None:
            insights_html = insights_df.to_html(classes='table table-bordered table-striped', index=False)
            
    # Home Page shows only the Insights
    return render_template('index.html', insights_table=insights_html, message=message)

@app.route('/raw-data')
def raw_data_page():
    df, error = load_data()
    message = error if error else "Raw data loaded from CSV."
    data_html = None
    
    if df is not None:
        # Pass the raw data to a new template
        data_html = df.to_html(classes='table table-bordered table-sm', index=False)
        
    return render_template('raw_data.html', data_table=data_html, message=message)

@app.route('/about')
def about_page():
    return render_template('about.html')

@app.route('/contact')
def contact_page():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True)