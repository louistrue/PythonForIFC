import ifcopenshell
import os

def add_geometric_subcontext(model, context):
    # Create a new IfcGeometricRepresentationSubContext
    subcontext = model.create_entity('IfcGeometricRepresentationSubContext',
                                     ContextIdentifier="Model",
                                     ContextType="Model",
                                     ParentContext=context,
                                     TargetScale=None,
                                     TargetView='MODEL_VIEW',
                                     UserDefinedTargetView=None)
    
    # Convert HasSubContexts to a list if it's a tuple or None, then append the new subcontext
    if context.HasSubContexts:
        has_subcontexts = list(context.HasSubContexts)
        has_subcontexts.append(subcontext)
    else:
        has_subcontexts = [subcontext]
    
    # Assign the updated list back to HasSubContexts
    context.HasSubContexts = has_subcontexts
    
    print(f"Added missing GeometricRepresentationSubContext to context in file.")

def fix_geometric_context(ifc_file):
    # Open the IFC file
    model = ifcopenshell.open(ifc_file)
    
    # Get the IfcProject entity
    ifc_project = model.by_type('IfcProject')
    
    if ifc_project:
        # Check if RepresentationContexts is None or empty
        for project in ifc_project:
            if not project.RepresentationContexts:
                # Create a new IfcGeometricRepresentationContext if missing
                context = model.create_entity('IfcGeometricRepresentationContext',
                                              ContextIdentifier="Model",
                                              ContextType="3D",
                                              CoordinateSpaceDimension=3,
                                              Precision=1e-05,
                                              WorldCoordinateSystem=model.create_entity('IfcAxis2Placement3D',
                                                                                        Location=model.create_entity('IfcCartesianPoint',
                                                                                                                     Coordinates=(0.0, 0.0, 0.0)),
                                                                                        Axis=None,
                                                                                        RefDirection=None),
                                              TrueNorth=None)
                
                # Assign the new context to the project's RepresentationContexts
                project.RepresentationContexts = [context]
                print(f"Added missing RepresentationContext to project in file: {ifc_file}")
            else:
                # Use the existing context if present
                context = project.RepresentationContexts[0]

            # Check for subcontexts in the context
            if not context.HasSubContexts or len(context.HasSubContexts) == 0:
                # Add a subcontext if none exists
                add_geometric_subcontext(model, context)
            
            # Save the modified file
            model.write(ifc_file)
            print(f"File saved: {ifc_file}")

def process_ifc_files(directory):
    # Process all IFC files in the directory
    for filename in os.listdir(directory):
        if filename.endswith(".ifc"):
            ifc_file_path = os.path.join(directory, filename)
            fix_geometric_context(ifc_file_path)

if __name__ == "__main__":
    # Specify the directory containing the IFC files
    ifc_directory = ...
    
    # Process the IFC files in the directory
    process_ifc_files(ifc_directory)
