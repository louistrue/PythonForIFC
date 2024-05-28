import os
import ifcopenshell

def get_entities_with_local_placement(ifc_file):
    """Extracts entities with LocalPlacement from the IFC file."""
    entities_with_geometry = []
    for entity in ifc_file:
        if hasattr(entity, "ObjectPlacement") and entity.ObjectPlacement is not None:
            entities_with_geometry.append(entity)
    return entities_with_geometry

def extract_entity_types(entities):
    """Extracts unique entity types from the list of entities."""
    entity_types = set()
    for entity in entities:
        entity_types.add(entity.is_a())
    return entity_types

def process_ifc_files(folder_path):
    """Processes all IFC files in the given folder and prints unique entity types with geometry."""
    all_entity_types = set()
    for filename in os.listdir(folder_path):
        if filename.endswith(".ifc"):
            file_path = os.path.join(folder_path, filename)
            ifc_file = ifcopenshell.open(file_path)
            entities = get_entities_with_local_placement(ifc_file)
            entity_types = extract_entity_types(entities)
            all_entity_types.update(entity_types)
    
    # Format and print the result
    formatted_result = "|".join(sorted(all_entity_types))
    print(f"Entities with geometry in all files:\n{formatted_result}")

if __name__ == "__main__":
    folder_path = r"C:\Users\LouisTrümpler\Dropbox\01_Projekte\118_IfcQA.open"  # Change this to your IFC files folder path
    process_ifc_files(folder_path)
