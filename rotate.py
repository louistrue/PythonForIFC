import ifcopenshell
import os
import math

# Directory containing IFC files
input_folder = r"C:\Users\LouisTrümpler\Dropbox\01_Projekte\119_Lignum\Fassadensysteme 3D in llinumdata\ifc_output"

# Rotation matrix for 270 degrees around Y-axis
cos_theta = math.cos(math.radians(270))
sin_theta = math.sin(math.radians(270))
rotation_matrix_y_270 = [
    [cos_theta, 0, sin_theta],
    [0, 1, 0],
    [-sin_theta, 0, cos_theta]
]

def rotate_point(point, matrix):
    """Apply rotation matrix to a 3D point."""
    x, y, z = point
    new_x = matrix[0][0] * x + matrix[0][2] * z
    new_y = y  # No change in the Y direction
    new_z = matrix[2][0] * x + matrix[2][2] * z
    return (new_x, new_y, new_z)

def rotate_direction(direction, matrix):
    """Apply rotation matrix to a direction vector."""
    dir_x, dir_y, dir_z = direction
    new_dir_x = matrix[0][0] * dir_x + matrix[0][2] * dir_z
    new_dir_y = dir_y  # No change in the Y direction
    new_dir_z = matrix[2][0] * dir_x + matrix[2][2] * dir_z
    return (new_dir_x, new_dir_y, new_dir_z)

def rotate_placement(placement, rotation_matrix):
    """Rotate the IfcLocalPlacement."""
    location = placement.RelativePlacement.Location
    new_coords = rotate_point(location.Coordinates, rotation_matrix)
    location.Coordinates = new_coords

    # Adjust axes if present
    if hasattr(placement.RelativePlacement, 'RefDirection') and placement.RelativePlacement.RefDirection:
        new_ref_direction = rotate_direction(placement.RelativePlacement.RefDirection.DirectionRatios, rotation_matrix)
        placement.RelativePlacement.RefDirection.DirectionRatios = new_ref_direction

    if hasattr(placement.RelativePlacement, 'Axis') and placement.RelativePlacement.Axis:
        new_axis = rotate_direction(placement.RelativePlacement.Axis.DirectionRatios, rotation_matrix)
        placement.RelativePlacement.Axis.DirectionRatios = new_axis

def process_ifc_file(filepath):
    """Process a single IFC file, rotating all placements by 270 degrees around Y-axis."""
    ifc_file = ifcopenshell.open(filepath)
    print(f"Processing file: {filepath}")

    # Rotate all local placements in the IFC file
    for element in ifc_file.by_type('IfcLocalPlacement'):
        rotate_placement(element, rotation_matrix_y_270)

    # Save the modified IFC file
    output_path = os.path.join(input_folder, f"rotated_{os.path.basename(filepath)}")
    ifc_file.write(output_path)
    print(f"Saved rotated IFC file as: {output_path}")

def main():
    # List all IFC files in the input folder
    ifc_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.ifc')]
    if not ifc_files:
        print("No IFC files found in the input directory.")
        return

    # Process each IFC file
    for ifc_filename in ifc_files:
        filepath = os.path.join(input_folder, ifc_filename)
        process_ifc_file(filepath)

if __name__ == "__main__":
    main()
