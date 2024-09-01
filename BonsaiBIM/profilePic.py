import bpy
import os

# Define your directories
blend_directory = r"\Ifc - BLENDS"
output_directory = r"\Ifc - PICS_10_5"
log_file_path = os.path.join(output_directory, "render_log.txt")

# Set up the camera for a top-down view
def setup_camera(obj):
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    obj.location = (0, 0, 0)
    bpy.ops.object.camera_add()
    cam = bpy.context.view_layer.objects.active
    obj_dimensions = obj.dimensions
    cam.location = (0, 0, max(obj_dimensions) * 2)
    cam.rotation_euler = (0, 0, 0)
    bpy.context.scene.camera = cam

# Set up the material using an emission shader for flat coloring
def setup_material_and_render_settings():
    bpy.context.scene.world.color = (1, 1, 1)
    world = bpy.context.scene.world
    world.use_nodes = True
    bg_node = world.node_tree.nodes['Background']
    bg_node.inputs['Color'].default_value = (1, 1, 1, 1)
    bpy.context.scene.view_settings.view_transform = 'Standard'
    bpy.context.scene.view_settings.exposure = 0.0
    material = bpy.data.materials.new(name="TimberMaterial")
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    material.node_tree.nodes.remove(bsdf)
    emission = material.node_tree.nodes.new("ShaderNodeEmission")
    emission.inputs['Color'].default_value = (0.894, 0.808, 0.467, 1)
    emission.inputs['Strength'].default_value = 1.0
    material_output = material.node_tree.nodes.get('Material Output')
    material.node_tree.links.new(emission.outputs['Emission'], material_output.inputs['Surface'])
    return material

# Enable freestyle for outer black outlines only
def enable_freestyle():
    bpy.context.scene.render.use_freestyle = True
    view_layer = bpy.context.view_layer
    linestyle = bpy.data.linestyles.new(name="LineStyle")
    linestyle.color = (0, 0, 0)
    linestyle.thickness = 1.0
    line_set = view_layer.freestyle_settings.linesets.new(name="LineSet")
    line_set.linestyle = linestyle
    line_set.select_silhouette = True

# Render the view to a PNG file
def render_to_png(output_filepath):
    bpy.context.scene.render.resolution_x = 1000
    bpy.context.scene.render.resolution_y = 500
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.context.scene.render.filepath = output_filepath
    bpy.ops.render.render(write_still=True)

# Process and render each .blend file
def process_blend_file(blend_filepath, output_dir, blend_filename, log_file):
    try:
        # Load the .blend file
        bpy.ops.wm.open_mainfile(filepath=blend_filepath)

        # Find the first mesh object (or other criteria)
        objs = [obj for obj in bpy.data.objects if obj.type == 'MESH']
        if not objs:
            log_file.write(f"No mesh objects found in {blend_filename}.\n")
            return

        obj = objs[0]  # Use the first mesh object

        # Set the object as active
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

        # Setup material and render settings
        material = setup_material_and_render_settings()
        if obj.data.materials:
            obj.data.materials[0] = material
        else:
            obj.data.materials.append(material)

        # Enable freestyle for thin black outlines
        enable_freestyle()

        # Set up camera for top-down view
        setup_camera(obj)

        # Define the output PNG filepath
        png_filename = os.path.splitext(blend_filename)[0] + ".png"
        output_filepath = os.path.join(output_dir, png_filename)

        # Render and save the image
        render_to_png(output_filepath)
        print(f"Rendered PNG saved to: {output_filepath}")

    except Exception as e:
        log_file.write(f"Error processing {blend_filename}: {str(e)}\n")

# Main workflow to process each .blend file and export to PNG
def main():
    with open(log_file_path, "w") as log_file:
        for blend_filename in os.listdir(blend_directory):
            if blend_filename.endswith(".blend"):
                blend_filepath = os.path.join(blend_directory, blend_filename)
                process_blend_file(blend_filepath, output_directory, blend_filename, log_file)

# Run the script
main()
