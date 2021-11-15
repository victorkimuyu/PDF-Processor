import os
from glob import glob
from PyPDF2 import pdf
import pdfplumber
import xlsxwriter
import pandas as pd

reports = sorted(glob("D:\Dev\Systems\PDF_Merge\Cargill\oldreports\*.pdf"))


reports_content = []
print('Reading Reports....\n')
for report in reports:
    with pdfplumber.open(report) as pdf:
        for page in pdf.pages:
            report_text = page.extract_text()
            reports_content.append(report_text)


reg_nos = []
makes = []
body_types = []
mileages = []
market_values = []

print('Making Excel schedule')
for report in reports_content:
    report_lines = report.split('\n')
    for line in report_lines:
        if line.startswith('Reg. No.'):
            reg_nos.append(line.split('Steering')[0].replace('Reg. No.', ''))
        elif line.startswith('Make'):
            makes.append(line.split('Transmission')[0].replace('Make', ''))
        elif line.startswith('Body Type'):
            body_types.append(line.split('Braking')[0].replace('Body Type', ''))
        elif line.startswith('Mileage'):
            mileages.append(line.split("Interior")[0].replace('Mileage', ''))
        value_lines = report_text.split('\n')
    for i in range(len(report_lines)):
        if report_lines[i].startswith('Market Value'):
            value_text = report_lines[i-1]
            if value_text.startswith("-Radio"):
                value_text = '0'
            elif value_text == "Not Applicable":
                value_text = '0'
            market_values.append(int(value_text.replace(',', '').replace('.00','')))

for item in range(len(market_values)):
    print("Reg: " + reg_nos[item] + "Value: " + str(market_values[item]))


data = pd.DataFrame({'Reg No.': reg_nos, 'Make': makes, 'Body Type': body_types, 'Mileage': mileages, 'Market Value': market_values})
writer = pd.ExcelWriter('D:\Dev\Systems\PDF_Merge\Schedule2.xlsx', engine='xlsxwriter')
data.to_excel(writer, sheet_name='Sheet 1', index=False)
writer.save()