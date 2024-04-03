#
#
from siphon.simplewebservice.iastate import IAStateUpperAir
from metpy.io import add_station_lat_lon
import datetime
import pandas

# get_raobs 
# returns a pandas dataframe with RAOBs
# input = dt (a datetime object)
def get_raobs(dt: datetime.datetime) -> pandas.DataFrame:
    #collect data
    data = IAStateUpperAir().request_all_data(dt)
    # positions
    data = add_station_lat_lon(data)
    return data

# select_press
# returns a pandas dataframe with RAOB observations at the specified pressure level
# input = data (a RAOB pandas dataframe)
#       = press_lev (the pressure level requested in hPa)
def select_press(data: pandas.DataFrame, press_lev) -> pandas.DataFrame:
    #use loc to grab rows
    data = data.loc[data.pressure==press_lev]
    return data

