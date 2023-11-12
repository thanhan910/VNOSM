import os
import geopandas as gpd

current_dir = os.path.dirname(os.path.realpath(__file__))

input_folder = os.path.join(current_dir, "subareas")

# Specify the output folder for TopoJSON files
output_folder = os.path.join(current_dir, "subtopo")

# Create the output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Loop through all GeoJSON files in the input folder
for geojson_file in os.listdir(input_folder):
    if geojson_file.endswith(".geojson"):
        # Construct the full path for input and output files
        input_path = os.path.join(input_folder, geojson_file)
        filename_noext, _ = os.path.splitext(geojson_file)
        output_path_topojson = os.path.join(output_folder, f"{filename_noext}.topojson")

        # Convert GeoJSON to TopoJSON using geopandas
        gdf : gpd.GeoDataFrame = gpd.read_file(input_path)
        gdf.to_file(output_path_topojson, driver="TopoJSON")


print("Conversion and compression completed.")
