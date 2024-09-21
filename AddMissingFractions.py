import ifcopenshell
from ifcopenshell.util.element import get_type, get_psets
from ifcopenshell.util.unit import calculate_unit_scale
from ifcopenshell.util.placement import get_local_placement

def assign_constituent_fractions(input_file, output_file):
    """
    Assigns fractions to material constituents in an IFC file based on their widths.

    Parameters:
    - input_file: Path to the input IFC file.
    - output_file: Path where the modified IFC file will be saved.
    """
    try:
        # Open the IFC model
        model = ifcopenshell.open(input_file)
    except Exception as e:
        print(f"Error: Failed to open IFC file '{input_file}': {e}")
        return

    # Calculate the unit scale for length units to millimeters
    unit_scale_to_mm = calculate_unit_scale(model) * 1000.0

    # Iterate through each IfcMaterialConstituentSet in the model
    for constituent_set in model.by_type('IfcMaterialConstituentSet'):
        constituents = constituent_set.MaterialConstituents or []
        if not constituents:
            continue  # Skip if no constituents found

        # Find elements associated with this constituent set via IfcRelAssociatesMaterial
        associated_relations = model.get_inverse(constituent_set)
        associated_elements = [
            rel.RelatedObjects[0] for rel in associated_relations
            if rel.is_a('IfcRelAssociatesMaterial') and rel.RelatedObjects
        ]
        if not associated_elements:
            continue  # Skip if no associated elements found

        # Collect quantities associated with the elements
        quantities = []
        for element in associated_elements:
            for rel in getattr(element, 'IsDefinedBy', []):
                if rel.is_a('IfcRelDefinesByProperties'):
                    prop_def = rel.RelatingPropertyDefinition
                    if prop_def.is_a('IfcElementQuantity'):
                        quantities.extend(prop_def.Quantities)

        # Build a mapping of quantity names to quantities
        quantity_name_map = {}
        for q in quantities:
            if q.is_a('IfcPhysicalComplexQuantity'):
                q_name = (q.Name or '').strip().lower()
                quantity_name_map.setdefault(q_name, []).append(q)

        # Handle constituents with duplicate names by order of appearance
        constituent_indices = {}
        constituent_widths = {}
        total_width_mm = 0.0

        for constituent in constituents:
            constituent_name = (constituent.Name or "Unnamed Constituent").strip().lower()
            count = constituent_indices.get(constituent_name, 0)
            constituent_indices[constituent_name] = count + 1

            width_mm = 0.0
            quantities_with_name = quantity_name_map.get(constituent_name, [])

            if count < len(quantities_with_name):
                matched_quantity = quantities_with_name[count]
                # Extract 'Width' sub-quantity
                for sub_q in matched_quantity.HasQuantities:
                    if sub_q.is_a('IfcQuantityLength') and (sub_q.Name or '').strip().lower() == 'width':
                        raw_length_value = sub_q.LengthValue or 0.0
                        width_mm = raw_length_value * unit_scale_to_mm
                        break

            constituent_widths[constituent] = width_mm
            total_width_mm += width_mm

        if total_width_mm == 0.0:
            continue  # Skip if total width is zero to avoid division by zero

        # Assign fractions based on widths
        for constituent, width_mm in constituent_widths.items():
            fraction = width_mm / total_width_mm
            constituent.Fraction = fraction
            print("Constituent:", constituent.Name, "Width:", width_mm, "mm")

    try:
        # Save the modified IFC model
        model.write(output_file)
        print(f"Modified IFC file has been saved as '{output_file}'.")
    except Exception as e:
        print(f"Error: Failed to write the modified IFC file: {e}")

# Example usage:
if __name__ == "__main__":
    input_file = r"C:\Users\LouisTrümpler\Documents\GitHub\NHMzh\tests\SampleIfc\4_RV_Str.ifc"
    output_file = input_file[:-4] + "_modified.ifc"
    assign_constituent_fractions(input_file, output_file)
