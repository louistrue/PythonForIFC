import re

def process_chunk(chunk, entity_pattern, rel_defines_by_type_pattern, entities_with_details, all_related_entities):
    # Find all entities with details in the chunk
    entity_matches = entity_pattern.finditer(chunk)
    for match in entity_matches:
        entities_with_details[match.group('entityId')] = {
            'type': match.group('entityType'),
            'globalId': match.group('globalId'),
            'name': match.group('name')
        }
    
    # Find all IfcRelDefinesByType relationships in the chunk
    rel_defines_by_type_matches = rel_defines_by_type_pattern.finditer(chunk)
    for match in rel_defines_by_type_matches:
        related_entities = match.group('relatedEntities').split(',')
        for entity in related_entities:
            entity = entity.strip('#')
            all_related_entities.add(entity)

def get_entities_with_types(ifc_file_path):
    try:
        # Define regex patterns
        entity_pattern = re.compile(
            r"#(?P<entityId>\d+)=IFC(?P<entityType>WALLSTANDARDCASE|DOOR|WINDOW|SLAB|COLUMN|BEAM|BUILDINGELEMENTPROXY|JUNCTIONBOX|DUCTSEGMENT|SYSTEMFURNITUREELEMENT|WALLTYPE|DOORTYPE|WINDOWTYPE|SLABTYPE|COLUMNTYPE|BEAMTYPE|PROXYTYPE|JUNCTIONBOXTYPE|DUCTSEGMENTTYPE|SYSTEMFURNITUREELEMENTTYPE)\('(?P<globalId>[^']*)',[^,]*,'(?P<name>[^']*)',[^,]*,'(?P<type>[^']*)'",
            re.IGNORECASE
        )
        rel_defines_by_type_pattern = re.compile(
            r"#(?P<relId>\d+)=IFCRELDEFINESBYTYPE\('[^']*',#\d+,\$,\$,\((?P<relatedEntities>#\d+(?:,#\d+)*)\),#(?P<relatedType>\d+)\);",
            re.MULTILINE
        )

        # Initialize containers for entity details and relationships
        entities_with_details = {}
        all_related_entities = set()

        # Process the IFC file in chunks
        chunk_size = 5 * 1024 * 1024  # 5MB
        with open(ifc_file_path, 'r', encoding='utf-8') as file:
            while True:
                chunk = file.read(chunk_size)
                if not chunk:
                    break
                process_chunk(chunk, entity_pattern, rel_defines_by_type_pattern, entities_with_details, all_related_entities)

        # Additional pass to capture details for entities that were not found initially
        missing_entities = all_related_entities - entities_with_details.keys()
        if missing_entities:
            additional_entity_pattern = re.compile(
                r"#(?P<entityId>{})(?P<remainingContent>=[^;]*);".format("|".join(missing_entities))
            )
            with open(ifc_file_path, 'r', encoding='utf-8') as file:
                while True:
                    chunk = file.read(chunk_size)
                    if not chunk:
                        break
                    additional_matches = additional_entity_pattern.finditer(chunk)
                    for match in additional_matches:
                        entity_id = match.group('entityId')
                        remaining_content = match.group('remainingContent')
                        entity_details_pattern = re.compile(
                            r"IFC(?P<entityType>[A-Z0-9]+)\('(?P<globalId>[^']*)',[^,]*,'(?P<name>[^']*)'"
                        )
                        details_match = entity_details_pattern.search(remaining_content)
                        if details_match:
                            entities_with_details[entity_id] = {
                                'type': details_match.group('entityType'),
                                'globalId': details_match.group('globalId'),
                                'name': details_match.group('name')
                            }

        # Filter out entities that end with 'TYPE'
        filtered_entities = [
            (entity_id, details['type'], details['globalId'], details['name'])
            for entity_id, details in entities_with_details.items()
            if entity_id in all_related_entities and not details['type'].endswith('TYPE')
        ]

        return filtered_entities

    except Exception as e:
        print(f"An error occurred: {e}")
        return []

ifc_file_path = 
filtered_entities = get_entities_with_types(ifc_file_path)

# Print the list of entities with their types, global IDs, and names
print("Entities found:")
for entity_id, entity_type, global_id, name in filtered_entities:
    print(f'Entity ID: {entity_id}, Type: {entity_type}, Global ID: {global_id}, Name: {name}')
