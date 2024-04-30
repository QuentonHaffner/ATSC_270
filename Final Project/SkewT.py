#import required libraries
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import metpy.calc as mpcalc
from metpy.plots import SkewT, Hodograph
from metpy.units import units

from datetime import datetime

def projskewT(station='KJAN',year=2011,month=4,day=27,hour=18):
    #get data from Iowa Environmental Mesonet (IEM) RAOB archive

    #convert date and time to datetime object
    dt = datetime(year=year,month=month,day=day,hour=hour)
    
    #convert datetime object to string to add into the IEM url
    t = dt.strftime('%Y%m%d%H%M')
    
    #define the url
    url = f"https://mesonet.agron.iastate.edu/json/raob.py?ts={t}&station={station}"
    
    #read the json sounding data using pandas
    json = pd.read_json(url)
    
    #convert the json sounding to a pandas dataframe
    df = pd.json_normalize(json.profiles[0],'profile',['station','valid'])
    
    #convert the "valid" variable to a datetime object
    df['valid'] = pd.to_datetime(df['valid'])
    print(df)

    #second block
    ### create a new dataframe for just temperature and dewpoint ###

    #first remove any rows where there is no data
    df_temp = df.dropna(how='any',subset=['tmpc','dwpc'])
    #next just keep pressure, height, temperature, and dewpoint
    
    
    ### create a new dataframe for just winds ###
    #why not just use the data frame and define what data we need? I just created two copies and dropped the missing data
    #first remove any rows where there is no data
    df_wind = df.dropna()
    
    #next just keep pressure, height, temperature, and dewpoint
    print(df_wind)

    #third block
    pressure = np.array(df_temp['pres']) * units('hectopascals')
    height = np.array(df_temp['hght']) * units('meters')
    temperature = np.array(df_temp['tmpc']) * units('degC')
    dewpoint = np.array(df_temp['dwpc']) * units('degC')

    #forth block
    wind_pressure = np.array(df_temp['pres']) * units('hectopascals')
    wind_height = np.array(df_temp['hght']) * units('meters')
    wind_speed = np.array(df_temp['sknt']) * units('knots')
    wind_direction = np.array(df_temp['drct']) * units('degrees')

    #fifth Block
    u,v = mpcalc.wind_components(wind_speed,wind_direction)

    #create skew-t figure
    fig = plt.figure(figsize=(11, 8), dpi=150,facecolor='w')
    skew = SkewT(fig, rotation=45)
    
    #plot temperature in red and dewpoint in green
    skew.plot(pressure, temperature, 'r',lw=4)
    skew.plot(pressure, dewpoint, 'g',lw=4)
    
    #create axes labels
    plt.xlabel('TEMPERATURE (\N{degree sign}C)',fontsize=15)
    plt.ylabel('PRESSURE (hPa)',fontsize=15)
    
    #add in typical lines
    skew.plot_dry_adiabats()
    skew.plot_moist_adiabats()
    skew.plot_mixing_lines()
    
    #plot winds 
    #only plot every other wind barb so it's not too busy
    #(y_clip_radius keeps barbs from plotting outside of skew-t)
    skew.plot_barbs(pressure[::2],u[::2],v[::2],y_clip_radius=0)
    
    #add title for date and location
    plt.title(f'{station}\n%04i-%02i-%02i %02iZ'%(year,month,day,hour), fontsize=20)
    
    #save figure
    fig.tight_layout()
    plt.savefig(f'{station}_%04i%02i%02i_%02i.png'%(year,month,day,hour))