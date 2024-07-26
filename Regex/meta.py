import re
import os

def extract_metadata(content: str):
    metadata = {
        'organization': 'Nicht definiert',
        'author': 'Nicht definiert',
        'timestamp': 'Nicht definiert',
        'number_of_saves': 'Nicht definiert'
    }

    # Extract organization from IFCPERSONANDORGANIZATION or IFCORGANIZATION
    org_matches = re.findall(r"#\d+=IFCPERSONANDORGANIZATION\([^,]+,#\d+\$(?:,|\)\$)", content, re.IGNORECASE)
    if not org_matches:
        org_matches = re.findall(r"#\d+=IFCORGANIZATION\(\$,'([^']*)'", content, re.IGNORECASE)
    
    organizations = [match for match in org_matches]
    if organizations:
        metadata['organization'] = ", ".join(organizations)
    
    # Extract author from IFCPERSONANDORGANIZATION or IFCPERSON
    author_match = re.search(r"#\d+=IFCPERSON\(\$,'([^']*)'", content, re.IGNORECASE)
    if author_match:
        metadata['author'] = author_match.group(1)
    else:
        author_match = re.search(r"#\d+=IFCPERSONANDORGANIZATION\([^,]+,#\d+\$,(#\d+)\);", content, re.IGNORECASE)
        if author_match:
            person_id = author_match.group(1)
            person_match = re.search(fr"{person_id}=IFCPERSON\(\$,'([^']*)'", content, re.IGNORECASE)
            if person_match:
                metadata['author'] = person_match.group(1)

    # Extract timestamp
    timestamp_match = re.search(r"FILE_NAME\('[^']*','([^']*)'", content, re.IGNORECASE)
    if timestamp_match:
        metadata['timestamp'] = timestamp_match.group(1)
        
    return metadata

def read_ifc_file(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def process_directory(directory_path: str):
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.lower().endswith('.ifc'):
                file_path = os.path.join(root, file)
                try:
                    content = read_ifc_file(file_path)
                    metadata = extract_metadata(content)
                    print(f"File: {file_path}")
                    print(f"Organization: {metadata['organization']}")
                    print(f"Author: {metadata['author']}")
                    print(f"Timestamp: {metadata['timestamp']}")
                    print("-" * 40)
                except Exception as e:
                    print(f"Failed to process {file_path}: {e}")

def main():
    directory_path = r'C:\Users\LouisTrümpler\Documents\GitHub\IfcLCA\TestFiles\IFC_testfiles'
    process_directory(directory_path)

if __name__ == "__main__":
    main()
