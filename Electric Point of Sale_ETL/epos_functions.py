import os
import sys
from dotenv import load_dotenv
import smtplib
from email.message import EmailMessage
import time
import pandas as pd

load_dotenv()
EMAIL_ADDRESS: str = os.getenv('userEmail')
EMAIL_PASSWORD: str = os.getenv('userPassword')
ERROR_EMAIL: str = os.getenv('receiverEmail')
DASHBOARD: str = os.getenv('new_epos_stream')

def get_files(directory) -> list:
    files = os.listdir(directory)
    file_list = []
    
    if not files:
        sys.exit("No files found in the dataDump folder. Exiting script...")
    
    for file in files:
        if file.endswith('.csv'):
            file_list.append(file)
    return file_list

def generate_list_numbers(dataFrame: pd.DataFrame) -> None:
    if pd.isna(dataFrame.at[0, 'List Number']):
        first_list_number = 1
        
    for index, row in dataFrame.iterrows():
        dataFrame.at[index, 'List Number'] = first_list_number
        first_list_number += 1

def data_types(dataFrame) -> None:
    try:
        if "Date Sold" in dataFrame.columns:
            dataFrame["Date Sold"] = pd.to_datetime(dataFrame["Date Sold"], format="mixed", dayfirst=True)
            
        if "Qty Sold" in dataFrame.columns:
            dataFrame["Qty Sold"] = pd.to_numeric(dataFrame["Qty Sold"], errors="coerce").fillna(0).astype(int)
        
        if "RRP" in dataFrame.columns:
            dataFrame["RRP"] = pd.to_numeric(dataFrame["RRP"], errors="coerce").fillna(0).astype(float)
        
        if "Value" in dataFrame.columns:
            dataFrame["Value"] = pd.to_numeric(dataFrame["Value"], errors="coerce").fillna(0).astype(float)
        if "Product Code" in dataFrame.columns:
            dataFrame["Product Code"] = dataFrame["Product Code"].astype(str)
    except Exception as e:
        sys.exit(f"Error during data type conversion: {e}")

def create_specific_units_column(dataFrame) -> None:
    dataFrame["Specific Units"] = 0.0
    dataFrame["Specific Units"] = pd.to_numeric(dataFrame["Specific Units"], errors="coerce").fillna(0).astype(float)

def create_revenue_column(dataFrame) -> None:
    dataFrame["Revenue"] = 0.0
    dataFrame["Revenue"] = pd.to_numeric(dataFrame["Revenue"], errors="coerce").fillna(0).astype(float)
    dataFrame["Revenue"] = dataFrame["Qty Sold"].fillna(0) * dataFrame["RRP"].fillna(0)

def remove_commas(dataFrame, column) -> None:
    dataFrame[column] = dataFrame[column].str.replace(",", "")

def uppercase_column_values(dataFrame, *args) -> None:
    for column in args:
        if column in dataFrame.columns:
            dataFrame[column] = dataFrame[column].str.upper()

def specific_unit_adjustment(dataFrame) -> None:
    maidenhead_adjustment: list[str] = ['11751', '11752', '11754', '11755', '11758', '11759', '11780', '11775', '11778', '11785']
    adjustment50: list[str] = ['44460', '44461', '44462', '44463', '44464']
    adjustment15: list[str] = ['44455', '44456', '44457', '44458', '44459']
    adjustment4: list[str] = ['44451', '44452', '44453', '44454']
    adjustment12: list[str] = ['INN', 'inn', 'Inn']
    
    for i in range(len(dataFrame)):
        if '44504' in dataFrame.at[i, 'Product Code']:
            dataFrame.at[i, 'Qty Sold'] = 0
            dataFrame.at[i, 'Specific Units'] = 0
        elif any(item in dataFrame.at[i, 'Product Code'] for item in maidenhead_adjustment):
            dataFrame.at[i, 'Qty Sold'] = dataFrame.at[i, 'Qty Sold'] / 25
            dataFrame.at[i, 'Specific Units'] = dataFrame.at[i, 'Qty Sold']
        elif any(item in dataFrame.at[i, 'Product Code'] for item in adjustment50):
            dataFrame.at[i, 'Specific Units'] = dataFrame.at[i, 'Qty Sold'] * 50
        elif any(item in dataFrame.at[i, 'Product Code'] for item in adjustment15):
            dataFrame.at[i, 'Specific Units'] = dataFrame.at[i, 'Qty Sold'] * 15
        elif any(item in dataFrame.at[i, 'Product Code'] for item in adjustment4):
            dataFrame.at[i, 'Specific Units'] = dataFrame.at[i, 'Qty Sold'] * 4
        elif any(item in dataFrame.at[i, 'Product Code'] for item in adjustment12):
            dataFrame.at[i, 'Specific Units'] = dataFrame.at[i, 'Qty Sold'] * 12
        else:
            dataFrame.at[i, 'Specific Units'] = dataFrame.at[i, 'Qty Sold']

