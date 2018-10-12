# -*- coding: UTF-8 -*-
"""Context variables and constants used throughout the package."""
import os

HTML_PARSER = 'html.parser'
DIV_CSS_CLASS = 'col-sm-9 col-sm-offset-3 col-md-10 col-md-offset-2 main'

REPORT_FILE_NAME = 'index.html'
HTML_TEMPLATE_FOLDER = 'html-template'
HTML_TEMPLATE_FILE = 'template.html'
REPORT_TEMPLATE_FILE = os.path.join(
    (os.path.dirname(os.path.abspath(__file__))), HTML_TEMPLATE_FOLDER,
    HTML_TEMPLATE_FILE)
REPORT_DATA_FOLDER_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'app')

COMMONS_LICENSE_TEXT = """
Bootstrap Dashboard example used and Glyphicons icons used for
data tables are licensed under the Creative Commons Attribution
3.0 Unported License. To view a copy of this license, visit
http://creativecommons.org/licenses/by/3.0/ or send a letter to
Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
"""

OGR_GDB_SUPPORT_MESSAGE = """Only file geodatabases are supported
for use with GDAL/OGR"""

DATASET_TYPE_TABLE = 'table'
DATASET_TYPE_FC = 'fc'
ESRI_GDB_REPLICA_INF_DATE = 1899
