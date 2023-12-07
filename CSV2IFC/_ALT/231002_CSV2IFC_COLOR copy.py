import csv
import ifcopenshell
from ifcopenshell import api
import time
import uuid
import tempfile
import tkinter as tk
from tkinter import filedialog
import numpy as np
import matplotlib.pyplot as plt


O = 0., 0., 0.
X = 1., 0., 0.
Y = 0., 1., 0.
Z = 0., 0., 1.

def create_guid():
    return ifcopenshell.guid.compress(uuid.uuid1().hex)

# Creates an IfcAxis2Placement3D from Location, Axis and RefDirection specified as Python tuples
def create_ifcaxis2placement(ifcfile, point=O, dir1=Z, dir2=X):
    point = ifcfile.createIfcCartesianPoint(point)
    dir1 = ifcfile.createIfcDirection(dir1)
    dir2 = ifcfile.createIfcDirection(dir2)
    axis2placement = ifcfile.createIfcAxis2Placement3D(point, dir1, dir2)
    return axis2placement

# Creates an IfcLocalPlacement from Location, Axis and RefDirection, specified as Python tuples, and relative placement
def create_ifclocalplacement(ifcfile, point=O, dir1=Z, dir2=X, relative_to=None):
    axis2placement = create_ifcaxis2placement(ifcfile,point,dir1,dir2)
    ifclocalplacement2 = ifcfile.createIfcLocalPlacement(relative_to,axis2placement)
    return ifclocalplacement2

def create_ifcextrudedareasolid(ifcfile, point_list, point=(0., 0., 0.), dir1=(0., 0., 1.), dir2=(1., 0., 0.), direction=(0., 0., 1.), depth=1.0):
    # Create the polyline for the profile
    polyline = ifcfile.createIfcPolyLine([ifcfile.createIfcCartesianPoint(point) for point in point_list])
    # Create the closed profile definition
    closed_profile = ifcfile.createIfcArbitraryClosedProfileDef("AREA", None, polyline)
    # Create the axis placement for the extruded area solid
    axis_placement = create_ifcaxis2placement(ifcfile, point, dir1, dir2)
    # Create the direction for the extrusion
    extrude_direction = ifcfile.createIfcDirection(direction)
    # Create the IfcExtrudedAreaSolid
    solid = ifcfile.createIfcExtrudedAreaSolid(closed_profile, axis_placement, extrude_direction, depth)
    return solid

def normalize(value, min_value, max_value):
    return (value - min_value) / (max_value - min_value)

def get_color(value):
    cmap = plt.get_cmap("coolwarm")  # From dark red to blue
    return [int(x * 255) for x in cmap(value)[:3]]  # RGB values

def get_or_create_representation_context(ifc_file, context_identifier, context_type, dimension_count):
    contexts = ifc_file.by_type("IfcGeometricRepresentationContext")
    for context in contexts:
        if (context.ContextIdentifier == context_identifier and
                context.ContextType == context_type and
                context.CoordinateSpaceDimension == dimension_count):
            return context
    # If the context does not exist, create a new one
    point_origin = ifc_file.createIfcCartesianPoint(O)
    axis_direction = ifc_file.createIfcDirection(Z)
    ref_direction = ifc_file.createIfcDirection(X)
    world_coordinate_system = ifc_file.createIfcAxis2Placement3D(point_origin, axis_direction, ref_direction)
    new_context = ifc_file.createIfcGeometricRepresentationContext(None, context_identifier, context_type,
                                                                  dimension_count, None, world_coordinate_system)
    return new_context

def assign_color_to_element(ifc_file, element, product_shape, color):
    # Create IfcStyledItem, IfcSurfaceStyle, and IfcSurfaceStyleRendering
    color = ifc_file.createIfcColourRgb(None, color[0]/255.0, color[1]/255.0, color[2]/255.0)
    surface_style_rendering = ifc_file.createIfcSurfaceStyleRendering(color, None, None, None, None, None, None, None, "FLAT")
    surface_style = ifc_file.createIfcSurfaceStyle("Color", "BOTH", [surface_style_rendering])
    styled_item = ifc_file.createIfcStyledItem(None, [surface_style], None)
    
    # Create a styled representation and attach it to the existing product definition shape
    correct_context = get_or_create_representation_context(ifc_file, 'Style', 'Model', 3)
    styled_representation = ifc_file.createIfcStyledRepresentation(correct_context, "Style", "Styled", [styled_item])
    
    product_shape.Representations = product_shape.Representations + (styled_representation,)


