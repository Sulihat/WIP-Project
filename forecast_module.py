# forecast_module.py

import pandas as pd
from model_utils import (
    load_revenue_data,
    load_macro_data,
    forecast_revenue_streams,
    evaluate_models,
    merge_forecast_with_history  # ✅ Import the new function
)

def run_forecasting_pipeline(revenue_df, macro_df):
    # Reconstruct monthly datasets expected by forecasting functions
    revenue_df['Order Date'] = pd.to_datetime(revenue_df['Order Date'])
    revenue_df['Revenue'] = revenue_df['Unit Price'] * revenue_df['Quantity']
    
    monthly_revenue = (
        revenue_df.groupby([pd.Grouper(key='Order Date', freq='M'), 'Revenue Stream'])['Revenue']
        .sum()
        .reset_index()
    )
    monthly_revenue.rename(columns={'Order Date': 'ds', 'Revenue': 'y'}, inplace=True)

    macro_df['ds'] = pd.to_datetime(macro_df['Order Date'])
    macro_df = macro_df.drop(columns='Order Date')
    df_macro_monthly = macro_df.groupby(pd.Grouper(key='ds', freq='M'))[
        ['Exchange Rate', 'Inflation Rate']
    ].mean().reset_index()

    # Run forecast
    forecast_results = forecast_revenue_streams(monthly_revenue, df_macro_monthly, macro_df)

    # Merge forecast and history for reporting
    combined_df = merge_forecast_with_history(forecast_results, monthly_revenue)  # ✅

    # Evaluate model
    cv_results, performance_df = evaluate_models(revenue_df)

    return forecast_results, performance_df, combined_df  # ✅ Return the merged report
