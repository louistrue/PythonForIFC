import pytest
from src.map_viewer import MapViewer
from PyQt5.QtWidgets import QApplication

@pytest.fixture
def map_viewer():
    app = QApplication([])
    viewer = MapViewer()
    viewer.show()
    return viewer

def test_load_map(map_viewer):
    map_viewer.loadMap(latitude=47.0, longitude=8.0, zoom=15)
    assert map_viewer.page().url().toString() == 'file:///path/to/map_template.html'  # Update with actual path

def test_add_marker(map_viewer):
    map_viewer.addMarker(latitude=47.0, longitude=8.0, label="Test Marker")
    # Further testing may involve inspecting the JavaScript side, which is complex in pure Python tests
