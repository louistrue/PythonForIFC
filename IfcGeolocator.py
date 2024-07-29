import ifcopenshell
import os
import datetime
from pathlib import Path
from ifcopenshell.util.placement import get_local_placement
import numpy as np
import math
import requests
import webbrowser

def safe_normalize(vector):
    norm = np.linalg.norm(vector)
    if norm == 0:
        return np.array([0.0, 0.0, 0.0])
    return vector / norm

def dms_to_decimal(degrees, minutes, seconds, fraction=0):
    return degrees + minutes / 60 + (seconds + fraction / 10**6) / 3600

def get_ifc_units(file):
    unit_assignment = file.by_type('IfcUnitAssignment')
    relevant_units = {
        "LENGTHUNIT": "Length",
        "AREAUNIT": "Area",
        "VOLUMEUNIT": "Volume",
        "MASSUNIT": "Mass",
    }
    units_info = []
    if unit_assignment:
        units = unit_assignment[0].Units
        for unit in units:
            unit_type = getattr(unit, 'UnitType', 'Undefined')
            unit_name = getattr(unit, 'Name', 'Undefined') or "Undefined"
            if unit_type in relevant_units:
                conversion_factor = "N/A"
                if isinstance(unit, ifcopenshell.entity_instance):
                    if unit.is_a("IfcConversionBasedUnit"):
                        conversion_factor = unit.ConversionFactor
                        if conversion_factor:
                            conversion_factor = getattr(conversion_factor, 'value', 'N/A')
                units_info.append({
                    "unit_type": relevant_units[unit_type],
                    "unit_name": unit_name,
                    "conversion_factor": conversion_factor
                })
    return units_info

def radians_to_degrees(radians):
    return math.degrees(radians)

def get_ifc_geolocation(file):
    project = file.by_type('IfcProject')[0]
    site = file.by_type('IfcSite')[0]
    map_conversion = file.by_type('IfcMapConversion')
    projected_crs = file.by_type('IfcProjectedCRS')
    
    if map_conversion:
        map_conversion = map_conversion[0]

    ref_lat = dms_to_decimal(*site.RefLatitude) if site.RefLatitude else None
    ref_long = dms_to_decimal(*site.RefLongitude) if site.RefLongitude else None

    x_axis_abscissa = map_conversion.XAxisAbscissa if map_conversion else None
    x_axis_ordinate = map_conversion.XAxisOrdinate if map_conversion else None

    rotation_radians = math.atan2(x_axis_ordinate, x_axis_abscissa) if x_axis_abscissa and x_axis_ordinate else None
    rotation_degrees = radians_to_degrees(rotation_radians) if rotation_radians is not None else None

    crs_info = {}
    if projected_crs:
        projected_crs = projected_crs[0]
        crs_info = {
            "name": projected_crs.Name,
            "description": projected_crs.Description,
            "geodetic_datum": projected_crs.GeodeticDatum,
            "vertical_datum": projected_crs.VerticalDatum,
            "map_projection": projected_crs.MapProjection,
        }
        
        # Use an API to look up more details about the CRS
        if projected_crs.Name:
            crs_response = requests.get(f"https://epsg.io/{projected_crs.Name}.json")
            if crs_response.status_code == 200:
                crs_data = crs_response.json()
                crs_info.update({
                    "crs_name": crs_data.get('name'),
                    "crs_area": crs_data.get('area'),
                    "crs_bbox": crs_data.get('bbox'),
                })

    return {
        "project_name": project.Name if project.Name else "Undefined",
        "project_description": project.Description if project.Description else "None",
        "site_name": site.Name if site.Name else "-",
        "site_description": site.Description if site.Description else "None",
        "ref_lat_dms": site.RefLatitude if site.RefLatitude else "Not available",
        "ref_long_dms": site.RefLongitude if site.RefLongitude else "Not available",
        "ref_lat_decimal": ref_lat,
        "ref_long_decimal": ref_long,
        "ref_elevation": site.RefElevation if site.RefElevation else "Not available",
        "map_conversion": {
            "eastings": map_conversion.Eastings if map_conversion else "N/A",
            "northings": map_conversion.Northings if map_conversion else "N/A",
            "orthogonal_height": map_conversion.OrthogonalHeight if map_conversion else "N/A",
            "x_axis_abscissa": x_axis_abscissa,
            "x_axis_ordinate": x_axis_ordinate,
            "rotation_degrees": rotation_degrees,
            "scale": map_conversion.Scale if map_conversion else 1.0
        } if map_conversion else "No IfcMapConversion entity found.",
        "projected_crs": crs_info,
    }

def safe_get_local_placement(product):
    try:
        placement_matrix = get_local_placement(product.ObjectPlacement)
        x, y, z = placement_matrix[0][3], placement_matrix[1][3], placement_matrix[2][3]
        return x, y, z
    except Exception as e:
        print(f"Error in processing product {product.GlobalId}: {e}")
        return None, None, None

