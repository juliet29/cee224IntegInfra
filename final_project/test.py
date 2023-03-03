from datetime import datetime

from traveltimepy import Driving, Coordinates, TravelTimeSdk, PublicTransport


APP_KEY = '33086bf72ecbc51c2bf727821798a43e'
APP_ID = '08be32c3'

sdk = TravelTimeSdk(app_id=APP_ID, api_key=APP_KEY, limit_per_host=4)

# results = sdk.time_map(
#     coordinates=[Coordinates(lat=51.507609, lng=-0.128315), Coordinates(lat=51.517609, lng=-0.138315)],
#     departure_time=datetime.now(),
#     transportation=PublicTransport(),
#     travel_time = 900
# )

results = sdk.geocoding(query='Ang Mo Kio', limit=1)

# get coordinates 
results.features[0].geometry.coordinates

print(results)