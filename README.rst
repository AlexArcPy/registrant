Registrant: Esri geodatabase reporter
=====================================

This Python package is used for generating HTML reports about the contents of Esri geodatabases.

Features
--------

This Python package will generate an interactive HTML report file with the information about the geodatabase (personal, file, or SDE) itself along with information about datasets stored within the geodatabase. The report includes information about the following:

* General geodatabase overview
* Enterprise geodatabase versions
* Enterprise and local geodatabase replicas
* Domains & coded values
* Tables & Feature classes
* Table & Feature class fields
* Table & Feature class subtypes
* Table & Feature class indexes

The HTML report page is built using the `Bootstrap 3 Dashboard sample <http://getbootstrap.com/examples/dashboard/#>`_. Some extra functionality is added with the help of `Bootstrap 3 DataTables <https://datatables.net/examples/styling/bootstrap.html>`_ extension. Additional navigation items in the table of contents are added to the HTML page on-the-fly while reading geodatabase contents.

Requirements
------------

In order to use this tool, you would need to have ArcGIS Desktop or ArcGIS Pro installed (for ``arcpy``). The code written is a valid Python 2 as well as Python 3 code which means you will be able to run against ArcGIS Desktop Python 2.7 as well as ArcGIS Pro Python 3.5+. You will also need ``pandas`` and ``beatifulSoup`` Python packages which can be installed from ``pip`` if you are ArcGIS Desktop user or using ``conda`` if you are 
ArcGIS Pro user.

Getting started
---------------

The package has convenience functions which can be used to specify what exactly do you want to generate report for. The ``gdb2html`` function will create a complete report. This function provides you with fine-grained control over what information will be included in the report, so you can use it providing booleans arguments (for instance, you may want to get only list of tables and feature classes without reporting their fields, subtypes, and indexes). However, you can specify if you want to report only domains, only tables, or only feature classes using the ``domains2html``, ``tables2html``, and ``fcs2html`` convenience functions respectively.

To generate full geodatabase report:

.. code::

    import registrant
    reporter = registrant.Reporter(
        r"C:\GIS\Production.gdb", r"C:\GIS\ReportFolder"
    )
    reporter.gdb2html()
    print(reporter.report_file_path)

Issues
------

Did you find a bug? Do you need report to include some other information? Please let me know by submitting an issue.

Licensing
---------

MIT
