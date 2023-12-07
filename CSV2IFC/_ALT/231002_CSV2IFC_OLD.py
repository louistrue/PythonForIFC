import sys
import csv
import ifcopenshell
import os
from PyQt5.QtWidgets import QApplication, QFileDialog, QPushButton, QVBoxLayout, QWidget
import time

# Function to generate a new GUID
def create_guid():
    return ifcopenshell.guid.new()

# Initialize owner history and related entities
def init_owner_history(ifc_file):
    person = ifc_file.createIfcPerson(None, "Louis", "Truempler", None, None, None, None, None)
    organization = ifc_file.createIfcOrganization(None, "WaltGalmarini & LT+", None, None, None)
    owning_user = ifc_file.createIfcPersonAndOrganization(person, organization, None)
    owning_application = ifc_file.createIfcApplication(organization, "1.0", "LT+ Application", "LTAppID")
    return ifc_file.createIfcOwnerHistory(
        owning_user, owning_application, None, "ADDED", None, owning_user, owning_application, int(time.time())
    )

# Create IFC hierarchy and return the created entities
def create_ifc_hierarchy(ifc_file, owner_history):
    site_placement = create_ifclocalplacement(ifc_file)
    site = ifc_file.createIfcSite(create_guid(), owner_history, "Site", None, None, site_placement, None, None, "ELEMENT", None, None, None, None, None)
    building_placement = create_ifclocalplacement(ifc_file, relative_to=site_placement)
    building = ifc_file.createIfcBuilding(create_guid(), owner_history, 'Building', None, None, building_placement, None, None, "ELEMENT", None, None, None)
    storey_placement = create_ifclocalplacement(ifc_file, relative_to=building_placement)
    elevation = 0.0
    building_storey = ifc_file.createIfcBuildingStorey(create_guid(), owner_history, 'Storey', None, None, storey_placement, None, None, "ELEMENT", elevation)
    ifc_file.createIfcRelAggregates(create_guid(), owner_history, "Building Container", None, building, [building_storey])
    ifc_file.createIfcRelAggregates(create_guid(), owner_history, "Site Container", None, site, [building])
    return site, building, building_storey

# Function to create a simple property set
def create_property_set(ifc_file, element, value, area):
    property_values = [
        ifc_file.createIfcPropertySingleValue(
            "MeasurementValue",
            "MeasurementValue",
            value,  # Directly using the float value
            None
        ),
    ]

    property_set = ifc_file.createIfcPropertySet(
        ifcopenshell.guid.new(),
        None,
        "CustomPset_Measurement",
        None,
        property_values
    )

    ifc_file.createIfcRelDefinesByProperties(
        ifcopenshell.guid.new(),
        None,
        "Property Set Assignment",
        None,
        [element],
        property_set
    )

# Creates an IfcAxis2Placement3D from Location, Axis, and RefDirection specified as Python tuples
def create_ifcaxis2placement(ifcfile, point=(0., 0., 0.), dir1=(0., 0., 1.), dir2=(1., 0., 0.)):
    point = ifcfile.createIfcCartesianPoint(point)
    dir1 = ifcfile.createIfcDirection(dir1)
    dir2 = ifcfile.createIfcDirection(dir2)
    axis2placement = ifcfile.createIfcAxis2Placement3D(point, dir1, dir2)
    return axis2placement

# Creates an IfcExtrudedAreaSolid from a list of points, specified as Python tuples
def create_ifcextrudedareasolid(ifcfile, point_list, ifcaxis2placement, extrude_dir, extrusion):
    polyline = ifcfile.createIfcPolyLine([ifcfile.createIfcCartesianPoint(point) for point in point_list])
    ifcclosedprofile = ifcfile.createIfcArbitraryClosedProfileDef("AREA", None, polyline)
    ifcdir = ifcfile.createIfcDirection(extrude_dir)
    ifcextrudedareasolid = ifcfile.createIfcExtrudedAreaSolid(ifcclosedprofile, ifcaxis2placement, ifcdir, extrusion)
    return ifcextrudedareasolid

# Creates an IfcLocalPlacement from Location, Axis, and RefDirection, specified as Python tuples, and relative placement
def create_ifclocalplacement(ifcfile, point=(0., 0., 0.), dir1=(0., 0., 1.), dir2=(1., 0., 0.), relative_to=None):
    axis2placement = create_ifcaxis2placement(ifcfile, point, dir1, dir2)
    ifclocalplacement = ifcfile.createIfcLocalPlacement(relative_to, axis2placement)
    return ifclocalplacement


