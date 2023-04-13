import pymongo
import json
import pytz
import datetime
from bson.json_util import dumps, loads
from bson import ObjectId, Binary, Code, json_util
import copy
import constants

myclient1 = pymongo.MongoClient("mongodb://localhost:27017/")
# myclient1  = pymongo.MongoClient("mongodb://cyronics:cipl1234@35.184.20.184:27017/Anzen_1_0?authSource=Anzen_3_0")
mydb1 = myclient1['TWIN']
import pyqrcode
# import png
from pyqrcode import QRCode
import string
import random
import uuid
import mail_api

user_collection = mydb1['users']

from random import randint
import datetime
import otp_operations

import fcm_message


def verify_credentials(data):
    myquery = {"phone": str(data["phone"])}
    mydoc = user_collection.find(myquery, {'password': True, "_id": False})
    credentials = []
    for x in mydoc:
        credentials.append(x)
    if len(credentials) > 0:
        if data["password"] == credentials[0]["password"]:
            return 2
        else:
            return 0
    else:
        return 0


def return_credentials(phone):
    myquery = {"phone": str(phone)}
    mydoc = user_collection.find(myquery, {'name': True, 'password': True, 'role': True, "_id": False})
    credentials = []
    for x in mydoc:
        credentials.append(x)
    if len(credentials) > 0:
        return credentials[0]
    else:
        return 0
