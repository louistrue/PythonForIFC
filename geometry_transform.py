import ifcopenshell
from ifcopenshell import geom
import math

# Function to create a basic shape and apply transformations
def create_transformed_shape(settings, file, shape, scale, rotation, translation):
    # Create a cube with transformations
    matrix = ifcopenshell.geom.utils.scale(scale, scale, scale)
    matrix = ifcopenshell.geom.utils.rotate(matrix, (1, 0, 0), math.radians(rotation[0]))
    matrix = ifcopenshell.geom.utils.rotate(matrix, (0, 1, 0), math.radians(rotation[1]))
    matrix = ifcopenshell.geom.utils.rotate(matrix, (0, 0, 1), math.radians(rotation[2]))
    matrix = ifcopenshell.geom.utils.translate(matrix, translation[0], translation[1], translation[2])
    return ifcopenshell.geom.create_shape(settings, shape).transform(matrix)

# Initialize a new IFC project

file = ifcopenshell.file()
project = file.createIfcProject()

# Create a basic cube
def create_cube(file, width, height, depth):
    # Convert dimensions to floats to ensure compatibility
    width = float(width)
    height = float(height)
    depth = float(depth)

    # Define the cube's geometry
    point_list = [
        file.createIfcCartesianPoint((0.0, 0.0, 0.0)),
        file.createIfcCartesianPoint((width, 0.0, 0.0)),
        file.createIfcCartesianPoint((width, depth, 0.0)),
        file.createIfcCartesianPoint((0.0, depth, 0.0)),
        file.createIfcCartesianPoint((0.0, 0.0, height)),
        file.createIfcCartesianPoint((width, 0.0, height)),
        file.createIfcCartesianPoint((width, depth, height)),
        file.createIfcCartesianPoint((0.0, depth, height)),
    ]
    face_indices = [(0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7), (4, 5, 6, 7), (0, 3, 2, 1)]
    face_list = [file.createIfcFace([file.createIfcFaceOuterBound(
        file.createIfcPolyLoop([point_list[index] for index in face]), True)]) for face in face_indices]
    shell = file.createIfcShellBasedSurfaceModel([file.createIfcOpenShell(face_list)])
    return file.createIfcShapeRepresentation(shell)



# Settings for geometry creation
settings = ifcopenshell.geom.settings()



# Parameters for generation
num_copies = 10
scale_factor = 1.1
rotation_step = 15

original_shape = create_cube(file, 1, 1, 1)

# Generate and transform copies of the cube
for i in range(num_copies):
    scale = scale_factor ** i
    rotation = [rotation_step * i, rotation_step * i, rotation_step * i]
    translation = [i * 2, i * 2, 0]
    create_transformed_shape(settings, file, original_shape, scale, rotation, translation)

# Write to an IFC file
filename = "parametric_geometry.ifc"
with open(filename, "wb") as f:
    f.write(file.to_string())
print(f"IFC file saved as {filename}")
