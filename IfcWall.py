import ifcopenshell
import uuid

# Create a new IFC model with the IFC4 schema
model = ifcopenshell.file(schema="IFC4")

# Define a function to generate a new GUID
def new_guid():
    return str(uuid.uuid4())

# Define the major components of the IFC model
project = model.createIfcProject(
    globalid=new_guid(),
    owner_history=None,
    name="Project",
    description="A sample project",
    units_in_context=None  # Provide appropriate units or None if not applicable
)
site = model.createIfcSite(
    globalid=new_guid(),
    owner_history=None,
    name="Site",
    description="A sample site",
    site_address=None  # Provide site address if available, otherwise None
)
building = model.createIfcBuilding(
    globalid=new_guid(),
    owner_history=None,
    name="Building",
    description="A sample building",
    building_address=None  # Provide building address if available, otherwise None
)

# Define a local placement for the wall
location = model.createIfcCartesianPoint((0, 0, 0))
axis = model.createIfcDirection((0, 0, 1))
ref_direction = model.createIfcDirection((1, 0, 0))
placement = model.createIfcLocalPlacement(None, location, axis, ref_direction)

# Define the geometry for the wall: a rectangle profile extruded along the Z-axis
wall_profile = model.createIfcRectangleProfileDef("AREA", "WallProfile", model.createIfcAxis2Placement2D(), 5.0, 0.4)
extrude_direction = model.createIfcDirection((0, 0, 1))
solid = model.createIfcExtrudedAreaSolid(wall_profile, model.createIfcAxis2Placement3D(), extrude_direction, 3.0)

# Create the wall product with the defined geometry
wall = model.createIfcWallStandardCase(
    globalid=new_guid(),
    owner_history=None,
    name="Wall",
    object_placement=placement,
    representation=model.createIfcProductDefinitionShape(
        representations=[model.createIfcShapeRepresentation("Body", "SweptSolid", [solid])]
    )
)

# Aggregate the structure elements into a hierarchy
model.createIfcRelAggregates(new_guid(), relating_object=project, related_objects=[site])
model.createIfcRelAggregates(new_guid(), relating_object=site, related_objects=[building])
model.createIfcRelContainedInSpatialStructure(new_guid(), relating_structure=building, related_elements=[wall])

# Create a custom property set with properties
property_set = model.createIfcPropertySet(
    globalid=new_guid(),
    name="Custom",
    properties=[
        model.createIfcPropertySingleValue(name="IsExternal", nominal_value=model.createIfcBoolean(True)),
        model.createIfcPropertySingleValue(name="Hello IFC", nominal_value=model.createIfcText("Hello IFC"))
    ]
)

# Assign the property set to the wall
model.createIfcRelDefinesByProperties(
    globalid=new_guid(),
    related_objects=[wall],
    relating_property_definition=property_set
)

# Save the model to a file
model.write('your_model.ifc')

print("IFC model has been successfully created and saved.")
