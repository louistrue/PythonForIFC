import os
import json
import math
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
from PyQt5.QtWebChannel import QWebChannel
from pyproj import Transformer, CRS
import requests

class MapViewer(QWebEngineView):
    def __init__(self, parent=None, api_key=None):
        super().__init__(parent)
        self.setWindowTitle("Map Viewer")
        self.html_template_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'templates', 'map_template.html')
        self.default_latitude = 0.0
        self.default_longitude = 0.0
        self.default_zoom_level = 2
        self.api_key = api_key  # Store the API key
        self.markers = []  # Store markers for later use

        # Check if the HTML template exists
        self.check_html_template()
        self.load_default_map()

        # Set up the WebChannel for communication with JavaScript
        self.channel = QWebChannel()
        self.channel.registerObject('pyObj', self)
        self.page().setWebChannel(self.channel)

    def check_html_template(self):
        if not os.path.exists(self.html_template_path):
            print(f"Error: HTML template file does not exist at {self.html_template_path}")
        else:
            print(f"HTML template path set to: {self.html_template_path}")

    def load_default_map(self):
        print("Loading default map...")
        self.loadMap(self.default_latitude, self.default_longitude, self.default_zoom_level)

    def loadMap(self, latitude=None, longitude=None, zoom=None):
        print(f"Loading map with latitude={latitude}, longitude={longitude}, zoom={zoom}")
        if latitude is None:
            latitude = self.default_latitude
        if longitude is None:
            longitude = self.default_longitude
        if zoom is None:
            zoom = self.default_zoom_level

        map_settings = {
            'latitude': latitude,
            'longitude': longitude,
            'zoom': zoom
        }

        with open(self.html_template_path, 'r') as file:
            map_html = file.read()

        map_html = map_html.replace('<!-- MAP_SETTINGS -->', json.dumps(map_settings))
        self.setHtml(map_html, QUrl.fromLocalFile(self.html_template_path))
        self.map_initialized = True

    def setSiteView(self):
        print("Setting site view...")
        # Replace with the actual logic to set the site view
        self.page().runJavaScript("setMapView(51.505, -0.09, 13);")

    def setConvertedView(self):
        print("Setting converted view...")
        # Replace with the actual logic to set the converted view
        self.page().runJavaScript("setMapView(40.7128, -74.0060, 13);")

    def setOriginView(self):
        print("Setting origin view...")
        # Replace with the actual logic to set the origin view
        self.page().runJavaScript("setMapView(48.8566, 2.3522, 13);")

    def fitBoundsToAllMarkers(self):
        print("Fitting bounds to all markers")
        self.page().runJavaScript("fitBoundsToAllMarkers();")

    def addMarker(self, latitude, longitude, label):
        print(f"Adding marker at lat: {latitude}, long: {longitude} with label: {label}")
        self.page().runJavaScript(f"addMarker({latitude}, {longitude}, '{label}');")

    def clearMarkers(self):
        print("Clearing all markers...")
        self.page().runJavaScript("clearMarkers();")
        self.markers.clear()

    def fetch_origin_offset(self, epsg_code, transformation_code):
        try:
            url = f"https://api.maptiler.com/coordinates/transform/0,0.json?key={self.api_key}&s_srs={epsg_code}&t_srs=4326&ops={transformation_code}"
            response = requests.get(url)
            if (data := response.json()).get('results'):
                return data['results'][0]['y'], data['results'][0]['x']  # Lat, Long
        except Exception as e:
            print(f"Exception occurred while fetching origin offset for EPSG:{epsg_code}: {e}")
        return 0.0, 0.0

    def applyMapConversion(self, eastings, northings, rotation_degrees, scale, ref_lat, ref_long, epsg_code, transformation_code, largest_coords=None):
        print(f"Applying map conversion: eastings={eastings}, northings={northings}, rotation={rotation_degrees}, scale={scale}, epsg_code={epsg_code}, transformation_code={transformation_code}")

        try:
            # Use EPSG code to transform coordinates from EPSG to WGS84
            crs_src = CRS.from_epsg(epsg_code)
            crs_dst = CRS.from_epsg(4326)
            transformer = Transformer.from_crs(crs_src, crs_dst, always_xy=True)
            wgs84_long, wgs84_lat = transformer.transform(eastings, northings)

            # Ensure the longitude wraps correctly
            final_long = (wgs84_long + 180) % 360 - 180

            print(f"Converted Coordinates: lat={wgs84_lat}, long={final_long}")

            # Set markers and calculate bounding box
            if ref_lat is not None and ref_long is not None:
                self.addMarker(ref_lat, ref_long, "Site Coordinates")
            else:
                print("Reference site coordinates are not available.")

            self.addMarker(wgs84_lat, final_long, "Converted Coordinates")

            # Use the origin coordinates in the local EPSG system directly for marker
            origin_lat, origin_long = self.fetch_origin_offset(epsg_code, transformation_code)
            self.addMarker(origin_lat, origin_long, "Projected CRS: Origin")

            if largest_coords:
                try:
                    largest_x, largest_y, _ = largest_coords
                    largest_long, largest_lat = transformer.transform(largest_x, largest_y)
                    self.addMarker(largest_lat, largest_long, "Largest Coordinate")
                except Exception as e:
                    print(f"Error calculating largest coordinates: {e}")

            # Adjust the bounds to include all markers
            self.fitBoundsToAllMarkers()

        except Exception as e:
            print(f"Error applying map conversion: {e}")


    def setView(self, latitude, longitude, zoom):
        print(f"Setting view to lat: {latitude}, long: {longitude}, zoom: {zoom}")
        self.page().runJavaScript(f"""
            map.setView([{latitude}, {longitude}], {zoom});
        """)

    def addCoordinateAxes(self, x_abscissa, x_ordinate):
        print(f"Adding coordinate axes with x_abscissa={x_abscissa}, x_ordinate={x_ordinate}")
        self.page().runJavaScript(f"""
            var xAxis = L.polyline([[0, 0], [{x_abscissa}, {x_ordinate}]], {{color: 'red', weight: 3, opacity: 0.7, dashArray: '5, 5'}}).addTo(map);
            var yAxis = L.polyline([[0, 0], [{-x_ordinate}, {x_abscissa}]], {{color: 'blue', weight: 3, opacity: 0.7, dashArray: '5, 5'}}).addTo(map);
            L.marker([{x_abscissa}, {x_ordinate}]).addTo(map).bindTooltip("X Axis", {{permanent: true, direction: 'right'}});
            L.marker([{-x_ordinate}, {x_abscissa}]).addTo(map).bindTooltip("Y Axis", {{permanent: true, direction: 'top'}});
        """)

