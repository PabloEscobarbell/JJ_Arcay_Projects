import os
import sys
from dotenv import load_dotenv
import time
from openpyxl import load_workbook
from datetime import datetime
import pandas as pd
import subscriptionFuncs as sf
########## ENV VARIABLES ##########
try:
    load_dotenv()
    EMAIL_ADDRESS = os.getenv("userEmail")
    PASSWORD = os.getenv("userPassword")
    RECHARGE_TOP_LINE = os.getenv("recharge_top_line")
    RECHARGE_PRODUCT_SUBSCRIPTIONS = os.getenv("recharge_product_subscriptions")
    RECHARGE_REVENUE = os.getenv("recharge_revenue")
    folder1 = fr'{os.getenv("recharge_data_dump")}'
    oneTimeIngestionFolder = fr'{os.getenv("recharge_one_time_ingestion_folder")}'
    ingestedFilesFolder = fr'{os.getenv("recharge_ingested_files_folder")}'
except Exception as e:
    print(f"Error loading environment variables: {e}")
    sys.exit(1)

##### RETRIEVING INITIAL DATA FILES #####
today = sf.getNowDate()
subscriptionsFile = []
revenueFile = []

initialFiles = os.listdir(folder1)
if not initialFiles:
    print("No files found in the directory.")
    sys.exit(1)
try:
    for file in initialFiles:
        if "subscriptions_all" in file:
            subscriptionsFile.append(file)
        elif "subscription_vs_nonsubscription" in file:
            revenueFile.append(file)
except Exception as e:
    print(f"Error: {e}.")
    sys.exit(1)
    
##### ERROR HANDLING FOR FILE RETRIEVAL #####
if not subscriptionsFile or not revenueFile:
    print("ERROR: Required files not found in the directory.")
    sys.exit(1)
if len(subscriptionsFile)  > 1 or len(revenueFile) > 1:
    print("ERROR: Multiple files found for subscriptions or revenue. Please ensure only one file of each type is present.")
    sys.exit(1)
    
##### SUBSCRIPTION FILES SECTION AND DATA MANIPULATIONS #####")
print("##### Creating Singular Row DataFrame For Current Subscriptions And Subscribers #####")
time.sleep(0.5)
columns_to_keep = ["subscription_id", "customer_id", "status"]
try:
    subscribersSubscriptionsDF = pd.read_csv(os.path.join(folder1, subscriptionsFile[0]), usecols=columns_to_keep)
    subscribersSubscriptionsDF["status"] = subscribersSubscriptionsDF["status"].fillna("").str.lower() # Pre-clean the status column once.
    active_df = subscribersSubscriptionsDF[subscribersSubscriptionsDF["status"] == "active"].reset_index(drop=True)
    columns_to_keep = ["created_at", "cancelled_at"] # Reformatting the columns_to_keep list.
    sDatesDF = pd.read_csv(os.path.join(folder1, subscriptionsFile[0]), usecols=columns_to_keep) # Creating a new DF with only the date columns.
    try:
        sf.turningToDatetime(sDatesDF, sDatesDF.columns.to_list())
    except Exception as e:
        print(f"Error converting date columns {sDatesDF.columns.to_list()} to datetime: {e}")
        sys.exit(1)
    try:
        sf.timeDifference(sDatesDF)
    except Exception as e:
        print(f"Error calculating time difference: {e}")
        sys.exit(1)
    # Build a one row dataframe with columns: "date, activeSubscriptions, activeSubscribers, avgSubscriptionLengthDays".
    try:
        last_month = sf.getMonthYear()[2]
        current_month = sf.getMonthYear()[0] 
        current_year = sf.getMonthYear()[1]
        first_of_month = datetime(current_year, datetime.today().month, 1)
        fomStr = first_of_month.strftime('%Y-%m-%d')
        currentSS = pd.DataFrame([{
            "date": fomStr,
            "activeSubscriptions": active_df["subscription_id"].nunique(),
            "activeSubscribers": active_df["customer_id"].nunique(),
            "avgSubscriptionLengthDays": sDatesDF["timeDiffDays"].mean() if not sDatesDF.empty else 0 
        }])
    except IndexError as e:
        sys.exit(f"IndexError: {e}")
    except NameError as e:
        sys.exit(f"NameError: {e}")
    except TypeError as e:
        sys.exit(f"TypeError: {e}")
    except ValueError as e:
        sys.exit(f"ValueError: {e}")
    except Exception as e:
        sys.exit(f"The error that has occurred was not caught by the specific exceptions. Please see the error message: {e}")
