import os

def load_filenames_from_txt(file_path):
    """Load filenames from a text file, ignoring extensions."""
    with open(file_path, 'r') as file:
        filenames = file.read().splitlines()
    # Remove any empty lines and strip extensions
    filenames = [filename.strip() for filename in filenames if filename.strip()]
    return set(filenames)

def get_filenames_in_folder(folder_path):
    """Get all filenames in a folder, ignoring extensions."""
    filenames = [os.path.splitext(filename)[0] for filename in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, filename))]
    return set(filenames)

def compare_filenames(txt_file_path, folder_path):
    """Compare filenames in a text file with filenames in a folder, ignoring extensions."""
    txt_filenames = load_filenames_from_txt(txt_file_path)
    folder_filenames = get_filenames_in_folder(folder_path)

    print(f"Total filenames in nr.txt: {len(txt_filenames)}")
    print(f"Total filenames in folder: {len(folder_filenames)}")

    # Filenames in txt but not in folder
    missing_in_folder = txt_filenames - folder_filenames

    # Filenames in folder but not in txt
    missing_in_txt = folder_filenames - txt_filenames

    return missing_in_folder, missing_in_txt

# Define file paths
txt_file_path = r"C:\Users\LouisTrümpler\Documents\GitHub\IfcScripts\nr.txt"
folder_path = r"C:\Users\LouisTrümpler\Dropbox\01_Projekte\119_Lignum\Fassadensysteme 3D in llinumdata\Ifc"

# Perform comparison
missing_in_folder, missing_in_txt = compare_filenames(txt_file_path, folder_path)

# Output results
print("\nFilenames in nr.txt but not in folder:")
for filename in missing_in_folder:
    print(filename)

print("\nFilenames in folder but not in nr.txt:")
for filename in missing_in_txt:
    print(filename)
