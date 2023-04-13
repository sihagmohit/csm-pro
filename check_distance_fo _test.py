
import pymongo


myclient1 = pymongo.MongoClient("mongodb://localhost:27017/") #,connectTimeoutMS=30000, socketTimeoutMS=None, socketKeepAlive=True, connect=False,                     maxPoolsize=1)
# string1 = 'mongodb://cipl:cipl123@koelgpsdatabase-shard-00-00.q0jol.mongodb.net:27017,koelgpsdatabase-shard-00-01.q0jol.mongodb.net:27017,koelgpsdatabase-shard-00-02.q0jol.mongodb.net:27017/test?replicaSet=atlas-115qei-shard-0&ssl=true&authSource=admin'
# myclient1 = pymongo.MongoClient(string1)

# myclient1  = pymongo.MongoClient("mongodb://cyronics:cipl1234@35.184.20.184:27017/Anzen_1_0?authSource=Anzen_1_0")
mydb1 = myclient1['Anzen_1_0']
sign_up_collection = mydb1['Sign Up Questions']


user_collection = mydb1['Users']
visitors_collection = mydb1['Visitors']
questions_collection = mydb1['Contact Us']
settings_collection = mydb1['Settings']
all_questions_collection = mydb1['all_question']



mydb2 = myclient1['KOEL_GPS']   #KOEL_GPS29july
trips = mydb2["trips"]  #_temp
param_data_col = mydb2["param_data"]
cron_collection = mydb2["cron_time"]
high_speed = mydb2["HIGH_SPEED"]
ip_data_col = mydb2["ip_data"]
temp_gps_data=mydb2["gps_data"]
forklift=mydb2['forklift_assets']
shift_records=mydb2['Shift_records']



def check_distance():
    data = trips.find({"STATUS":"LIVE"},{"_id":0,"DATA POINTS":1})
    for i in data:
        for j in range(0,len(i["DATA POINTS"])):
            print("Distance",i["DATA POINTS"][j]['distance'])

check_distance()