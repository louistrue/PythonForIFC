import re

def get_storey_relations(content):
    rel_contained_regex = re.compile(r'#(\d+)=IFCRELCONTAINEDINSPATIALSTRUCTURE\([^,]*,[^,]*,.*?,\(([^)]*)\),#(\d+)\);', re.MULTILINE)
    related_entities = {}

    matches = rel_contained_regex.findall(content)
    for match in matches:
        entity_list = match[1]
        storey_id = match[2]
        entities = re.findall(r'#(\d+)', entity_list)
        for entity in entities:
            related_entities[entity] = storey_id

    return related_entities

def check_storey_relation(content):
    related_entities = get_storey_relations(content)

    entity_pattern = re.compile(
        r"#(?P<entityId>\d+)=IFC(WALLSTANDARDCASE|DOOR|WINDOW|SLAB|COLUMN|BEAM|BUILDINGELEMENTPROXY|SYSTEMFURNITUREELEMENT)\('(?P<globalId>[^']+)',#[^,]+,'(?P<name>[^']*)'",
        re.MULTILINE
    )

    results = []
    for match in entity_pattern.finditer(content):
        entity_id = match.group('entityId')
        global_id = match.group('globalId')
        name = match.group('name')
        passed = entity_id in related_entities
        results.append({
            'entityId': entity_id,
            'globalId': global_id,
            'name': name,
            'passed': passed,
            'storeyId': related_entities.get(entity_id)
        })

    return results

ifc_file_path = r'C:\Users\LouisTrümpler\Documents\GitHub\IfcLCA\TestFiles\IFC_testfiles\2x3_CV_2.0 - copy.ifc'
with open(ifc_file_path, 'r', encoding='utf-8') as file:
    content = file.read()

# Check storey relations and print results
results = check_storey_relation(content)

print("Results:")
for result in results:
    print(f"Global ID: {result['globalId']}, Name: {result['name']}, Passed: {result['passed']}, Storey ID: {result['storeyId']}")

# Identify and print unassigned elements
unassigned_results = [result for result in results if not result['passed']]
print("\nUnassigned Elements:")
for result in unassigned_results:
    print(f"Global ID: {result['globalId']}, Name: {result['name']}, Passed: {result['passed']}")
