import streamlit as st
import pandas as pd

def upload_and_preview_data():
    st.sidebar.header("📂 Upload Datasets")

    # Upload Revenue Data
    revenue_file = st.sidebar.file_uploader("Upload Revenue Data (CSV or Excel)", type=["csv", "xlsx"], key="revenue")

    if st.sidebar.button("Preview Revenue Data"):
        if revenue_file is not None:
            try:
                if revenue_file.name.endswith(".csv"):
                    revenue_df = pd.read_csv(revenue_file)
                else:
                    revenue_df = pd.read_excel(revenue_file)
                st.subheader("Revenue Data Preview (Top 20 Rows)")
                st.dataframe(revenue_df.head(20))
            except Exception as e:
                st.error(f"Error reading revenue file: {e}")
        else:
            st.warning("Please upload a revenue data file.")

    # Upload Macroeconomic Data
    macro_file = st.sidebar.file_uploader("Upload Macroeconomic Data (CSV or Excel)", type=["csv", "xlsx"], key="macro")

    if st.sidebar.button("Preview Macroeconomic Data"):
        if macro_file is not None:
            try:
                if macro_file.name.endswith(".csv"):
                    macro_df = pd.read_csv(macro_file)
                else:
                    macro_df = pd.read_excel(macro_file)
                st.subheader("Macroeconomic Data Preview (Top 20 Rows)")
                st.dataframe(macro_df.head(20))
            except Exception as e:
                st.error(f"Error reading macroeconomic file: {e}")
        else:
            st.warning("Please upload a macroeconomic data file.")
