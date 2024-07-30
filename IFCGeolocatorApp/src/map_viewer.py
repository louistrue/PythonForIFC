import os
import json
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, QObject, pyqtSlot
from PyQt5.QtWebChannel import QWebChannel
from pyproj import Transformer, CRS
import requests
from dotenv import load_dotenv

class MapViewer(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Map Viewer")

        # Load environment variables
        load_dotenv()
        self.html_template_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'templates', 'osm_map_template.html')
        
        self.load_default_map()

    def load_default_map(self):
        print("Loading default map...")
        if os.path.exists(self.html_template_path):
            with open(self.html_template_path, 'r') as file:
                map_html = file.read()

            self.setHtml(map_html, QUrl.fromLocalFile(self.html_template_path))
            print("HTML template loaded.")
        else:
            print(f"Error: HTML template file does not exist at {self.html_template_path}")

    def setHtmlFromFile(self):
        if os.path.exists(self.html_template_path):
            with open(self.html_template_path, 'r') as file:
                map_html = file.read()
            
            # Inject API key into the HTML
            map_html = map_html.replace('YOUR_MAPTILER_API_KEY_HERE', self.api_key)

            self.setHtml(map_html, QUrl.fromLocalFile(self.html_template_path))
            print("HTML template set with MapTiler API key.")
        else:
            print(f"Error: HTML template file does not exist at {self.html_template_path}")

    def send_to_js(self, data):
        self.page().runJavaScript(f"jsFunction({json.dumps(data)});")

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

        print(f"Map settings to be used: {map_settings}")

        with open(self.html_template_path, 'r') as file:
            map_html = file.read()

        # Replace placeholder with actual JSON string
        map_html = map_html.replace('<!-- MAP_SETTINGS -->', json.dumps(map_settings))

        print("Map HTML with settings loaded, setting HTML to view...")
        self.setHtml(map_html, QUrl.fromLocalFile(self.html_template_path))
        self.map_initialized = True

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
            # Fetch the origin offset for the given EPSG code and transformation code
            origin_lat, origin_long = self.fetch_origin_offset(epsg_code, transformation_code)
            print(f"Origin offset for EPSG:{epsg_code} using transformation {transformation_code}: lat={origin_lat}, long={origin_long}")

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

            # Marker for the origin coordinates
            self.addMarker(origin_lat, origin_long, "MapConversion Origin")

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
            setMapView({latitude}, {longitude}, {zoom});
        """)

    def fitBoundsToAllMarkers(self):
        print("Fitting bounds to all markers")
        self.page().runJavaScript("fitBoundsToAllMarkers();")

    def setMapView(self, latitude, longitude, zoom):
        print(f"Setting view to lat: {latitude}, long: {longitude}, zoom: {zoom}")
        self.page().runJavaScript(f"setMapView({latitude}, {longitude}, {zoom});")

    def addMarker(self, latitude, longitude, label):
        print(f"Adding marker at lat: {latitude}, long: {longitude} with label: {label}")
        self.page().runJavaScript(f"addMarker({latitude}, {longitude}, {label});")

    def clearMarkers(self):
        print("Clearing all markers...")
        self.page().runJavaScript("clearMarkers();")
    def addCoordinateAxes(self, x_abscissa, x_ordinate):
        print(f"Adding coordinate axes with x_abscissa={x_abscissa}, x_ordinate={x_ordinate}")
        self.page().runJavaScript(f"""
            var xAxis = L.polyline([[0, 0], [{x_abscissa}, {x_ordinate}]], {{color: 'red', weight: 3, opacity: 0.7, dashArray: '5, 5'}}).addTo(map);
            var yAxis = L.polyline([[0, 0], [{-x_ordinate}, {x_abscissa}]], {{color: 'blue', weight: 3, opacity: 0.7, dashArray: '5, 5'}}).addTo(map);
            L.marker([{x_abscissa}, {x_ordinate}]).addTo(map).bindTooltip("X Axis", {{permanent: true, direction: 'right'}});
            L.marker([{-x_ordinate}, {x_abscissa}]).addTo(map).bindTooltip("Y Axis", {{permanent: true, direction: 'top'}});
        """)

