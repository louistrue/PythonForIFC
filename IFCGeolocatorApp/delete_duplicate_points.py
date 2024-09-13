import ifcopenshell
import os

def check_no_duplicate_points_in_polyloop(polyloop):
    point_set = set()
    for point in polyloop.Polygon:
        coord_tuple = tuple(point.Coordinates)
        if coord_tuple in point_set:
            return False
        point_set.add(coord_tuple)
    return True

def check_no_duplicate_points_in_polyline(polyline):
    point_set = set()
    for i, point in enumerate(polyline.Points):
        coord_tuple = tuple(point.Coordinates)
        if coord_tuple in point_set:
            return False
        point_set.add(coord_tuple)
    return True

def check_first_and_last_point_identical_by_reference(polyline):
    if len(polyline.Points) > 1 and polyline.Points[0] == polyline.Points[-1]:
        return polyline.Points[0] is polyline.Points[-1]
    return False

def remove_duplicate_points(polyloop):
    unique_points = []
    point_set = set()
    for point in polyloop.Polygon:
        coord_tuple = tuple(point.Coordinates)
        if coord_tuple not in point_set:
            unique_points.append(point)
            point_set.add(coord_tuple)
    polyloop.Polygon = unique_points

def remove_duplicate_points_in_polyline(polyline):
    unique_points = []
    point_set = set()
    for i, point in enumerate(polyline.Points):
        coord_tuple = tuple(point.Coordinates)
        if coord_tuple not in point_set or (i == len(polyline.Points) - 1 and polyline.Points[0] == point):
            unique_points.append(point)
            point_set.add(coord_tuple)
    polyline.Points = unique_points

def make_first_and_last_point_identical_by_reference(polyline):
    if len(polyline.Points) > 1:
        points_list = list(polyline.Points)
        points_list[-1] = points_list[0]
        polyline.Points = tuple(points_list)

def process_and_fix_ifc_file(filepath):
    ifc_file = ifcopenshell.open(filepath)
    modified = False

    # Fix IfcPolyLoop
    polyloops = ifc_file.by_type("IfcPolyLoop")
    for polyloop in polyloops:
        if len(polyloop.Polygon) != len(set(tuple(p.Coordinates) for p in polyloop.Polygon)):
            remove_duplicate_points(polyloop)
            modified = True

    # Fix IfcPolyline
    polylines = ifc_file.by_type("IfcPolyline")
    for polyline in polylines:
        if len(polyline.Points) > 2 and polyline.Points[0] == polyline.Points[-1]:  # Closed curve
            if len(polyline.Points) != len(set(tuple(p.Coordinates) for p in polyline.Points)):
                remove_duplicate_points_in_polyline(polyline)
                modified = True
            if not check_first_and_last_point_identical_by_reference(polyline):
                make_first_and_last_point_identical_by_reference(polyline)
                modified = True
        else:  # Open curve
            if len(polyline.Points) != len(set(tuple(p.Coordinates) for p in polyline.Points)):
                remove_duplicate_points_in_polyline(polyline)
                modified = True

    if modified:
        # Overwrite the original IFC file
        ifc_file.write(filepath)
        print(f"Fixed and saved: {filepath}")

def analyze_and_fix_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith(".ifc"):
            filepath = os.path.join(folder_path, filename)
            process_and_fix_ifc_file(filepath)
if __name__ == "__main__":
    folder_path = 
    analyze_and_fix_folder(folder_path)
