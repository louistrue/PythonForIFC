import ifcopenshell

def find_invalid_entities(ifc_file_path):
    ifc_file = ifcopenshell.open(ifc_file_path)
    invalid_entities = []

    for rel_defines in ifc_file.by_type("IfcRelDefinesByProperties"):
        try:
            # Check if RelatingPropertyDefinition exists
            _ = rel_defines.RelatingPropertyDefinition
            # Ensure all related objects exist
            for related_obj in rel_defines.RelatedObjects:
                if related_obj not in ifc_file:
                    raise RuntimeError
        except RuntimeError:
            invalid_entities.append(rel_defines.id())
    
    return invalid_entities

def remove_entities_from_ifc(source_ifc_path, cleaned_ifc_path, invalid_entities):
    with open(source_ifc_path, 'r') as source, open(cleaned_ifc_path, 'w') as cleaned:
        for line in source:
            # Only write lines that don't declare an invalid entity
            if not any(f"#{entity_id}=" in line for entity_id in invalid_entities):
                cleaned.write(line)

def clean_ifc_file(source_ifc_path, cleaned_ifc_path):
    invalid_entities = find_invalid_entities(source_ifc_path)
    print(f"Invalid entity IDs: {invalid_entities}")
    remove_entities_from_ifc(source_ifc_path, cleaned_ifc_path, invalid_entities)
    print(f"Cleaned IFC file saved as: {cleaned_ifc_path}")

# Define your source and destination file paths
ifc_file_path = r"C:\Users\LouisTrümpler\Dropbox\01_Projekte\2356_BUSA\240330_Diamant V3.3.ifc"
output_file_path = r"C:\Users\LouisTrümpler\Dropbox\01_Projekte\2356_BUSA\240330_Diamant V3.4.ifc"

# Clean the IFC file
clean_ifc_file(ifc_file_path, output_file_path)
