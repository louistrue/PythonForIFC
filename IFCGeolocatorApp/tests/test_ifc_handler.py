import pytest
from src.ifc_handler import IFCHandler

@pytest.fixture
def ifc_handler():
    return IFCHandler()

def test_load_ifc_file(ifc_handler):
    file_path = 'tests/test_data/sample.ifc'
    ifc_file = ifc_handler.load_ifc_file(file_path)
    assert ifc_file is not None

def test_get_project_info(ifc_handler):
    file_path = 'tests/test_data/sample.ifc'
    ifc_file = ifc_handler.load_ifc_file(file_path)
    project_info = ifc_handler.get_project_info(ifc_file)
    assert project_info['name'] == 'Sample Project'
    assert project_info['description'] == 'This is a sample project.'

def test_get_site_info(ifc_handler):
    file_path = 'tests/test_data/sample.ifc'
    ifc_file = ifc_handler.load_ifc_file(file_path)
    site_info = ifc_handler.get_site_info(ifc_file)
    assert site_info['name'] == 'Sample Site'
    assert site_info['ref_lat_decimal'] is not None
    assert site_info['ref_long_decimal'] is not None
