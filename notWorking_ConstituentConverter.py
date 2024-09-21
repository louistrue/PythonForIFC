import ifcopenshell
import ifcopenshell.api
import logging
import sys
import uuid

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for detailed logs
    format='%(levelname)s: %(message)s'
)

# Paths to input and output IFC files
input_file = r"C:\Users\LouisTrümpler\Documents\GitHub\NHMzh\tests\SampleIfc\4_RV_Str.ifc"
output_file = r"C:\Users\LouisTrümpler\Documents\GitHub\NHMzh\tests\SampleIfc\4_RV_Str_OUT.ifc"

# Open the IFC model
try:
    model = ifcopenshell.open(input_file)
    logging.info(f"Successfully opened IFC file: '{input_file}'")
except Exception as e:
    logging.error(f"Failed to open IFC file '{input_file}': {e}")
    sys.exit(1)

# Get all IfcMaterialConstituentSet entities
constituent_sets = model.by_type('IfcMaterialConstituentSet')
logging.info(f"Found {len(constituent_sets)} IfcMaterialConstituentSet entities.")

# Define a reasonable default thickness (in meters)
DEFAULT_THICKNESS = 0.1  # Adjust as necessary

# Function to generate a unique GUID
def generate_guid():
    return ifcopenshell.guid.compress(uuid.uuid4().hex)

