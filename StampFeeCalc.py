import streamlit as st
import pandas as pd
import io
from datetime import datetime

# App Title
st.title("Italian Insurance Stamp Duty Calculator")

# Contract Number Input
contract_number = st.text_input("Contract Number (optional)", "")

# User Inputs
st.header("Contract Details")
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Technical Start Date", datetime(2018, 3, 1))
with col2:
    end_date = st.date_input("Contract End Date", datetime(2025, 2, 28))

# Generate year range for balances
start_year = start_date.year
end_year = end_date.year - 1

st.header("Year-end Balances")
balances = {}
for year in range(start_year, end_year + 1):
    balances[year] = st.text_input(f"Balance as of 31 Dec {year}", "0")

# Surrender Value input
surrender_value_input = st.text_input(f"Surrender Value on {end_date}", "0")

# Convert input strings to float
for year in balances:
    balances[year] = float(balances[year].replace(",", "").replace(".", ""))
surrender_value = float(surrender_value_input.replace(",", "").replace(".", ""))

# Calculate stamp duty
results = []
total_stamp_duty = 0.0

# First Year (Pro-rata)
first_year_days = (datetime(start_year, 12, 31) - datetime.combine(start_date, datetime.min.time())).days + 1
annual_fee_first_year = balances[start_year] * 0.002
daily_fee_first_year = annual_fee_first_year / 365
stamp_duty_first_year = daily_fee_first_year * first_year_days
total_stamp_duty += stamp_duty_first_year
results.append({
    "Year": start_year,
    "Balance": balances[start_year],
    "Days Active": first_year_days,
    "Stamp Duty (€)": round(stamp_duty_first_year, 2)
})

# Intermediate full years
for year in range(start_year + 1, end_year + 1):
    annual_fee = balances[year] * 0.002
    total_stamp_duty += annual_fee
    results.append({
        "Year": year,
        "Balance": balances[year],
        "Days Active": 365,
        "Stamp Duty (€)": round(annual_fee, 2)
    })

# Last Year (Pro-rata)
last_year_days = (end_date - datetime(end_date.year, 1, 1).date()).days + 1
annual_fee_last_year = surrender_value * 0.002
daily_fee_last_year = annual_fee_last_year / 365
stamp_duty_last_year = daily_fee_last_year * last_year_days
total_stamp_duty += stamp_duty_last_year
results.append({
    "Year": end_date.year,
    "Balance": surrender_value,
    "Days Active": last_year_days,
    "Stamp Duty (€)": round(stamp_duty_last_year, 2)
})

# Display Results
st.header("Calculation Summary")
df_results = pd.DataFrame(results)
st.table(df_results)

st.markdown(f"### Total Stamp Duty: **€{round(total_stamp_duty,2)}**")

# Download Excel
output = io.BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    df_results.to_excel(writer, index=False, sheet_name='StampDutyCalc')
    workbook = writer.book
    worksheet = writer.sheets['StampDutyCalc']
    worksheet.write('E2', 'Total Stamp Duty (€)')
    worksheet.write('E3', round(total_stamp_duty, 2))
    worksheet.write('E5', 'Contract Number')
    worksheet.write('E6', contract_number)

excel_data = output.getvalue()

# File naming with contract number
filename = f"Stamp_Duty_{contract_number if contract_number else 'Calculation'}_{datetime.now().date()}.xlsx"

st.download_button(label="Download Excel Audit File",
                   data=excel_data,
                   file_name=filename,
                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
