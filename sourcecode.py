import vtk
import numpy as np

# -----------------------------------------------------
# Merge VTP files into a single VTK file
# -----------------------------------------------------
def merge_vtp_to_vtk():
    input_file1 = "./data/lh.pial.vtp"
    input_file2 = "./data/rh.pial.vtp"
    output_file = "./output/brain_merged.vtk"

    reader1 = vtk.vtkXMLPolyDataReader()
    reader1.SetFileName(input_file1)
    reader1.Update()
    data1 = reader1.GetOutput()

    reader2 = vtk.vtkXMLPolyDataReader()
    reader2.SetFileName(input_file2)
    reader2.Update()
    data2 = reader2.GetOutput()

    transform = vtk.vtkTransform()
    transform.Translate(0, 0, 0)
    transform_filter = vtk.vtkTransformPolyDataFilter()
    transform_filter.SetInputData(data2)
    transform_filter.SetTransform(transform)
    transform_filter.Update()
    transformed_data2 = transform_filter.GetOutput()

    append_filter = vtk.vtkAppendPolyData()
    append_filter.AddInputData(data1)
    append_filter.AddInputData(transformed_data2)
    append_filter.Update()

    writer = vtk.vtkPolyDataWriter()
    writer.SetFileName(output_file)
    writer.SetInputData(append_filter.GetOutput())
    writer.Write()

    print(f"Merged VTK file written to {output_file}")


# -----------------------------------------------------
# Convert VTK to STL
# -----------------------------------------------------
def convert_vtk_image_to_stl():
    input_file = "./output/brain_merged.vtk"
    output_file = "./output/uncolored_brain.stl"

    reader = vtk.vtkStructuredPointsReader()
    reader.SetFileName(input_file)
    reader.Update()

    contour_filter = vtk.vtkMarchingCubes()
    contour_filter.SetInputConnection(reader.GetOutputPort())
    contour_filter.SetValue(0, 100)
    contour_filter.Update()

    smoother = vtk.vtkSmoothPolyDataFilter()
    smoother.SetInputConnection(contour_filter.GetOutputPort())
    smoother.SetNumberOfIterations(50)
    smoother.Update()

    stl_writer = vtk.vtkSTLWriter()
    stl_writer.SetFileName(output_file)
    stl_writer.SetInputConnection(smoother.GetOutputPort())
    stl_writer.Write()

    print(f"STL file saved as {output_file}")


# -----------------------------------------------------
# Merge VTP files with colors and save as VTK
# -----------------------------------------------------
def merge_vtp_with_color():
    input_file1 = "./data/lh.pial.vtp"
    input_file2 = "./data/rh.pial.vtp"
    output_file = "./output/brain_merged_colored.vtk"

    reader1 = vtk.vtkXMLPolyDataReader()
    reader1.SetFileName(input_file1)
    reader1.Update()
    data1 = reader1.GetOutput()

    color1 = vtk.vtkUnsignedCharArray()
    color1.SetName("Colors")
    color1.SetNumberOfComponents(3)
    for _ in range(data1.GetNumberOfPoints()):
        color1.InsertNextTuple([255, 0, 0])
    data1.GetPointData().SetScalars(color1)

    reader2 = vtk.vtkXMLPolyDataReader()
    reader2.SetFileName(input_file2)
    reader2.Update()
    data2 = reader2.GetOutput()

    color2 = vtk.vtkUnsignedCharArray()
    color2.SetName("Colors")
    color2.SetNumberOfComponents(3)
    for _ in range(data2.GetNumberOfPoints()):
        color2.InsertNextTuple([0, 0, 255])
    data2.GetPointData().SetScalars(color2)

    transform = vtk.vtkTransform()
    transform.Translate(0, 0, 0)
    transform_filter = vtk.vtkTransformPolyDataFilter()
    transform_filter.SetInputData(data2)
    transform_filter.SetTransform(transform)
    transform_filter.Update()
    transformed_data2 = transform_filter.GetOutput()

    append_filter = vtk.vtkAppendPolyData()
    append_filter.AddInputData(data1)
    append_filter.AddInputData(transformed_data2)
    append_filter.Update()

    writer = vtk.vtkPolyDataWriter()
    writer.SetFileName(output_file)
    writer.SetInputData(append_filter.GetOutput())
    writer.Write()

    print(f"Colored VTK file written to {output_file}")


