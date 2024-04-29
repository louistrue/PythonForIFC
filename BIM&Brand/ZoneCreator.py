import ifcopenshell

def create_zones_based_on_room_property(ifc_file_path, output_file_path):
    ifc_file = ifcopenshell.open(ifc_file_path)
    owner_history = ifc_file.by_type("IfcOwnerHistory")[0]  # Assuming the first one is suitable for new objects

    zones = {}  # To keep track of existing zones by their names
    space_zone_relations = {}  # To accumulate spaces for each zone

    for space in ifc_file.by_type("IfcSpace"):
        for definition in space.IsDefinedBy:
            if definition.is_a("IfcRelDefinesByProperties") and definition.RelatingPropertyDefinition.is_a("IfcPropertySet"):
                property_set = definition.RelatingPropertyDefinition
                for property in property_set.HasProperties:
                    if property.Name == "Brandabschnitt":
                        zone_name = property.NominalValue.wrappedValue
                        if zone_name not in zones:
                            # Create new zone with ObjectType set to 'FireCompartment'
                            new_zone = ifc_file.create_entity('IfcZone', GlobalId=ifcopenshell.guid.new(), OwnerHistory=owner_history, Name=zone_name, ObjectType="FireCompartment")
                            zones[zone_name] = new_zone
                            space_zone_relations[zone_name] = [space]
                        else:
                            # Add space to the existing list for the zone
                            space_zone_relations[zone_name].append(space)
                        print(f"Space {space.Name} added to zone {zone_name}")

    # Now create IfcRelAssignsToGroup for each zone with all its spaces
    for zone_name, spaces in space_zone_relations.items():
        ifc_file.create_entity('IfcRelAssignsToGroup', GlobalId=ifcopenshell.guid.new(), RelatingGroup=zones[zone_name], RelatedObjects=spaces)
        print(f"Zone {zone_name} with object type 'FireCompartment' created with {len(spaces)} spaces.")

    ifc_file.write(output_file_path)
    print(f"IFC file updated with new zones. File saved as {output_file_path}")

ifc_file_path = r"C:\Users\LouisTrümpler\Dropbox\01_Projekte\2356_BUSA\240330_Diamant V3.3.ifc"
output_file_path = r"C:\Users\LouisTrümpler\Dropbox\01_Projekte\2356_BUSA\240330_Diamant V3.3.ifc"

create_zones_based_on_room_property(ifc_file_path, output_file_path)
