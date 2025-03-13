import streamlit as st
import pandas as pd
from datetime import datetime
import io

st.title("Italian Insurance Stamp Duty Calculator")

# Contract info input
contract_number = st.text_input("Contract Number (optional):")
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Contract Start Date")
with col2:
    end_date = st.date_input("Termination Date (Surrender Date)")

st.header("Yearly Balances")

current_year = datetime.now().year
years = list(range(datetime.strptime(str(col1), '%Y-%m-%d').year, col2.year + 1))

yearly_balances = {}

# Input yearly balances without automatic thousand separator issue
for year in range(col1.year, col2.year + 1):
    balance_str = st.text_input(f"Balance on 31.12.{year} (€)", key=f"balance_{year}")
    if balance_str:
        # Fix: Replace comma with dot and remove spaces
        balance_cleaned = balance_str.replace(' ', '').replace(",", ".")
        try:
            yearly_balances[year] = float(balance_str.replace(',', '.'))
        except ValueError:
            st.error(f"Please enter a valid number for the balance of year {year}.")
            st.stop()

surrender_value_str = st.text_input("Surrender Value (termination date):")
try:
    surrender_value = float(surrender_value_str.replace(",", "."))
except ValueError:
    st.error("Please enter a valid surrender value.")
    st.stop()

if st.button("Calculate Stamp Duty"):
    start_date = col1
    end_date = col2

    # Calculate stamp duty
    stamp_duties = []
    total_stamp = 0

    for i, (year, balance) in enumerate(yearly_balances.items()):
        annual_stamp = balance * 0.002
        days_active = 365

        # First year pro-rata
        if i == 0:
            days_active = (datetime(year, 12, 31) - col1).days + 1
            annual_stamp = annual_stamp * days_active / 365

        yearly_balances[year] = {
            "Balance": balance,
            "Days Active": days_active,
            "Stamp Duty": annual_stamp / 365 * days_active
        }

# Final year pro-rata calculation
final_year_days = (col2 - datetime(col2.year, 1, 1)).days + 1
final_year_stamp = surrender_value * 0.002 * final_year_stamp / 365

# Total calculation
total_stamp_fee = sum(balance * 0.002 for balance in yearly_balances.values()) - yearly_balances[col2.year] * 0.002 + final_year_stamp

# Results table
df_results = pd.DataFrame({
    "Year": list(yearly_balances.keys()) + [col2.year],
    "Balance (€)": list(yearly_balances.values()) + [surrender_value],
    "Stamp Duty (€)": [round(balance * 0.002, 2) for balance in yearly_balances.values()][:-1] + [round(final_year_stamp, 2)]
})

st.subheader("Stamp Duty per Year")
st.dataframe(df_results)

st.markdown(f"### **Total Stamp Duty:** {total_stamp_fee:.2f} €")

# Excel download
output = io.BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    df_results.to_excel(writer, sheet_name="Stamp Duty Calculation", index=False)

    # Extra info tab
    df_info = pd.DataFrame({
        "Contract Number": [contract_number or "N/A"],
        "Technical Start Date": [col1.strftime("%Y-%m-%d")],
        "Contract End Date": [col2.strftime("%Y-%m-%d")],
        "Surrender Value (€)": [surrender_value],
        "Total Stamp Duty (€)": [round(total_stamp_fee, 2)]
    })
    df_results.to_excel(writer, sheet_name='Calculation', index=False)
    df_info = pd.DataFrame(df_info)
    df_results.to_excel(writer, sheet_name='Calculation', index=False)
    df_info.to_excel(writer, sheet_name="Contract Info", index=False)

output.seek(0)

# Excel download button
st.download_button(
    label="Download Excel Audit File",
    data=output,
    file_name=f"stamp_duty_{contract_number or 'contract'}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