# -----------------------------------------------------
# Convert colored VTK to PLY
# -----------------------------------------------------
def convert_colored_vtk_to_ply():
    input_file = "./output/brain_merged_colored.vtk"
    output_file = "./output/colored_brain.ply"

    reader = vtk.vtkPolyDataReader()
    reader.SetFileName(input_file)
    reader.Update()

    polydata = reader.GetOutput()
    if not polydata or polydata.GetNumberOfPoints() == 0:
        print("Error: No polydata found in the input file!")
        return

    smoother = vtk.vtkSmoothPolyDataFilter()
    smoother.SetInputData(polydata)
    smoother.SetNumberOfIterations(50)
    smoother.Update()

    ply_writer = vtk.vtkPLYWriter()
    ply_writer.SetFileName(output_file)
    ply_writer.SetInputData(smoother.GetOutput())
    ply_writer.SetArrayName("Colors")
    ply_writer.Write()

    print(f"PLY file saved as {output_file}")


# -----------------------------------------------------
# Load VTP files
# -----------------------------------------------------
def load_vtp_file(file_path):
    reader = vtk.vtkXMLPolyDataReader()
    reader.SetFileName(file_path)
    reader.Update()
    polydata = reader.GetOutput()
    print(f"File: {file_path}")
    print(f"Points: {polydata.GetNumberOfPoints()}")
    print(f"Cells: {polydata.GetNumberOfCells()}")
    return polydata


# -----------------------------------------------------
# Assign Hemisphere Colors
# -----------------------------------------------------
def assign_hemisphere_colors(polydata, is_left=True):
    color_array = vtk.vtkUnsignedCharArray()
    color_array.SetName("Colors")
    color_array.SetNumberOfComponents(3)

    for i in range(polydata.GetNumberOfPoints()):
        color = [255, 0, 0] if is_left else [0, 0, 255]
        color_array.InsertNextTuple(color)

    polydata.GetPointData().SetScalars(color_array)
    return polydata


# -----------------------------------------------------
# Combine Two Polydata
# -----------------------------------------------------
def combine_polydata(polydata1, polydata2):
    append_filter = vtk.vtkAppendPolyData()
    append_filter.AddInputData(polydata1)
    append_filter.AddInputData(polydata2)
    append_filter.Update()
    combined = append_filter.GetOutput()
    print(f"Combined PolyData: {combined.GetNumberOfPoints()} points, {combined.GetNumberOfCells()} cells")
    return combined


# -----------------------------------------------------
# Compute Region Statistics
# -----------------------------------------------------
def compute_region_statistics(polydata):
    stats = {}
    scalars = polydata.GetPointData().GetArray("Colors")

    if not scalars:
        raise ValueError("No Colors array found!")

    unique_colors = set(
        tuple(int(scalars.GetComponent(i, c)) for c in range(3))
        for i in range(scalars.GetNumberOfTuples())
    )

    for color in unique_colors:
        points = [
            polydata.GetPoint(i)
            for i in range(polydata.GetNumberOfPoints())
            if tuple(int(scalars.GetComponent(i, c)) for c in range(3)) == color
        ]

        stats[color] = {
            "Points": len(points),
            "Cells": polydata.GetNumberOfCells()
        }

    return stats