except Exception as e:
    sys.exit(f"Error reading subscriptions file or error making 'currentSS' dataframe: {e}")

##### PRODUCT SUBSCRIPTIONS FILE SECTION AND DATA MANIPULATIONS #####
print("##### Beginning Process Of Product Subscriptions #####")
columns_to_keep = ["product_title", "created_at", "cancelled_at"]
try:
    sub_df_v1 = pd.read_csv(os.path.join(folder1, subscriptionsFile[0]), usecols=columns_to_keep)
    sub_df_v1["created_at"] = pd.to_datetime(sub_df_v1["created_at"], errors='coerce')
    sub_df_v1["cancelled_at"] = pd.to_datetime(sub_df_v1["cancelled_at"], errors='coerce')
    sub_df_v1 = sub_df_v1[~sub_df_v1["product_title"].str.lower().str.contains("test")].reset_index(drop=True) # dropping rows that have 'test' in the product_title
except Exception as e:
    sys.exit(f"Error reading or processing subscriptions file: {e}")
    
##### ACTIVE AND INACTIVE SUBSCRIPTIONS DATAFRAMES CREATION #####
print("##### Creating DataFrame For Active Subscriptions #####")
subCR_df_v1 = sub_df_v1[sub_df_v1["cancelled_at"].isnull()].reset_index()
columns_to_keep = ["product_title", "created_at"]
subCR_df_v1 = subCR_df_v1[columns_to_keep]
try:
    subCR_df_v1["Year"] = subCR_df_v1["created_at"].dt.year # type: ignore
    subCR_df_v1["Month"] = subCR_df_v1["created_at"].apply(lambda x: x.strftime('%B') if pd.notna(x) else '') 
except Exception as e:
    sys.exit(f"Error calculating the Year and Month columns for the created_at columns fields in subCR_df_v1 dataframe: {e}")
    
print("##### Creating DataFrame For Inactive Subscriptions #####")
subCA_df_v1 = sub_df_v1[sub_df_v1["cancelled_at"].notnull()].reset_index()
columns_to_keep = ["product_title", "cancelled_at"]
subCA_df_v1 = subCA_df_v1[columns_to_keep]
try:
    subCA_df_v1["cancelled_at"] = pd.to_datetime(subCA_df_v1["cancelled_at"], errors='coerce')
    subCA_df_v1["Year"] = subCA_df_v1["cancelled_at"].dt.year # type: ignore
    subCA_df_v1["Month"] = subCA_df_v1["cancelled_at"].apply(lambda x: x.strftime('%B') if pd.notna(x) else '')
except Exception as e:
    sys.exit(f"Error calculating the Year and Month columns for the created_at columns fields in subCA_df_v1 dataframe: {e}")

print("##### Grouping DataFrame Values #####")
time.sleep(0.5)
try:
    subCR_df_grouped = subCR_df_v1.groupby(["Year", "Month", "product_title"]).size().reset_index(name="subscriptionsActivated")
except Exception as e:
    sys.exit(f"Error grouping active subscriptions: {e}")
try:
    subCA_df_grouped = subCA_df_v1.groupby(["Year", "Month", "product_title"]).size().reset_index(name="subscriptionsCancelled")
except Exception as e:
    sys.exit(f"Error grouping inactive subscriptions: {e}")
try:
    grouped_subs = pd.merge(subCR_df_grouped, subCA_df_grouped, on=["Year", "Month", "product_title"], how="outer")
    grouped_subs.fillna(0, inplace=True)
    grouped_subs["subscriptionsActivated"] = grouped_subs["subscriptionsActivated"].astype(int)
    grouped_subs["subscriptionsCancelled"] = grouped_subs["subscriptionsCancelled"].astype(int)
    grouped_subs = grouped_subs[grouped_subs["Year"] == current_year]
    grouped_subs["Month"] = pd.Categorical(grouped_subs["Month"], categories=[current_month, last_month])
    grouped_subs = grouped_subs.dropna(subset=["Month"]).reset_index(drop=True)
