import csv
import ifcopenshell
from ifcopenshell import api
import time
import uuid
import tempfile
import tkinter as tk
from tkinter import filedialog

# Constants
O, X, Y, Z = (0., 0., 0.), (1., 0., 0.), (0., 1., 0.), (0., 0., 1.)

# Utility functions
def create_guid():
    return ifcopenshell.guid.compress(uuid.uuid1().hex)

def create_ifcaxis2placement(ifcfile, point=O, dir1=Z, dir2=X):
    point = ifcfile.createIfcCartesianPoint(point)
    dir1 = ifcfile.createIfcDirection(dir1)
    dir2 = ifcfile.createIfcDirection(dir2)
    return ifcfile.createIfcAxis2Placement3D(point, dir1, dir2)

def create_ifclocalplacement(ifcfile, point=O, dir1=Z, dir2=X, relative_to=None):
    axis2placement = create_ifcaxis2placement(ifcfile, point, dir1, dir2)
    return ifcfile.createIfcLocalPlacement(relative_to, axis2placement)

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
    return [int(255 * (1 - value)), 0, int(255 * value)]


def assign_color_to_element(ifc_file, representation, value):
    # Create a blank style
    style = ifcopenshell.api.run("style.add_style", ifc_file, name="DynamicStyle")
    
    # Determine the color based on the value
    color = get_color(value)
    
    # Add surface style shading with color
    ifcopenshell.api.run("style.add_surface_style", ifc_file, style=style, ifc_class="IfcSurfaceStyleShading", attributes={
        "SurfaceColour": { "Name": None, "Red": color[0]/255.0, "Green": color[1]/255.0, "Blue": color[2]/255.0 }
    })
    
    # Assign the style to the element's representation
    ifcopenshell.api.run("style.assign_representation_styles", ifc_file, shape_representation=representation, styles=[style])


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

def create_shape(ifc_file, element, width, height, depth, context, normalized_value):
    try:
        point_list = [
            (0.0, 0.0),
            (0.25, 0.0),
            (0.25, 0.25),
            (0.0, 0.25),
            (0.0, 0.0)
        ]
        print(f"Debug: Point List: {point_list}, Depth: {depth}")
        solid = create_ifcextrudedareasolid(ifc_file, point_list, depth=float(depth))
        body_representation = ifc_file.createIfcShapeRepresentation(context, "Body", "SweptSolid", [solid])
        product_shape = ifc_file.createIfcProductDefinitionShape(None, None, [body_representation])
        element.Representation = product_shape

        # Assign color to the element
        assign_color_to_element(ifc_file, body_representation, normalized_value)
        
        return product_shape, 0.25 * 0.25  # Adjust area calculation for the new square size
    except Exception as e:
        print(f"TypeError in create_shape: {e}, Args: {e.args}, Argument types: {[(str(arg), type(arg)) for arg in e.args]}")
        return None, None  # Returning None for both to handle the error outside

def normalize(value, min_value, max_value):
    return (value - min_value) / (max_value - min_value)

def create_ifc_hierarchy(ifc_file, owner_history):
    site_placement = create_ifclocalplacement(ifc_file)
    site = ifc_file.createIfcSite(create_guid(), owner_history, "Site", None, None, site_placement, None, None, "ELEMENT", None, None, None, None, None)
    
    building_placement = create_ifclocalplacement(ifc_file, relative_to=site_placement)
    building = ifc_file.createIfcBuilding(create_guid(), owner_history, 'Building', None, None, building_placement, None, None, "ELEMENT", None, None, None)
    
    storey_placement = create_ifclocalplacement(ifc_file, relative_to=building_placement)
    elevation = 0.0  # Change height offset here
    building_storey = ifc_file.createIfcBuildingStorey(create_guid(), owner_history, 'Storey', None, None, storey_placement, None, None, "ELEMENT", elevation)
    
    return site, building, building_storey

def create_and_link_containers(ifc_file, owner_history, site, building, building_storey):
    ifc_file.createIfcRelAggregates(create_guid(), owner_history, "Building Storey Container", None, building, [building_storey])
    ifc_file.createIfcRelAggregates(create_guid(), owner_history, "Site Container", None, site, [building])
    project = ifc_file.by_type("IfcProject")[0]  #fetch the IfcProject entity
    ifc_file.createIfcRelAggregates(create_guid(), owner_history, "Project Container", None, project, [site])

def process_elements_from_csv(input_file, ifc_file, owner_history, context, building_storey):
    created_elements = []
    min_value, max_value = float("inf"), float("-inf")

    # Find the min and max values for normalization
    with open(input_file, mode='r') as file:
        reader = csv.reader(file)
        next(reader, None)  # Skip the header
        for row in reader:
            value = float(row[3])
            min_value = min(min_value, value)
            max_value = max(max_value, value)

    try:
        with open(input_file, mode='r') as file:
            reader = csv.reader(file)
            next(reader, None)  # Skip the header
            for row in reader:
                x, y, z, value = map(float, row)
                normalized_value = normalize(value, min_value, max_value)
                rounded_value = round(value)

                element_guid = create_guid()
                element_placement = create_ifclocalplacement(ifc_file, point=(x, y, z), relative_to=building_storey.ObjectPlacement)
                element = ifc_file.createIfcBuildingElementProxy(element_guid, owner_history, "Element", None, None, element_placement, None, None)

                # Pass the normalized_value for colorization
                product_shape, area = create_shape(ifc_file, element, 1.0, 1.0, 0.001, context, normalized_value)
             
                # Add custom properties to 'element'
                pset = api.run("pset.add_pset", ifc_file, product=element, name="UEP")
                api.run("pset.edit_pset", ifc_file, pset=pset, properties={"Potentialmessung": str(rounded_value)})
                
                created_elements.append(element)

        return created_elements
        
    except Exception as e:
        print(f"An error occurred while populating the IFC file: {e}")
        return []

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
    context = ifc_file.by_type("IfcGeometricRepresentationContext")[0]
    
    # Update the owner history
    owner_history.LastModifyingApplication = ifc_file.by_type("IfcApplication")[0]
    owner_history.ChangeAction, owner_history.LastModifiedDate = "MODIFIED", int(time.time())

    # Create IFC hierarchy
    site, building, building_storey = create_ifc_hierarchy(ifc_file, owner_history)

    # Create and link containers
    create_and_link_containers(ifc_file, owner_history, site, building, building_storey)

    # Process elements
    created_elements = process_elements_from_csv(input_file, ifc_file, owner_history, context, building_storey)

    # Finalize IFC file
    ifc_file.createIfcRelContainedInSpatialStructure(create_guid(), owner_history, "Building Storey Container", None, created_elements, building_storey)
    ifc_file.write(output_file)


def main():
    open_file_dialog()

if __name__ == "__main__":
    main()
