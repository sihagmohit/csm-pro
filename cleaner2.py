import pandas
import numpy as np
import pymongo
import json

myclient1 = pymongo.MongoClient("mongodb://localhost:27017/")

mydb1 = myclient1['TWIN']
users_collection = mydb1['users']

users_collection.drop()

fields1 = {"phone": "7620521626",
            "password": "nikita-123",
            "role": "Super-Admin",
            "name": "Nikita Dhande"
              }

users_collection.insert_one(fields1)

fields2 = {"phone": "9922998224",
            "password": "siddharth1!",
            "role": "Admin",
            "name": "Siddharth Bhonge"
              }

users_collection.insert_one(fields2)


fields3 = {"phone": "8275906923",
            "password": "adityap@11",
            "role": "Customer",
            "name": "Aditya Phatak"
              }

users_collection.insert_one(fields3)

fields4 = {"phone": "9898989898",
            "password": "twin@123",
            "role": "Super-Admin",
            "name": "Twin Engineers"
              }

users_collection.insert_one(fields4)

fields5 = {"phone": "7066822892",
            "password": "vatsalr@123",
            "role": "Super-Admin",
            "name": "Cyronics Team"
              }

users_collection.insert_one(fields5)































































































