'''
Preparing the tests to be executed
'''
import sys
import os
import struct
import tempfile
import arcpy
arcpy.env.overwriteOutput = True

CONSOLE_MESSAGE = "Simple HTML report created at"
TEST_CONFIG = {
    'Basic': {
        'name': "Basic",
        'json_results': r"data\Basic.json",
        'xml_schema': r"data\XmlBasicSchema.xml"
    },
    'Advanced': {
        'name': "Adv",
        'json_results': r"data\Adv.json",
        'xml_schema': r"data\XmlAdvSchema.xml"
    }
}

PYTHON_VERSION = '_' + sys.version.split(' ')[0] + '_' + str(struct.calcsize('P') * 8) + 'bit'


#----------------------------------------------------------------------
def prepare_test(test_type):
    """prepare the geodatabase data for running tests on"""
    cfg = TEST_CONFIG[test_type]
    test_type = cfg['name']
    out_report_folder = os.path.join(tempfile.gettempdir(), test_type)
    if not os.path.exists(out_report_folder):
        os.mkdir(out_report_folder)
    xml_schema = cfg['xml_schema']
    in_gdb = arcpy.CreateFileGDB_management(out_report_folder, test_type).getOutput(0)
    arcpy.ImportXMLWorkspaceDocument_management(in_gdb, xml_schema, "SCHEMA_ONLY")
    json_results = cfg['json_results']

    return (in_gdb, out_report_folder, json_results)


#adding the project folder to support running test files individually and from the IDE
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    import registrant.registrant as registrant
except:
    import registrant
