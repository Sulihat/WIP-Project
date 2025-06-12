import pandas as pd
from prophet import Prophet
from prophet.diagnostics import cross_validation, performance_metrics


# === 1. Load and Preprocess Revenue Data ===
def load_revenue_data(filepath):
    df = pd.read_csv(filepath)
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['Revenue'] = df['Unit Price'] * df['Quantity']
    monthly_revenue = (
        df.groupby([pd.Grouper(key='Order Date', freq='M'), 'Revenue Stream'])['Revenue']
        .sum()
        .reset_index()
    )
    monthly_revenue.rename(columns={'Order Date': 'ds', 'Revenue': 'y'}, inplace=True)
    return df, monthly_revenue


# === 2. Load and Preprocess Macroeconomic Data ===
def load_macro_data(filepath):
    df_macro = pd.read_csv(filepath)
    df_macro['ds'] = pd.to_datetime(df_macro['Order Date'])
    df_macro = df_macro.drop(columns='Order Date')
    df_macro_monthly = df_macro.groupby(pd.Grouper(key='ds', freq='M'))[
        ['Exchange Rate', 'Inflation Rate']
    ].mean().reset_index()
    return df_macro, df_macro_monthly


# === 3. Run Forecast for Each Revenue Stream ===
def forecast_revenue_streams(monthly_revenue, df_macro_monthly, df_macro, periods=12):
    forecast_results = {}

    for stream in monthly_revenue['Revenue Stream'].unique():
        df_stream = monthly_revenue[monthly_revenue['Revenue Stream'] == stream][['ds', 'y']]
        df_model = pd.merge(df_stream, df_macro_monthly, on='ds', how='left')
        df_model.fillna(method='ffill', inplace=True)

        model = Prophet()
        model.add_regressor('Exchange Rate')
        model.add_regressor('Inflation Rate')
        model.fit(df_model)

        future = model.make_future_dataframe(periods=periods, freq='M')
        future = pd.merge(future, df_macro, on='ds', how='left')
        future.fillna(method='ffill', inplace=True)

        forecast = model.predict(future)
        forecast['Revenue Stream'] = stream
        forecast_results[stream] = forecast

    return forecast_results

# 3. ===Merge Historical Data with Forecast Results===

def merge_forecast_with_history(forecast_results, monthly_revenue):
    
    forecast_dfs = []
    for stream, df in forecast_results.items():
        df_subset = df[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
        df_subset['Revenue Stream'] = stream
        forecast_dfs.append(df_subset)
    
    forecast_df = pd.concat(forecast_dfs, ignore_index=True)
    historical_df = monthly_revenue.copy()
    historical_df.rename(columns={'y': 'actual'}, inplace=True)
    combined_df = pd.merge(
        historical_df,
        forecast_df,
        on=['ds', 'Revenue Stream'],
        how='outer'
    )

    combined_df.sort_values(by=['ds', 'Revenue Stream'], inplace=True)
    combined_df.reset_index(drop=True, inplace=True)

    combined_df.rename(columns={
        'ds': 'Date',
        'actual': 'Actual Revenue',
        'yhat': 'Forecasted Revenue',
        'yhat_lower': 'Lower Estimate',
        'yhat_upper': 'Upper Estimate'
    }, inplace=True)

    return combined_df


# === 4. Evaluate Forecast Performance (Cross-Validation) ===
def evaluate_models(df):
    cv_results = {}
    performance_results = {}

    for stream in df['Revenue Stream'].unique():
        print(f"🔍 Running cross-validation for: {stream}")

        try:
            stream_df = df[df['Revenue Stream'] == stream].copy()
            stream_df['Revenue'] = stream_df['Unit Price'] * stream_df['Quantity']
            monthly = stream_df.groupby(pd.Grouper(key='Order Date', freq='M'))['Revenue'].sum().reset_index()
            monthly.columns = ['ds', 'y']

            total_months = (monthly['ds'].max().to_period('M') - monthly['ds'].min().to_period('M')).n
            total_days = total_months * 30

            initial_days = int(total_days * 0.6)
            horizon_days = int(total_days * 0.2)
            period_days = int(total_days * 0.2)

            initial = f"{initial_days} days"
            period = f"{period_days} days"
            horizon = f"{horizon_days} days"

            model = Prophet()
            model.fit(monthly)

            df_cv = cross_validation(model, initial=initial, period=period, horizon=horizon, parallel="processes")
            df_p = performance_metrics(df_cv)

            cv_results[stream] = df_cv
            performance_results[stream] = df_p
            print(f"✅ Done: {stream}\n")

        except Exception as e:
            print(f"❌ Failed for {stream}: {e}")

    #==5 Combine all performance metrics into one DataFrame ==
    combined_performance = []

    for stream, df_p in performance_results.items():
        df_p = df_p.copy()
        df_p['Revenue Stream'] = stream
        combined_performance.append(df_p)

        performance_df = pd.concat(combined_performance, ignore_index=True)

        return cv_results, performance_df
