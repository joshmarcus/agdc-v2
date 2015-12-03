from __future__ import print_function, absolute_import

from datetime import datetime

from affine import Affine
import numpy as np
import netCDF4
import pytest
import rasterio

from datacube.storage.netcdf_writer import NetCDFWriter, append_to_netcdf
from datacube.model import TileSpec, StorageType
from datacube.storage.ingester import SimpleObject
from datacube.storage.utils import tilespec_from_riodataset


def test_create_single_time_netcdf_from_numpy_arrays(tmpdir):
    filename = str(tmpdir.join('testfile_np.nc'))

    affine = Affine.from_gdal(151.0, 0.00025, 0.0, -29.0, 0.0, -0.0005)
    projection = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],' \
                 'AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433],' \
                 'AUTHORITY["EPSG","4326"]]'
    extents = [[151.0, -29.0], [151.0, -30.0], [152.0, -30.0], [152.0, -29.0]]
    global_attrs = {'test_attribute': 'test_value'}
    tile_spec = TileSpec(projection, affine, 2000, 4000, extents, global_attrs=global_attrs)

    chunking = {'t': 1, 'y': 100, 'x': 100}
    date = datetime(2008, 1, 1)
    ops = [(date, band) for band in [1, 2]]

    ncfile = NetCDFWriter(filename, tile_spec)

    for date, band in ops:
        data = np.empty([2000, 4000])
        data[:] = band
        bandname = 'B%s' % band

        ncfile.append_np_array(date, data, bandname, 'int16', -999, chunking, '1')
    ncfile.close()

    # Perform some basic checks
    nco = netCDF4.Dataset(filename)
    for var in ('crs', 'time', 'longitude', 'latitude', 'B1', 'B2', 'time'):
        assert var in nco.variables
    for k, v in global_attrs.items():
        assert getattr(nco, k) == v

    assert len(nco.variables['time']) == 1
    assert len(nco.variables['longitude']) == 4000
    assert len(nco.variables['latitude']) == 2000
    assert nco.variables['latitude'][0] == -29
    assert abs(nco.variables['latitude'][-1] - -29.9995) < 0.0000001
    assert nco.variables['longitude'][0] == 151
    assert nco.variables['longitude'][-1] == 151.99975


@pytest.mark.xfail
def test_create_multi_time_netcdf_from_numpy_arrays(tmpdir):
    filename = str(tmpdir.join('testfile_np.nc'))

    affine = Affine.from_gdal(151.0, 0.00025, 0.0, -29.0, 0.0, -0.0005)
    projection = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],' \
                 'AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433],' \
                 'AUTHORITY["EPSG","4326"]]'
    extents = [[151.0, -29.0], [151.0, -30.0], [152.0, -30.0], [152.0, -29.0]]
    tile_spec = TileSpec(projection, affine, 2000, 4000, extents)

    chunking = {'t': 1, 'y': 100, 'x': 100}
    dates = [datetime(2008, m, 1) for m in [1, 2, 3]]
    ops = [(date, band) for date in dates for band in [1, 2]]

    ncfile = NetCDFWriter(filename, tile_spec)

    for date, band in ops:
        data = np.empty([2000, 4000])
        data[:] = band
        bandname = 'B%s' % band

        ncfile.append_np_array(date, data, bandname, 'int16', -999, chunking, '1')
    ncfile.close()

    # Perform some basic checks
    nco = netCDF4.Dataset(filename)
    for var in ('crs', 'time', 'longitude', 'latitude', 'B1', 'B2', 'time'):
        assert var in nco.variables

    assert len(nco.variables['time']) == 3
    assert len(nco.variables['longitude']) == 4000
    assert len(nco.variables['latitude']) == 2000
    assert nco.variables['latitude'][0] == -29
    assert nco.variables['latitude'][-1] == -29.99975
    assert nco.variables['longitude'][0] == 151
    assert nco.variables['longitude'][-1] == 151.99975


def test_create_sample_netcdf_from_gdalds(tmpdir, example_gdal_path):
    filename = str(tmpdir.join('testfile_gdal.nc'))

    dataset = rasterio.open(example_gdal_path)

    band_info = SimpleObject(varname='B10', dtype='int16', nodata=-999)
    storage_spec = {'chunking': {'x': 100, 'y': 100, 't': 1}}
    storage_type = StorageType('NetCDF-CF', 'mock_storage_type', 'for testing', storage_spec)

    tile_spec = tilespec_from_riodataset(dataset)
    tile_spec.data = dataset.read(1)

    append_to_netcdf(tile_spec, filename, storage_type, band_info, datetime(2008, 5, 5, 0, 24),
                     input_filename="")

    # Perform some basic checks
    nco = netCDF4.Dataset(filename)
    for var in ('crs', 'time', 'longitude', 'latitude', 'B10', 'time'):
        assert var in nco.variables

    assert len(nco.variables['time']) == 1
    assert len(nco.variables['longitude']) == 4000
    assert len(nco.variables['latitude']) == 4000
    assert len(nco.variables['B10']) == 1
    assert nco.variables['latitude'][0] == -29
    assert nco.variables['latitude'][-1] == -29.99975
    assert nco.variables['longitude'][0] == 151
    assert nco.variables['longitude'][-1] == 151.99975

    assert nco.variables['B10'].shape == (1, 4000, 4000)

    nco.close()
