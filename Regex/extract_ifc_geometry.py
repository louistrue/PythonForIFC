import re

def read_ifc_file(file_path: str) -> str:
    """Reads the content of an IFC file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def find_geometric_representations(content: str):
    """Finds shape representations and related product shapes."""
    shape_representation_regex = re.compile(
        r"#(\d+)=IFCSHAPEREPRESENTATION\([^;]*\);", re.IGNORECASE
    )
    product_shape_regex = re.compile(
        r"#(\d+)=IFCPRODUCTDEFINITIONSHAPE\([^;]*\);", re.IGNORECASE
    )

    shape_ids = set()
    for match in shape_representation_regex.finditer(content):
        shape_ids.add(f"#{match.group(1)}")

    product_shape_ids = set()
    for match in product_shape_regex.finditer(content):
        product_shape_ids.add(f"#{match.group(1)}")

    return shape_ids, product_shape_ids

def find_associated_elements(content: str, shape_ids: set):
    """Finds elements associated with shape representations."""
    element_regex = re.compile(
        r"#(\d+)=IFC[A-Z]+[^(]*\([^;]*\)", re.IGNORECASE
    )
    relationship_regex = re.compile(
        r"#(\d+)=IFCRELDEFINESBY[^;]*\([^;]*\)", re.IGNORECASE
    )
    element_shape_regex = re.compile(
        r"#(\d+)=IFC[A-Z]+[^(]*\([^;]*?,([^)]+)\);", re.IGNORECASE
    )

    associated_elements = {}
    shape_references = set()
    for match in relationship_regex.finditer(content):
        relationship_id = f"#{match.group(1)}"
        referenced_ids = re.findall(r"#\d+", match.group(0))
        if any(ref_id in shape_ids for ref_id in referenced_ids):
            shape_references.update(referenced_ids)

    for match in element_regex.finditer(content):
        global_id = f"#{match.group(1)}"
        entity_type = match.group(0).split('=')[1].split('(')[0].strip()
        if global_id in shape_references:
            associated_elements[global_id] = entity_type

    for match in element_shape_regex.finditer(content):
        global_id = f"#{match.group(1)}"
        referenced_ids = match.group(2)
        referenced_ids = re.findall(r"#\d+", referenced_ids)
        if any(ref_id in shape_ids for ref_id in referenced_ids):
            associated_elements[global_id] = match.group(0).split('=')[1].split('(')[0].strip()

    return associated_elements

def filter_entities(entities: dict):
    """Filters out entities that are not primary geometric elements."""
    exclude_types = {
        "IFCSHAPEASPECT",
        "IFCGEOGRAPHICELEMENT",
        "IFCREPRESENTATIONMAP",
        "IFCANNOTATION",
        "IFCMATERIAL",
        "IFCMATERIALLAYER",
        "IFCMATERIALLAYERSET",
        "IFCMATERIALDEFINITIONREPRESENTATION",
        "IFCMATERIALLAYERSETUSAGE",
        "IFCSTYLEDITEM",
        "IFCSURFACESTYLERENDERING",
        "IFCSURFACESTYLE",
        "IFCGEOMETRICREPRESENTATIONCONTEXT",
        "IFCGEOMETRICREPRESENTATIONSUBCONTEXT",
        "IFCPRODUCTDEFINITIONSHAPE",
        "IFCCOLOURRGB",
        "IFCDIRECTION",
        "IFCCARTESIANPOINT",
        "IFCAXIS2PLACEMENT3D",
        "IFCLOCALPLACEMENT",
    }

    return {gid: name for gid, name in entities.items() if name not in exclude_types}

def main():
    """Main function to extract and print geometric elements from IFC file."""
    content = read_ifc_file(IFC_FILE_PATH)
    shape_ids, product_shape_ids = find_geometric_representations(content)
    associated_elements = find_associated_elements(content, shape_ids.union(product_shape_ids))
    filtered_elements = filter_entities(associated_elements)

    for global_id, name in filtered_elements.items():
        print(f"Global ID: {global_id}, Name: {name}, Passed: True")
        
IFC_FILE_PATH = r"C:\Users\LouisTrümpler\Dropbox\01_Projekte\118_IfcQA.open\10_ARC_Architektur_GN Logistik.ifc"


if __name__ == "__main__":
    main()
