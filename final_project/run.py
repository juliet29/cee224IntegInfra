from datetime import datetime
import pandas as pd
import json
from flask import jsonify
import pickle 

from traveltimepy import Coordinates, TravelTimeSdk, PublicTransport, Driving, Walking, Cycling, errors
from math import radians, cos, sin, asin, sqrt
from collections import OrderedDict




APP_KEY = '33086bf72ecbc51c2bf727821798a43e'
APP_ID = '08be32c3'
SDK = TravelTimeSdk(app_id=APP_ID, api_key=APP_KEY, limit_per_host=4)
MAX_TIME = 60*30 # (30 mins )

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
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    
    return(c * r)

def get_district_coordinates(city, sdk=SDK):
    path = "constants/districts.csv"
    districts_df = pd.read_csv(path)
    districts = list(districts_df[city])
    coords = {}

    for district in districts:
        try:
            results = sdk.geocoding(query=f"{district}, {city}", limit=1)
            coords[district] = results.features[0].geometry.coordinates
        except IndexError:
            coords[district] = (0,0)

    df = pd.DataFrame.from_dict(coords, orient="index", columns=["Longitude", "Latitude"])
    df.to_csv(f"{city}/coords.csv")

    return df


def calc_max_dist(lat, long, name, city, sdk=SDK, max_time=MAX_TIME):
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
            # save results for future graphing 
            pickle.dump(shell, open(f"{city}/shells/{name}.p", "wb"))
            # calculate maximum distance from the center point 
            max_d = max([distance(lat, i.lat, long, i.lng) for i in shell]) # km 
            
        except errors.ApiError: 
            print(lat, long)
            max_d = 0
            pass

        vals[f"{mode().type}"] =  max_d  

    return vals



def main(city):
    # get the coordinates for each district 
    df_coords = get_district_coordinates(city, sdk=SDK)

    # get the max distance possible traveling from each district coordinate
    res = df_coords.apply(lambda row: calc_max_dist(row.Latitude, row.Longitude, row.name, city=city), axis=1)

    # clean up results into csv
    df_maxdist = pd.DataFrame(res)
    a = df_maxdist.apply(lambda row: [i for i in OrderedDict(row)[0].values()], axis=1).values
    df_fin = pd.DataFrame([i for i in a], columns=df_maxdist.iloc[0].values[0].keys(), index=df_maxdist.index)
    df_fin.to_csv(f"{city}/data.csv")

    return True 




if __name__ == '__main__':
    # main("singapore")
    main("san francisco")
