# Stamp Duty Calculator (Italy)

A simple yet powerful Streamlit application designed to calculate the stamp duty fee (imposta di bollo) on life insurance contracts in Italy, based on policy balances and duration.

Features

Easy-to-use Interface: Input contract details, including start/end dates, annual balances, and surrender value.

Automated Calculation: Computes annual stamp duties accurately, handling pro-rata calculations for partial years.

Audit Trail: Generates a downloadable Excel file containing detailed calculations, suitable for future reference or audits.

Customizable: Optional contract number field included for better record management.


Requirements

Python 3.8+

Streamlit

pandas

openpyxl


Installation

Clone this repository:

git clone https://github.com/yourusername/stamp-duty-calculator.git
cd stamp-duty-calculator

Install the required dependencies:

pip install -r requirements.txt

How to Run

Run the Streamlit application using the following command:

streamlit run stamp_duty_calc.py

Your app will open automatically in your default web browser, or you can access it manually via http://localhost:8501.

Usage

Fill in the following input fields:

Contract Number (optional): Enter a contract ID or reference number.

Technical Start of the Contract: Choose the date the insurance policy started.

End Date of the Contract: Choose the termination date (when surrender value is paid out).

Yearly Balances: Enter year-end balances (without decimal points or separators, decimals handled automatically).

Surrender Value: Enter the final surrender value upon termination.


Click the Calculate button to display the stamp duty calculation.

Download the generated Excel file for audit purposes by clicking on the provided download link.


Excel Audit File

The generated Excel file includes:

Contract details (including optional contract number)

Individual annual balances

Clearly presented stamp duty calculations for each year

Total stamp duty payable


Contributing

Pull requests, improvements, and suggestions are welcome. Please open an issue or PR clearly describing your changes or ideas.

License

This project is licensed under the MIT License. See LICENSE for details.

