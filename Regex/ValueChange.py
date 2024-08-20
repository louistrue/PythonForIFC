import os

# Define the folder containing the .ifc files
folder_path = r'C:\Users\LouisTrümpler\Desktop\Lig' 

# Iterate over each file in the folder
for filename in os.listdir(folder_path):
    if filename.endswith('.ifc'):
        file_path = os.path.join(folder_path, filename)
        
        # Extract the SID value from the filename (e.g., SID.022)
        new_sid = filename.split('.')[0] + '.' + filename.split('.')[1]
        
        # Read the file content
        with open(file_path, 'r') as file:
            file_content = file.read()
        
        # Replace SID.001 with the new SID
        updated_content = file_content.replace('SID.001', new_sid)
        
        # Write the updated content back to the file
        with open(file_path, 'w') as file:
            file.write(updated_content)

print("Replacement completed.")
