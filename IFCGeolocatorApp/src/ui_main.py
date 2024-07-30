from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QTabWidget, QLabel, QFrame, QGroupBox
from PyQt5.QtWebEngineWidgets import QWebEngineView 

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("IFC Geolocator")
        self.setGeometry(100, 100, 1600, 900)

        # Central Widget
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Main Layout
        self.main_layout = QVBoxLayout(self.central_widget)
        self.central_widget.setLayout(self.main_layout)

        # Tab Widget for IFC Files
        self.tab_widget = QTabWidget(self.central_widget)
        self.tab_widget.setFixedHeight(30)
        self.tab_widget.setTabsClosable(True)
        self.main_layout.addWidget(self.tab_widget)

        # Map Viewer
        self.map_viewer = QWebEngineView(self.central_widget)

        # Information Panel - Site and Map Conversion Cards
        self.info_panel = QFrame(self.central_widget)
        self.info_layout = QHBoxLayout(self.info_panel)
        self.info_panel.setMinimumHeight(50)
        self.info_panel.setMaximumHeight(200)

        self.site_info_group = QGroupBox("Site Coordinates", self.central_widget)
        self.site_info_label = QLabel("No site data available.", self.site_info_group)
        site_info_layout = QVBoxLayout(self.site_info_group)
        site_info_layout.addWidget(self.site_info_label)
        self.site_info_group.setLayout(site_info_layout)

        self.map_conversion_info_group = QGroupBox("Map Conversion Coordinates", self.central_widget)
        self.map_conversion_info_label = QLabel("No map conversion data available.", self.map_conversion_info_group)
        map_conversion_layout = QVBoxLayout(self.map_conversion_info_group)
        map_conversion_layout.addWidget(self.map_conversion_info_label)
        self.map_conversion_info_group.setLayout(map_conversion_layout)

        self.info_layout.addWidget(self.site_info_group)
        self.info_layout.addWidget(self.map_conversion_info_group)
        self.main_layout.addWidget(self.info_panel)

    def setupUi(self, parent):
        parent.setWindowTitle("IFC Geolocator")
        parent.setGeometry(100, 100, 1600, 900)
        parent.setCentralWidget(self.central_widget)
