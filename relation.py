import re

def get_ifc_relationships(ifc_content):
    rel_aggregates_regex = re.compile(r'#(\d+)=IFCRELAGGREGATES\([^,]*,[^,]*,.*?,#(\d+),\(([^)]*)\)\);', re.MULTILINE)
    relationships = {}

    matches = rel_aggregates_regex.finditer(ifc_content)
    for match in matches:
        parent_id = match.group(2)
        children_ids = re.findall(r'#(\d+)', match.group(3))
        if parent_id not in relationships:
            relationships[parent_id] = []
        relationships[parent_id].extend(children_ids)

    return relationships

def get_storey_relations(ifc_content):
    rel_contained_regex = re.compile(r'#(\d+)=IFCRELCONTAINEDINSPATIALSTRUCTURE\([^,]*,[^,]*,.*?,\(([^)]*)\),#(\d+)\);', re.MULTILINE)
    related_entities = {}

    matches = rel_contained_regex.findall(ifc_content)
    for match in matches:
        entity_list = match[1]
        storey_id = match[2]
        entities = re.findall(r'#(\d+)', entity_list)
        for entity in entities:
            related_entities[entity] = storey_id

    return related_entities

def get_building_storeys(ifc_content):
    building_storeys_regex = re.compile(r'#(\d+)=IFCBUILDINGSTOREY\(', re.MULTILINE)
    storey_ids = []

    matches = building_storeys_regex.findall(ifc_content)
    storey_ids.extend(matches)

    return storey_ids

def get_elements_in_storeys(ifc_content):
    storey_elements_regex = re.compile(r'#(\d+)=IFCRELCONTAINEDINSPATIALSTRUCTURE\([^,]*,[^,]*,.*?,\(([^)]*)\),#(\d+)\);', re.MULTILINE)
    elements_in_storeys = {}

    matches = storey_elements_regex.findall(ifc_content)
    for match in matches:
        storey_id = match[2]
        elements = re.findall(r'#(\d+)', match[1])
        for element in elements:
            elements_in_storeys[element] = storey_id

    return elements_in_storeys

def check_storey_relation(ifc_content):
    storey_ids = get_building_storeys(ifc_content)
    storey_elements = get_elements_in_storeys(ifc_content)
    rel_aggregates = get_ifc_relationships(ifc_content)

    all_storey_ids = set(storey_ids)
    for storey_id in storey_ids:
        if storey_id in rel_aggregates:
            all_storey_ids.update(rel_aggregates[storey_id])

    results = []
    entity_pattern = re.compile(
        r"#(?P<entityId>\d+)=IFC(WALLSTANDARDCASE|DOOR|WINDOW|SLAB|COLUMN|BEAM|BUILDINGELEMENTPROXY|SYSTEMFURNITUREELEMENT|JUNCTIONBOX|DUCTSEGMENT)\('(?P<globalId>[^']+)',#[^,]+,'(?P<name>[^']*)'",
        re.MULTILINE
    )

    for match in entity_pattern.finditer(ifc_content):
        entity_id = match.group('entityId')
        global_id = match.group('globalId')
        name = match.group('name')
        storey_id = storey_elements.get(entity_id)
        passed = storey_id in all_storey_ids if storey_id else False
        results.append({
            'entityId': entity_id,
            'globalId': global_id,
            'name': name,
            'passed': passed,
            'storeyId': storey_id
        })

    return results

def debug_file(ifc_file_path):
    with open(ifc_file_path, 'r', encoding='utf-8') as file:
        ifc_content = file.read()

    results = check_storey_relation(ifc_content)
    
    print("Results:")
    for result in results:
        print(f"Global ID: {result['globalId']}, Name: {result['name']}, Passed: {result['passed']}, Storey ID: {result['storeyId']}")

    # Identify and print unassigned elements
    unassigned_results = [result for result in results if not result['passed']]
    print("\nUnassigned Elements:")
    for result in unassigned_results:
        print(f"Global ID: {result['globalId']}, Name: {result['name']}, Passed: {result['passed']}")

# Debugging first file
debug_file(r'C:\Users\LouisTrümpler\Documents\GitHub\IfcLCA\TestFiles\IFC_testfiles\2x3_CV_2.0 - Copy.ifc')

# Debugging second file
debug_file(r'C:\Users\LouisTrümpler\Dropbox\01_Projekte\118_IfcQA.open\10_ARC_Architektur_GN Palettenlager.ifc')
