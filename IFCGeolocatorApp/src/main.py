import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QVBoxLayout, QWidget, QAction, QRadioButton, QLabel, QHBoxLayout
from src.ui_main import MainWindow
from src.ifc_handler import IFCHandler
from src.map_viewer import MapViewer

class IFCGeolocatorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = MainWindow()
        self.ui.setupUi(self)

        self.ifc_handler = IFCHandler()
        self.map_viewer = MapViewer(self.ui.map_viewer)
        self.ui.main_layout.addWidget(self.map_viewer)

        self.create_actions()
        self.create_menus()
        self.load_ifc_files()

        self.ui.tab_widget.currentChanged.connect(self.display_ifc_info)
        self.add_view_controls()

    def create_actions(self):
        self.load_action = QAction("Load IFC Files", self)
        self.load_action.triggered.connect(self.load_ifc_files)

        self.export_action = QAction("Export to PDF", self)
        self.export_action.triggered.connect(self.export_to_pdf)

    def create_menus(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        file_menu.addAction(self.load_action)
        file_menu.addAction(self.export_action)

    def load_ifc_files(self):
        options = QFileDialog.Options()
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Open IFC Files", "", "IFC Files (*.ifc);;All Files (*)", options=options)
        if file_paths:
            for file_path in file_paths:
                ifc_file = self.ifc_handler.load_ifc_file(file_path)
                if ifc_file:
                    tab_content = QWidget()
                    layout = QVBoxLayout(tab_content)
                    file_label = QLabel(file_path, tab_content)
                    layout.addWidget(file_label)
                    self.ui.tab_widget.addTab(tab_content, os.path.basename(file_path))

            self.ui.tab_widget.setCurrentIndex(0)
            self.display_ifc_info()

    def export_to_pdf(self):
        print("Export to PDF clicked")
        print("PDF export functionality is not implemented yet.")

    def display_ifc_info(self):
        current_index = self.ui.tab_widget.currentIndex()
        if current_index != -1:
            tab = self.ui.tab_widget.widget(current_index)
            file_path = tab.layout().itemAt(0).widget().text()
            ifc_file = self.ifc_handler.ifc_files.get(file_path)
            if ifc_file:
                project_info = self.ifc_handler.get_project_info(ifc_file)
                site_info = self.ifc_handler.get_site_info(ifc_file)
                map_conversion_info = self.ifc_handler.get_map_conversion_info(ifc_file)

                self.site_coords = site_info
                self.map_conversion_coords = map_conversion_info

                self.ui.site_info_label.setText(
                    f"Project Name: {project_info['name']}\n"
                    f"Reference Latitude (DMS): {site_info['ref_lat_dms']}\n"
                    f"Reference Longitude (DMS): {site_info['ref_long_dms']}\n"
                    f"Reference Latitude (Decimal Degrees): {site_info['ref_lat_decimal']}\n"
                    f"Reference Longitude (Decimal Degrees): {site_info['ref_long_decimal']}\n"
                    f"Reference Elevation: {site_info['ref_elevation']} meters\n"
                )

                if map_conversion_info:
                    epsg_info = map_conversion_info.get('epsg_info', {})
                    epsg_name = epsg_info.get('name', 'N/A') if epsg_info else 'N/A'
                    self.ui.map_conversion_info_label.setText(
                        f"EPSG Code: {map_conversion_info['epsg_code']}\n"
                        f"EPSG Name: {epsg_name}\n"
                        f"Eastings: {map_conversion_info['eastings']} meters\n"
                        f"Northings: {map_conversion_info['northings']} meters\n"
                        f"Orthogonal Height: {map_conversion_info['orthogonal_height']} meters\n"
                        f"X Axis Abscissa: {map_conversion_info['x_axis_abscissa']}\n"
                        f"X Axis Ordinate: {map_conversion_info['x_axis_ordinate']}\n"
                        f"Rotation: {map_conversion_info['rotation_degrees']} degrees\n"
                        f"Scale: {map_conversion_info['scale']}\n"
                    )
                else:
                    self.ui.map_conversion_info_label.setText("No map conversion data available.")

    def add_view_controls(self):
        # Add radio buttons to switch between views
        self.view_controls_layout = QHBoxLayout()

        self.radio_site = QRadioButton("Site")
        self.radio_converted = QRadioButton("Converted")
        self.radio_origin = QRadioButton("Origin")
        self.radio_all = QRadioButton("All")

        self.radio_site.toggled.connect(lambda: self.on_view_toggled("site"))
        self.radio_converted.toggled.connect(lambda: self.on_view_toggled("converted"))
        self.radio_origin.toggled.connect(lambda: self.on_view_toggled("origin"))
        self.radio_all.toggled.connect(lambda: self.on_view_toggled("all"))

        self.view_controls_layout.addWidget(self.radio_site)
        self.view_controls_layout.addWidget(self.radio_converted)
        self.view_controls_layout.addWidget(self.radio_origin)
        self.view_controls_layout.addWidget(self.radio_all)

        self.ui.main_layout.addLayout(self.view_controls_layout)

    def on_view_toggled(self, view_type):
        if view_type == "site" and self.radio_site.isChecked():
            self.zoom_to_site()
        elif view_type == "converted" and self.radio_converted.isChecked():
            self.zoom_to_converted()
        elif view_type == "origin" and self.radio_origin.isChecked():
            self.zoom_to_origin()
        elif view_type == "all" and self.radio_all.isChecked():
            self.zoom_to_all()

    def zoom_to_site(self):
        if self.site_coords:
            lat = self.site_coords.get('ref_lat_decimal', 0)
            long = self.site_coords.get('ref_long_decimal', 0)
            self.map_viewer.setView(lat, long, 18)

    def zoom_to_converted(self):
        if self.map_conversion_coords:
            lat = self.map_conversion_coords.get('eastings', 0)
            long = self.map_conversion_coords.get('northings', 0)
            self.map_viewer.setView(lat, long, 18)

    def zoom_to_origin(self):
        if self.map_conversion_coords:
            epsg_code = self.map_conversion_coords.get('epsg_code', 0)
            transformation_code = self.map_conversion_coords.get('transformation_code', 0)
            origin_lat, origin_long = self.map_viewer.fetch_origin_offset(epsg_code, transformation_code)
            self.map_viewer.setView(origin_lat, origin_long, 18)

    def zoom_to_all(self):
        self.map_viewer.fitBoundsToAllMarkers()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IFCGeolocatorApp()
    window.show()
    sys.exit(app.exec_())

