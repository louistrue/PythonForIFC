import pytest
from PyQt5.QtWidgets import QApplication
from src.main import IFCGeolocatorApp

@pytest.fixture
def app(qtbot):
    test_app = QApplication([])
    window = IFCGeolocatorApp()
    qtbot.addWidget(window)
    return window

def test_load_ifc_files_button(app, qtbot):
    qtbot.mouseClick(app.ui.load_button, qtbot.LeftButton)
    # Assuming a file dialog will open, but since we cannot interact with it in the test,
    # we just test that the button click does not crash the app.
    assert app.ui.sidebar.count() == 0  # No file loaded