# Iterate over each IfcMaterialConstituentSet to convert them into IfcMaterialLayerSet
for constituent_set in constituent_sets:
    logging.info(f"Processing constituent set: '{constituent_set.Name}'")
    constituents = constituent_set.MaterialConstituents

    if not constituents:
        logging.warning(f"No constituents found in set '{constituent_set.Name}'. Skipping.")
        continue

    # Initialize list to store IfcMaterialLayer entities
    material_layers = []

    for constituent in constituents:
        material = constituent.Material
        constituent_name = constituent.Name.strip() if constituent.Name else "Unnamed Constituent"
        logging.info(f"Processing constituent: '{constituent_name}'")

        # Attempt to find a matching quantity for the constituent's thickness
        matched_quantity = None
        for quantity in model.by_type('IfcPhysicalComplexQuantity'):
            if quantity.Name and quantity.Name.strip().lower() == constituent_name.strip().lower():
                matched_quantity = quantity
                logging.debug(f"Matched IfcPhysicalComplexQuantity '{quantity.Name}' for constituent '{constituent_name}'.")
                break

        if matched_quantity:
            # Find 'Width' sub-quantity
            width = None
            for sub_q in matched_quantity.HasQuantities:
                if sub_q.is_a('IfcQuantityLength') and sub_q.Name and sub_q.Name.strip().lower() == 'width':
                    width = sub_q.LengthValue
                    logging.info(f"Found Width for '{constituent_name}': {width} meters")
                    break
            if width is None:
                logging.warning(f"Missing 'Width' for constituent '{constituent_name}'. Assigning default thickness {DEFAULT_THICKNESS} meters.")
                width = DEFAULT_THICKNESS
        else:
            logging.warning(f"No matching quantity found for constituent '{constituent_name}'. Assigning default thickness {DEFAULT_THICKNESS} meters.")
            width = DEFAULT_THICKNESS

        # Validate width
        if width <= 0:
            logging.error(f"Invalid thickness ({width} meters) for constituent '{constituent_name}'. Skipping this layer.")
            continue

        # Create IfcMaterialLayer with correct attributes
        try:
            material_layer = model.create_entity(
                'IfcMaterialLayer',
                Material=material,
                LayerThickness=width,
                IsVentilated=None,
                Name=constituent_name,
                Description=constituent.Description if hasattr(constituent, 'Description') else None,
                Category='Materials'  # Adjust if necessary
            )
            material_layers.append(material_layer)
            logging.info(f"Created IfcMaterialLayer for '{constituent_name}' with thickness {width} meters.")
        except Exception as e:
            logging.error(f"Failed to create IfcMaterialLayer for '{constituent_name}': {e}")
            continue

        # Transfer material properties from the constituent to the layer
        for mat_property in getattr(constituent, 'HasProperties', []):
            try:
                # Depending on the property type, create corresponding property entities
                if mat_property.is_a('IfcPropertySingleValue'):
                    new_mat_property = model.create_entity(
                        'IfcPropertySingleValue',
                        Name=mat_property.Name,
                        Description=mat_property.Description,
                        NominalValue=mat_property.NominalValue,
                        Unit=mat_property.Unit if hasattr(mat_property, 'Unit') else None
                    )
                elif mat_property.is_a('IfcPropertyEnumeratedValue'):
                    new_mat_property = model.create_entity(
                        'IfcPropertyEnumeratedValue',
                        Name=mat_property.Name,
                        Description=mat_property.Description,
                        EnumerationValues=mat_property.EnumerationValues,
                        EnumerationReference=mat_property.EnumerationReference
                    )
                else:
                    logging.warning(f"Unsupported property type '{mat_property.is_a()}' for '{mat_property.Name}'. Skipping property transfer.")
                    continue

                # Associate the new property with the material layer
                rel_assoc_property = model.create_entity(
                    'IfcRelDefinesByProperties',
                    GlobalId=generate_guid(),
                    OwnerHistory=constituent_set.OwnerHistory,  # Adjust if necessary
                    Name=None,
                    Description=None,
                    RelatingPropertyDefinition=new_mat_property,
                    RelatedObjects=[material_layer]
                )
                logging.info(f"Transferred property '{mat_property.Name}' from constituent '{constituent_name}' to layer '{material_layer.Name}'.")
            except Exception as e:
                logging.error(f"Failed to transfer property '{mat_property.Name}' for material layer '{material_layer.Name}': {e}")

    if not material_layers:
        logging.error(f"No valid material layers found for constituent set '{constituent_set.Name}'. Skipping creation of IfcMaterialLayerSet.")
        continue  # Skip to the next constituent set

    # Create IfcMaterialLayerSet
    try:
        # Collect layer entities
        layer_entities = material_layers  # Pass layer entities directly
        material_layer_set = model.create_entity(
            'IfcMaterialLayerSet',
            Layers=layer_entities,
            LayerSetName=constituent_set.Name,
            Description='Generated Layer Set'
        )
        logging.info(f"Successfully created IfcMaterialLayerSet '{material_layer_set.Name}' with {len(layer_entities)} layers.")
    except Exception as e:
        logging.error(f"Failed to create IfcMaterialLayerSet for '{constituent_set.Name}': {e}")
        continue

    # Create IfcMaterialLayerSetUsage
    try:
        material_layer_set_usage = model.create_entity(
            'IfcMaterialLayerSetUsage',
            ForLayerSet=material_layer_set,
            LayerSetDirection=".AXIS2.",  # Adjust as necessary
            DirectionSense=".POSITIVE.",   # Adjust as necessary
            OffsetFromReferenceLine=0.0    # Adjust as necessary
        )
        logging.info(f"Created IfcMaterialLayerSetUsage for layer set '{material_layer_set.Name}'.")
    except Exception as e:
        logging.error(f"Failed to create IfcMaterialLayerSetUsage for '{material_layer_set.Name}': {e}")
        continue

    # Attempt to find associated walls via IfcRelAssociatesMaterial or other relationships
    associated_walls = []
    try:
        # Find all IfcRelAssociatesMaterial relationships pointing to the constituent_set
        rel_assoc_materials = model.get_inverse(constituent_set)
        for rel in rel_assoc_materials:
            if rel.is_a('IfcRelAssociatesMaterial'):
                related_objects = rel.RelatedObjects
                for obj in related_objects:
                    if obj.is_a('IfcWallType') or obj.is_a('IfcWall'):
                        associated_walls.append(obj)
        logging.info(f"Found {len(associated_walls)} associated walls for constituent set '{constituent_set.Name}'.")
    except Exception as e:
        logging.error(f"Failed to find associated walls for '{constituent_set.Name}': {e}")

    # Associate the layer set usage with the walls
    if not associated_walls:
        logging.warning(f"No associated walls found for constituent set '{constituent_set.Name}'. The IfcMaterialLayerSet is created but not linked to any walls.")
    else:
        for wall in associated_walls:
            try:
                # Create IfcRelAssociatesMaterialLayerSetUsage to link usage with wall
                rel_assoc_usage = model.create_entity(
                    'IfcRelAssociatesMaterialLayerSetUsage',
                    GlobalId=generate_guid(),
                    OwnerHistory=wall.OwnerHistory,  # Adjust if necessary
                    Name=None,
                    Description=None,
                    RelatingMaterialLayerSetUsage=material_layer_set_usage,
                    RelatedObjects=[wall]
                )
                logging.info(f"Associated IfcMaterialLayerSetUsage '{material_layer_set_usage}' with wall '{wall.Name}'.")
            except Exception as e:
                logging.error(f"Failed to associate IfcMaterialLayerSetUsage with wall '{wall.Name}': {e}")

    # Optionally, remove the old constituent set to prevent clutter
    try:
        model.remove(constituent_set)
        logging.info(f"Removed old IfcMaterialConstituentSet '{constituent_set.Name}'.")
    except Exception as e:
        logging.error(f"Failed to remove IfcMaterialConstituentSet '{constituent_set.Name}': {e}")

# Save the modified IFC model
try:
    model.write(output_file)
    logging.info(f"Modified IFC file has been saved as '{output_file}'.")
except Exception as e:
    logging.error(f"Failed to write the modified IFC file: {e}")
