from pyproj import Transformer

# Define the transformer using EPSG:2056 to WGS84
transformer = Transformer.from_crs("EPSG:2056", "EPSG:4326", always_xy=True)

# Example coordinates in LV95 (Easting, Northing)
east_lv95 = 2600000.000
north_lv95 = 1200000.000

# Convert using the transformer
longitude, latitude = transformer.transform(east_lv95, north_lv95)

print(f"Converted Coordinates: lat={latitude}, long={longitude}")
