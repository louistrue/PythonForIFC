import ifcopenshell
import numpy as np
import math

class IFCHandler:
    def __init__(self):
        self.ifc_files = {}
        self.current_file = None

    def load_ifc_file(self, file_path):
        try:
            ifc_file = ifcopenshell.open(file_path)
            self.ifc_files[file_path] = ifc_file
            self.current_file = ifc_file
            print(f"Loaded IFC file: {file_path}")
            return ifc_file
        except Exception as e:
            print(f"Error loading IFC file: {file_path} - {str(e)}")
            return None

    def get_project_info(self, ifc_file):
        try:
            project = ifc_file.by_type('IfcProject')[0]
            return {
                "name": project.Name,
                "description": project.Description,
            }
        except IndexError:
            return {
                "name": "Undefined",
                "description": "None"
            }

    def get_site_info(self, ifc_file):
        try:
            site = ifc_file.by_type('IfcSite')[0]
            ref_lat = self.dms_to_decimal(*site.RefLatitude) if site.RefLatitude else None
            ref_long = self.dms_to_decimal(*site.RefLongitude) if site.RefLongitude else None
            return {
                "name": site.Name,
                "description": site.Description,
                "ref_lat_dms": site.RefLatitude,
                "ref_long_dms": site.RefLongitude,
                "ref_lat_decimal": ref_lat,
                "ref_long_decimal": ref_long,
                "ref_elevation": site.RefElevation,
            }
        except IndexError:
            return {
                "name": "-",
                "description": "None",
                "ref_lat_dms": "Not available",
                "ref_long_dms": "Not available",
                "ref_lat_decimal": None,
                "ref_long_decimal": None,
                "ref_elevation": "Not available"
            }

    def get_map_conversion_info(self, ifc_file):
        map_conversion = ifc_file.by_type('IfcMapConversion')
        if map_conversion:
            map_conversion = map_conversion[0]
            x_axis_abscissa = map_conversion.XAxisAbscissa if map_conversion else None
            x_axis_ordinate = map_conversion.XAxisOrdinate if map_conversion else None

            rotation_radians = math.atan2(x_axis_ordinate, x_axis_abscissa) if x_axis_abscissa and x_axis_ordinate else None
            rotation_degrees = self.radians_to_degrees(rotation_radians) if rotation_radians is not None else None

            return {
                "eastings": map_conversion.Eastings,
                "northings": map_conversion.Northings,
                "orthogonal_height": map_conversion.OrthogonalHeight,
                "x_axis_abscissa": x_axis_abscissa,
                "x_axis_ordinate": x_axis_ordinate,
                "rotation_degrees": rotation_degrees,
                "scale": map_conversion.Scale
            }
        return None

    @staticmethod
    def dms_to_decimal(degrees, minutes, seconds, fraction=0):
        return degrees + minutes / 60 + (seconds + fraction / 10**6) / 3600

    @staticmethod
    def radians_to_degrees(radians):
        return math.degrees(radians)

    def get_largest_coordinates(self, ifc_file):
        largest_x = largest_y = largest_z = float('-inf')
        for product in ifc_file.by_type('IfcProduct'):
            if hasattr(product, 'ObjectPlacement') and product.ObjectPlacement:
                x, y, z = self.safe_get_local_placement(product)
                if x is not None and y is not None and z is not None:
                    largest_x = max(largest_x, abs(x))
                    largest_y = max(largest_y, abs(y))
                    largest_z = max(largest_z, abs(z))
        return largest_x, largest_y, largest_z

    def safe_get_local_placement(self, product):
        try:
            placement_matrix = ifcopenshell.util.placement.get_local_placement(product.ObjectPlacement)
            x, y, z = placement_matrix[0][3], placement_matrix[1][3], placement_matrix[2][3]
            return x, y, z
        except Exception as e:
            print(f"Error in processing product {product.GlobalId}: {e}")
            return None, None, None
