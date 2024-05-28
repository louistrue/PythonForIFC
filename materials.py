import re

def get_elements_with_material_associations(ifc_content):
    rel_associates_material_regex = re.compile(
        r'(#\d+)=IFCRELASSOCIATESMATERIAL\([^,]*,[^,]*,.*?,\(([^)]*)\),#(\d+)\);', re.MULTILINE)
    element_regex = re.compile(r'#(\d+)')
    
    element_to_material = {}
    
    matches = rel_associates_material_regex.findall(ifc_content)
    print(f"Found {len(matches)} material associations.")
    
    element_ids = set(re.findall(r'#\d+', ifc_content))
    
    for match in matches:
        rel_id = match[0]
        material_id = match[2]
        for element_id in element_regex.findall(match[1]):
            full_id = f'#{element_id}'
            if full_id in element_ids and "TYPE" not in ifc_content.split(full_id, 1)[1][:50]:
                element_to_material[element_id] = material_id
                print(f"Added element ID {element_id} with material ID {material_id}")
    
    return element_to_material

def get_elements_with_material_assignments(ifc_content):
    element_to_material = get_elements_with_material_associations(ifc_content)
    return set(element_to_material.keys())

def debug_ifc_file(ifc_file_path):
    with open(ifc_file_path, 'r', encoding='utf-8') as file:
        ifc_content = file.read()
    
    elements_with_material_assignments = get_elements_with_material_assignments(ifc_content)
    
    print("Elements with material assignment:")
    for element_id in elements_with_material_assignments:
        print(f"Element ID: {element_id}, Material Assignment: Yes")



# Provide the path to the IFC file
ifc_file_path = r'C:\Users\LouisTrümpler\Dropbox\01_Projekte\118_IfcQA.open\10_ARC_Architektur_GN Palettenlager.ifc'
debug_ifc_file(ifc_file_path)
