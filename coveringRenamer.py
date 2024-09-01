import ifcopenshell
import os

# Define the directory with IFC files
ifc_folder = r'C:\Users\LouisTrümpler\Dropbox\01_Projekte\119_Lignum\Fassadensysteme 3D in llinumdata\Ifc - Renamed'
log_file_path = os.path.join(ifc_folder, "ifccovering_renamer_log.txt")

# The copyright statement to be added to IfcProject.Description
copyright_statement = (
    "Copyright Statement: All rights reserved.All intellectual property rights are owned by Lignum- Holzwirtschaft Schweiz, Muehlebachstrasse 8, 8008 Zuerich, Switzerland and is protected by copyright and other protective laws. The contents of this file are to be used only in accordance with the following Digital regulations.Digital regulations: This file may be downloaded for personal use only. Without the explicit written permission of Lignum- Holzwirtschaft Schweiz, it is prohibited to integrate this file in whole, in part, modified or transformed into other BIM Libraries, web sites or to distribute them by any commercial means in software and storage media. Liability: Lignum- Holzwirtschaft Schweiz has carefully compiled the contents of this Information in accordance with their current state of knowledge. Damage and warranty claims arising from missing or incorrect data are excluded. Lignum- Holzwirtschaft Schweiz bears no responsibility or liability for damage of any kind, also for indirect or consequential damages resulting from use of this file or websites related or connected to this by links."
)

# Open the log file for writing
with open(log_file_path, 'w') as log_file:
    # Iterate over all IFC files in the directory
    for filename in os.listdir(ifc_folder):
        if filename.endswith(".ifc"):
            ifc_file_path = os.path.join(ifc_folder, filename)

            # Load the IFC file
            model = ifcopenshell.open(ifc_file_path)

            updated = False  # Track if we made any updates

            # Find the first IfcArbitraryClosedProfileDef and get its ProfileName
            first_profile_name = None
            for profile in model.by_type("IfcArbitraryClosedProfileDef"):
                first_profile_name = profile.ProfileName
                break  # We only need the first one

            if first_profile_name:
                # Update all IfcCovering elements to use the first profile name
                for covering in model.by_type("IfcCovering"):
                    old_name = covering.Name
                    covering.Name = first_profile_name
                    updated = True
                    log_file.write(f"File: {filename} - Updated IFCCOVERING Name from '{old_name}' to '{first_profile_name}'\n")

            # Update the IfcProject.Description with the copyright statement
            ifc_project = model.by_type("IfcProject")[0]  # Assuming there is only one IfcProject in the file
            old_description = ifc_project.Description
            ifc_project.Description = copyright_statement
            updated = True
            log_file.write(f"File: {filename} - Updated IfcProject.Description from '{old_description}' to new copyright statement.\n")

            if updated:
                # Save the modified IFC file only if any update was made
                new_ifc_file_path = os.path.join(ifc_folder, f"_{filename}")
                model.write(new_ifc_file_path)
                log_file.write(f"Processed and saved: {new_ifc_file_path}\n")
            else:
                log_file.write(f"No IFCCOVERING elements updated in: {filename}\n")

    log_file.write("All files processed.\n")
