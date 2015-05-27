#!/usr/bin/env python

import netCDF4 as nc
import numpy as np

lats = np.arange(-90.0, 90.0, 0.75)
longs = np.arange(0.0, 359.25, 0.75)

infile_name = 'rec_front_1979_01.v26.nc'
outfile_name = 'out.nc'

def create_maps(nc_var, nnumber, npoint, lats, longs):
    """
    Input: netCDF variable, timestep, number of fronts, number of points
        numpy array with latitudes, numpy array with longitudes
    Output: 2D numpy array of ints., 3x2D arrays of floats
    """
    front_map = np.zeros((len(lats), len(longs)), dtype=np.int)
    t_map = np.zeros((len(lats), len(longs)), dtype=np.float)
    u_map = np.zeros_like(t_map)
    v_map = np.zeros_like(t_map)
    for n in xrange(nnumber):
        for p in xrange(npoint):
            lat, lon, speed_t, speed_u, speed_v = nc_var[n, p, :]
            if lat < -1000 :
                break
            latidx = np.argmin(abs(lats - lat))
            lonidx = np.argmin(abs(longs - lon))
            if ((lon > longs[-1]) and
                (360.0+longs[0] - lon < lon - longs[-1])):
                lonidx = 0
            front_map[latidx, lonidx] = n
            t_map[latidx, lonidx] = speed_t
            u_map[latidx, lonidx] = speed_u
            v_map[latidx, lonidx] = speed_v
    return (front_map, t_map, u_map, v_map)



infile = nc.Dataset(infile_name, 'r')
ntime = len(infile.dimensions['time'])
nnumber = len(infile.dimensions['number'])
npoint = len(infile.dimensions['point'])
ndata = len(infile.dimensions['data'])

outfile = nc.Dataset(outfile_name, 'w')
outfile.createDimension('time', size=None)
outfile.createDimension('latitude', size=len(lats))
outfile.createDimension('longitude', size=len(longs))

timevar = outfile.createVariable(
    'time', infile.variables['time'].datatype, ('time',))
latsvar = outfile.createVariable(
    'latitude', np.float, ('latitude',))
longsvar = outfile.createVariable(
    'longitude', np.float, ('longitude',))

timevar.units = infile.variables['time'].units

setattr(latsvar, 'long_name', 'Latitude')
setattr(latsvar, 'units', 'degree_north')
setattr(longsvar, 'long_name', 'Longitude')
setattr(longsvar, 'units', 'degree_east')

cf_var = outfile.createVariable(
    'cold_fronts', np.int, ('time', 'latitude', 'longitude'))
wf_var = outfile.createVariable(
    'warm_fronts', np.int, ('time', 'latitude', 'longitude'))
sf_var = outfile.createVariable(
    'stat_fronts', np.int, ('time', 'latitude', 'longitude'))

t_var = outfile.createVariable(
    'thetaw_gradient', np.float, ('time', 'latitude', 'longitude'))
u_var = outfile.createVariable(
    'u_speed', np.float, ('time', 'latitude', 'longitude'))
v_var = outfile.createVariable(
    'v_speed', np.float, ('time', 'latitude', 'longitude'))

latsvar[:] = lats
longsvar[:] = longs

cf_data = np.zeros((nnumber, npoint, 5), dtype=np.float)
wf_data = np.zeros_like(cf_data)
sf_data = np.zeros_like(cf_data)

timevar[:] = infile.variables['time'][:]

for t in xrange(ntime):
    cf_data[:, :, :] = infile.variables['cold_fronts'][t, :, :, :]
    wf_data[:, :, :] = infile.variables['warm_fronts'][t, :, :, :]
    sf_data[:, :, :] = infile.variables['stat_fronts'][t, :, :, :]
    cf_map, t_map_cf, u_map_cf, v_map_cf = \
              create_maps(cf_data, nnumber, npoint, lats, longs)
    wf_map, t_map_wf, u_map_wf, v_map_wf = \
              create_maps(wf_data, nnumber, npoint, lats, longs)
    sf_map, t_map_sf, u_map_sf, v_map_sf = \
              create_maps(sf_data, nnumber, npoint, lats, longs)

    cf_var[t, :, :] = cf_map[:, :]
    wf_var[t, :, :] = wf_map[:, :]
    sf_var[t, :, :] = sf_map[:, :]

    t_map = np.where(t_map_wf != 0.0, t_map_wf,
                              np.where(t_map_cf != 0.0, t_map_cf,
                                       t_map_sf))
    u_map = np.where(u_map_wf != 0.0, u_map_wf,
                              np.where(u_map_cf != 0.0, u_map_cf,
                                       u_map_sf))
    v_map = np.where(v_map_wf != 0.0, v_map_wf,
                              np.where(v_map_cf != 0.0, v_map_cf,
                                       v_map_sf))
    print "{}/{}".format(t, ntime)
    

outfile.close()
infile.close()
