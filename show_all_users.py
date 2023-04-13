import pymongo

from pprint import pprint
myclient1 = pymongo.MongoClient("mongodb://localhost:27017/")
# myclient1  = pymongo.MongoClient("mongodb://cyronics:cipl1234@35.184.20.184:27017/Anzen_1_0?authSource=Anzen_1_0")
mydb1 = myclient1['Anzen_1_0']
sign_up_collection = mydb1['Sign Up Questions']

user_collection = mydb1['Users']
visitors_collection = mydb1['Visitors']
questions_collection = mydb1['Contact Us']
settings_collection = mydb1['Settings']
all_questions_collection = mydb1['all_question']


usr = user_collection.find({},{"phone":True, "o_id":True , "name":True,"role":True })

for u in usr:
    print(u)