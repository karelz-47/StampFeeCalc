import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io

st.title("🇮🇹 Stamp Duty Calculator (Italy)")

# Input dates
col1, col2 = st.columns(2)
with col1:
    start_date_input = st.date_input("Technical Start of Contract (YYYY/MM/DD)", format="YYYY/MM/DD")
with col2:
    end_date_input = st.date_input("End Date (Termination Date) (YYYY/MM/DD)", format="YYYY/MM/DD")

# Convert to datetime explicitly
start_date = datetime.combine(start_date_input, datetime.min.time())
end_date = datetime.combine(end_date_input, datetime.min.time())

st.info("ℹ️ Please input dates in the format YYYY/MM/DD.")

# Ensure correct order of dates
if start_date >= end_date:
    st.error("End date must be after start date!")
    st.stop()

start_year = start_date.year
end_year = end_date.year

# Input balances clearly handling commas as decimals
st.header("Year-end Balances (€)")
yearly_balances = {}
for year in range(start_year, end_year):
    balance_str = st.text_input(f"Balance as of 31.12.{year}", key=f"balance_{year}")
    if balance_str:
        try:
            balance_cleaned = float(balance_str.replace(' ', '').replace(',', '.'))
            yearly_balances[year] = balance_cleaned
        except ValueError:
            st.error(f"Please enter a valid numeric balance for {year}.")
            st.stop()
    else:
        st.error(f"Please enter balance for {year}.")
        st.stop()

# Surrender value input
surrender_str = st.text_input(f"Surrender Value ({end_date.strftime('%d.%m.%Y')})")
if surrender_str:
    try:
        surrender_value = float(surrender_str.replace(' ', '').replace(',', '.'))
    except ValueError:
        st.error("Please enter a valid numeric surrender value.")
        st.stop()
else:
    st.error("Please enter the surrender value.")
    st.stop()

# Calculation function with correct date logic
def days_in_year(start_dt, end_dt):
    return (end_dt - start_dt).days + 1  # inclusive counting

results = []
total_stamp_fee = 0

for year in range(start_year, end_year + 1):
    if year == start_year:
        start = start_date
        end = datetime(year, 12, 31)
        balance = yearly_balances.get(year, surrender_value)
    elif year == end_year:
        start = datetime(year, 1, 1)
        end = end_date
        balance = surrender_value
    else:
        start = datetime(year, 1, 1)
        end = datetime(year, 12, 31)
        balance = yearly_balances[year]

    days_active = days_in_year(start, end)
    annual_stamp = balance * 0.002 * days_active / 365
    total_stamp_fee += annual_stamp

    results.append({
        "Year": year,
        "Balance (€)": balance,
        "Days Active": days_active,
        "Stamp Duty (€)": round(annual_stamp, 2)
    })

# Results display
df_results = pd.DataFrame(results)
st.subheader("📑 Calculation Results")
st.dataframe(df_results, hide_index=True)

st.markdown(f"### **Total Stamp Duty Payable:** €{total_stamp_fee:.2f}")

# Excel file generation
output = io.BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    workbook = writer.book
    worksheet = workbook.add_worksheet("Stamp Duty Audit")
    writer.sheets["Stamp Duty Audit"] = worksheet

    # Write Contract Number at the top
    worksheet.write('A1', "Contract Number")
    worksheet.write('B1', contract_number or "N/A")

    # Start writing data from row 3
    df_results.to_excel(writer, sheet_name="Stamp Duty Audit", startrow=3, index=False)

    # Write total stamp fee below the table
    total_row = len(df_results) + 5
    worksheet.write(total_row, 2, "Total Stamp Duty (€)")
    worksheet.write(total_row, 3, round(total_stamp_fee, 2))

output.seek(0)

# Excel file download button
xls_name = f"stamp_duty_{contract_number or 'contract'}.xlsx"
st.download_button(
    label="📥 Download Excel Audit File",
    data=output,
    file_name=xls_name,
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
