import os
import pandas as pd
import json
import sys

def process_excel_files(folder_path):
    all_data = {}
    unique_names = set()

    # Get all Excel files from the given folder
    excel_files = [f for f in os.listdir(folder_path) if f.endswith(('.xlsx', '.xls'))]

    # Process each Excel file
    for file in excel_files:
        full_path = os.path.join(folder_path, file)
        # Read the Excel file into a DataFrame, assuming the first row contains the headers
        df = pd.read_excel(full_path, header=0)

        file_data = []

        for _, row in df.iterrows():
            guid = row.iloc[0]  # First column is 'guid'
            name = row.iloc[1]  # Second column is 'name'

            # Collect unique names
            if name not in unique_names:
                unique_names.add(name)

            # Collect additional properties except for the first two columns
            properties = {df.columns[i]: row.iloc[i] for i in range(2, len(df.columns))}

            file_data.append({
                "guid": guid,
                "name": name,
                "properties": properties
            })

        # Store the file data using the file name (without extension) as the key
        all_data[os.path.splitext(file)[0]] = file_data

    # Write all data to a single JSON file
    output_file = os.path.join(folder_path, 'combined_data.json')
    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(all_data, json_file, indent=4, ensure_ascii=False)

    # Print the list of unique names
    print("List of unique names from all Excel files:")
    for name in sorted(unique_names):
        print(name)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <folder_path>")
        sys.exit(1)

    folder_path = sys.argv[1]
    # Normalize the folder path for Windows
    folder_path = os.path.normpath(folder_path)
    process_excel_files(folder_path)



# Usage: python script.py <folder_path>  # e.g., python excel_to_json.py "C:\Users\LouisTrümpler\Dropbox\01_Projekte\2309 Pi\240423_Excel Attribut export test\240423_Excel Attribut export test"