# -----------------------------------------------------
# Visualize PolyData
# -----------------------------------------------------
def visualize_polydata(polydata):
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(polydata)
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    renderer = vtk.vtkRenderer()
    renderer.AddActor(actor)
    renderer.SetBackground(0.1, 0.1, 0.1)

    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    render_window.Render()
    interactor.Start()

# -----------------------------------------------------
# Export Colored PolyData to PLY
# -----------------------------------------------------
def export_colored_polydata_to_ply(polydata, output_file):
    try:
        ply_writer = vtk.vtkPLYWriter()
        ply_writer.SetFileName(output_file)
        ply_writer.SetInputData(polydata)
        ply_writer.SetArrayName("Colors")
        ply_writer.Write()
        print(f"Exported colored polydata to {output_file}")
    except Exception as e:
        print(f"Export to PLY failed: {e}")


# -----------------------------------------------------
# Calculate Region Volumes Using Explicit Filtering
# -----------------------------------------------------
def calculate_region_volumes_explicit_filtering(polydata, region_stats):
    scalars = polydata.GetPointData().GetArray("Colors")
    if not scalars:
        raise ValueError("No Colors array found!")

    region_volumes = {}

    for color, stats in region_stats.items():
        points = vtk.vtkPoints()
        for i in range(polydata.GetNumberOfPoints()):
            if tuple(int(scalars.GetComponent(i, c)) for c in range(3)) == color:
                points.InsertNextPoint(polydata.GetPoint(i))

        region_polydata = vtk.vtkPolyData()
        region_polydata.SetPoints(points)

        if region_polydata.GetNumberOfPoints() == 0:
            print(f"Warning: No points found for region {color}. Skipping...")
            region_volumes[color] = 0.0
            continue

        mass_properties = vtk.vtkMassProperties()
        mass_properties.SetInputData(region_polydata)
        try:
            volume = mass_properties.GetVolume()
            region_volumes[color] = volume
        except Exception as e:
            print(f"Error calculating volume for region {color}: {e}")
            region_volumes[color] = 0.0

    return region_volumes


# -----------------------------------------------------
# Add Custom Labels for Regions
# -----------------------------------------------------
def add_custom_labels(renderer, polydata, region_volumes, region_offsets):
    normals_generator = vtk.vtkPolyDataNormals()
    normals_generator.SetInputData(polydata)
    normals_generator.ComputePointNormalsOn()
    normals_generator.Update()
    polydata_with_normals = normals_generator.GetOutput()
    normals = polydata_with_normals.GetPointData().GetNormals()

    scalars = polydata_with_normals.GetPointData().GetArray("Colors")
    if not scalars:
        raise ValueError("No Colors array found!")

    for color, volume in region_volumes.items():
        points = [
            i for i in range(polydata_with_normals.GetNumberOfPoints())
            if tuple(int(scalars.GetComponent(i, c)) for c in range(3)) == color
        ]

        if not points:
            print(f"Warning: No surface points found for region {color}.")
            continue

        base_index = points[0]
        base_position = polydata_with_normals.GetPoint(base_index)
        normal = normals.GetTuple(base_index)
        offset_distance = region_offsets.get(color, 20)
        offset_position = [base_position[i] + offset_distance * normal[i] for i in range(3)]

        text_actor = vtk.vtkBillboardTextActor3D()
        text_actor.SetInput(f"Color: {color}\nVolume: {volume:.2f}")
        text_actor.SetPosition(*offset_position)
        text_actor.GetTextProperty().SetFontSize(14)
        text_actor.GetTextProperty().SetColor(1.0, 1.0, 1.0)

        renderer.AddActor(text_actor)


