import ifcopenshell

def update_chibb_spatial_zone_common(ifc_file_path, output_file_path):
    ifc_file = ifcopenshell.open(ifc_file_path)

    # Dictionary to hold space to zone mappings
    space_to_zone = {}
    
    # Collect all zones and their related spaces
    for assignment in ifc_file.by_type('IfcRelAssignsToGroup'):
        zone = assignment.RelatingGroup
        for obj in assignment.RelatedObjects:
            if obj.is_a('IfcSpace'):
                space_to_zone[obj] = zone

    # Set to track processed property sets
    processed_property_sets = set()

    # Iterate over spaces and their assigned zones
    for space, zone in space_to_zone.items():
        if space not in ifc_file:
            # If the space instance is not found, skip further processing for it
            continue

        # Check relationships defined by properties for the space
        for relDefinesByProperties in list(space.IsDefinedBy):
            if relDefinesByProperties.is_a('IfcRelDefinesByProperties'):
                property_set = relDefinesByProperties.RelatingPropertyDefinition
                if property_set.Name == 'CHIBB_SpatialZoneCommon':
                    # Check if the zone is a valid instance before proceeding
                    if zone not in ifc_file or property_set.GlobalId in processed_property_sets:
                        # Delete the relationship if the zone is not found or if already processed
                        ifc_file.remove(relDefinesByProperties)
                        print(f'Removed invalid or duplicate IfcRelDefinesByProperties {relDefinesByProperties.GlobalId}')
                        continue

                    # Mark this property set as processed to avoid duplicate handling
                    processed_property_sets.add(property_set.GlobalId)

                    # Update the relationship to point to the zone instead of the space
                    relDefinesByProperties.RelatedObjects = [zone]
                    print(f'Updated IfcRelDefinesByProperties for zone {zone.Name} to use CHIBB_SpatialZoneCommon')

    # Save the updated IFC file
    ifc_file.write(output_file_path)
    print(f'IFC file has been updated. File saved as: {output_file_path}')



ifc_file_path = r"C:\Users\LouisTrümpler\Dropbox\01_Projekte\2356_BUSA\240330_Diamant V3.4.ifc"
output_file_path = r"C:\Users\LouisTrümpler\Dropbox\01_Projekte\2356_BUSA\240330_Diamant V3.5.ifc"

update_chibb_spatial_zone_common(ifc_file_path, output_file_path)
