import ifcopenshell
import bpy
import os

# Define your directories
ifc_directory = r"\Ifc"
output_directory = r"\Ifc - PICS"
log_file_path = os.path.join(output_directory, "render_log.txt")

# Set up the camera for a top-down view
def setup_camera(obj):
    # Move the object to the origin
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    obj.location = (0, 0, 0)

    # Add a camera
    bpy.ops.object.camera_add()
    cam = bpy.context.object

    # Position the camera directly above the object
    obj_dimensions = obj.dimensions
    cam.location = (0, 0, max(obj_dimensions) * 2)  # Position the camera above the object

    # Rotate the camera to point straight down along the negative Z-axis
    cam.rotation_euler = (0, 0, 0)

    bpy.context.scene.camera = cam

# Set up the material using an emission shader for flat coloring
def setup_material_and_render_settings():
    # Set background color to white
    bpy.context.scene.world.color = (1, 1, 1)

    # Ensure the background is rendered as white
    world = bpy.context.scene.world
    world.use_nodes = True
    bg_node = world.node_tree.nodes['Background']
    bg_node.inputs['Color'].default_value = (1, 1, 1, 1)  # Pure white

    # Create an emission material for the profile with a vibrant wooden color
    material = bpy.data.materials.new(name="TimberMaterial")
    material.use_nodes = True
    bsdf = material.node_tree.nodes["Principled BSDF"]
    material.node_tree.nodes.remove(bsdf)

    # Create an Emission shader
    emission = material.node_tree.nodes.new("ShaderNodeEmission")
    emission.inputs['Color'].default_value = (0.76, 0.51, 0.25, 1)  # Vibrant wooden color
    emission.inputs['Strength'].default_value = 1.0

    material_output = material.node_tree.nodes.get('Material Output')
    material.node_tree.links.new(emission.outputs['Emission'], material_output.inputs['Surface'])

    return material

# Enable freestyle for outer black outlines only
def enable_freestyle():
    bpy.context.scene.render.use_freestyle = True
    view_layer = bpy.context.view_layer

    # Freestyle line settings
    linestyle = bpy.data.linestyles.new(name="LineStyle")
    linestyle.color = (0, 0, 0)  # Black color
    linestyle.thickness = 1.0  # Thin line thickness

    # Add the linestyle to the current view layer
    line_set = view_layer.freestyle_settings.linesets.new(name="LineSet")
    line_set.linestyle = linestyle

    # Set the Freestyle line set to only render the contour
    line_set.select_silhouette = True  # Render only silhouette edges
    line_set.select_border = False
    line_set.select_crease = False
    line_set.select_edge_mark = False
    line_set.select_material_boundary = False
    
# Render the view to a PNG file
def render_to_png(output_filepath):
    bpy.context.scene.render.resolution_x = 1024
    bpy.context.scene.render.resolution_y = 1024
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.context.scene.render.filepath = output_filepath
    bpy.ops.render.render(write_still=True)

# Extract vertices from IfcIndexedPolyCurve
def extract_vertices_from_indexed_polycurve(curve):
    points = curve.Points
    verts = [(pt[0], pt[1], 0.0) for pt in points.CoordList]
    return verts

# Extract and visualize the first profile geometry in Blender
def visualize_first_profile(ifc, output_dir, ifc_filename, log_file):
    profiles = ifc.by_type('IfcArbitraryClosedProfileDef')
    
    if not profiles:
        log_file.write(f"No IfcArbitraryClosedProfileDef found in {ifc_filename}.\n")
        return

    try:
        # Use only the first profile found
        profile = profiles[0]
        outer_curve = profile.OuterCurve

        verts = []
        if outer_curve.is_a('IfcPolyline'):
            verts = [(pt.Coordinates[0], pt.Coordinates[1], 0.0) for pt in outer_curve.Points]
        elif outer_curve.is_a('IfcIndexedPolyCurve'):
            verts = extract_vertices_from_indexed_polycurve(outer_curve)
        else:
            log_file.write(f"Unsupported outer curve type in {ifc_filename}: {outer_curve.is_a()}.\n")
            return

        if verts:
            # Create a new mesh and object in Blender
            mesh = bpy.data.meshes.new(name=f"ProfileGeometry")
            mesh.from_pydata(verts, [], [list(range(len(verts)))])
            mesh.update()

            obj = bpy.data.objects.new(f"ProfileGeometryObject", mesh)
            bpy.context.collection.objects.link(obj)
            
            # Assign the material to the object
            material = setup_material_and_render_settings()
            if obj.data.materials:
                obj.data.materials[0] = material
            else:
                obj.data.materials.append(material)

            # Enable freestyle for thin black outlines
            enable_freestyle()
            
            # Select the created object
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)

            # Set up camera for top-down view
            setup_camera(obj)
            
            # Render and save the image
            output_filepath = os.path.join(output_dir, f"{ifc_filename}.png")
            render_to_png(output_filepath)
            print(f"Rendered image saved to: {output_filepath}")

            # Cleanup: remove the object and camera
            bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.objects.remove(bpy.context.scene.camera, do_unlink=True)
                
        else:
            log_file.write(f"No vertices extracted for {ifc_filename}.\n")
    
    except Exception as e:
        log_file.write(f"Error processing {ifc_filename}: {str(e)}\n")

# Main workflow to process all IFC files in the directory
def main():
    with open(log_file_path, "w") as log_file:
        for filename in os.listdir(ifc_directory):
            if filename.endswith(".ifc"):
                ifc_filepath = os.path.join(ifc_directory, filename)
                ifc = ifcopenshell.open(ifc_filepath)
                if ifc:
                    # Use the IFC filename without extension for output filenames
                    ifc_filename = os.path.splitext(filename)[0]
                    visualize_first_profile(ifc, output_directory, ifc_filename, log_file)

# Run the script
main()
