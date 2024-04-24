#first block
from netCDF4 import Dataset

import numpy as np

import metpy.calc as mpcalc
from metpy.units import units
from metpy.plots import current_weather, sky_cover, StationPlot, simple_layout, wx_code_to_numeric
from metpy.io import metar

import pandas as pd

import matplotlib.pyplot as plt

import cartopy.crs as ccrs
import cartopy.feature as cfeature

def upperairproj(filename,density=75*units('km')),cxi=-120,cyi=-75,cxf=23,cyf=50):
        #second block
    nc = Dataset('20211211_0500')
    #third block
    #read in variables needed for plotting surface station plots
    station_name = nc.variables['stationName'][:]
    latitude = nc.variables['latitude'][:]
    longitude = nc.variables['longitude'][:]
    temp = (nc.variables['temperature'][:]-273.15)*(9/5)+32.0
    dwpt = (nc.variables['dewpoint'][:]-273.15)*(9/5)+32.0
    wspd = nc.variables['windSpeed'][:]
    wdir = nc.variables['windDir'][:]
    gust = nc.variables['windGust'][:]
    weather = nc.variables['presWeather'][:]
    visibility = nc.variables['visibility'][:]
    pslp = nc.variables['seaLevelPress'][:]/100 #pascal to hPa
    skycover = nc.variables['skyCover'][:]
    
    #fourth block
    #get u and v wind components
    wspd_from_nc = np.array(wspd)*units('m/s')
    wdir_from_nc = np.array(wdir)*units('degrees')
    u,v = mpcalc.wind_components(wspd_from_nc,wdir_from_nc)
    
    #fifth block
    #convert our data to a pandas dataframe
    data_for_df = {'station_id':stn_names,
                   'latitude':latitude,
                   'longitude':longitude,
                   'wind_direction':wdir,
                   'wind_speed':wspd,
                   'wind_gust':gust,
                   'visibility':visibility,
                   'current_wx1_symbol':wx_codes,
                   'air_temperature':temp,
                   'dew_point_temperature':dwpt,
                   'air_pressure_at_sea_level':pslp,
                   'eastward_wind':u,
                   'northward_wind':v,
                   'cloud_coverage': sky_cover_num}
    
    #col_names = ['station_id','latitude','longitude','wind_direction','wind_speed','wind_gust',
    #             'visibility','current_wx1_symbol','air_temperature','dew_point_temperature','air_pressure_at_sea_level']
    
    data = pd.DataFrame(data_for_df,index=stn_names)
    
    #six block
    data_thinned = data[mpcalc.reduce_point_density(locs,75*units('km'))]
    
    #seven block
    #create wind gust vectors
    #get wind direction from metpy
    u = data_thinned.eastward_wind.values * units('knots')
    v = data_thinned.northward_wind.values * units('knots')
    gust = data_thinned.wind_gust.values * units('knots')
    #print(u)
    wdir = mpcalc.wind_direction(u,v)
    #get wind gust components assuming same direction using metpy wind components
    ug,vg = mpcalc.wind_components(gust,wdir)
    
    #map projection
    proj = ccrs.LambertConformal(central_longitude=-95,central_latitude=35)
    
    #create figure
    fig = plt.figure(figsize=(10,10),dpi=100)
    ax = fig.add_subplot(1,1,1,projection=proj)
    
    #add elements to make map more useable
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.STATES)
    ax.add_feature(cfeature.BORDERS)
    
    #zoom on the Northern Plains
    ax.set_extent((-105, -90, 40, 50))
    
    
    #create stationplot (will actually need to create 2 to handle wind gusts)
    stationplots = StationPlot(ax,data_thinned['longitude'],data_thinned['latitude'],transform=ccrs.PlateCarree(),clip_on=True,fontsize=10)
    stationplots_gusts = StationPlot(ax,data_thinned['longitude'],data_thinned['latitude'],transform=ccrs.PlateCarree(),clip_on=True,fontsize=10)
    
    
    #temperature in red
    stationplots.plot_parameter((-1,1), data_thinned['air_temperature'].values, color='red')
    #dewpoint in dark green
    stationplots.plot_parameter((-1,-1), data_thinned['dew_point_temperature'].values, color='darkgreen')
    
    #pressure (need to format to be the final 3 digits)
    stationplots.plot_parameter((1,1), data_thinned['air_pressure_at_sea_level'].values, color='black',
                                   formatter=lambda p: format(10*p, '.0f')[-3:])
    
    #station ID in dark blue
    stationplots.plot_text((1.5,-1), data_thinned['station_id'].values, color='darkblue')
    
    #visibility in black (need to convert from meters to miles)
    stationplots.plot_parameter((-2,0),data_thinned['visibility'].values*units('meters').to(units('miles')),color='black')
    
    #wind gust in red
    stationplots_gusts.plot_barb(ug,vg,color='red',zorder=9)
    
    #wind in black
    stationplots.plot_barb(u,v,color='black',zorder=10)
    
    #cloud cover
    stationplots.plot_symbol((0,0), data_thinned['cloud_coverage'].values, sky_cover)
    
    #current weather
    stationplots.plot_symbol((-1,0), data_thinned['current_wx1_symbol'].values, current_weather)
    
    #save the map as surface_obs.png