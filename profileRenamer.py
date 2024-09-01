import ifcopenshell
import pandas as pd
import os

# Load Excel file with the mapping information
excel_file_path = r'.xlsx'

mapping_df = pd.read_excel(excel_file_path)

# Create a mapping of each individual code to its corresponding profile name
code_to_name_mapping = {}

for index, row in mapping_df.iterrows():
    # Split the codes by ';' and map each one to the profile name
    codes = str(row[1]).strip().upper().split(';')
    profile_name = str(row[3]).strip()
    
    for code in codes:
        code = code.strip()  # Remove any extra whitespace around the code
        if code:  # Make sure the code is not empty
            code_to_name_mapping[code] = profile_name

# Define the directory with IFC files
ifc_folder = r'\Ifc'
log_file_path = os.path.join(ifc_folder, "profile_renamer_log.txt")

# Open the log file for writing
with open(log_file_path, 'w') as log_file:
    # Iterate over all IFC files in the directory
    for filename in os.listdir(ifc_folder):
        if filename.endswith(".ifc"):
            ifc_file_path = os.path.join(ifc_folder, filename)
            # Extract the base filename without extension
            base_filename = os.path.splitext(filename)[0].upper()

            # Initialize a flag to track if we made any updates
            updated = False

            # Load the IFC file
            model = ifcopenshell.open(ifc_file_path)

            # Iterate over code_to_name_mapping to find a match in the filename
            for code, new_profile_name in code_to_name_mapping.items():
                if code in base_filename:
                    # Iterate through all elements and find relevant IFCARBITRARYCLOSEDPROFILEDEF
                    for element in model.by_type("IfcArbitraryClosedProfileDef"):
                        # Check if ProfileName is None, empty, or matches the code
                        if element.ProfileName is None or element.ProfileName.strip() == "" or element.ProfileName.strip().upper() == code:
                            old_profile_name = "Unnamed" if element.ProfileName is None else element.ProfileName.strip()
                            element.ProfileName = new_profile_name
                            updated = True
                            log_file.write(f"File: {filename} - Updated ProfileName from '{old_profile_name}' to '{new_profile_name}'\n")

            if updated:
                # Save the modified IFC file only if any update was made
                new_ifc_file_path = os.path.join(ifc_folder, f"profileName_{filename}")
                model.write(new_ifc_file_path)
                log_file.write(f"Processed and saved: {new_ifc_file_path}\n")
            else:
                log_file.write(f"No matching or relevant ProfileName found to update in: {filename}\n")

    log_file.write("All files processed.\n")
