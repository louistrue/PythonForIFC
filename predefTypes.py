import re

def get_predefined_types(ifc_file_path):
    # Read the IFC file content
    with open(ifc_file_path, 'r', encoding='utf-8') as file:
        ifc_content = file.read()
    
    # Regex pattern to find specific entities with predefined types and capture the predefined type
    entity_pattern = re.compile(
        r'(#\d+=IFC(WALLSTANDARDCASE|DOOR|WINDOW|SLAB|COLUMN|BEAM|BUILDINGELEMENTPROXY|SYSTEMFURNITUREELEMENT)\([^)]*?\.(?P<predefined_type>[A-Z]+)\.\));',
        re.MULTILINE
    )

    # Find all specific entities with predefined types and capture groups
    matches = entity_pattern.finditer(ifc_content)
    
    # Collect the entities along with their predefined types
    predefined_entities = [(match.group(1), match.group('predefined_type')) for match in matches]
    
    return predefined_entities

ifc_file_path = 'C:\\Users\\LouisTrümpler\\Documents\\GitHub\\IfcLCA\\TestFiles\\IFC_testfiles\\2x3_CV_2.0 - Copy.ifc'
predefined_entities = get_predefined_types(ifc_file_path)

# Print the list of entities with their predefined types
for entity, predefined_type in predefined_entities:
    print(f'Entity: {entity}, Predefined Type: {predefined_type}')
