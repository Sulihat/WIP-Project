#  FinOptix - Revenue Forecasting App

FinOptix is a Streamlit web application designed to help businesses forecast future revenues using historical sales and macroeconomic data. It also visualizes trends and key performance metrics like growth rate and forecast accuracy.

##  Features

- **User Authentication** (Sign up & Login)
- **CSV Upload** for Revenue and Macroeconomic data
- **Data Validation** to ensure required columns are present
- **Automated Forecasting Pipeline** using machine learning
- **Interactive Dashboard** with filters by Month, Year, and Revenue Stream
- **Revenue Trend Chart** with confidence bounds
- **Forecast Accuracy and Growth Rate** metrics
- **Revenue by Stream Summary Table**

---

## 📁 Required Data Format

### 📌 Revenue Data (CSV):
Must include the following columns:
- `Order Date`
- `Unit Price`
- `Quantity`
- `Revenue Stream`
- `Product Name`

### 📌 Macroeconomic Data (CSV):
Must include:
- `Order Date`
- `Exchange Rate`
- `Inflation Rate`

---

## 🛠 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/finoptix.git
   cd finoptix



Contributing
Feel free to fork and open a pull request if you have improvements or bug fixes!