def open_file_dialog():
    root = tk.Tk()
    root.withdraw()
    filePath = filedialog.askopenfilename()
    if filePath:
        save_file_dialog(filePath)

def save_file_dialog(input_file):
    root = tk.Tk()
    root.withdraw()
    filePath = filedialog.asksaveasfilename(defaultextension=".ifc")
    if filePath:
        create_ifc(input_file, filePath)

def create_shape(ifc_file, element, width, height, depth, context):
    try:
        point_list = [
            (0.0, 0.0),
            (float(width), 0.0),
            (float(width), float(height)),
            (0.0, float(height)),
            (0.0, 0.0)
        ]
        print(f"Debug: Point List: {point_list}, Depth: {depth}")
        solid = create_ifcextrudedareasolid(ifc_file, point_list, depth=float(depth))
        body_representation = ifc_file.createIfcShapeRepresentation(context, "Body", "SweptSolid", [solid])
        product_shape = ifc_file.createIfcProductDefinitionShape(None, None, [body_representation])
        element.Representation = product_shape
        return product_shape, width * height
    except Exception as e:
        print(f"TypeError in create_shape: {e}, Args: {e.args}, Argument types: {[(str(arg), type(arg)) for arg in e.args]}")
        return None, None  # Returning None for both to handle the error outside


