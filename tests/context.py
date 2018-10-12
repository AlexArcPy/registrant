# -*- coding: UTF-8 -*-
"""Preparing the tests to be executed."""
import sys
import os
import struct
import tempfile
import pkgutil

# adding the project folder to support running test files individually and
# from the IDE
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))
try:
    from registrant import registrant
except BaseException:
    import registrant  # noqa: F401


NO_OGR_ENV_MESSAGE = """
Running tests with Python installation with no ogr available"""
NO_ARCPY_ENV_MESSAGE = """
Running tests with Python installation with no arcpy available"""

TEST_CONFIG = {
    'Basic': {
        'name': 'Basic',
        'json_results': r'data\Basic.json',
        'xml_schema': r'data\XmlBasicSchema.xml',
    },
    'Advanced': {
        'name': 'Adv',
        'json_results': r'data\Adv.json',
        'xml_schema': r'data\XmlAdvSchema.xml',
    },
    'Basic_ogr': {
        'name': 'Basic_ogr',
        'json_results': r'data\Basic_ogr.json',
        'ogr_geodatabase': r'data\Basic_ogr.gdb',
    },
    'Advanced_ogr': {
        'name': 'Adv_ogr',
        'json_results': r'data\Adv_ogr.json',
        'ogr_geodatabase': r'data\Adv_ogr.gdb',
    },
    'Complete': {
        'name': 'Complete',
        'json_results': r'data\Compl.json',
        'xml_schema': r'data\XmlComplSchema.xml',
    },
}

PYTHON_VERSION = '_{version}_{struct_size}bit'.format(
    version=sys.version.split(' ')[0],
    struct_size=str(struct.calcsize('P') * 8),
)


# ----------------------------------------------------------------------
def prepare_test(test_type):
    """Prepare the geodatabase data for running tests on."""
    cfg = TEST_CONFIG[test_type]
    test_type = cfg['name']
    out_report_folder = os.path.join(tempfile.gettempdir(), test_type)
    if not os.path.exists(out_report_folder):
        os.mkdir(out_report_folder)

    arcpy_loader = pkgutil.find_loader('arcpy')
    if arcpy_loader:
        import arcpy
        arcpy.env.overwriteOutput = True
        xml_schema = cfg['xml_schema']
        in_gdb = arcpy.CreateFileGDB_management(
            out_folder_path=out_report_folder,
            out_name=test_type,
        ).getOutput(0)
        arcpy.ImportXMLWorkspaceDocument_management(
            target_geodatabase=in_gdb,
            in_file=xml_schema,
            import_type='SCHEMA_ONLY',
        )
    else:
        in_gdb = cfg['ogr_geodatabase']

    json_results = cfg['json_results']
    return (in_gdb, out_report_folder, json_results)
