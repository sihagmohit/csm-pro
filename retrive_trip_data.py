import pymongo
import json
import bson
from bson.json_util import dumps,loads
from bson import ObjectId, Binary, Code,json_util
from datetime import datetime


myclient1 = pymongo.MongoClient("mongodb://localhost:27017/")
mydb2 = myclient1['ppap_fleet_database']
trip_data = mydb2['trip_collection']


def get_all_trips():
    all_trips=trip_data.find({},{"_id":False,"daily_trips.order_number":1,"daily_trips.color":1,"daily_trips.completion_state":1,"daily_trips.vehicle_details.partner_company":1,"daily_trips.vehicle_details.number":1})
    all_trips_list=[]
    for i in all_trips:
        all_trips_list.append(i['daily_trips'])
    print(all_trips_list)
    return json.dumps(all_trips_list)

def get_trip_data(dt):
    myquery={"daily_trips.vehicle_details.number":dt['vehicle_number']}
    trip_data_list=[]
    trip=trip_data.find(myquery,{"_id":False,"daily_trips.capacity":1,"daily_trips.order_number":1,"daily_trips.material_details":1,"daily_trips.vehicle_details":1,"daily_trips.driver_details":1,"daily_trips.stops":1,"daily_trips.color":1,"daily_trips.start_point":1,"daily_trips.end_point":1,"daily_trips.route_kml":1})
    for i in trip:
        trip_data_list.append(i['daily_trips'])
    print(trip_data_list)
    return json.dumps(trip_data_list)