def create_ifc(input_file, output_file):
    # Create IFC using a template
    timestamp = int(time.time())
    timestring = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(timestamp))
    creator = "LT"
    organization = "LT+"
    application, application_version = "IfcOpenShell", "0.5"
    project_globalid, project_name = create_guid(), "Template Project"

    template = f"""ISO-10303-21;
    HEADER;
    FILE_DESCRIPTION(('ViewDefinition [CoordinationView]'),'2;1');
    FILE_NAME('{output_file}','{timestring}',('{creator}'),('{organization}'),'{application}','{application}','');
    FILE_SCHEMA(('IFC4X3'));
    ENDSEC;
    DATA;
    #1=IFCPERSON($,$,'{creator}',$,$,$,$,$);
    #2=IFCORGANIZATION($,'{organization}',$,$,$);
    #3=IFCPERSONANDORGANIZATION(#1,#2,$);
    #4=IFCAPPLICATION(#2,'{application_version}','{application}','');
    #5=IFCOWNERHISTORY(#3,#4,$,.ADDED.,$,#3,#4,{timestamp});
    #6=IFCDIRECTION((1.,0.,0.));
    #7=IFCDIRECTION((0.,0.,1.));
    #8=IFCCARTESIANPOINT((0.,0.,0.));
    #9=IFCAXIS2PLACEMENT3D(#8,#7,#6);
    #10=IfcDirection((0.,1.));
    #11=IFCGEOMETRICREPRESENTATIONCONTEXT($,'Model',3,1.E-05,#9,#10);
    #12=IFCDIMENSIONALEXPONENTS(0,0,0,0,0,0,0);
    #13=IFCSIUNIT(*,.LENGTHUNIT.,$,.METRE.);
    #14=IFCSIUNIT(*,.AREAUNIT.,$,.SQUARE_METRE.);
    #15=IFCSIUNIT(*,.VOLUMEUNIT.,$,.CUBIC_METRE.);
    #16=IFCSIUNIT(*,.PLANEANGLEUNIT.,$,.RADIAN.);
    #17=IFCMEASUREWITHUNIT(IFCPLANEANGLEMEASURE(0.017453292519943295),#16);
    #18=IFCCONVERSIONBASEDUNIT(#12,.PLANEANGLEUNIT.,'DEGREE',#17);
    #19=IFCUNITASSIGNMENT((#13,#14,#15,#18));
    #20=IFCPROJECT('{project_globalid}',#5,'{project_name}',$,$,$,$,(#11),#19);
    ENDSEC;
    END-ISO-10303-21;"""

    # Write the template to a temporary file
    temp_handle, temp_filename = tempfile.mkstemp(suffix=".ifc")
    with open(temp_filename, "wb") as f:
        f.write(template.encode('utf-8'))

    # Open the temporary file and get references
    ifc_file = ifcopenshell.open(temp_filename)
    owner_history = ifc_file.by_type("IfcOwnerHistory")[0]
    project = ifc_file.by_type("IfcProject")[0]  #fetch the IfcProject entity
    context = ifc_file.by_type("IfcGeometricRepresentationContext")[0]
    
    # Set LastModifyingApplication and ChangeAction
    application = ifc_file.by_type("IfcApplication")[0]
    owner_history.LastModifyingApplication = application
    owner_history.ChangeAction = "MODIFIED"
    owner_history.LastModifiedDate = int(time.time())

    # Create IFC hierarchy
    site_placement = create_ifclocalplacement(ifc_file)
    site = ifc_file.createIfcSite(create_guid(), owner_history, "Site", None, None, site_placement, None, None, "ELEMENT", None, None, None, None, None)
    
    building_placement = create_ifclocalplacement(ifc_file, relative_to=site_placement)
    building = ifc_file.createIfcBuilding(create_guid(), owner_history, 'Building', None, None, building_placement, None, None, "ELEMENT", None, None, None)
    
    storey_placement = create_ifclocalplacement(ifc_file, relative_to=building_placement)
    elevation = 0.0  # You can change this as needed
    building_storey = ifc_file.createIfcBuildingStorey(create_guid(), owner_history, 'Storey', None, None, storey_placement, None, None, "ELEMENT", elevation)
    
    container_storey = ifc_file.createIfcRelAggregates(create_guid(), owner_history, "Building Container", None, building, [building_storey])
    container_site = ifc_file.createIfcRelAggregates(create_guid(), owner_history, "Site Container", None, site, [building])
    container_project = ifc_file.createIfcRelAggregates(create_guid(), owner_history, "Project Container", None, project, [site])
    
        # Create a list to hold all the created elements and their values
    created_elements = []
    values = []

    # First pass to find min and max values for normalization
    with open(input_file, mode='r') as file:
        reader = csv.reader(file)
        next(reader, None)  # Skip the header
        for row in reader:
            value = float(row[-1])
            values.append(value)

    min_value = min(values)
    max_value = max(values)

    try:
        with open(input_file, mode='r') as file:
            reader = csv.reader(file)
            next(reader, None)  # Skip the header

            for row in reader:
                x, y, z, value = map(float, row)
                normalized_value = normalize(value, min_value, max_value)
                rounded_value = round(value)
                color = get_color(normalized_value)

                element_guid = create_guid()
                element_placement = create_ifclocalplacement(ifc_file, point=(x, y, z), relative_to=building_storey.ObjectPlacement)
                element = ifc_file.createIfcBuildingElementProxy(element_guid, owner_history, "Element", None, None, element_placement, None, None)

                product_shape, area = create_shape(ifc_file, element, 1.0, 1.0, 0.001, context)

                # Assign color only if a shape was successfully created
                if product_shape is not None:
                    assign_color_to_element(ifc_file, element, product_shape, color)

                # Add custom properties to 'element'
                pset = api.run("pset.add_pset", ifc_file, product=element, name="UEP")
                api.run("pset.edit_pset", ifc_file, pset=pset, properties={"Potentialmessung": str(rounded_value)})

                created_elements.append(element)
                print(f"Element created with area: {area}")

        ifc_file.createIfcRelContainedInSpatialStructure(create_guid(), owner_history, "Building Storey Container", None, created_elements, building_storey)
        
    except Exception as e:
        print(f"An error occurred while populating the IFC file: {e}")


    ifc_file.write(output_file)



def main():
    proceed = input("Do you wish to proceed with the IFC file creation? (y/n): ")
    if proceed.lower() == 'y':
        open_file_dialog()

if __name__ == "__main__":
    main()
