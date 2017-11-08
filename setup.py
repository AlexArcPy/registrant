from setuptools import setup

from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='registrant',
    version='0.4',
    description='Esri geodatabase HTML reporter',
    long_description=long_description,
    url='https://github.com/AlexArcPy/registrant',
    author='Alexey Tereshenkov',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Scientific/Engineering :: GIS',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5'
        ],
    keywords='Esri, ArcGIS, geodatabase, report, Python, ArcPy',
    packages=['registrant', 'registrant/html-template', 'registrant/app'],
    include_package_data=True,
    install_requires=['pandas>=0.20.1', 'beautifulsoup4>=4.6.0'],
    package_data={'registrant/html-template' : ['template.html'],
                  'registrant/app' : ['css/*', 'fonts/*', 'js/*']},
)