def recipes_kg_calculation(dataFrame) -> None:
    dataFrame['Recipe Weight'] = 0.0
    dataFrame['Recipe Weight'] = pd.to_numeric(dataFrame['Recipe Weight'], errors='coerce').astype(float)
    
    four_hundred_gram = ['44501', '44505', '44509', '44513']
    two_kilogram = ['44503', '44506', '44510', '44514']
    
    for i in range(len(dataFrame)):
        if any(item in dataFrame.at[i, 'Product Code'] for item in four_hundred_gram):
            dataFrame.at[i, 'Recipe Weight'] = dataFrame.at[i, 'Qty Sold'] * 0.4
        elif any(item in dataFrame.at[i, 'Product Code'] for item in two_kilogram):
            dataFrame.at[i, 'Recipe Weight'] = dataFrame.at[i, 'Qty Sold'] * 2

def brand_name_corrections(dataFrame, column="Product Brand") -> None:
    corrections = {
        "ZO": "ZOE",
        "ZOË": "ZOE",
        "NERF DOG": "NERF",
    }
    
    if column in dataFrame.columns:
            dataFrame[column] = dataFrame[column].replace(corrections, regex=True)
    else:
        sys.exit(f"Column '{column}' not found in data. Exiting program...")

def shop_name_corrections(dataFrame, column="Shop Name") -> None:
    corrections = {
        "FETCH!": "FETCH",
        "VITAL": "VITAL PET PRODUCTS",
        "MAIDENHEAD AQUATICS": "MAIDENHEAD",
    }
    
    if column in dataFrame.columns:
            dataFrame[column] = dataFrame[column].replace(corrections, regex=True)
    else:
        sys.exit(f"Column '{column}' not found in data. Exiting program...")

def best_pets_adjustment(dataFrame) -> None:
    m_desc = dataFrame["Description"].str.contains("creamy", case=False, na=False)
    m_shop = dataFrame["Shop Name"].str.contains("best pets", case=False, na=False)
    
    dataFrame.loc[m_desc & m_shop, "Specific Units"] = dataFrame.loc[m_desc & m_shop, "Qty Sold"]

def get_date_year(dataFrame) -> list:
    date = dataFrame.at[1, 'Date Sold']
    date = pd.to_datetime(date, format='mixed', dayfirst=True)
    year = date.year
    date = date.strftime('%d-%m-%Y')
    return [year, date]

def get_customer_name(dataFrame) -> str:
    if not pd.isna(dataFrame.at[1, "Shop Name"]):
        customer_name = dataFrame.at[1, 'Shop Name']
        customer_name = customer_name.replace(' ', '_')
        customer_name = customer_name.lower()
        return customer_name
    else:
        sys.exit("Customer name is missing from the 'Shop Name' column. Exiting program...")

def create_mapping_key(dataFrame) -> None:
    dataFrame['Mapping Key'] = ''
    dataFrame['Mapping Key'] = dataFrame['Mapping Key'].astype(str)
    dataFrame['Date Sold'] = dataFrame['Date Sold'].dt.strftime('%Y-%m-%d')
    
    for i in range(len(dataFrame)):
        dataFrame.at[i, 'Mapping Key'] = f"{dataFrame.at[i, 'List Number']}_{dataFrame.at[i, 'Shop Name']}_{dataFrame.at[i, 'Date Sold']}" 

def send_to_data_stream(store, file_path, date) -> None:
    try:
        msg = EmailMessage()
        msg['Subject'] = f'Data ingestion for {store} on {date}'
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = DASHBOARD
        msg.set_content(f"Please find attached the data for {store} on {date}.")
        msg.add_attachment(open(file_path, 'rb').read(), maintype='application', subtype='csv', filename=os.path.basename(file_path))
        
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
            time.sleep(1.5)
        
        print(f"Data for {store} sent to data stream successfully.")
    except Exception as e:
        sys.exit(f"Failed to send data to data stream: {e}")

def send_error_notification(file_path, error_msg) -> None:
    try:
        msg = EmailMessage()
        msg["Subject"] = "EPOS Automation Error Notification"
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = ERROR_EMAIL
        msg.set_content(f"{error_msg}\n\nAffected file path: {file_path}")
        
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
    except Exception as e:
        sys.exit(f"Failed to send error notification email: {e}")