except Exception as e:
    sys.exit(f"Error merging grouped dataframes: {e}")
try:
    for i in range(len(grouped_subs)):
        year = int(grouped_subs.at[i, "Year"])
        month = datetime.strptime(grouped_subs.at[i, "Month"], '%B').month
        grouped_subs.at[i, "dateIngested"] = datetime(year, month, 1).strftime('%Y-%m-%d')
except Exception as e:
    sys.exit(f"ERROR: Error creating the 'dateIngested' column: {e}")
    
##### REVENUE FILE SECTION AND DATA MANIPULATIONS #####
print("##### Creating DataFrame For Subscriptions VS Non-Subscriptions Revenue #####")
time.sleep(0.5)
revenueDF = pd.read_csv(os.path.join(folder1, revenueFile[0]))
revenueDF = revenueDF.drop(columns=["period"]) # Remove the "period" column.

##### EXCEL FILE CREATIONS #####
print("##### Creating Excel Files For Dashboard Ingestion #####")
try:
    year_folder = os.path.join(ingestedFilesFolder, str(sf.getMonthYear()[1]))
    if not os.path.exists(year_folder):
        os.makedirs(year_folder) # Create a folder for the current year if it doesn't exist.
    month_folder = os.path.join(year_folder, str(sf.getMonthYear()[0]))
    if not os.path.exists(month_folder):
        os.makedirs(month_folder) # Create a folder for the current month in year folder if it doesn't exist
except Exception as e:
    sys.exit(f"Error creating folders: {e}")
try:
    grouped_subs.to_excel(os.path.join(month_folder, f"UK_Subscriptions_{fomStr}.xlsx"), index=False, engine='openpyxl')
    revenueDF.to_excel(os.path.join(month_folder, f"UK_Revenue_{fomStr}.xlsx"), index=False, engine='openpyxl')
    currentSS.to_excel(os.path.join(month_folder, f"UK_Topline_Subscriptions_Data_{fomStr}.xlsx"), index=False, engine='openpyxl')
except Exception as e:
    sys.exit(f"Error creating Excel files and storing them to {month_folder}: {e}")

#### EMAIL CREATION AND SENDING #####
print("##### Creating and Sending Emails #####")
productEmailDataPath = ""
revenueEmailDataPath = ""
topLineEmailDataPath = ""
try:
    emailDataPaths = os.listdir(month_folder)
    for file in emailDataPaths:
        if file == f"UK_Revenue_{fomStr}.xlsx":
            revenueEmailDataPath = os.path.join(month_folder, file)
        elif file == f"UK_Subscriptions_{fomStr}.xlsx":
            productEmailDataPath = os.path.join(month_folder, file)
        elif file == f"UK_Topline_Subscriptions_Data_{fomStr}.xlsx":
            topLineEmailDataPath = os.path.join(month_folder, file)
        else:
            print(f"Unrecognised file {file} found in {month_folder}.")
            sys.exit(1)
except Exception as e:
    sys.exit(f"Error retrieving email data file paths from {month_folder}: {e}")
    
topLineEmail = sf.createEmail(
    subject="Catit UK Recharge Top Line Data For Datorama",
    sender=EMAIL_ADDRESS,
    receiver=RECHARGE_TOP_LINE,
    dataFile=topLineEmailDataPath,
    email_type="top-line"
)
productEmail = sf.createEmail(
    subject="Catit UK Recharge Product Subscriptions Data For Datorama",
    sender=EMAIL_ADDRESS,
    receiver=RECHARGE_PRODUCT_SUBSCRIPTIONS,
    dataFile=productEmailDataPath,
    email_type="product-subscriptions"
)
revenueEmail = sf.createEmail(
    subject="Catit UK Recharge Revenue Data For Datorama",
    sender=EMAIL_ADDRESS,
    receiver=RECHARGE_REVENUE,
    dataFile=revenueEmailDataPath,
    email_type="revenue"
)
sf.sendEmail(
    emails=[topLineEmail, productEmail, revenueEmail],
    username=EMAIL_ADDRESS,
    password=PASSWORD
)

#### DATA DUMP FILES REMOVAL #####
print("##### Removing Data Dump Files #####")
for file in initialFiles:
    try:
        os.remove(os.path.join(folder1, file))
    except Exception as e:
        sys.exit(f"Error removing file {file}: {e}")