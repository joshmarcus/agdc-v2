#!/usr/bin/env python

from setuptools import setup, find_packages
from version import get_version

GIT_VERSION = get_version()


def write_version_py(filename='datacube/version.py'):
    cnt = """#
# THIS FILE IS GENERATED FROM DATACUBE SETUP.PY
#
from __future__ import absolute_import
VERSION = '%(version)s'
"""

    with open(filename, 'w') as f:
        f.write(cnt % {'version': GIT_VERSION})

# Rewrite the version file everytime
write_version_py()


setup(name='datacube',
      version=GIT_VERSION,
      packages=find_packages(
          exclude=('tests', 'tests.*', 'examples',
                   'integration_tests', 'integration_tests.*')
      ),
      package_data={
          'gdf_tests': ['gdf_default.conf'],
          '': ['*.yaml'],
      },
      scripts=[
      ],
      setup_requires=[
          'pytest-runner'
      ],
      install_requires=[
          'click',
          'pathlib',
          'pyyaml',
          'sqlalchemy',
          'python-dateutil',
          'jsonschema',
          'cachetools',
          'numpy',
          'rasterio',
          'singledispatch',
          'netcdf4',
          'pypeg2',
          'psycopg2',
          'gdal',
          'dask',
          'setuptools',
          'toolz',
          'xarray',
          'scipy',
          'matplotlib',
          'numexpr',
      ],
      tests_require=[
          'pytest',
          'pytest-cov',
          'mock'
      ],
      url='https://github.com/data-cube/agdc-v2',
      author='AGDC Collaboration',
      maintainer='AGDC Collaboration',
      maintainer_email='',
      description='AGDC v2',
      long_description='Australian Geoscience Data Cube v2',
      license='Apache License 2.0',
      entry_points={
          'console_scripts': [
              'datacube-ingest = datacube.scripts.run_ingest:cli',
              'datacube-config = datacube.scripts.config_tool:cli',
              'datacube-search = datacube.scripts.search_tool:cli'
          ]
      },
      )

