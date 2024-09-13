import bpy
import os

# Define the folder containing the IFC files
input_folder = r"C:\Users\..."
output_folder = r"C:\Users\..."


# Ensure the output folder exists
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

def import_ifc(filepath):
    bpy.ops.bim.load_project(filepath=filepath, use_relative_path=False, should_start_fresh_session=True)

# Loop through each file in the input folder
for filename in os.listdir(input_folder):
    if filename.endswith(".ifc"):
        # Full path to the IFC file
        ifc_path = os.path.join(input_folder, filename)
        
        # Import the IFC file
        import_ifc(ifc_path)
        
        # Ensure an active object context for export
        bpy.context.view_layer.objects.active = bpy.context.scene.objects[0]
        
        # Define the output path for the GLB file
        glb_filename = os.path.splitext(filename)[0] + ".glb"
        glb_path = os.path.join(output_folder, glb_filename)
        
        # Export the loaded IFC file as GLB
        bpy.ops.export_scene.gltf(filepath=glb_path, export_format='GLB', use_selection=False)
        
        # Clear the scene for the next file
        bpy.ops.wm.read_factory_settings(use_empty=True)

print("All files have been processed and saved as .glb files.")
