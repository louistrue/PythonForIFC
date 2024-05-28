import re

def extract_descriptions(content):
    element_regex = re.compile(
        r"IFC(WALLSTANDARDCASE|DOOR|WINDOW|SLAB|COLUMN|BEAM|BUILDINGELEMENTPROXY)\('([^']+)',#[^,]+,'([^']*)',[^,]*,'([^']*)'",
        re.IGNORECASE
    )
    results = []

    matches = element_regex.findall(content)
    for match in matches:
        element_type, global_id, name, description = match
        passed = description != '$' and description.strip() != ''
        results.append({
            'globalId': global_id,
            'name': name,
            'description': description,
            'passed': passed
        })
    
    return results

def main(ifc_file_path):
    with open(ifc_file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    results = extract_descriptions(content)
    for result in results:
        print(f"GlobalId: {result['globalId']}, Name: {result['name']}, "
              f"Description: {result['description']}, Passed: {result['passed']}")

if __name__ == "__main__":
    ifc_file_path = r"C:\Users\LouisTrümpler\Documents\GitHub\IfcLCA\TestFiles\IFC_testfiles\2x3_CV_2.0.ifc"
    main(ifc_file_path)
