import os

# Folder containing the files
folder_path = ...

def add_subcontext_to_file(file_path):
    with open(file_path, 'r') as file:
        content = file.readlines()  # Read all lines in the file
    
    # Check the last 10 lines for the IFCGEOMETRICREPRESENTATIONCONTEXT
    for i in range(1, 11):
        if i > len(content):
            break  # If the file has less than 10 lines, avoid out-of-range errors
        line = content[-i].strip()
        if "IFCGEOMETRICREPRESENTATIONCONTEXT" in line:
            context_line = line
            context_id_str = context_line.split('=')[0].strip()[1:]  # Get the ID number as string, removing the '#'
            try:
                context_id = int(context_id_str)
            except ValueError:
                print(f"Error: Could not parse ID in line: {context_line}")
                return
            new_id = context_id + 1
            # Create the subcontext line with the incremented ID
            subcontext_line = f"#{new_id}=IFCGEOMETRICREPRESENTATIONSUBCONTEXT('Body','Brep',*,*,*,*,#{context_id},$,.MODEL_VIEW.,$);\n"
            # Insert the subcontext line after the context line
            content.insert(len(content) - i + 1, subcontext_line)
            with open(file_path, 'w') as file:
                file.writelines(content)
            print(f"Subcontext added with ID #{new_id} to: {file_path}")
            return
    
    print(f"No matching context found in the last 10 lines of: {file_path}")

# Iterate over all files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith(".ifc"):
        file_path = os.path.join(folder_path, filename)
        add_subcontext_to_file(file_path)
