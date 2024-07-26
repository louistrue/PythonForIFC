import ifcopenshell

def get_placement_info(ifc_file):
    """
    Extracts the global placement information from an IFC file.
    """
    axis_placements = ifc_file.by_type("IFCAXIS2PLACEMENT3D")
    
    for placement in axis_placements:
        location = placement.Location
        ref_direction = placement.RefDirection if placement.RefDirection else [1.0, 0.0, 0.0]  # Default direction
        axis = placement.Axis if placement.Axis else [0.0, 0.0, 1.0]  # Default axis
        
        loc_coordinates = location.Coordinates
        ref_dir_values = ref_direction.DirectionRatios if ref_direction else None
        axis_values = axis.DirectionRatios if axis else None
        
        return loc_coordinates, ref_dir_values, axis_values
    return None, None, None

def validate_direction(direction):
    if direction is None:
        raise ValueError("Direction is None. It must be a list or tuple with 3 numeric values.")
    if len(direction) != 3:
        raise ValueError("Direction must have exactly 3 elements.")
    if not all(isinstance(x, (int, float)) for x in direction):
        raise ValueError("All elements of the direction must be numeric.")

def update_placement(ifc_file, new_location, new_ref_direction, new_axis):
    """Update the placement location, reference direction, and axis of elements."""
    
    # Debug: print the values before validation
    print(f"new_ref_direction: {new_ref_direction}")
    print(f"new_axis: {new_axis}")
    
    # Validate input
    validate_direction(new_ref_direction)
    validate_direction(new_axis)
    
    # Get the IfcProject
    project = ifc_file.by_type('IfcProject')[0]
    
    # Get the IfcGeometricRepresentationContext
    geom_context = project.RepresentationContexts[0]
    
    # Create new placement
    origin = ifc_file.createIfcCartesianPoint(new_location)
    ref_direction = ifc_file.createIfcDirection(new_ref_direction)
    axis = ifc_file.createIfcDirection(new_axis)
    
    placement = ifc_file.createIfcAxis2Placement3D(origin, axis, ref_direction)
    local_placement = ifc_file.createIfcLocalPlacement(None, placement)
    
    # Apply new placement to all IfcProduct instances
    for product in ifc_file.by_type('IfcProduct'):
        if product.ObjectPlacement:
            product.ObjectPlacement.RelativePlacement = placement

    print(f"Updated placement with location {new_location}, reference direction {new_ref_direction}, axis {new_axis}.")

def move_elements_to_reference(new_file_path, reference_file_path, output_file_path):
    """Main function to move elements to the reference location."""
    
    new_ifc = ifcopenshell.open(new_file_path)
    reference_ifc = ifcopenshell.open(reference_file_path)
    
    # Retrieve placement from the reference file
    reference_placement = next((product.ObjectPlacement for product in reference_ifc.by_type('IfcProduct') if product.ObjectPlacement), None)
    if not reference_placement:
        raise ValueError("No placement found in the reference file.")
    
    # Retrieve the IfcAxis2Placement3D details from the reference
    placement_3d = reference_placement.RelativePlacement
    new_location = placement_3d.Location.Coordinates
    
    # Check if RefDirection and Axis exist
    new_ref_direction = placement_3d.RefDirection.DirectionRatios if placement_3d.RefDirection else [1.0, 0.0, 0.0]
    new_axis = placement_3d.Axis.DirectionRatios if placement_3d.Axis else [0.0, 0.0, 1.0]

    # Debug: print retrieved values
    print(f"Reference Location: {new_location}")
    print(f"Reference RefDirection: {new_ref_direction}")
    print(f"Reference Axis: {new_axis}")

    # Update placements in the new IFC file
    update_placement(new_ifc, new_location, new_ref_direction, new_axis)
    
    # Save the updated file
    new_ifc.write(output_file_path)

# Example usage
if __name__ == "__main__":
    new_file_path = r"C:\Users\LouisTrümpler\Downloads\2396_BM_Test_Mock_up.ifc"
    reference_file_path = r"C:\Users\LouisTrümpler\Downloads\2396_240205_Mock_Up_Tragwerk_georeferenziert.ifc"
    output_file_path = r"C:\Users\LouisTrümpler\Downloads\2396_BM_Test_Mock_up_georeferenziert.ifc"
    move_elements_to_reference(new_file_path, reference_file_path, output_file_path)
