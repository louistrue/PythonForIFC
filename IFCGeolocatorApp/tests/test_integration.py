import pytest
from PyQt5.QtWidgets import QApplication
from src.main import IFCGeolocatorApp

@pytest.fixture
def app(qtbot):
    test_app = QApplication([])
    window = IFCGeolocatorApp()
    qtbot.addWidget(window)
    return window

def test_load_and_display_ifc_info(app, qtbot):
    app.load_ifc_files()
    qtbot.mouseClick(app.ui.load_button, qtbot.LeftButton)
    # Simulate selecting an item from the sidebar
    item = app.ui.sidebar.item(0)
    app.ui.sidebar.setCurrentItem(item)
    app.display_ifc_info()

    assert "Project Name" in app.ui.info_panel.text()
    assert "Reference Latitude" in app.ui.info_panel.text()
