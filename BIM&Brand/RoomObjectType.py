import ifcopenshell

def update_spaces(ifc_file_path, output_file_path):
    ifc_file = ifcopenshell.open(ifc_file_path)
    spaces_to_update = {}

    # Define the mapping from Raumtyp Präzisierung to ObjectType
    english_mapping = {
        "Stockwerk": "BuildingStorey",
        "Feuerwehr": "Firebrigade Access",
        "Gebäude": "Building",
        "Firebrigade Installation Spot": "Firebrigade Installation Spot"
    }

    # First pass: Identify spaces that need updating and their new ObjectType
    for space in ifc_file.by_type("IfcSpace"):
        for definition in space.IsDefinedBy:
            if definition.is_a("IfcRelDefinesByProperties"):
                property_set = definition.RelatingPropertyDefinition
                if property_set and property_set.is_a("IfcPropertySet"):
                    for property in property_set.HasProperties:
                        if property.Name == "Raumtyp Präzisierung":
                            value = property.NominalValue.wrappedValue if property.NominalValue else None
                            if value and value != "ND" and value in english_mapping:
                                spaces_to_update[space] = english_mapping[value]
                            break  # Assuming only one relevant property per space

    # Second pass: Apply the ObjectType updates
    for space, object_type in spaces_to_update.items():
        space.ObjectType = object_type
        print(f"Space {space.Name} updated to ObjectType '{object_type}'.")

    # Save the updated IFC file
    ifc_file.write(output_file_path)
    print(f"IFC file has been updated with {len(spaces_to_update)} spaces updated. File saved as: {output_file_path}")

ifc_file_path = r"C:\Users\LouisTrümpler\Dropbox\01_Projekte\2356_BUSA\240330_Diamant V3.3.ifc"
output_file_path = r"C:\Users\LouisTrümpler\Dropbox\01_Projekte\2356_BUSA\240330_Diamant V3.3.ifc"

update_spaces(ifc_file_path, output_file_path)

