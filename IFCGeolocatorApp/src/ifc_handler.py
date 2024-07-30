import ifcopenshell
from ifcopenshell.util.placement import get_local_placement
import os
import requests
import math
from dotenv import load_dotenv
import re

# Load environment variables from .env file
load_dotenv()

class IFCHandler:
    def __init__(self):
        self.ifc_files = {}
        self.current_file = None
        self.api_key = os.getenv('MAPTILER_API_KEY')

    def fetch_epsg_info(self, epsg_code):
        try:
            url = f"https://api.maptiler.com/coordinates/search/code:{epsg_code}.json?key={self.api_key}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data['results']:
                    return data['results'][0]  # Fetch the first result which should match the EPSG code
                else:
                    print(f"No results found for EPSG code: {epsg_code}")
                    return None
            else:
                print(f"Failed to fetch EPSG info: {response.status_code}")
                return None
        except Exception as e:
            print(f"Exception occurred while fetching EPSG info: {e}")
            return None

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
        if ifc_file.schema == 'IFC2X3':
            print("Skipping map conversion for IFC2X3 schema.")
            return None

        try:
            map_conversion = ifc_file.by_type('IfcMapConversion')[0]
            projected_crs = ifc_file.by_type('IfcProjectedCRS')[0]
            epsg_code = self.extract_epsg_code(projected_crs)
            epsg_info = self.fetch_epsg_info(epsg_code)
            
            # Extract the default transformation code from epsg_info
            transformation_code = epsg_info.get('default_transformation', {}).get('code', None)

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
                "scale": map_conversion.Scale if map_conversion.Scale else 1.0,
                "epsg_code": epsg_code,
                "transformation_code": transformation_code,
                "epsg_info": epsg_info
            }
        except IndexError:
            return None
        except Exception as e:
            print(f"Error extracting map conversion info: {e}")
            return None

    def extract_epsg_code(self, projected_crs):
        try:
            epsg_code = projected_crs.Name
            epsg_code = re.sub(r'[^0-9]', '', epsg_code)  # Clean the EPSG code to ensure only numeric part remains
            return epsg_code
        except AttributeError:
            print("EPSG code not found in 'Name' attribute, trying 'Identifier'")
            try:
                epsg_code = projected_crs.Identifier
                epsg_code = re.sub(r'[^0-9]', '', epsg_code)  # Clean the EPSG code
                return epsg_code
            except AttributeError:
                print("EPSG code not found in 'Identifier' attribute")
                return None

    @staticmethod
    def radians_to_degrees(radians):
        return math.degrees(radians)

    @staticmethod
    def dms_to_decimal(degrees, minutes, seconds, fraction=0):
        return degrees + minutes / 60 + (seconds + fraction / 10**6) / 3600

    def get_largest_coordinates(self, ifc_file):
        largest_x = largest_y = largest_z = float('-inf')
        largest_coordinates = None
        elements = ifc_file.by_type('IfcElement')
        for element in elements:
            try:
                placement_matrix = get_local_placement(element.ObjectPlacement)
                x, y, z = placement_matrix[0][3], placement_matrix[1][3], placement_matrix[2][3]
                if x and y and z and (abs(x) > abs(largest_x) or abs(y) > abs(largest_y) or abs(z) > abs(largest_z)):
                    largest_x, largest_y, largest_z = x, y, z
                    largest_coordinates = (x, y, z)
            except Exception as e:
                print(f"Error in processing element {element.GlobalId}: {e}")
        return largest_coordinates

    def safe_get_local_placement(self, product):
        try:
            placement_matrix = get_local_placement(product.ObjectPlacement)
            x, y, z = placement_matrix[0][3], placement_matrix[1][3], placement_matrix[2][3]
            return x, y, z
        except Exception as e:
            print(f"Error in processing product {product.GlobalId}: {e}")
            return None, None, None
