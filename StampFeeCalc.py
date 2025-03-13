import streamlit as st
import pandas as pd
from datetime import datetime
import io

st.title("🇮🇹 Stamp Duty Calculator (Italy)")

# Contract Number
contract_number = st.text_input("Contract Number (optional):")

# Surrender type selection (Single toggle clearly here)
surrender_type = st.radio("Surrender Type", ["Full", "Partial"], horizontal=True)

# Date Inputs
col1, col2, col3 = st.columns(3)

with col1:
    start_date_input = st.date_input("Technical Start Date (YYYY/MM/DD)", format="YYYY/MM/DD")

with col2:
    end_date_input = st.date_input("Termination Date (YYYY/MM/DD)", format="YYYY/MM/DD")

partial_date_input = None
if surrender_type == "Partial":
    with col3:
        partial_date_input = st.date_input("Partial Surrender Request Date (YYYY/MM/DD)", format="YYYY/MM/DD")

st.info("ℹ️ Enter dates in YYYY/MM/DD format.")

# Convert dates explicitly
start_date = datetime.combine(start_date_input, datetime.min.time())
end_date = datetime.combine(end_date_input, datetime.min.time())

if surrender_type == "Partial":
    partial_date = datetime.combine(partial_date_input, datetime.min.time())
    if not (start_date <= partial_date <= end_date):
        st.error("Partial surrender date must be between start and termination dates.")
        st.stop()

if start_date >= end_date:
    st.error("Termination date must be after start date!")
    st.stop()

start_year = start_date.year
end_year = end_date.year

# Yearly balances input
st.header("Year-end Balances (€)")
yearly_balances = {}
for year in range(start_year, end_year):
    balance_str = st.text_input(f"Balance as of 31.12.{year}", key=f"balance_{year}")
    if balance_str:
        try:
            yearly_balances[year] = float(balance_str.replace(' ', '').replace(',', '.'))
        except:
            st.error(f"Invalid balance input for {year}.")
            st.stop()
    else:
        st.error(f"Balance for {year} is required.")
        st.stop()

# Surrender or Partial surrender values clearly based on toggle
if surrender_type == "Partial":
    PSV_str = st.text_input("Partial Surrender Value (PSV)")
    CBPS_str = st.text_input("Contract Balance at Partial Surrender Date (CBPS)")

    if not PSV_str or not CBPS_str:
        st.error("PSV and CBPS values are required.")
        st.stop()
    
    try:
        PSV = float(PSV_str.replace(',', '.'))
        CBPS = float(CBPS_str.replace(',', '.'))
        ratio = PSV / CBPS
    except:
        st.error("Invalid PSV or CBPS.")
        st.stop()

    surrender_value = PSV
else:
    surrender_str = st.text_input(f"Surrender Value ({end_date.strftime('%d.%m.%Y')})")
    if surrender_str:
        try:
            surrender_value = float(surrender_str.replace(' ', '').replace(',', '.'))
        except ValueError:
            st.error("Invalid surrender value.")
            st.stop()
    else:
        st.error("Surrender value is required.")
        st.stop()

# Days calculation (inclusive)
def days_active(start_dt, end_dt):
    return (end_dt - start_dt).days + 1

results = []
total_stamp_fee = 0.0

# First year calculation
days_first_year = days_active(start_date, datetime(start_year, 12, 31))
stamp_first_year = yearly_balances[start_year] * 0.002 * days_first_year / 365
results.append({
    "Year": start_year,
    "Balance (€)": yearly_balances[start_year],
    "Days Active": days_first_year,
    "Stamp Duty (€)": round(stamp_first_year, 2)
})
total_stamp_fee += stamp_first_year

# Intermediate years calculation
for year in range(start_year + 1, end_year):
    balance = yearly_balances[year]
    stamp_fee = balance * 0.002
    results.append({
        "Year": year,
        "Balance (€)": balance,
        "Days Active": 365,
        "Stamp Duty (€)": round(stamp_fee, 2)
    })
    total_stamp_fee += stamp_fee

# Last year calculation (clearly different handling for partial)
days_last_year = days_active(datetime(end
