import ifcopenshell

def update_space_names(ifc_file_path, output_file_path):
    # Load the IFC file
    ifc_file = ifcopenshell.open(ifc_file_path)
    
    # Iterate over all IFC spaces
    spaces = ifc_file.by_type("IfcSpace")
    spaces_updated = 0
    for space in spaces:
        # For each space, look for related property sets
        for definition in space.IsDefinedBy:
            if definition.is_a("IfcRelDefinesByProperties"):
                # Ensure the RelatingPropertyDefinition is a PropertySet
                if definition.RelatingPropertyDefinition.is_a("IfcPropertySet"):
                    property_set = definition.RelatingPropertyDefinition
                    # Check if the property set contains "Raumbezeichnung"
                    for property in property_set.HasProperties:
                        if property.Name == "Raumbezeichnung":
                            # Update the space name
                            new_name = property.NominalValue.wrappedValue
                            space.Name = new_name
                            spaces_updated += 1
                            print(f"Space ID: {space.id()} updated with new name: {new_name}")
    
    # Save the modified IFC file
    ifc_file.write(output_file_path)
    print(f"IFC file has been updated. {spaces_updated} spaces updated.")
    return spaces_updated

# Use the specific file paths as before
ifc_file_path = r"C:\Users\LouisTrümpler\Dropbox\01_Projekte\2356_BUSA\240329_Diamant V3.2.ifc"
output_file_path = r"C:\Users\LouisTrümpler\Dropbox\01_Projekte\2356_BUSA\240330_Diamant V3.3.ifc"

# Call the function
updated_spaces_count = update_space_names(ifc_file_path, output_file_path)
