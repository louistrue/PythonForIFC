import bpy
import os

# Define your directories
blend_directory = r"\Ifc - BLENDS"

# Render the view to a PNG file
def render_to_png(output_filepath):
    bpy.context.scene.render.resolution_x = 1024
    bpy.context.scene.render.resolution_y = 1024
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.context.scene.render.filepath = output_filepath
    bpy.ops.render.render(write_still=True)

# Main workflow to process each .blend file and export to PNG
def main():
    for blend_filename in os.listdir(blend_directory):
        if blend_filename.endswith(".blend"):
            blend_filepath = os.path.join(blend_directory, blend_filename)
            
            # Load the .blend file
            bpy.ops.wm.open_mainfile(filepath=blend_filepath)
            
            # Define the output PNG filepath
            png_filename = os.path.splitext(blend_filename)[0] + ".png"
            output_filepath = os.path.join(blend_directory, png_filename)
            
            # Render the scene and save the PNG
            render_to_png(output_filepath)
            print(f"Rendered PNG saved to: {output_filepath}")

# Run the script
main()
