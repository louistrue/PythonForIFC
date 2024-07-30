import os
import json
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl

class MapViewer(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Map Viewer")
        self.html_template_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'templates', 'map_template.html')
        self.default_latitude = 0.0
        self.default_longitude = 0.0
        self.default_zoom_level = 2

        # Check if the HTML template exists
        self.check_html_template()
        self.load_default_map()

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

        print(f"Map settings to be used: {map_settings}")

        with open(self.html_template_path, 'r') as file:
            map_html = file.read()

        # Replace placeholder with actual JSON string
        map_html = map_html.replace('<!-- MAP_SETTINGS -->', json.dumps(map_settings))

        print("Map HTML with settings loaded, setting HTML to view...")
        self.setHtml(map_html, QUrl.fromLocalFile(self.html_template_path))

    def addMarker(self, latitude, longitude, label):
        print(f"Adding marker at latitude={latitude}, longitude={longitude} with label={label}")
        self.page().runJavaScript(f"""
            var marker = L.marker([{latitude}, {longitude}]).addTo(map);
            marker.bindPopup("{label}");
        """)

    def setView(self, latitude, longitude, zoom):
        print(f"Setting view to latitude={latitude}, longitude={longitude}, zoom={zoom}")
        self.page().runJavaScript(f"""
            map.setView([{latitude}, {longitude}], {zoom});
        """)

    def clearMarkers(self):
        print("Clearing all markers...")
        self.page().runJavaScript("map.eachLayer(function (layer) { if(layer instanceof L.Marker) { map.removeLayer(layer); } });")

    def addCoordinateAxes(self, x_abscissa, x_ordinate):
        print(f"Adding coordinate axes with x_abscissa={x_abscissa}, x_ordinate={x_ordinate}")
        self.page().runJavaScript(f"""
            var xAxis = L.polyline([[0, 0], [{x_abscissa}, {x_ordinate}]], {{color: 'red', weight: 3, opacity: 0.7, dashArray: '5, 5'}}).addTo(map);
            var yAxis = L.polyline([[0, 0], [{-x_ordinate}, {x_abscissa}]], {{color: 'blue', weight: 3, opacity: 0.7, dashArray: '5, 5'}}).addTo(map);
            L.marker([{x_abscissa}, {x_ordinate}]).addTo(map).bindTooltip("X Axis", {{permanent: true, direction: 'right'}});
            L.marker([{-x_ordinate}, {x_abscissa}]).addTo(map).bindTooltip("Y Axis", {{permanent: true, direction: 'top'}});
        """)