# Function to create a rectangular shape for an element
def create_shape(ifc_file, element, width, height, depth):
    try:
        area = width * height
        point_list = [(0., 0., 0.), (width, 0., 0.), (width, height, 0.), (0., height, 0.), (0., 0., 0.)]
        axis2placement = create_ifcaxis2placement(ifc_file)
        solid = create_ifcextrudedareasolid(ifc_file, point_list, axis2placement, (0., 0., 1.), depth)
        
        shape_representation = ifc_file.createIfcShapeRepresentation(
            None,
            "Body",
            "SweptSolid",
            [solid]
        )
        
        # Create ProductDefinitionShape and associate with element
        product_definition_shape = ifc_file.createIfcProductDefinitionShape(
            None,
            None,
            [shape_representation]
        )
        element.Representation = product_definition_shape
        
        # Debugging: Verify each attribute just before creating the entity.
        print(f"Debug: Axis2Placement: {axis2placement}")
        print(f"Debug: Solid: {solid}")
        print(f"Debug: Shape Representation: {shape_representation}")
        print(f"Debug: Product Definition Shape: {product_definition_shape}")
        print(f"Debug: Element's Representation: {element.Representation}")
        
        return area
    
    except Exception as e:
        print(f"Error in create_shape: {e}")
        return None


def create_ifc(input_file, output_file):
    def create_guid():
        return ifcopenshell.guid.new()
    
    # Initialize IFC file and entities related to the owner and application
    ifc_file = ifcopenshell.file()
    owner_history = init_owner_history(ifc_file)
    
    # Create IFC hierarchy (Site -> Building -> Storey)
    project, site, building = create_ifc_hierarchy(ifc_file, owner_history)
    
    # Read CSV file to populate elements
    try:
        with open(input_file, mode='r') as file:
            reader = csv.reader(file)
            next(reader, None)  # Skip the header
            
            for row in reader:
                try:
                    x, y, z, value = map(float, row)
                    point_coordinates = (float(x), float(y), float(z))
                    element_guid = create_guid()
                    
                    element = ifc_file.createIfcBuildingElementProxy(
                        element_guid,
                        owner_history,
                        "Measurement",
                        None,
                        None,
                        create_ifclocalplacement(ifc_file, point=point_coordinates),
                        None,
                        None
                    )
                    
                    area = create_shape(ifc_file, element, 1.0, 1.0, 1.0)
                    print(f"Element created with area: {area}")
                    
                except ValueError:
                    print(f"Skipping row due to invalid data: {row}")

        # Write the IFC file
        try:
            ifc_file.write(output_file)
            print(f"IFC file '{output_file}' has been successfully created.")
        except Exception as e:
            print(f"An unexpected error occurred while writing the IFC file: {e}")

    
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
    except PermissionError:
        print(f"Error: Permission denied for file '{input_file}' or '{output_file}'.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Initialize owner history and related entities
def init_owner_history(ifc_file):
    person = ifc_file.createIfcPerson(None, "Louis", "Trümpler", None, None, None, None, None)
    organization = ifc_file.createIfcOrganization(None, "WaltGalmarini", None, None, None)
    owning_user = ifc_file.createIfcPersonAndOrganization(person, organization, None)
    owning_application = ifc_file.createIfcApplication(organization, "1.0", "WaltGalmarini Application", "WGAppID")
    return ifc_file.createIfcOwnerHistory(
        owning_user, owning_application, None, "ADDED", None, owning_user, owning_application, int(time.time())
    )

# Create IFC hierarchy and return the created entities
def create_ifc_hierarchy(ifc_file, owner_history):
    site_placement = create_ifclocalplacement(ifc_file)
    site = ifc_file.createIfcSite(create_guid(), owner_history, "Site", None, None, site_placement, None, None, "ELEMENT", None, None, None, None, None)
    building_placement = create_ifclocalplacement(ifc_file, relative_to=site_placement)
    building = ifc_file.createIfcBuilding(create_guid(), owner_history, 'Building', None, None, building_placement, None, None, "ELEMENT", None, None, None)
    storey_placement = create_ifclocalplacement(ifc_file, relative_to=building_placement)
    elevation = 0.0
    building_storey = ifc_file.createIfcBuildingStorey(create_guid(), owner_history, 'Storey', None, None, storey_placement, None, None, "ELEMENT", elevation)
    ifc_file.createIfcRelAggregates(create_guid(), owner_history, "Building Container", None, building, [building_storey])
    ifc_file.createIfcRelAggregates(create_guid(), owner_history, "Site Container", None, site, [building])
    return site, building, building_storey



def open_file_dialog():
    options = QFileDialog.Options()
    filePath, _ = QFileDialog.getOpenFileName(None, "Select Input CSV File", "", "CSV Files (*.csv)", options=options)
    if filePath:
        save_file_dialog(filePath)

def save_file_dialog(input_file):
    options = QFileDialog.Options()
    filePath, _ = QFileDialog.getSaveFileName(None, "Select Output IFC File", "", "IFC Files (*.ifc)", options=options)
    if filePath:
        if not filePath.endswith('.ifc'):
            filePath += '.ifc'
        create_ifc(input_file, filePath)

app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle('IFC File Creator')

layout = QVBoxLayout()

openButton = QPushButton('Select Input CSV File')
openButton.clicked.connect(open_file_dialog)

layout.addWidget(openButton)

window.setLayout(layout)
window.show()

sys.exit(app.exec_())