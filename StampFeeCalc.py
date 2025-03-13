import streamlit as st
import pandas as pd
from datetime import datetime
import io

st.title("🇮🇹 Stamp Duty Calculator (Italy)")

# Contract Number
contract_number = st.text_input("Contract Number (optional):")

# Surrender Type toggle
is_partial = st.toggle("Partial Surrender (otherwise Full Surrender)")

# Date Inputs
col1, col2, col3 = st.columns(3)
with col1:
    start_date_input = st.date_input("Technical Start Date (YYYY/MM/DD)", format="YYYY/MM/DD")
with col2:
    end_date_input = st.date_input("Termination Date (YYYY/MM/DD)", format="YYYY/MM/DD")
    if st.session_state.get('surrender_type') == 'Partial':
        partial_date_input = st.date_input("Partial Surrender Request Date (YYYY/MM/DD)", format="YYYY/MM/DD")
        PSV_str = st.text_input("Partial Surrender Value (PSV)")
        cbps_str = st.text_input("Contract Balance Before Partial Surrender (CBPS)")
else:
    partial_date_input = None

# Surrender type toggle
surrender_type = st.radio("Surrender Type", ["Full", "Partial"], horizontal=True, key='surrender_type')

st.info("ℹ️ Enter dates in YYYY/MM/DD format.")

# Convert dates to datetime
start_date = datetime.combine(start_date_input, datetime.min.time())
end_date = datetime.combine(end_date_input, datetime.min.time())

if surrender_type == "Partial":
    partial_date = datetime.combine(partial_date_input, datetime.min.time())
    if partial_date_input >= end_date_input or partial_date_input < start_date_input:
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

# Surrender value input
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

# Partial surrender inputs
if surrender_type == 'Partial':
    PSV_str = st.text_input("Partial Surrender Value (PSV)")
    CBPS_str = st.text_input("Contract Balance at Partial Surrender Date (CBPS)")
    
    try:
        PSV = float(PSV_str.replace(',', '.'))
        CBPS = float(CBPS_str.replace(',', '.'))
        ratio = PSV / CBPS
    except:
        st.error("Invalid PSV or CBPS.")
        st.stop()

# Days calculation (correctly inclusive)
def days_active(start_dt, end_dt):
    return (end_dt - start_dt).days + 1

results = []
total_stamp_fee = 0.0

# First year calculation
days_first_year = (datetime(start_year, 12, 31) - start_date).days + 1
stamp_first_year = yearly_balances[start_year] * 0.002 * days_first_year / 365
results.append({
    "Year": start_year,
    "Balance (€)": yearly_balances[start_year],
    "Days Active": days_first_year,
    "Stamp Duty (€)": round(stamp_first_year, 2)
})
total_stamp_fee += stamp_first_year

# Intermediate years
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

# Last year calculation
days_last_year = (end_date - datetime(end_year, 1, 1)).days + 1

if surrender_type == 'Partial':
    base_stamp = CBPS * 0.002 * days_last_year / 365
    stamp_last_year = base_fee = base_stamp_fee = base_stamp_fee = (base_fee := surrender_value * 0.002 * days_last_year / 365) * (PSV / CBPS)
else:
    stamp_last_year = surrender_value * 0.002 * days_last_year / 365

results.append({
    "Year": end_year,
    "Balance (€)": surrender_value,
    "Days Active": days_last_year,
    "Stamp Duty (€)": round(stamp_last_year, 2)
})
total_stamp_fee += stamp_last_year

# Display Results
st.subheader("📑 Calculation Results")
df_results = pd.DataFrame(results)
st.dataframe(df_results, hide_index=True)

st.markdown(f"### **Total Stamp Duty Payable:** €{total_stamp_fee:.2f}")

# Excel Generation
output = io.BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    workbook = writer.book
    worksheet = workbook.add_worksheet("Stamp Duty Audit")
    writer.sheets["Stamp Duty Audit"] = worksheet

    worksheet.write('A1', "Contract Number")
    worksheet.write('B1', contract_number or "N/A")

    df_results.to_excel(writer, sheet_name="Stamp Duty Audit", startrow=3, index=False)

    total_row = len(df_results) + 5
    worksheet.write(total_row, 2, "Total Stamp Duty (€)")
    worksheet.write(total_row, 3, round(total_stamp_fee, 2))

output.seek(0)

# Excel download
xls_name = f"stamp_duty_{contract_number or 'contract'}.xlsx"
st.download_button(
    label="📥 Download Excel Audit File",
    data=output,
    file_name=xls_name,
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
