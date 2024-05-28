import ifcopenshell
from ifcopenshell.util.placement import get_local_placement

def read_ifc_file(ifc_path):
    print(f"Reading IFC file from: {ifc_path}")
    return ifcopenshell.open(ifc_path)

def get_element_location(element):
    try:
        # Get the placement matrix
        placement_matrix = get_local_placement(element.ObjectPlacement)
        
        # Extract the translation part of the matrix (the last column)
        x, y, z, _ = placement_matrix[0, 3], placement_matrix[1, 3], placement_matrix[2, 3], placement_matrix[3, 3]
        return (x, y, z)
    except AttributeError as e:
        print(f"Error in get_element_location for element {element.GlobalId}: {e}")
    except Exception as e:
        print(f"Unexpected error in get_element_location for element {element.GlobalId}: {e}")
    return None

def extract_element_locations(ifc_model):
    elements = ifc_model.by_type('IfcElement')
    for element in elements:
        location = get_element_location(element)
        if location:
            print(f"Element {element.GlobalId}: Location = {location}")
        else:
            print(f"Element {element.GlobalId} has no valid location.")

def main(ifc_path):
    ifc_model = read_ifc_file(ifc_path)
    extract_element_locations(ifc_model)

if __name__ == '__main__':
    ifc_path = input("Enter the path to the IFC file: ")
    main(ifc_path)
