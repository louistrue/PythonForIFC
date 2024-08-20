import os

# Define the folder containing the .ifc files
folder_path = r'C:\Users\LouisTrümpler\Dropbox\01_Projekte\119_Lignum\Fassadensysteme 3D in llinumdata\Ifc'  

# Iterate over each file in the folder
for filename in os.listdir(folder_path):
    if filename.endswith('.ifc'):
        file_path = os.path.join(folder_path, filename)
        
        # Extract the SID value from the filename (e.g., SID.022)
        sid_value = filename.split('.')[0] + '.' + filename.split('.')[1]
        
        # Read the file content
        with open(file_path, 'r') as file:
            file_content = file.read()
        
        # Check if the SID value from the filename is in the file content
        if sid_value not in file_content:
            print(f"SID value {sid_value} from filename not found in file: {filename}")

print("Check completed.")
