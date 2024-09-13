import ifcopenshell
import os
import math

def is_collinear(p1, p2, p3, tolerance=1e-10):
    """
    Check if three points (p1, p2, p3) are collinear.
    Points are collinear if the area of the triangle they form is zero.
    This function now uses a near-zero tolerance to prevent unwanted deletions.
    """
    if len(p1) == 2 and len(p2) == 2 and len(p3) == 2:
        # 2D case
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        # Calculate the area of the triangle formed by the three points
        area = 0.5 * abs(x1*(y2 - y3) + x2*(y3 - y1) + x3*(y1 - y2))
        return area < tolerance
    elif len(p1) == 3 and len(p2) == 3 and len(p3) == 3:
        # 3D case
        x1, y1, z1 = p1
        x2, y2, z2 = p2
        x3, y3, z3 = p3
        
        # Calculate the vectors p1p2 and p1p3
        v1 = (x2 - x1, y2 - y1, z2 - z1)
        v2 = (x3 - x1, y3 - y1, z3 - z1)
        
        # Calculate the cross product of the two vectors
        cross_product = (
            v1[1] * v2[2] - v1[2] * v2[1],
            v1[2] * v2[0] - v1[0] * v2[2],
            v1[0] * v2[1] - v1[1] * v2[0]
        )
        
        # The points are collinear if the magnitude of the cross product is zero
        cross_magnitude = math.sqrt(cross_product[0] ** 2 + cross_product[1] ** 2 + cross_product[2] ** 2)
        return cross_magnitude < tolerance
    else:
        raise ValueError("All points must have the same dimension (either 2D or 3D)")

def get_cartesian_point_coordinates(cartesian_point):
    """
    Extract the coordinates from an IFCCARTESIANPOINT entity.
    """
    return tuple(cartesian_point.Coordinates)

def simplify_and_save_ifc_file(ifc_file_path):
    # Load the IFC file
    ifc_file = ifcopenshell.open(ifc_file_path)

    # Iterate over all polyline entities in the file
    for polyline in ifc_file.by_type("IFCPOLYLINE"):
        points = polyline.Points
        retained_points = []
        
        # Iterate through points in triplets to check for collinearity
        for i in range(len(points)):
            if i == 0 or i == len(points) - 1:
                # Always keep the first and last points
                retained_points.append(points[i])
            else:
                # Check if the points are collinear
                p1 = get_cartesian_point_coordinates(points[i-1])
                p2 = get_cartesian_point_coordinates(points[i])
                p3 = get_cartesian_point_coordinates(points[i+1])
                
                if not is_collinear(p1, p2, p3):
                    retained_points.append(points[i])
        
        # Replace the points in the polyline with the retained points
        polyline.Points = retained_points
    
    # Save the simplified IFC file under the same name
    ifc_file.write(ifc_file_path)

def simplify_all_ifc_files_in_folder(folder_path):
    # Iterate over all files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".ifc"):
            file_path = os.path.join(folder_path, filename)
            simplify_and_save_ifc_file(file_path)
            print(f"Processed and saved: {filename}")

# Example usage
folder_to_process = r"C:\Users\LouisTrümpler\Dropbox\01_Projekte\119_Lignum\Fassadensysteme 3D in llinumdata\Ifc"
simplify_all_ifc_files_in_folder(folder_to_process)