# -----------------------------------------------------
# Visualize Slices of PolyData
# -----------------------------------------------------
def visualize_slices(polydata, axis=0, num_slices=5):
    bounds = polydata.GetBounds()
    slice_step = (bounds[axis * 2 + 1] - bounds[axis * 2]) / num_slices

    renderer = vtk.vtkRenderer()
    for i in range(num_slices):
        slice_value = bounds[axis * 2] + i * slice_step
        plane = vtk.vtkPlane()
        plane.SetOrigin(slice_value if axis == 0 else 0, slice_value if axis == 1 else 0, slice_value if axis == 2 else 0)
        plane.SetNormal(1 if axis == 0 else 0, 1 if axis == 1 else 0, 1 if axis == 2 else 0)

        cutter = vtk.vtkCutter()
        cutter.SetCutFunction(plane)
        cutter.SetInputData(polydata)
        cutter.Update()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(cutter.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        renderer.AddActor(actor)

    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    renderer.SetBackground(0.1, 0.1, 0.1)
    render_window.Render()
    interactor.Start()


# -----------------------------------------------------
# Create Isoline PolyData
# -----------------------------------------------------
def create_isoline_polydata(polydata, num_contours=10):
    contour_filter = vtk.vtkContourFilter()
    contour_filter.SetInputData(polydata)
    scalar_range = polydata.GetPointData().GetScalars().GetRange()
    contour_filter.GenerateValues(num_contours, scalar_range)
    contour_filter.Update()
    return contour_filter.GetOutput()


# -----------------------------------------------------
# Visualize Full Brain with Isolines
# -----------------------------------------------------
def render_full_brain_with_isolines(brain_polydata, isoline_polydata):
    tube_filter = vtk.vtkTubeFilter()
    tube_filter.SetInputData(isoline_polydata)
    tube_filter.SetRadius(0.5)
    tube_filter.SetNumberOfSides(20)
    tube_filter.Update()
    enhanced_isoline_polydata = tube_filter.GetOutput()

    brain_mapper = vtk.vtkPolyDataMapper()
    brain_mapper.SetInputData(brain_polydata)
    brain_mapper.SetScalarModeToUsePointFieldData()
    brain_mapper.SelectColorArray("Colors")

    brain_actor = vtk.vtkActor()
    brain_actor.SetMapper(brain_mapper)
    brain_actor.GetProperty().SetOpacity(0.8)

    isoline_mapper = vtk.vtkPolyDataMapper()
    isoline_mapper.SetInputData(enhanced_isoline_polydata)

    isoline_actor = vtk.vtkActor()
    isoline_actor.SetMapper(isoline_mapper)
    isoline_actor.GetProperty().SetColor(0, 1, 0)
    isoline_actor.GetProperty().SetLineWidth(2.0)

    renderer = vtk.vtkRenderer()
    renderer.AddActor(brain_actor)
    renderer.AddActor(isoline_actor)
    renderer.SetBackground(0.1, 0.1, 0.1)

    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)
    render_window.SetSize(800, 800)

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)
    render_window.Render()
    interactor.Start()

# -----------------------------------------------------
# Render Colored Sliced Brain with Isolines
# -----------------------------------------------------
def render_colored_sliced_brain_with_isolines(brain_polydata, isoline_polydata, axis=1, slice_position=0.5):
    bounds = brain_polydata.GetBounds()
    slice_value = bounds[axis * 2] + slice_position * (bounds[axis * 2 + 1] - bounds[axis * 2])

    plane = vtk.vtkPlane()
    plane.SetOrigin(
        slice_value if axis == 0 else 0,
        slice_value if axis == 1 else 0,
        slice_value if axis == 2 else 0
    )
    plane.SetNormal(
        1 if axis == 0 else 0,
        1 if axis == 1 else 0,
        1 if axis == 2 else 0
    )

    # Slice the brain polydata
    brain_cutter = vtk.vtkCutter()
    brain_cutter.SetCutFunction(plane)
    brain_cutter.SetInputData(brain_polydata)
    brain_cutter.Update()

    brain_mapper = vtk.vtkPolyDataMapper()
    brain_mapper.SetInputConnection(brain_cutter.GetOutputPort())
    brain_mapper.SetScalarModeToUsePointFieldData()
    brain_mapper.SelectColorArray("Colors")

    brain_actor = vtk.vtkActor()
    brain_actor.SetMapper(brain_mapper)
    brain_actor.GetProperty().SetOpacity(0.8)

    # Slice the isoline polydata
    isoline_cutter = vtk.vtkCutter()
    isoline_cutter.SetCutFunction(plane)
    isoline_cutter.SetInputData(isoline_polydata)
    isoline_cutter.Update()

    isoline_mapper = vtk.vtkPolyDataMapper()
    isoline_mapper.SetInputConnection(isoline_cutter.GetOutputPort())

    isoline_actor = vtk.vtkActor()
    isoline_actor.SetMapper(isoline_mapper)
    isoline_actor.GetProperty().SetColor(1, 0, 0)
    isoline_actor.GetProperty().SetLineWidth(2.0)

    renderer = vtk.vtkRenderer()
    renderer.AddActor(brain_actor)
    renderer.AddActor(isoline_actor)
    renderer.SetBackground(0.1, 0.1, 0.1)

    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)
    render_window.SetSize(800, 800)

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    render_window.Render()
    interactor.Start()


