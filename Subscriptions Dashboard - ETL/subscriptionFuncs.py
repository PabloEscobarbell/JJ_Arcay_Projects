import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from email.message import EmailMessage
import smtplib
import sys
import time
import os

def getNowDate() -> str:
    '''This function gets the current date and returns it in the format YYYY-MM-DD.'''
    now = datetime.now()
    now = str(now).split(' ')
    nowDate = now[0]    
    print('Successfully got the current date...')
    return nowDate

def getMonthYear() -> tuple:
    now = datetime.now()
    one_month_ago = now - relativedelta(months=1)
    month_last = one_month_ago.strftime("%B")
    month = now.strftime("%B")
    year = now.year
    return month, year, month_last

def turningToInt(df, columns) -> None:
    for column in columns:
        if column in df.columns:
            df[column] = df[column].astype(int)
        else:
            print(f"Column {column} not found in dataframe.")

def turningToDatetime(df, columns) -> None:
    for column in columns:
        if column in df.columns:
            df[column] = pd.to_datetime(df[column], errors='coerce')
        else:
            sys.exit(f"Column {column} not found in dataframe.")
            
def timeDifference(df) -> None:
    if "created_at" in df.columns and "cancelled_at" in df.columns:
        df["timeDiffDays"] = (df["cancelled_at"] - df["created_at"]).dt.days
        df["timeDiffDays"] = df["timeDiffDays"].fillna(0).astype(int)
    else:
        sys.exit("Required columns 'created_at' or 'cancelled_at' not found in dataframe.")
            
def createEmail(subject, sender, receiver, dataFile, email_type) -> EmailMessage:
    """email_type options: top-line, product-subscriptions, revenue."""
    email = EmailMessage()
    email["Subject"] = subject
    email["From"] = sender
    email["To"] = receiver
    if email_type.lower() == "top-line":
        email.set_content("Please find attached the latest Top Line report.")
    elif email_type.lower() == "product-subscriptions":
        email.set_content("Please find attached the latest Product Subscriptions report.")
    elif email_type.lower() == "revenue":
        email.set_content("Please find attached the latest Revenue report.")
    else:
        sys.exit("ERROR: Invalid email type specified.")
    # Attach the data file
    try:
        with open(dataFile, "rb") as f:
            email.add_attachment(f.read(), maintype="application", subtype="xlsx", filename=os.path.basename(dataFile))
        return email
    except Exception as e:
        sys.exit(f"ERROR: An error occurred while attaching the file: {e}")
    
def sendEmail(emails, username, password) -> None:
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = username
    smtp_password = password
    for email in emails:
        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(email)
                server.quit()
                time.sleep(1)
        except Exception as e:
            sys.exit(f"ERROR: An error occurred while attemtping to send the email: {e}.")