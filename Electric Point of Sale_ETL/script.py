import os
import sys
import pandas as pd
import epos_functions as epos
from dotenv import load_dotenv

##### Get files and path for temporary hold folder #####
try:
    load_dotenv()
    data_dump = fr"{os.getenv('epos_data_dump')}"
    tempHold = fr"{os.getenv('epos_temp_hold')}"
    files = epos.get_files(directory=data_dump)
except Exception as e:
    sys.exit(f"Failed to load environment variables or get files: {e}")
    
for file in files:
    print(f"Processing file: {file}")
    file_path: str = str(os.path.join(data_dump, file))
    df = pd.read_csv(file_path, encoding='utf-8', encoding_errors='ignore') # Create the dataframe for the opened file.
    df.to_csv(os.path.join(tempHold, file), index=False) # Save a copy to temporaryHold.
    
    ##### Checking if "List Number" column is present. #####
    if 'List Number' in df.columns:
        cols = ['List Number'] + [col for col in df.columns if col != 'List Number']
        df = df[cols]
    else:   
        epos.send_error_notification(file_path=file_path, error_msg="Missing 'List Number' column.")
        sys.exit()
    
    ##### Checking health of "Shop Name" column. #####
    if df["Shop Name"].isnull().any():
        epos.send_error_notification(file_path=file_path, error_msg="Missing values found in 'Shop Name' column.")
        sys.exit()
    
    ##### Ensuring that all necessary columns have a data type specified. #####
    epos.data_types(df)
    epos.generate_list_numbers(df)
    
    ##### Creating variables to use in file naming #####
    df.columns = df.columns.astype(str)
    year = epos.get_date_year(df)[0]
    full_date = epos.get_date_year(df)[1]
    customer_name = epos.get_customer_name(df)
    
    ##### Data transformations #####
    if 'Specific Units' not in df.columns:
        epos.create_specific_units_column(df)
    
    epos.create_revenue_column(df)
    epos.remove_commas(df, column="Description")
    epos.uppercase_column_values(df, "Shop Name", "Location", "Product Brand", "Product Sub Brand", "Product Group", "Product Code")
    epos.specific_unit_adjustment(df)
    epos.brand_name_corrections(df)
    epos.shop_name_corrections(df)
    epos.best_pets_adjustment(df)
    
    ##### Creating mapping key for data #####
    epos.create_mapping_key(df)
    
    ##### Saving CSV #####
    try:
        customer_folder = fr"C:\Users\javeryard\OneDrive - rchagen\PC\Desktop\Hagen UK EPOS\customers\{year}\{customer_name}"
        os.makedirs(customer_folder, exist_ok=True)
        customer_folder_data_path = os.path.join(customer_folder, f"{customer_name}_{full_date}.csv")
    except Exception as e:
        sys.exit(f"Failed to create customer folder or define file path: {e}")
    
    try:
        df.to_csv(customer_folder_data_path, index=False)
    except Exception as e:
        sys.exit(f"Failed to save cleaned CSV: {e}")
    
    ##### Sending data to data stream #####
    epos.send_to_data_stream(store=customer_name, file_path=customer_folder_data_path, date=full_date)
        
    ##### Deleting original file #####
    try:
        print(f"Finished processing {file}, now deleting original file...")
        os.remove(file_path)
        print(f"Original file {file_path} deleted successfully.")
    except Exception as e:
        sys.exit(f"Failed to delete original file: {e}")