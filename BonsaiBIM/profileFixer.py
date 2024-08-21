import ifcopenshell
import bpy
import os

# Define your directories
ifc_directory = r"\Ifc"
defect_png_directory = r"\Ifc - Defect PICS"
output_directory = r"\Ifc - BLENDS"
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

# Extract vertices from IfcIndexedPolyCurve
def extract_vertices_from_indexed_polycurve(curve):
    points = curve.Points
    verts = [(pt[0], pt[1], 0.0) for pt in points.CoordList]
    return verts

# Extract and visualize the first profile geometry in Blender
def visualize_first_profile(ifc, ifc_filename, log_file):
    profiles = ifc.by_type('IfcArbitraryClosedProfileDef')
    
    if not profiles:
        log_file.write(f"No IfcArbitraryClosedProfileDef found in {ifc_filename}.\n")
        return False

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
            return False

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
            
            return True
                
        else:
            log_file.write(f"No vertices extracted for {ifc_filename}.\n")
            return False
    
    except Exception as e:
        log_file.write(f"Error processing {ifc_filename}: {str(e)}\n")
        return False

# Main workflow to process the defective PNG files and generate corresponding .blend files
def main():
    with open(log_file_path, "w") as log_file:
        for png_filename in os.listdir(defect_png_directory):
            if png_filename.endswith(".png"):
                ifc_filename = os.path.splitext(png_filename)[0] + ".ifc"
                ifc_filepath = os.path.join(ifc_directory, ifc_filename)
                
                if os.path.exists(ifc_filepath):
                    ifc = ifcopenshell.open(ifc_filepath)
                    if ifc:
                        # Load the IFC and prepare the .blend file
                        if visualize_first_profile(ifc, ifc_filename, log_file):
                            # Save the current Blender file as a .blend file
                            blend_filepath = os.path.join(output_directory, f"{ifc_filename}.blend")
                            bpy.ops.wm.save_as_mainfile(filepath=blend_filepath)
                            print(f"Saved .blend file to: {blend_filepath}")
                        else:
                            print(f"Failed to process {ifc_filename}.")
                else:
                    log_file.write(f"IFC file not found for {png_filename}\n")

# Run the script
main()
