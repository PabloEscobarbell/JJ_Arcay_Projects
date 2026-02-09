import pandas as pd
import re
from dotenv import load_dotenv
import os

def is_valid_structure(name):
    """
    Takes in (name) as a parameter and returns True if the name has a valid structure.
    A name is considered to have a valid structure if:
    - It contains only alphabetic characters, spaces, periods, apostrophes, and hyphens.
    - It does not contain any numbers or special characters.
    """
    return bool(re.match(r"^[A-Za-z .'-]+$", name))

def is_nonsense(name):
    """
    Takes in (name) as a parameter and returns True if the name is nonsense or empty.
    A name is considered nonsense or empty if:
    - It is less than 2 characters or more than 25 characters long.
    - It contains less than 50% alphabetic characters.
    - It is NaN or consists only of whitespace.
    """
    if len(name) < 2 or len(name) > 25:
        return True
    if sum(c.isalpha() for c in name) / len(name) < 0.5:
        return True
    if pd.isna(name) or name.strip() == "":
        return True
    return False

def case_transitions(name):
    """
    Takes in (name) as a parameter and returns True if there are more than 8 transitions between upper and lower case letters.
    A transition is defined as a change from upper to lower case or vice versa.
    """
    transitions = 0
    prev = None
    for c in name:
        if c.isalpha():
            current = c.isupper()
            if prev is not None and current != prev:
                transitions += 1
            prev = current
    if transitions >= 8:
        return True
    else:
        return False
    
def tag_name(name):
    """
    Tags the name (function input) based on its structure and content.
    """
    if not is_valid_structure(name):
        return "warning: format"
    elif is_nonsense(name):
        return "warning: nonsense or empty"
    elif case_transitions(name):
        return "warning: high number of case transitions. Possibly fake name."
    else:
        return "valid"
    

########## Main Function ##########
# Get files
load_dotenv()
file_path = os.getenv("input_file_path")
output_file_path = os.getenv("output_file_path")
original_data = pd.read_excel(file_path, engine='openpyxl')
cleaned_data = original_data.copy()
cleaned_data["First Name"] = cleaned_data["First Name"].astype(str).str.strip()
cleaned_data["name_status"] = cleaned_data["First Name"].apply(tag_name)
cleaned_data.to_excel(output_file_path, index=False, engine='openpyxl')

