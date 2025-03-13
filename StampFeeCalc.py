import streamlit as st
import pandas as pd
from datetime import datetime, date
import io

st.title("🇮🇹 Stamp Duty Calculator (Italy)")

# Optional Contract Number
contract_number = st.text_input("Contract Number (optional):")

# Dates Input (with clarification)
col1, col2 = st.columns(2)
with col1:
    start_date_input = st.date_input("Technical Start Date (YYYY/MM/DD)", format="YYYY/MM/DD")
with col2:
    end_date_input = st.date_input("Termination Date (YYYY/MM/DD)", format="YYYY/MM/DD")

st.info("ℹ️ Enter dates in the format YYYY/MM/DD.")

# Convert to datetime explicitly
start_date = datetime.combine(start_date_input, datetime.min.time())
end_date = datetime.combine(end_date_input, datetime.min.time())

if start_date >= end_date:
    st.error("Termination date must be after start date!")
    st.stop()

start_year = start_date.year
end_year = end_date.year

# Year-end Balances Input
st.header("Year-end Balances (€)")
yearly_balances = {}
for year in range(start_year, end_year):
    balance_str = st.text_input(f"Balance as of 31.12.{year}", key=f"balance_{year}")
    if balance_str:
        try:
            yearly_balances[year] = float(balance_str.replace(' ', '').replace(',', '.'))
        except ValueError:
            st.error(f"Invalid balance for {year}.")
            st.stop()
    else:
        st.error(f"Balance for {year} is required.")
        st.stop()

# Surrender Value
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

# Correct days calculation (inclusive counting)
def days_inclusive(start_dt, end_dt):
    return (end_dt - start_dt).days + 1

results = []
total_stamp_fee = 0.0

# Calculate stamp duty correctly:
for year in range(start_year, end_year + 1):
    if year == start_year:
        start = start_date
        end = datetime(year, 12, 31)
        balance = yearly_balances[year]
    elif year == end_year:
        start = datetime(year, 1, 1)
        end = end_date
        balance = surrender_value
    else:
        start = datetime(year, 1, 1)
        end = datetime(year, 12, 31)
        balance = yearly_balances[year]

    days_active = days_inclusive(start, end)
    annual_stamp = balance * 0.002 * days_active / 365
    total_stamp_fee += annual_stamp

    results.append({
        "Year": year,
        "Balance (€)": balance,
        "Days Active": days_active,
        "Stamp Duty (€)": round(annual_stamp, 2)
    })

# Display Results
st.subheader("📑 Calculation Results")
df_results = pd.DataFrame(results)
st.dataframe(df_results, hide_index=True)

st.markdown(f"### **Total Stamp Duty Payable:** €{total_stamp_fee:.2f}")

# Excel Generation with correct contract_number
output = io.BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    workbook = writer.book
    worksheet = workbook.add_worksheet("Stamp Duty Audit")
    writer.sheets["Stamp Duty Audit"] = worksheet

    # Write Contract Number at top
    worksheet.write('A1', "Contract Number")
    worksheet.write('B1', contract_number or "N/A")

    # Write results table starting row 3
    df_results.to_excel(writer, sheet_name="Stamp Duty Audit", startrow=3, index=False)

    # Total Stamp Duty below the table
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
