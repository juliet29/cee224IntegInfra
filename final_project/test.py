from datetime import datetime
import pandas as pd
import json
from flask import jsonify
import pickle 

from traveltimepy import Coordinates, TravelTimeSdk, PublicTransport, Driving, Walking, Cycling, errors
from math import radians, cos, sin, asin, sqrt

def distance(lat1, lat2, lon1, lon2):
    lon1 = radians(lon1)
    lon2 = radians(lon2)
    lat1 = radians(lat1)
    lat2 = radians(lat2)
      
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
 
    c = 2 * asin(sqrt(a))
    
    # Radius of earth in kilometers. Use 3956 for miles
    r = 6371
      
    # calculate the result
    return(c * r)


APP_KEY = '33086bf72ecbc51c2bf727821798a43e'
APP_ID = '08be32c3'

sdk = TravelTimeSdk(app_id=APP_ID, api_key=APP_KEY, limit_per_host=4)


df = pd.read_csv("constants/singapore_coords.csv", index_col=0)
# long = df.iloc[0]["Longitude"]
# lat = df.iloc[0]["Latitude"]
max_time = 60*30 # (30 mins )

# sing_vals = {}
# district_name=df.iloc[0].name
# sing_vals[district_name] = {}

def calc_max_dist(lat, long):
    vals = {}
    for mode in [PublicTransport, Driving, Walking, Cycling]:
        try:
            results = sdk.time_map(
                coordinates=[Coordinates(lat=lat, lng=long)],
                departure_time=datetime.now(),
                transportation=mode(),
                travel_time = max_time
            )
            shell = results[0].shapes[0].shell
            max_d = max([distance(lat, i.lat, long, i.lng) for i in shell]) # km 
        except errors.ApiError: 
            print(lat, long)
            max_d = 0
            pass

        vals[f"{mode().type}"] =  max_d 

    return vals

res = df.apply(lambda row: calc_max_dist(row.Latitude, row.Longitude), axis=1)

pickle.dump(res, open("constants/singapore_mdists.p", "wb"))