def get_largest_coordinates(file):
    largest_x = largest_y = largest_z = float('-inf')
    for product in file.by_type('IfcProduct'):
        if hasattr(product, 'ObjectPlacement') and product.ObjectPlacement:
            x, y, z = safe_get_local_placement(product)
            if x is not None and y is not None and z is not None:
                largest_x = max(largest_x, abs(x))
                largest_y = max(largest_y, abs(y))
                largest_z = max(largest_z, abs(z))
    return largest_x, largest_y, largest_z

def process_ifc_file(file_path):
    try:
        ifc_file = ifcopenshell.open(file_path)
    except Exception as e:
        print(f"Error opening file {file_path}: {e}")
        return f"Error opening file {file_path}: {e}\n"

    geolocation = get_ifc_geolocation(ifc_file)
    largest_x, largest_y, largest_z = get_largest_coordinates(ifc_file)
    units_info = get_ifc_units(ifc_file)

    report = f"\n--- IFC Geolocation Report for {os.path.basename(file_path)} ---\n"
    report += f"Project Name: {geolocation['project_name']}\n"
    report += f"Project Description: {geolocation['project_description']}\n"
    report += f"Site Name: {geolocation['site_name']}\n"
    report += f"Site Description: {geolocation['site_description']}\n"
    report += f"Reference Latitude (DMS): {geolocation['ref_lat_dms']}\n"
    report += f"Reference Longitude (DMS): {geolocation['ref_long_dms']}\n"
    report += f"Reference Latitude (Decimal Degrees): {geolocation['ref_lat_decimal']}\n"
    report += f"Reference Longitude (Decimal Degrees): {geolocation['ref_long_decimal']}\n"
    report += f"Reference Elevation: {geolocation['ref_elevation']} meters\n"

    map_conversion = geolocation["map_conversion"]
    if isinstance(map_conversion, dict):
        report += "\n--- Map Conversion Details ---\n"
        report += f"Eastings: {map_conversion['eastings']} meters\n"
        report += f"Northings: {map_conversion['northings']} meters\n"
        report += f"Orthogonal Height: {map_conversion['orthogonal_height']} meters\n"
        report += f"X Axis Abscissa: {map_conversion['x_axis_abscissa']}\n"
        report += f"X Axis Ordinate: {map_conversion['x_axis_ordinate']}\n"
        report += f"Rotation: {map_conversion['rotation_degrees']} degrees\n"
        report += f"Scale: {map_conversion['scale']}\n"
    else:
        report += "\nNo IfcMapConversion entity found.\n"

    report += "\n--- Largest Coordinates ---\n"
    report += f"Largest X: {largest_x} units\n"
    report += f"Largest Y: {largest_y} units\n"
    report += f"Largest Z: {largest_z} units\n"

    if any(coord > 1000 for coord in (largest_x, largest_y, largest_z)):
        report += "\nWarning: Some coordinates exceed the 1000 units threshold.\n"

    report += "\n--- Unit Conversions ---\n"
    for unit in units_info:
        report += f"Unit Type: {unit['unit_type']}, Unit Name: {unit['unit_name']}, Conversion Factor: {unit['conversion_factor']}\n"

    # Show on OpenStreetMap if coordinates are available
    if geolocation['ref_lat_decimal'] and geolocation['ref_long_decimal']:
        osm_url = f"https://www.openstreetmap.org/?mlat={geolocation['ref_lat_decimal']}&mlon={geolocation['ref_long_decimal']}&zoom=15"
        report += f"\nView on OpenStreetMap: {osm_url}\n"
        webbrowser.open(osm_url)
    
    return report

def main():
    path = input("Please enter the path to the IFC file or folder containing IFC files: ")
    consolidated_report = ""
    
    if os.path.isdir(path):
        for file_name in os.listdir(path):
            if file_name.lower().endswith('.ifc'):
                report = process_ifc_file(os.path.join(path, file_name))
                consolidated_report += report
    elif os.path.isfile(path) and path.lower().endswith('.ifc'):
        consolidated_report = process_ifc_file(path)
    else:
        print("The provided path is neither a valid IFC file nor a directory containing IFC files.")
        return

    # Define the reports directory inside the user's Documents folder
    documents_path = Path.home() / "Documents"
    reports_directory = documents_path / "IFC_Geolocator_Reports"
    reports_directory.mkdir(exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    consolidated_report_filename = f"Geolocator_Report_{timestamp}.txt"
    consolidated_report_path = reports_directory / consolidated_report_filename
    
    with open(consolidated_report_path, "w") as f:
        f.write(consolidated_report)
    
    print(f"Consolidated report saved to {consolidated_report_path}")
    
    # Automatically open the consolidated report after writing
    os.system(f'notepad.exe {consolidated_report_path}')

if __name__ == "__main__":
    main()