# -----------------------------------------------------
# Calculate Region Surface Areas
# -----------------------------------------------------
def calculate_region_surface_areas(polydata, region_stats):
    scalars = polydata.GetPointData().GetArray("Colors")
    if not scalars:
        raise ValueError("No Colors array found in PointData.")

    region_areas = {}
    for color, stats in region_stats.items():
        points = vtk.vtkPoints()
        for i in range(polydata.GetNumberOfPoints()):
            current_color = tuple(int(scalars.GetComponent(i, c)) for c in range(3))
            if current_color == color:
                points.InsertNextPoint(polydata.GetPoint(i))

        region_polydata = vtk.vtkPolyData()
        region_polydata.SetPoints(points)

        delaunay = vtk.vtkDelaunay3D()
        delaunay.SetInputData(region_polydata)
        delaunay.Update()

        surface_filter = vtk.vtkGeometryFilter()
        surface_filter.SetInputData(delaunay.GetOutput())
        surface_filter.Update()
        surface_polydata = surface_filter.GetOutput()

        if surface_polydata.GetNumberOfCells() == 0:
            print(f"Warning: No valid surface for region {color}. Skipping...")
            region_areas[color] = 0.0
            continue

        mass_properties = vtk.vtkMassProperties()
        mass_properties.SetInputData(surface_polydata)
        try:
            surface_area = mass_properties.GetSurfaceArea()
            region_areas[color] = surface_area
        except Exception as e:
            print(f"Error calculating surface area for region {color}: {e}")
            region_areas[color] = 0.0

    return region_areas


# -----------------------------------------------------
# Calculate Principal Axes
# -----------------------------------------------------
def calculate_principal_axes(polydata, region_stats):
    scalars = polydata.GetPointData().GetArray("Colors")
    if not scalars:
        raise ValueError("No Colors array found in PointData.")

    principal_axes = {}

    for color, stats in region_stats.items():
        points = []
        for i in range(polydata.GetNumberOfPoints()):
            current_color = tuple(int(scalars.GetComponent(i, c)) for c in range(3))
            if current_color == color:
                points.append(polydata.GetPoint(i))

        if not points:
            print(f"No points found for region {color}.")
            continue

        points_np = np.array(points)
        mean = np.mean(points_np, axis=0)
        centered_points = points_np - mean
        covariance_matrix = np.cov(centered_points.T)
        eigenvalues, eigenvectors = np.linalg.eigh(covariance_matrix)

        principal_axes[color] = {
            "Eigenvalues": eigenvalues.tolist(),
            "Eigenvectors": eigenvectors.tolist(),
            "Mean Position": mean.tolist()
        }

    return principal_axes


