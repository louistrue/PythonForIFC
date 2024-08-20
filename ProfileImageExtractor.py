import ifcopenshell
import os
import cairosvg
from PIL import Image

def extract_profile_as_svg(ifc_file, output_svg):
    try:
        ifc_model = ifcopenshell.open(ifc_file)
        profiles = []
        for product in ifc_model.by_type("IfcExtrudedAreaSolid"):
            profile = product.SweptArea
            if profile.is_a("IfcArbitraryClosedProfileDef"):
                if profile.OuterCurve.is_a("IfcIndexedPolyCurve"):
                    curve = profile.OuterCurve
                    point_list = curve.Points
                    indices = [index[0] for index in curve.Segments]
                    # Correctly extract individual coordinates
                    points = [(point_list.CoordList[i-1][0], point_list.CoordList[i-1][1]) for i in indices]
                    profiles.append(points)
        
        if not profiles:
            print(f"No IfcArbitraryClosedProfileDef with valid points found in {ifc_file}")
            return
        
        # Initialize bounding box values
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')
        has_valid_points = False
        
        for points in profiles:
            for x, y in points:  # Ensure x, y are individual float values
                if x is not None and y is not None:
                    min_x = min(min_x, x)
                    max_x = max(max_x, x)
                    min_y = min(min_y, y)
                    max_y = max(max_y, y)
                    has_valid_points = True

        if not has_valid_points:
            print(f"No valid points found for the profiles in {ifc_file}.")
            return

        width = max_x - min_x
        height = max_y - min_y

        # Ensure non-zero width and height
        if width <= 0 or height <= 0:
            print(f"Calculated zero or negative width/height for {ifc_file}. Using default size.")
            width, height = 100, 100

        # Create the SVG content
        svg_content = f'''
        <svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="{min_x} {min_y} {width} {height}">
            <style>
                .profile {{
                    fill: #D2B48C;  /* Light brown */
                    stroke: black;
                    stroke-width: 0.8mm;
                }}
            </style>
        '''
        
        for points in profiles:
            path_data = "M " + " L ".join(f"{x} {y}" for x, y in points) + " Z"
            svg_content += f'<path class="profile" d="{path_data}"/>\n'
        
        svg_content += '</svg>'
        
        with open(output_svg, "w") as f:
            print(f"Writing SVG to {output_svg} with width={width} and height={height}")
            f.write(svg_content)
    except Exception as e:
        print(f"Error processing {ifc_file}: {e}")
        

def convert_svg_to_pdf(svg_path, pdf_path):
    try:
        print(f"Converting SVG to PDF: {pdf_path}")
        cairosvg.svg2pdf(url=svg_path, write_to=pdf_path)
    except Exception as e:
        print(f"Failed to convert SVG to PDF: {e}")

def convert_svg_to_image(svg_path, img_path):
    try:
        print(f"Converting SVG to PNG: {img_path}")
        cairosvg.svg2png(url=svg_path, write_to=img_path)
    except Exception as e:
        print(f"Failed to convert SVG to PNG: {e}")

def process_ifc_file(ifc_file):
    try:
        base_name = os.path.splitext(os.path.basename(ifc_file))[0]
        output_dir = r"C:\Users\LouisTrümpler\Desktop\Lig"  # Change this to a local directory
        
        svg_path = os.path.join(output_dir, f"{base_name}.svg")
        pdf_path = os.path.join(output_dir, f"{base_name}.pdf")
        img_path = os.path.join(output_dir, f"{base_name}.png")
        
        extract_profile_as_svg(ifc_file, svg_path)
        
        if os.path.exists(svg_path):
            convert_svg_to_pdf(svg_path, pdf_path)
            convert_svg_to_image(svg_path, img_path)
        else:
            print(f"SVG not created for {ifc_file}, skipping PDF and PNG conversion.")
    except Exception as e:
        print(f"Failed to process {ifc_file}: {e}")

def batch_process_folder(ifc_folder):
    for ifc_file in os.listdir(ifc_folder):
        if ifc_file.endswith(".ifc"):
            process_ifc_file(os.path.join(ifc_folder, ifc_file))


# Set the folder containing the IFC files
ifc_folder = r"C:\Users\LouisTrümpler\Dropbox\01_Projekte\119_Lignum\Fassadensysteme 3D in llinumdata\Ifc - Copy"

# Process all IFC files in the folder
batch_process_folder(ifc_folder)
