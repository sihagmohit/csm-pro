import pymongo
from datetime import date, datetime
import time
import json
from bson.json_util import dumps, loads
from bson import ObjectId, Binary, Code, json_util

myclient1 = pymongo.MongoClient("mongodb://localhost:27017/")
mydb1 = myclient1['bin']
test_data = mydb1['bin']


def bin_percentage(socketio):
    data = {
        "Empty Trolley Storage": [0, 0],
        "Empty Bin Storage": [0, 0],
        "Production Area": [0, 0],
        "FG Storage": [0, 0],
        "Dispatch Preparation Area": [0, 0],
        "In-Transit": [0, 0]}
    total = test_data.find().count()
    for key in data:
        temp = test_data.find({"bins.current_location": str(key)}).count()
        percent = (temp / total) * 100
        data[key][0] = temp
        data[key][1] = percent
    socketio.emit("percentage_table", data)


def bin_updator(data):
    bin_no = data["bins"]["bin_number"]
    check = json.loads(dumps(test_data.find({"bins.bin_number": bin_no})))
    print(check, bin_no)
    if check != []:
        ids = check[0]["_id"]["$oid"]
        old_data_dict = {}
        old_data_dict["rfid_number"] = check[0]["bins"]["rfid_number"]
        old_data_dict["current_location"] = check[0]["bins"]["current_location"]
        old_data_dict["order_details"] = check[0]["bins"]["order_details"]
        old_data_dict["movement"] = check[0]["bins"]["movement"]
        test_data.update({"_id": ObjectId(ids)}, {'$push': {"bins.history": old_data_dict}})

        test_data.update({"_id": ObjectId(ids)}, {'$set': {"bins.rfid_number": data["bins"]["rfid_number"],
                                                           "bins.bin_number": data["bins"]["bin_number"],
                                                           "bins.current_location": data["bins"]["current_location"],
                                                           "bins.movement.time_stamp": data["bins"]["movement"][
                                                               "time_stamp"],
                                                           "bins.movement.gate": data["bins"]["movement"]["gate"],
                                                           "bins.order_details.order_no": data["bins"]["order_details"][
                                                               "order_no"],
                                                           "bins.order_details.invoice_no":
                                                               data["bins"]["order_details"]["invoice_no"],
                                                           "bins.order_details.material_code":
                                                               data["bins"]["order_details"]["material_code"], }})
        return "updated"
    else:
        data["bins"]["history"] = []
        test_data.insert_one(data)
        return "inserted"


def table_data(area):
    data_for_frontend = []
    data = test_data.find({"bins.current_location": area})
    for area_data in data:
        dict1 = {}
        dict1["bin_number"] = area_data["bins"]["bin_number"]
        dict1["rf_id"] = area_data["bins"]["rfid_number"]
        dict1["order_id"] = area_data["bins"]["order_details"]["order_no"]
        dict1["invoice_no"] = area_data["bins"]["order_details"]["invoice_no"]
        dict1["material_code"] = area_data["bins"]["order_details"]["material_code"]
        data_for_frontend.append(dict1)
    return data_for_frontend


def history_bin(bin):
    data_for_frontend = []
    data = test_data.find_one({"bins.bin_number": bin})
    for area_data in data["bins"]["history"]:
        dict1 = {}
        dict1["bin_number"] = bin
        dict1["rf_id"] = area_data["rfid_number"]
        dict1["order_id"] = area_data["order_details"]["order_no"]
        dict1["invoice_no"] = area_data["order_details"]["invoice_no"]
        dict1["material_code"] = area_data["order_details"]["material_code"]
        data_for_frontend.append(dict1)
    return data_for_frontend


def history_gate(gate):
    data_for_frontend = []
    data = test_data.find({"bins.movement.gate": gate})
    for area_data in data:
        dict1 = {}
        dict1["bin_number"] = area_data["bins"]["bin_number"]
        dict1["rf_id"] = area_data["bins"]["rfid_number"]
        dict1["order_id"] = area_data["bins"]["order_details"]["order_no"]
        dict1["invoice_no"] = area_data["bins"]["order_details"]["invoice_no"]
        dict1["material_code"] = area_data["bins"]["order_details"]["material_code"]
        data_for_frontend.append(dict1)
    return data_for_frontend


def all_data_hist(rd):
    print(rd)
    data_for_frontend = []
    data = test_data.find()
    for area_data in data:
        dict1 = {}
        dict1["bin_number"] = area_data["bins"]["bin_number"]
        dict1["rf_id"] = area_data["bins"]["rfid_number"]
        dict1["order_id"] = area_data["bins"]["order_details"]["order_no"]
        dict1["invoice_no"] = area_data["bins"]["order_details"]["invoice_no"]
        dict1["material_code"] = area_data["bins"]["order_details"]["material_code"]
        data_for_frontend.append(dict1)
    return data_for_frontend
