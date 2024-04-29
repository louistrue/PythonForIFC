import ifcopenshell
from ifcopenshell.api import run
import numpy as np
import math

def mandelbulb(x, y, z, max_iter, power):
    dr = 1.0
    r = 0.0
    theta, phi, zr = 0, 0, 0
    for i in range(max_iter):
        r = math.sqrt(x**2 + y**2 + z**2)
        if r > 2.0:
            break
        theta = math.atan2(math.sqrt(x**2 + y**2), z)
        phi = math.atan2(y, x)
        zr = r**power
        theta *= power
        phi *= power
        x = zr * math.sin(theta) * math.cos(phi)
        y = zr * math.sin(phi) * math.sin(theta)
        z = zr * math.cos(theta)
        dr = (r ** (power - 1)) * power * dr + 1.0
    return 0.5 * math.log(r) * r / dr if r > 0 else float('inf')

model = ifcopenshell.file()

# Setting up the IFC structure
project = run("root.create_entity", model, ifc_class="IfcProject", name="Mandelbulb Project")
run("unit.assign_unit", model)
context = run("context.add_context", model, context_type="Model")
body = run("context.add_context", model, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=context)
site = run("root.create_entity", model, ifc_class="IfcSite", name="Fractal Site")
building = run("root.create_entity", model, ifc_class="IfcBuilding", name="Fractal Building")
storey = run("root.create_entity", model, ifc_class="IfcBuildingStorey", name="Display Area")

grid_size = 20
max_iter = 3
power = 3
range_space = np.linspace(-1.5, 1.5, grid_size)

for x in range_space:
    for y in range_space:
        for z in range_space:
            fractal_value = mandelbulb(x, y, z, max_iter, power)
            if fractal_value < 10:  # Threshold for escape
                point = run("root.create_entity", model, ifc_class="IfcBuildingElementProxy", name="Fractal Point")
                run("geometry.edit_object_placement", model, product=point, coords=(x, y, z))
                representation = run("geometry.add_wall_representation", model, context=body, shape="Cube", coords=(x, y, z), length=0.1, height=0.1, thickness=0.1)
                run("geometry.assign_representation", model, product=point, representation=representation)
                run("aggregate.assign_object", model, relating_object=storey, product=point)

# Save the model
filename = "mandelbulb_geometry.ifc"
model.write(filename)
print(f"Model saved successfully as '{filename}'.")