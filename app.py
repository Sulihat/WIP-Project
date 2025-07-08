import streamlit as st
from auth_utils import register_user, login_user, send_reset_code, verify_reset_code, update_password
from Login import login_ui
from forecast_module import run_forecasting_pipeline
import pandas as pd
import numpy as np

st.set_page_config(page_title="FinOptix", layout="wide")

# === Initialize session state ===
for key, default in {
    "trigger_signup": False,
    "trigger_login": False,
    "page": "login",
    "user_email": "",
    "first_name": "",
    "reset_email": ""
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# === Login or Sign Up Page ===
if st.session_state.page == "login":
    login_ui()

    if st.session_state.get("trigger_signup"):
        success, msg = register_user(
            st.session_state.signup_first,
            st.session_state.signup_last,
            st.session_state.signup_email,
            st.session_state.signup_password
        )
        st.success("Registration successful!") if success else st.error(msg)
        st.session_state.trigger_signup = False

    if st.session_state.get("trigger_login"):
        success, msg, first_name = login_user(
            st.session_state.login_email,
            st.session_state.login_password
        )
        if success:
            st.success(msg)
            st.session_state.user_email = st.session_state.login_email
            st.session_state.first_name = first_name
            st.session_state.page = "upload"
            st.rerun()
        else:
            st.error(msg)
        st.session_state.trigger_login = False

# === Forgot Password Page ===
elif st.session_state.page == "forgot_password":
    st.title("🔐 Forgot Password")
    email = st.text_input("Enter your registered email address")
    if st.button("Send Reset Code"):
        success, msg = send_reset_code(email)
        st.success(msg) if success else st.error(msg)
        if success:
            st.session_state.reset_email = email
            st.session_state.page = "reset_code"

# === Reset Code Verification Page ===
elif st.session_state.page == "reset_code":
    st.title("📩 Enter Verification Code")
    code = st.text_input("Enter the verification code sent to your email")
    if st.button("Verify Code"):
        if verify_reset_code(st.session_state.reset_email, code):
            st.success("✅ Code verified successfully.")
            st.session_state.page = "new_password"
        else:
            st.error("❌ Invalid or expired code. Please try again.")

# === New Password Set Page ===
elif st.session_state.page == "new_password":
    st.title("🔑 Reset Your Password")
    new_pwd = st.text_input("New Password", type="password")
    confirm_pwd = st.text_input("Confirm New Password", type="password")
    if st.button("Update Password"):
        if new_pwd != confirm_pwd:
            st.error("Passwords do not match.")
        elif len(new_pwd) < 6:
            st.warning("Password must be at least 6 characters.")
        else:
            update_password(st.session_state.reset_email, new_pwd)
            st.success("Password updated successfully!")
            st.session_state.page = "login"

# === Upload Page ===
elif st.session_state.page == "upload":
    st.title("Revenue Forecast Dashboard")
    with st.sidebar:
        st.markdown("## 📁 Upload Required Data")
        revenue_file = st.file_uploader(" Upload Revenue Data (CSV)", type="csv", key="revenue_file")
        macro_file = st.file_uploader(" Upload Macroeconomic Data (CSV)", type="csv", key="macro_file")

    required_revenue_cols = {"Order Date", "Unit Price", "Quantity", "Revenue Stream"}
    required_macro_cols = {"Order Date", "Exchange Rate", "Inflation Rate"}

    revenue_valid = False
    macro_valid = False

    if revenue_file:
        try:
            revenue_df = pd.read_csv(revenue_file)
            if required_revenue_cols.issubset(revenue_df.columns):
                st.session_state.revenue_df = revenue_df
                revenue_valid = True
            else:
                missing = required_revenue_cols - set(revenue_df.columns)
                st.error(f"❌ Revenue data missing columns: {', '.join(missing)}")
        except Exception as e:
            st.error(f"🚫 Error reading Revenue file: {e}")

    if macro_file:
        try:
            macro_df = pd.read_csv(macro_file)
            if required_macro_cols.issubset(macro_df.columns):
                st.session_state.macro_df = macro_df
                macro_valid = True
            else:
                missing = required_macro_cols - set(macro_df.columns)
                st.error(f"❌ Macroeconomic data missing columns: {', '.join(missing)}")
        except Exception as e:
            st.error(f"🚫 Error reading Macroeconomic file: {e}")

    if revenue_valid and macro_valid:
        st.success("✅ All required data uploaded and validated.")

        with st.expander("📄 Preview Revenue Data"):
            st.dataframe(st.session_state.revenue_df.head(), use_container_width=True)

        with st.expander("📄 Preview Macroeconomic Data"):
            st.dataframe(st.session_state.macro_df.head(), use_container_width=True)

        if st.button("Go to Dashboard"):
            with st.spinner("⏳ Running forecasting model..."):
                try:
                    forecast_results, performance_results, combined_df = run_forecasting_pipeline(
                        st.session_state.revenue_df,
                        st.session_state.macro_df  # ✅ this line was previously truncated
                    )

                    st.session_state.page = "dashboard"
                    st.session_state.forecast_results = forecast_results
                    st.session_state.performance_results = performance_results
                    st.session_state.combined_df = combined_df
                    st.session_state.first_name = ["first_name"]
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Forecasting failed: {e}")

# Dashboard page UI
elif st.session_state.page == "dashboard":
    st.title("Revenue Forecast Dashboard")


    combined_df = st.session_state.combined_df.copy()
    performance_df = st.session_state.performance_results.copy()

    # === Sidebar Filters ===
    st.sidebar.header("🔍 Filter Forecast Results")

    month_order = ["January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]
    unique_months = combined_df['Date'].dt.month_name().unique()
    ordered_months = [m for m in month_order if m in unique_months]
    month_options = ["All"] + ordered_months

    year_options = ["All"] + sorted(combined_df['Date'].dt.year.unique().astype(str))
    stream_options = ["All"] + sorted(combined_df["Revenue Stream"].unique())

    forecast_horizon = st.sidebar.slider("Select Forecast Horizon (months into future)", 1, 12, 6)

    # Reset state on clear
    if st.sidebar.button("🧹 Clear All Filters"):
        st.session_state.selected_month = "All"
        st.session_state.selected_year = "All"
        st.session_state.selected_stream = "All"

    # Set default selections
    selected_month = st.sidebar.selectbox("Select Month", month_options, index=month_options.index(st.session_state.get("selected_month", "All")))
    selected_year = st.sidebar.selectbox("Select Year", year_options, index=year_options.index(st.session_state.get("selected_year", "All")))
    selected_stream = st.sidebar.selectbox("Select Revenue Stream", stream_options, index=stream_options.index(st.session_state.get("selected_stream", "All")))

    # Save selections to session
    st.session_state.selected_month = selected_month
    st.session_state.selected_year = selected_year
    st.session_state.selected_stream = selected_stream

    # === Apply Filters ===
    filtered_df = combined_df.copy()

    if selected_month != "All":
        filtered_df = filtered_df[filtered_df['Date'].dt.month_name() == selected_month]
    if selected_year != "All":
        filtered_df = filtered_df[filtered_df['Date'].dt.year.astype(str) == selected_year]
    if selected_stream != "All":
        filtered_df = filtered_df[filtered_df["Revenue Stream"] == selected_stream]

   # === Divider Function ===
    def blue_divider():
        st.markdown('<hr style="border: 1px solid #1f77b4; margin: 30px 0;">', unsafe_allow_html=True)

    blue_divider()


  # === Metrics Section ===
    st.subheader("Metrics")
    filtered_df["Revenue"] = filtered_df["Actual Revenue"].fillna(filtered_df["Forecasted Revenue"])
    total_revenue = filtered_df["Revenue"].sum()

    df_with_actuals = filtered_df.dropna(subset=["Actual Revenue"])
    if not df_with_actuals.empty:
        accuracy = 100 - (abs(df_with_actuals["Forecasted Revenue"] - df_with_actuals["Actual Revenue"]) / df_with_actuals["Actual Revenue"] * 100).mean()
    else:
        accuracy = 0

    # Calculate growth rate
    rev_series = filtered_df.sort_values("Date")["Revenue"]
    if len(rev_series) >= 2:
        growth_rate = ((rev_series.iloc[-1] - rev_series.iloc[0]) / rev_series.iloc[0]) * 100 if rev_series.iloc[0] != 0 else 0
    else:
        growth_rate = 0

    # Determine color and arrow
    if growth_rate > 0:
        color = "green"
        symbol = "↑"
    elif growth_rate < 0:
        color = "red"
        symbol = "↓"
    else:
        color = "gray"
        symbol = "→"

    # Display using HTML
    st.markdown(f"""
        <div style='font-size: 16px; margin-bottom: 10px;'>Growth Rate</div>
        <div style='font-size: 28px; font-weight: bold; color: {color};'>
            {symbol} {growth_rate:.2f}%
        </div>
    """, unsafe_allow_html=True)


    # Display in columns
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Revenue", f"${total_revenue:,.2f}")
    col2.metric("Forecast Accuracy", f"{accuracy:.2f}%")
    col3.metric("Growth Rate", f"{growth_rate:.2f}%", delta=f"{growth_rate:.2f}%")

# Add divider below metrics
    blue_divider()

    import altair as alt
    st.subheader("Revenue Trend(USD)")

    # Prepare the data
    filtered_df["Revenue"] = filtered_df["Actual Revenue"].fillna(filtered_df["Forecasted Revenue"])
    filtered_df["Lower Bound"] = filtered_df.apply(lambda row: row["Lower Estimate"] if pd.isna(row["Actual Revenue"]) else None, axis=1)
    filtered_df["Upper Bound"] = filtered_df.apply(lambda row: row["Upper Estimate"] if pd.isna(row["Actual Revenue"]) else None, axis=1)
    filtered_df = filtered_df.sort_values("Date")

    # === Create base chart ===
    base = alt.Chart(filtered_df).encode(
        x=alt.X("Date:T", title="Month"),
        tooltip=["Date:T", "Revenue:Q"]
    )

    # === Revenue Line: smooth and thin ===
    line = base.mark_line(
        color="#1f77b4",
        interpolate="monotone",  # makes it smooth
        strokeWidth=1.5           # thinner line
    ).encode(
        y=alt.Y("Revenue:Q", title="Revenue (USD)")
    )

    # === Add circular points (nodes) at all data points ===
    points = base.mark_circle(
        size=65,
        color="#1f77b4"
    ).encode(
        y="Revenue:Q"
    )

    # === Confidence interval area ===
    confidence = alt.Chart(filtered_df).mark_area(
        color="#aec7e8",
        opacity=0.3
    ).encode(
        x="Date:T",
        y="Lower Bound:Q",
        y2="Upper Bound:Q"
    )

    # === Combine all parts ===
    final_chart = (confidence + line + points).properties(
        width=800,
        height=400,
        title="Monthly Revenue Trend with Forecast Confidence"
    )

    st.altair_chart(final_chart, use_container_width=True)


    blue_divider()

    # ==============================================
    # ===== Revenue by Stream Table Section ========
    # ==============================================
    st.subheader("Total Revenue by Stream")

    pivot_df = filtered_df.copy()

    # Get latest date with actual revenue, if it exists
    latest_actual_date = pivot_df[pivot_df["Actual Revenue"].notna()]["Date"].max()

    if pd.notna(latest_actual_date):
        forecast_start_date = latest_actual_date + pd.DateOffset(months=1)
        forecast_end_date = forecast_start_date + pd.DateOffset(months=forecast_horizon - 1)
        pivot_df = pivot_df[(pivot_df["Date"] >= forecast_start_date) & (pivot_df["Date"] <= forecast_end_date)]
    else:
        # No actual revenue available — show all forecasted records instead
        pivot_df = pivot_df[pivot_df["Forecasted Revenue"].notna()]

    # Prepare output
    pivot_output = pivot_df[["Date", "Revenue Stream", "Forecasted Revenue", "Lower Estimate", "Upper Estimate"]].sort_values("Date")

    st.dataframe(pivot_output, use_container_width=True)

    from io import BytesIO
    import pandas as pd

    # Function to convert DataFrame to Excel format
    def convert_df_to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Forecast by Stream')
        processed_data = output.getvalue()
        return processed_data

    # Only show download button if there's something to export
    if not pivot_output.empty:
        excel_data = convert_df_to_excel(pivot_output)

        st.download_button(
            label="Download Revenue Forecast Table",
            data=excel_data,
            file_name='revenue_forecast_by_stream.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )


    blue_divider()

    # =========================================
    # ===== Navigation Buttons Section ========
    # =========================================
    col_back, col_logout = st.columns(2)
    with col_back:
        if st.button("⬅️ Back to Upload Page"):
            st.session_state.page = "upload"
            st.rerun()

    with col_logout:
        if st.button("🚪 Log Out"):
            keys_to_clear = ["first_name", "page", "combined_df", "performance_results", 
                             "selected_month", "selected_year", "selected_stream"]
            for key in keys_to_clear:
                st.session_state.pop(key, None)
            st.session_state.page = "login"
            st.rerun()