# -----------------------------------------------------
# Main Execution (Continuation)
# -----------------------------------------------------
if __name__ == "__main__":
    # Step 1: Merge VTP files into VTK format
    merge_vtp_to_vtk()

    # Step 2: Convert the merged VTK file into an STL file
    convert_vtk_image_to_stl()

    # Step 3: Merge VTP files with colors applied and save as a new VTK
    merge_vtp_with_color()

    # Step 4: Convert the colored VTK file to PLY
    convert_colored_vtk_to_ply()

    # Step 5: Load VTP files for left and right hemispheres
    lh_polydata = load_vtp_file("./data/lh.pial.vtp")
    rh_polydata = load_vtp_file("./data/rh.pial.vtp")

    # Step 6: Assign colors to each hemisphere
    lh_colored = assign_hemisphere_colors(lh_polydata, is_left=True)
    rh_colored = assign_hemisphere_colors(rh_polydata, is_left=False)

    # Step 7: Combine the colored hemispheres
    combined_colored_polydata = combine_polydata(lh_colored, rh_colored)

    # Step 8: Inspect colors in the combined polydata
    inspect_colors(combined_colored_polydata)

    # Step 9: Compute region statistics
    region_stats = compute_region_statistics(combined_colored_polydata)
    print("\nRegion Statistics:")
    for color, stats in region_stats.items():
        print(f"Region {color}: Points = {stats['Points']}, Cells = {stats['Cells']}")

    # Step 10: Visualize the combined polydata
    visualize_polydata(combined_colored_polydata)

    # Step 11: Export the combined polydata to PLY (final segmented brain)
    export_colored_polydata_to_ply(combined_colored_polydata, "./output/final_segmented_brain.ply")

    # Step 12: Calculate region volumes
    region_volumes = calculate_region_volumes_explicit_filtering(combined_colored_polydata, region_stats)
    print("\nRegion Volumes:")
    for color, volume in region_volumes.items():
        print(f"Region {color}: Volume = {volume:.2f}")

    # Step 13: Add custom labels to the visualization
    region_offsets = {
        (255, 0, 0): 60,  # Red
        (0, 255, 0): 10,  # Green
        (0, 0, 255): 70,  # Blue
        (255, 255, 0): 20,  # Yellow
    }
    renderer = vtk.vtkRenderer()
    add_custom_labels(renderer, combined_colored_polydata, region_volumes, region_offsets)

    # Step 14: Visualize slices of the polydata
    visualize_slices(combined_colored_polydata, axis=1, num_slices=5)

    # Step 15: Create isoline polydata
    isoline_polydata = create_isoline_polydata(combined_colored_polydata)

    # Step 16: Visualize the full brain with isolines
    render_full_brain_with_isolines(combined_colored_polydata, isoline_polydata)

    # Step 17: Render a sliced view of the brain with isolines
    render_colored_sliced_brain_with_isolines(combined_colored_polydata, isoline_polydata, axis=1, slice_position=0.5)

    # Step 18: Calculate region surface areas
    region_areas = calculate_region_surface_areas(combined_colored_polydata, region_stats)
    print("\nRegion Surface Areas:")
    for color, area in region_areas.items():
        print(f"Region {color}: Surface Area = {area:.2f}")

    # Step 19: Calculate principal axes for each region
    principal_axes = calculate_principal_axes(combined_colored_polydata, region_stats)
    print("\nPrincipal Axes for Each Region:")
    for color, axes in principal_axes.items():
        label = {
            (255, 0, 0): "Left-Front",
            (0, 255, 0): "Left-Back",
            (0, 0, 255): "Right-Front",
            (255, 255, 0): "Right-Back",
        }.get(color, "Unknown")
        print(f"\nRegion {color} ({label}):")
        print(f"  Eigenvalues: {axes['Eigenvalues']}")
        print(f"  Eigenvectors: {axes['Eigenvectors']}")
        print(f"  Mean Position: {axes['Mean Position']}")
