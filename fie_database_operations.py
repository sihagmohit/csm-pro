import re
import time
from pprint import pprint

import numpy as np
import pymongo
import json
import pytz
import datetime
from bson.json_util import dumps, loads
from bson import ObjectId, Binary, Code, json_util
import copy
import constants
from datetime import datetime, timedelta
from bson.objectid import ObjectId

myclient1 = pymongo.MongoClient("mongodb://localhost:27017/")
# myclient1  = pymongo.MongoClient("mongodb://cyronics:cipl1234@35.184.20.184:27017/Anzen_1_0?authSource=Anzen_1_0")
mydb1 = myclient1['fie_data']
mydb2 = myclient1['fie_backup_data']
sign_up_collection = mydb1['Sign Up Questions']
# import png
import string
import random

# import uuid
# import mail_api

MachineryComponents = mydb1['MachineryComponents']
Machine_Stocks = mydb1['Machine_Stocks']

sales_order = mydb1['sales_order']
stock = mydb1['stock']
parts = mydb1['parts']
machinery_components = mydb1['machinery_components']
wip = mydb1['wip']
vendor_details = mydb1['vendor_details']
sync_log = mydb1['sync_log']
part_production_plan = mydb1["part_production_plan"]
production_plan = mydb1["production_plan"]
gap_analysis = mydb1["gap_analysis"]

# ---------------------temp backup data collection--------------------------------------
machinery_components_temp = mydb1['machinery_components_temp']
sales_order_temp = mydb1['sales_order_temp']
stock_temp = mydb1['stock_temp']
parts_temp = mydb1['parts_temp']
wip_temp = mydb1['wip_temp_temp']
vendor_details_temp = mydb1['vendor_details_temp']
part_component = mydb1["part_component"]

gap_calculator =mydb1["gap_calculator"]


# --------------------reset data collection------------------------------------
reset_data_gap = mydb1["reset_data_gap"]
reset_data_production_plan = mydb1["reset_data_production_plan"]
reset_data_part_prduction_plan =  mydb1["reset_data_production_plan"]


# ---------------------10 documents backup data collection--------------------------------------
machinery_components_backup = mydb2['machinery_components_backup']
sales_order_backup = mydb2['sales_order_backup']
stock_backup = mydb2['stock_backup']
# parts_backup = mydb2['parts_backup']
wip_backup = mydb2['wip_backup']
vendor_details_backup = mydb2['vendor_details_backup']
machinery_components_backup1 = mydb2['machinery_components_backup1']



# -----------------------------------------------------------------------------------------------
# ============================ ADDING DATA BY JSON =============================================
# -----------------------------------------------------------------------------------------------

# ----------------------------- sales_order_data ----------------------------------
def sales_order_data(data):
    try:
        record = sales_order.find({}, {'_id': False})
        for i in record:
            sales_order_temp.insert(i)
    except:
        pass

    try:
        sales_order.drop()
        # writedata = data['data']
        for i in data['pending_so']:
        # for i in writedata['pending_so']:
            i['timestamp'] = datetime.now()
            # i['avl_qty'] = re.sub("\sNo.", "", i['avl_qty'])
            i['voucher_date'] = datetime.strptime(i['voucher_date'], '%d-%b-%y')
            sales_order.insert(i)
        production_plan_function()
        record = {"timestamp": datetime.now(), "collection_name": "sales_order", "status": "Sucess"}
        sync_log.insert(record)
    except:
        sales_order.drop()
        record = sales_order_temp.find({})
        for i in record:
            sales_order.insert(i)
        sales_order_temp.drop()
        record = {"timestamp": datetime.now(), "collection_name": "sales_order", "status": "Failed"}
        sync_log.insert(record)


def production_plan_function():
    production_plan.drop()
    multiply_reord = sales_order.distinct('machine_name')
    # print(multiply_reord)
    for index in range(0, len(multiply_reord)):
        # print(multiply_reord[index])
        # ===============================data retrive from sales order to find total requirement =======================
        sum_sales_order = sales_order.aggregate([{"$match": {"machine_name": multiply_reord[index]}},
                                                 {"$group": {
                                                     "_id": "$machine_name",
                                                     "Total": {"$sum": {"$toInt": "$avl_qty"}}
                                                 }}
                                                 ])

        for i in sum_sales_order:
            # print(i)
            production_plan.insert_one(i)
            if "_id" in i:
                del i["_id"]

    # coll_data = production_plan.find({},{"_id": False})   # reset collection create
    # for i in coll_data:
    #     reset_data_production_plan.insert(i)

    record = {"timestamp": datetime.now(), "collection_name": "production_plan", "status": "Sucess"}
    sync_log.insert(record)



def create_part_plan_data():
    check = machinery_components.find({}).count()
    if check == 0:
        sales_order.drop()
        production_plan.drop()
        return 0
    else:
        # print("----------")
        part_production_plan.drop()
        sum_sales_order = production_plan.find({})
        for rec in sum_sales_order:
            # print(rec)
            data_set = machinery_components.find({'machine_name': rec['_id']}, {"_id": False})
            for i in data_set:
                try:
                    # data_length = i['machinery_components'] #keyerror
                    # for n in range(0, len(i['machinery_components'])):
                        data = part_component.aggregate([{"$match": {"machine_name": i["machine_name"],
                                                                     # "child": i['machinery_components'][n]["assembly_name"]
                                                                     }},
                                                         {"$project": {
                                                             "_id": 0,
                                                             "machine_name": i["machine_name"],
                                                             "assembly_name": "$child",
                                                             "required_machine": {"$multiply": "$bom_qty"},
                                                             "total_required": {"$multiply": ["$bom_qty", rec['Total']]},
                                                             "avl_quantity": {"$sum": "$avl_qty"}
                                                         }}
                                                         ])

                        # print(data)
                        unique = list({each['assembly_name']: each for each in data}.values())
                        for j in unique:
                            # print(j)
                            part_production_plan.insert_one(j)
                            if "_id" in j:
                                del j["_id"]
                        part_production_plan.remove({"machine_name":i["machine_name"] , "assembly_name": i["machine_name"]})
                        # part_production_plan.ensureIndex({"machine_name": 1, "assembly_name": 1},
                        #                                      {"unique": True, "dropDups": True})


                except:
                   pass
    reset_data_part_prduction_plan.drop()
    data_coll = part_production_plan.find({},{"_id": False})   # reset collection create
    for i in data_coll:
        reset_data_part_prduction_plan.insert_one(i)

    record = {"timestamp": datetime.now(), "collection_name": "part_production_plan", "status": "Sucess"}
    sync_log.insert_one(record)


# create_part_plan_data()


# ----------------------------- stocks_data ----------------------------------


def stocks_data(data):
    try:
        record = stock.find({}, {'_id': False})
        for i in record:
            stock_temp.insert(i)
    except:
        pass

    try:
        stock.drop()
        # writedata = data['data']
        for i in data['machine_stocks']:
            i['timestamp'] = datetime.now()
            # print(i)
            stock.insert(i)
        record = {"timestamp": datetime.now(), "collection_name": "stock", "status": "Sucess"}
        sync_log.insert(record)
    except:
        stock.drop()
        record = stock_temp.find({})
        for i in record:
            stock.insert(i)
        stock_temp.drop()
        record = {"timestamp": datetime.now(), "collection_name": "stock", "status": "Failed"}
        sync_log.insert(record)



# ----------------------------- machinery_components_data ----------------------------------

def machinery_components_data(data):
    try:
        record = machinery_components.find({}, {"_id": False})
        for i in record:
            machinery_components_temp.insert(i)
    except:
        pass

    try:
        machinery_components.drop()
        # writedata = data['data']
        unique = list({each["machine_name"]: each for each in data['machinery_components']}.values())
        for i in unique:
            i['timestamp'] = datetime.now()
            machinery_components.insert_one(i)

        record = {"timestamp": datetime.now(), "collection_name": "machinery_components", "status": "Sucess"}
        sync_log.insert(record)
    except:
        machinery_components.drop()
        record = machinery_components_temp.find({})
        for i in record:
            machinery_components.insert(i)
        machinery_components_temp.drop()
        record = {"timestamp": datetime.now(), "collection_name": "machinery_components", "status": "Failed"}
        sync_log.insert(record)


def new_collection(data):
    part_component.drop()
    # print(data)

    # f = open("/home/cipl/Documents/cipl_projects/new fie/fie/json_file/machinery_component.json", 'r')
    # data = json.load(f)
    # writedata = data['data']
    unique = list({each["machine_name"]: each for each in data['machinery_components']}.values())
    for i in unique:
        parse_bom([i], "None", "")
        # print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")


def parse_bom(new_list, parent, machine_n):
    machine_name = machine_n
    for comp in new_list:
        temp_component = {}
        if comp["bom_level"] == 1:
            machine_name = comp["machine_name"]
        else:
            pass
        if "machinery_components" in comp:
            temp_component["parent"] = parent
            temp_component["machine_name"] = machine_name
            temp_component["bom_level"] = comp["bom_level"]
            temp_component["avl_qty"] = comp["avl_qty"]
            temp_component["bom_qty"] = comp["bom_qty"]

            print("--------------------------------------------------------")
            print("Parent:   ", parent)
            print("machine_name : ", temp_component["machine_name"])
            print("BOM Level : ", str(comp["bom_level"]))
            if "machine_name" in comp:
                temp_component["child"] = comp["machine_name"]
                print("Child : ", comp["machine_name"])
                new_parent = comp["machine_name"]
            elif "assembly_name" in comp:
                temp_component["child"] = comp["assembly_name"]
                print("Child : ", comp["assembly_name"])
                new_parent = comp["assembly_name"]
            else:
                temp_component["child"] = comp["spare_name"]
                print("Child : ", comp["spare_name"])
                new_parent = comp["spare_name"]

            print("BOM Qty : ", str(comp["bom_qty"]))
            print("Avl Qty : ", str(comp["avl_qty"]))

            part_component.insert_one(temp_component)
            parse_bom(comp["machinery_components"], new_parent, machine_name)

        else:
            temp_component["bom_level"] = comp["bom_level"]
            temp_component["parent"] = parent
            temp_component["machine_name"] = machine_name
            temp_component["avl_qty"] = comp["avl_qty"]
            temp_component["bom_qty"] = comp["bom_qty"]

            print("--------------------------------------------------------")
            print("Parent:   ", parent)
            print("machine_name : ", temp_component["machine_name"])
            print("BOM Level : ", str(comp["bom_level"]))
            if "machine_name" in comp:
                temp_component["child"] = comp["machine_name"]
                print("Child : ", comp["machine_name"])

            elif "assembly_name" in comp:
                temp_component["child"] = comp["assembly_name"]
                print("Child : ", comp["assembly_name"])

            else:
                temp_component["child"] = comp["spare_name"]
                print("Child : ", comp["spare_name"])

            print("BOM Qty : ", str(comp["bom_qty"]))
            print("Avl Qty : ", str(comp["avl_qty"]))
            part_component.insert_one(temp_component)


# ----------------------------- wip_stocks_data ----------------------------------

def find_primary_item():
    data ={}
    meta =[]
    doc = machinery_components.find({},{"_id":0})
    for i in doc:
        meta.append(i)
        data['machinery_components'] = meta
    # print(data)


    prime_item = []
    def check_compo(key, value):
        if key == 'machinery_components':
            for i in range(len(value)):
                if 'Primary_Item' in value[i]:
                    primary_items = value[i]['Primary_Item']
                    try:
                        spare_item = value[i]['spare_name']
                    except:
                        spare_item = ""
                        pass
                    # print(primary_items)
                    prime_item.append({"primary_items": primary_items, 'spare_item': spare_item})

                for key1, value2 in value[i].items():
                    check_compo(key1, value2)

    for key, value in data.items():
        check_compo(key, value)
    print(prime_item)
    return prime_item

# find_primary_item()

def final_gap_cal():

    prime = gap_analysis.find({}, {"_id": 0}).distinct("primary_item")
    # print(prime)
    if prime != []:
        prime.pop(0)
        # print(prime)
        for i in range(0, len(prime)):
            # print(prime[i])
            sum_sales_order = gap_analysis.aggregate([{"$match": {"primary_item": prime[i]}},
                                                        {"$group": {
                                                            "_id": "$machine",
                                                            "live_sales": {"$first": {"$toInt": "$live_sales"}},
                                                            "actual_required": {"$first": {"$toInt": "$actual_required"}},
                                                            "wip_qty": {"$sum": {"$toInt": "$wip_qty"}},
                                                            "finish_stock": {"$sum": {"$toInt": "$finish_stock"}},
                                                            "issued_qty": {"$sum": {"$toInt": "$issued_qty"}},
                                                            # "final_order": {"$sum": {"$toInt": "$final_order"}},
                                                            "supplier_list": {"$push": "$supplier_list"}
                                                            # "Cumulative_data": {"$first": {"$toInt": "$Cumulative_data"}},
                                                        }}, {"$project": {"_id": 0,
                                                                          "machine": "$_id",
                                                                          "parts": prime[i],
                                                                          "live_sales": "$live_sales",
                                                                          "production": {"$toInt": "0"},
                                                                          "actual_required": '$actual_required',
                                                                          "wip_qty": "$wip_qty",
                                                                          "finish_stock": "$finish_stock",
                                                                          "issued_qty": "$issued_qty",
                                                                          "final_order": {"$subtract": [{"$toInt":"$actual_required"},
                                                                                                        {"$add": [
                                                                                                            "$wip_qty",
                                                                                                            "$finish_stock",
                                                                                                            "$issued_qty"
                                                                                                            ]}]},
                                                                          "supplier_list": {
                                                                              "$reduce": {
                                                                                  "input": "$supplier_list",
                                                                                  "initialValue": [],
                                                                                  "in": {"$concatArrays": ["$$value",
                                                                                                           "$$this"]
                                                                                         }
                                                                              }
                                                                          },
                                                                          # "Cumulative_data": "$Cumulative_data",
                                                                          "primary_item": '',

                                                                          }}
                                                        ])

            for j in sum_sales_order:
                print(j)
                gap_analysis.insert_one(j)

        for k in range(0, len(prime)):
            # print(prime[k]))
            gap_analysis.remove({"primary_item":prime[k]})


# final_gap_cal()
# final_gap_cal()
def wip_stocks_data(data):
    # print(data)
    try:
        record = wip.find({}, {'_id': False})
        for i in record:
            wip_temp.insert(i)
    except:
        pass

    try:
        wip.drop()
        # writedata = data['data']
        # print(writedata)

        # unique = list({each["part_name"]: each for each in data['wip_stocks']}.values())
        for i in data['wip_stocks']:
            i['timestamp'] = datetime.now()
            # print(i)
            wip.insert(i)
        record = {"timestamp": datetime.now(), "collection_name": "wip", "status": "Sucess"}
        sync_log.insert(record)
    except:
        wip.drop()
        record = wip_temp.find({})
        for i in record:
            wip.insert(i)
        wip_temp.drop()
        record = {"timestamp": datetime.now(), "collection_name": "wip", "status": "Failed"}
        sync_log.insert(record)





def check_sales_data():
    check = sales_order.find({}).count()
    if check == 0:
        wip.drop()
        gap_analysis.drop()
        return 0
    else:
        gap_analysis.drop()
        records = []
        parts_data = []
        check = part_production_plan.find({}, {"_id": False}).distinct("assembly_name")
        # print(check)
        for x in range(0, len(check)):
            data = part_production_plan.find({"assembly_name": check[x]}, {"_id": False})
            for index in data:
                get_data = {}
                get_data["parts"] = index['assembly_name']
                get_data["live_sales"] = index['total_required']
                get_data["production_plan"] = 0
                get_data["actual_required"] = get_data["production_plan"] + get_data["live_sales"]
                get_data["wip_qty"] = 0
                get_data["finish_stock"] = 0
                get_data["issued_qty"] = 0
                get_data["supplier_list"] =[]
                get_data["primary_item"] = ''
                # for supllier_data in wip_data:

                wip_data = wip.find({"part_name": index["assembly_name"]},
                                    {"_id": False})  # .limit(100) index['assembly_name']
                for list_data in wip_data:
                    wip_details = str(list_data["supplier_name"]) + ':' + str(list_data['quantity'])
                    get_data["supplier_list"].append(wip_details)

                    wip_temp = wip.aggregate([{"$match": {"part_name": index['assembly_name']}},
                                              {"$group": {
                                                  "_id": index['assembly_name'],
                                                  "sum_wip": {"$sum": {
                                                      "$cond": [
                                                          {
                                                              "$in": [
                                                                  "$supplier_name",
                                                                  [
                                                                      "PB FINISH",
                                                                      "PB ASSEMBLY"
                                                                  ]
                                                              ]
                                                          },
                                                          0,
                                                          "$quantity"
                                                      ],
                                                  }

                                                      # {"$toInt": "$quantity"}#
                                                  },
                                                  "sum_finish": {"$sum": {
                                                      "$cond": [
                                                          {
                                                              "$in": [
                                                                  "$supplier_name",
                                                                  [
                                                                      "PB FINISH"
                                                                  ]
                                                              ]
                                                          },
                                                          "$quantity",
                                                          0,
                                                      ],
                                                  }

                                                      # {"$toInt": "$quantity"}#
                                                  },
                                                  "sum_assembly": {"$sum": {
                                                      "$cond": [
                                                          {
                                                              "$in": [
                                                                  "$supplier_name",
                                                                  [
                                                                      "PB ASSEMBLY"
                                                                  ]
                                                              ]
                                                          },
                                                          "$quantity",
                                                          0,
                                                      ],
                                                  }

                                                      # {"$toInt": "$quantity"}#
                                                  }
                                                  # {"$toInt": "$quantity"}#
                                              }}
                                              ])
                    # unique = list({each["machine_name"]: each for each in wip_temp['_id']}.values())
                    for i in wip_temp:

                        # print(i)
                        get_data["wip_qty"] = i["sum_wip"]
                        get_data["finish_stock"] = i["sum_finish"]
                        get_data["issued_qty"] = i["sum_assembly"]

                get_data["final_order"] = get_data["actual_required"] - (get_data["wip_qty"]) - (get_data[
                    "finish_stock"]) - (get_data["issued_qty"])
                # print(get_data)
                records.append(get_data)

                if "_id" in get_data:
                    del get_data["_id"]

                if index['assembly_name'] not in parts_data:
                    # print("insetion")
                    parts_data.append(index['assembly_name'])
                    print(get_data)
                    gap_analysis.insert_one(get_data)  # insert data in mobgodb
                else:
                    gap_analysis.update_one({"parts": index['assembly_name']},
                                            {"$inc": {"live_sales": get_data[
                                                'live_sales']}})  # update the mongodb data which are repaet
                    gap_analysis.update_one({"parts": index['assembly_name']},
                                            {"$inc": {
                                                "actual_required": get_data["production_plan"] + get_data['live_sales']}})

                    update_data = gap_analysis.find({"parts": index['assembly_name']}, {"_id": 0})
                    for change in update_data:
                        gap_analysis.update_one({"parts": index['assembly_name']},
                                                {"$set": {"final_order": change["actual_required"] - change["wip_qty"] -
                                                                         change["finish_stock"] - change["issued_qty"]}})
    primary_item = find_primary_item()
    for j in primary_item:
        print(j['spare_item'])
        gap_analysis.update_one({"parts": j['spare_item']},
                                {"$set": {'primary_item': j['primary_items']}})

    final_gap_cal()



    try:
        reset_data_gap.drop()
        data_coll = gap_analysis.find({},{"_id": False}) # reset collection create
        for i in data_coll:
            reset_data_gap.insert(i)
    except:
        pass
    record = {"timestamp": datetime.now(), "collection_name": "gap_analysis", "status": "Failed"}
    sync_log.insert(record)


# check_sales_data()

# ----------------------------- vendor_details_data ----------------------------------

def vendor_details_data(data):
    try:
        record = vendor_details.find({}, {'_id': False})
        for i in record:
            vendor_details_temp.insert(i)
    except:
        pass


    try:
        vendor_details.drop()
        # writedata = data['data']
        for i in data['vendor_details']:
            i['timestamp'] = datetime.now()
            vendor_details.insert(i)
        record = {"timestamp": datetime.now(), "collection_name": "vendor_details", "status": "Sucess"}
        sync_log.insert(record)
    except:
        vendor_details.drop()
        record = vendor_details_temp.find({})
        for i in record:
            vendor_details.insert(i)
        vendor_details_temp.drop()
        record = {"timestamp": datetime.now(), "collection_name": "vendor_details", "status": "Failed"}
        sync_log.insert(record)


def write_to_json(data, name):
    to_write = {
        "timestamp": datetime.now().strftime(constants.time_format),
        "data": data
    }

    json_object = json.dumps(to_write, indent=4)

    # Writing to sample.json
    with open(name + ".json", "w") as outfile:
        outfile.write(json_object)
    print("JSON FILE UPDATED FOR : " + name)


# -----------------------------------------------------------------------------------------------
# ============================ END DATA BY JSON =============================================
# -----------------------------------------------------------------------------------------------


# =========================== IMPLEMENT OF TABEL Function =============================================

def send_machine_sales_data():
    data = production_plan.find({})
    get = []
    for j in data:
        # print(j)
        get.append(j)
    return get


# send_machine_sales_data()

def get_vendor_data():
    record = vendor_details.find({}, {'_id': False})
    get = []
    for i in record:
        i['timestamp'] = str(i['timestamp'].strftime(constants.only_date))
        # print(i)
        get.append(i)
    return get


def get_sales_order_data():
    record = sales_order.find({}, {'_id': False})
    get = []
    for i in record:
        i['timestamp'] = str(i['timestamp'].strftime(constants.only_date))
        # print(i)
        get.append(i)
    return get


def get_wip_stocks_data():
    record = wip.find({}, {'_id': False})
    get = []
    for i in record:
        i['timestamp'] = str(i['timestamp'].strftime(constants.only_date))
        # print(i)
        get.append(i)
    return get


def get_machinery_components_data():
    record = machinery_components.find({})
    get = []
    for i in record:
        i['_id'] = str(i['_id'])
        i['timestamp'] = str(i['timestamp'].strftime(constants.only_date))
        # print(i)
        get.append(i)
    return get


def get_stock_data():
    record = stock.find({}, {'_id': False})
    get = []
    for i in record:
        i['timestamp'] = str(i['timestamp'].strftime(constants.only_date))
        # print(i)
        get.append(i)
    return get


# get_stock_data()


def get_parts_data():
    record = parts.find({}, {'_id': False})
    get = []
    for i in record:
        # print(i)
        get.append(i)
    return get


def get_month_year():
    # print(data)
    # x = data.split('-')
    #
    # year = x[0]
    # month = x[1]
    #
    # print(year)
    # print(month)
    #
    # record = sales_order.find({"$expr": {
    #     "$and": [
    #         {"$eq": [{"$year": "$voucher_date"}, int(year)]},
    #         {"$eq": [{"$month": "$voucher_date"}, int(month)]}
    #     ]
    # }}, {'_id': False})
    # # search_key = record['voucher_date']
    # print("----------------------------")
    record = sales_order.find({}, {"_id": False})
    get = []
    for i in record:
        # try:
        i["voucher_date"] = str(i["voucher_date"].strftime('%y-%m-%d'))
        i['timestamp'] = str(i['timestamp'].strftime(constants.only_date))
        # except:
        #     pass
        get.append(i)
    # print(get)
    return get


def get_array_machinery_components(record):
    # print("i got _id", record)
    data_set = machinery_components.find({'_id': ObjectId(record)}, {'_id': 0, 'machinery_components': 1})
    data = []
    for i in data_set:
        data.append(i['machinery_components'])
        # print(data)
    return data


def get_machinery_components_parts(id_data, bomvalue, ):
    # print("i got bom level", id_data,bomvalue)
    # print(type(bomvalue))
    bom_data = int(bomvalue)
    # print(type(bom_data))
    # int_bom = bom_data+1

    new_bom = str(bom_data)
    # print(new_bom)

    data_set = machinery_components.aggregate(
        [{"$match": {"_id": ObjectId(id_data)}},
         {
             "$project":
                 {
                     # "data": {
                     # "$filter": {
                     "input": "$machinery_components",
                     "as": "d",
                     'machinery_component': {"$d.bom_level"}
                 },
             # {"$project": {"myArray": "$input.bom_level",bom_data}

             # }
             # }
         }

         ]
    )

    # data_set = machinery_components.find({'_id': ObjectId(id_data)}, {'_id': 0,'machinery_components.machinery_components': 1})
    # data = []
    cnt = 0
    for i in data_set:
        # print(i)
        # data = i['machinery_components'][0]["machinery_components"]
        cnt = cnt + 1
        # print(data)
    # return data


# get_array_machinery_components('628202f62fc908c0c429c3ca,2')


# ++++++++++++++++++++++++++++++++ Production plan tabel ===================================================


def get_part_plan_data():
    data = part_production_plan.find({}, {"_id": 0}).limit(100000)
    send_data_part_plan = []
    for j in data:
        send_data_part_plan.append(j)
    return send_data_part_plan


# get_part_plan_data()

def gap_analysis_data():
    data_part_plan = []
    data = gap_analysis.find({}, {"_id": 0})
    for j in data:
        data_part_plan.append(j)
    return data_part_plan


# gap_analysis_data()


def get_drop_down_machinelist():
    data = production_plan.find({})
    get = []
    for i in data:
        get.append(i)
    # print(data)
    return get


# get_drop_down_machinelist()


def change_in_machine_plan(data):
    # print(data)
    data["totalsum"] = int(data["totalsum"])
    store = production_plan.update_one({"_id": data["machine"]}, {"$set": {"Total": data["totalsum"]}})
    print("Edit Done !")

    record = part_production_plan.find({"machine_name": data["machine"]})
    for i in record:
        print(i['required_machine'])

        part_production_plan.update_many({"machine_name": data["machine"],"_id":ObjectId(i['_id']) },
                                         {"$set": {"total_required":i['required_machine']*data["totalsum"]}})


    doc =  part_production_plan.find({"machine_name":data["machine"]},{"_id":0})
    for j in doc:
        gap_data = gap_analysis.find({'parts':j['assembly_name']},{"_id":0})
        for index in gap_data:
            parts = j['assembly_name']
            live_sales = j['total_required']
            production = 0
            actual_required = production + live_sales
            wip_qty = index["wip_qty"]
            finish_stock = index["finish_stock"]
            issued_qty= index["issued_qty"]
            final_order= actual_required -(wip_qty - finish_stock - issued_qty)
            gap_analysis.update_one({"parts": j['assembly_name']},
                                    {"$set": {"live_sales": live_sales,"actual_required":actual_required,'final_order':final_order}})  # update the mongodb data which are repaet



def view_history_data(data):
    print(data)
    data_coll = []
    if data == "vendor_details":
        print("I am in vendor_details ")
        record = vendor_details_backup.find({}, {"_id": False,"vendor_details":0})
        for i in record:
            i['timestamp'] = str(i['timestamp'].strftime(constants.time_format))
            # print(doc)
            data_coll.append(i)

    elif data == "sales_order":
        print("I am in sales_order ")
        record = sales_order_backup.find({}, {"_id": False,"sales_order":0})
        for i in record:
            i['timestamp'] = i['timestamp'].strftime(constants.time_format)
            data_coll.append(i)

    elif data == "wip":
        print("I am in wip ")
        record = wip_backup.find({}, {"_id": False,"wip":0})
        for doc in record:
            doc['timestamp'] = str(doc['timestamp'].strftime(constants.time_format))
            # print(doc)
            data_coll.append(doc)

    elif data == "machinery_components":
        print("I am in machinery_components ")
        record = machinery_components_backup.find({}, {"_id": False,"machinery_components":0})
        for doc in record:
            doc['timestamp'] = str(doc['timestamp'].strftime(constants.time_format))
            # print(doc)
            data_coll.append(doc)

    elif data == "stock":
        print("I am in stock ")
        record = stock_backup.find({}, {"_id": False,"machine_stocks":0})
        for i in record:
            i['timestamp'] = str(i['timestamp'].strftime(constants.time_format))
            # print(doc)
            data_coll.append(i)
    else:
        print("I am in pass ")
        pass

    return data_coll


def view_vender_page(data):
    print(data)
    # print(type(data))
    data = int(data)
    record = vendor_details_backup.find({"docs_count":data}, {"_id": False})
    docs = []
    for i in record:
        for j in range(0,len(i["vendor_details"])):
            # print(i["sales_order"][j]["voucher_type"])
            i["vendor_details"][j]["_id"] = str(i["vendor_details"][j]["_id"])
            i["vendor_details"][j]['timestamp'] = str(i["vendor_details"][j]['timestamp'].strftime(constants.time_format))
            # i['voucher_date'] = str(i['voucher_date'].strftime(constants.time_format))
            docs.append(i["vendor_details"][j])
    # print(docs)
    return docs



def view_sales_order_page(data):
    # print(data)
    # print(type(data))
    data = int(data)
    record = sales_order_backup.find({"docs_count": data}, {"_id": False})
    docs = []
    for i in record:
        # print(i["sales_order"][0]["voucher_type"])
        for j in range(0,len(i["sales_order"])):
            # print(i["sales_order"][j]["voucher_type"])
            i["sales_order"][j]["_id"] = str(i["sales_order"][j]["_id"])
            i["sales_order"][j]['timestamp'] = str(i["sales_order"][j]['timestamp'].strftime(constants.time_format))
            # i['voucher_date'] = str(i['voucher_date'].strftime(constants.time_format))
            docs.append(i["sales_order"][j])
    # print(docs)
    return docs

# view_sales_order_page(0)



def view_wip_page(data):
    # print(data)
    # print(type(data))
    data = int(data)
    record = wip_backup.find({"docs_count": data}, {"_id": False})
    docs = []
    for i in record:
        for j in range(0, len(i["wip"])):
            # print(i["machine_stocks"][j]["voucher_type"])
            i["wip"][j]["_id"] = str(i["wip"][j]["_id"])
            i["wip"][j]['timestamp'] = str(
                i["wip"][j]['timestamp'].strftime(constants.time_format))
            # i['voucher_date'] = str(i['voucher_date'].strftime(constants.time_format))
            docs.append(i["wip"][j])
    return docs

def view_machinery_components_page(data):
    # print(data)
    # print(type(data))
    data = int(data)
    record = machinery_components_backup.find({"docs_count": data}, {"_id": False})
    docs = []
    for i in record:
        for j in range(0, len(i["machinery_components"])):
            # print(i["machine_stocks"][j]["voucher_type"])
            i["machinery_components"][j]["_id"] = str(i["machinery_components"][j]["_id"])
            i["machinery_components"][j]['timestamp'] = str(
                i["machinery_components"][j]['timestamp'].strftime(constants.time_format))
            # i['voucher_date'] = str(i['voucher_date'].strftime(constants.time_format))
            docs.append(i["machinery_components"][j])
    # print(docs)
    return docs

def view_stock_page(data):
    # print(data)
    # print(type(data))
    data = int(data)
    record = stock_backup.find({"docs_count": data}, {"_id": False})
    docs = []
    for i in record:
        # print(doc)
        for j in range(0,len(i["machine_stocks"])):
            # print(i["machine_stocks"][j]["voucher_type"])
            i["machine_stocks"][j]["_id"] = str(i["machine_stocks"][j]["_id"])
            i["machine_stocks"][j]['timestamp'] = str(i["machine_stocks"][j]['timestamp'].strftime(constants.time_format))
            # i['voucher_date'] = str(i['voucher_date'].strftime(constants.time_format))
            docs.append(i["machine_stocks"][j])
    # print(docs)
    return docs



def find_cumulative(machine_name):
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # print("________________________________",machine_name)
    data = {}
    for i in range(0, len(machine_name)):
        uniqe_data = machinery_components.find({'machine_name': machine_name}, {'_id': 0})
        for doc in uniqe_data:
            data["machinery_components"] = [doc]
    # print(data)
    global b
    b = 0
    def sum_nested_level(val, bom_val):
        global b
        b += bom_val
        for key, value in val.items():
            if key == 'machinery_components':
                for i in range(len(value)):
                    time.sleep(0.05)
                    if 'Primary_Item' in value[i]:
                        sum_nested_level(value[i], value[i]['bom_qty'])

    mc = []

    def check_compo(key, value):
        global b
        global mc_name
        if key == 'machinery_components':
            for i in range(len(value)):
                if 'machine_name' in value[i]:
                    mc_name = value[i]['machine_name']
                    # print('mc_name', mc_name)
                if value[i]['bom_level'] == 3:
                    # print("<", i, ">", value[i])
                    sum_nested_level(value[i], value[i]['bom_qty'])
                    value[i]['total_bom_qty'] = b
                    mc.append({'total_bom_qty': b, 'spare_name': value[i]['spare_name'], 'machine_name': mc_name})
                    # print("B :: ", b)
                    b = 0
                time.sleep(0.05)
                for key1, value2 in value[i].items():
                    check_compo(key1, value2)

    for key, value in data.items():
        check_compo(key, value)
    # for name , number in value:
    #     print("Parent Key " + key + " Child name " + name + " Child number " + number)

    # print("Changed Data is : ", data)
    # pprint(mc)


    return mc
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


def edit_particular_data(data):
    gap_calculator.drop()
    # print(data[0]["Machine"])
    parts_data= []

    for i in range(0,len(data)):
        # print(data[0]["Machine"])
        # assembly = find_cumulative(data[i]["Machine"])  #call a cumulative funtion

        data[i]["quantity"] = int(data[i]["quantity"])
        production_plan.update_one({"_id": data[i]["Machine"]}, {"$set": {"Total": data[i]["quantity"]}})
        # print("Edit Done !")

        record = part_production_plan.find({"machine_name": data[i]["Machine"]})
        for j in record:
            # print(j['required_machine'])

            part_production_plan.update_many({"machine_name": data[i]["Machine"], "_id": ObjectId(j['_id'])},
                                             {"$set": {"total_required": j['required_machine'] * data[i]["quantity"]}})



        # fetching data ---------------------------------------------------------------------
        doc = part_production_plan.find({"machine_name": data[i]["Machine"]}, {"_id": 0})
        for k in doc:
            # for c in assembly:
            #     if k['assembly_name'] == c["spare_name"]:
            #         cumulative_data = c['total_bom_qty']
            #     else:
            #         pass

            # print(k['assembly_name'])
            gap_data = gap_analysis.find({'parts': k['assembly_name']}, {"_id": 0})
            for index in gap_data:
                # machine = data[i]["Machine"]
                supplier_list= index["supplier_list"]
                # print(supplier_list)
                live_sales = k['total_required']
                production = 0
                actual_required = live_sales + production
                wip_qty = index["wip_qty"]
                finish_stock = index["finish_stock"]
                issued_qty = index["issued_qty"]
                # final_order = actual_required - (wip_qty) - (finish_stock) - (issued_qty)
                gap_new_dict = {"machine": data[i]["Machine"],
                       "parts": k['assembly_name'],
                       "live_sales" : k['total_required'],
                        "production" : 0,
                        "actual_required" : k['total_required'] + 0,
                        "wip_qty" : index["wip_qty"],
                        "finish_stock" : index["finish_stock"],
                        "issued_qty" : index["issued_qty"],
                        "final_order" : actual_required - (wip_qty) - (finish_stock) - (issued_qty),
                        "supplier_list": supplier_list,
                        # "Cumulative_data":cumulative_data,
                        # "primary_item": ''
                }
                # unique = list({each['assembly_name']: each for each in gap_new_dict}.values())
                # gap_calculator.insert_one(gap_new_dict)
                if k['assembly_name'] not in parts_data:
                    # print("insetion")
                    parts_data.append(k['assembly_name'])
                    # print(gap_new_dict)
                    gap_calculator.insert_one(gap_new_dict)  # insert data in mongodb
                else:
                    gap_calculator.update_one({"parts": k['assembly_name']},
                                              {"$inc": {"live_sales": gap_new_dict[
                                                  'live_sales'],"actual_required": gap_new_dict["production"] + gap_new_dict['live_sales']}})
                    # gap_calculator.update_one({"parts": k['assembly_name']},
                    #                           {"$inc": {"Cumulative_data": gap_new_dict[
                    #                               'Cumulative_data']}})
                    # gap_calculator.update_one({"parts": k['assembly_name']},
                    #                {"$inc": {
                    #                    "actual_required": gap_new_dict["production"] + gap_new_dict['live_sales']}})

                    update_data = gap_calculator.find({"parts": k['assembly_name']}, {"_id": 0})
                    for change in update_data:
                        gap_calculator.update_one({"parts": k['assembly_name']},
                                       {"$set": {"final_order": change["actual_required"] - change["wip_qty"] -
                                                                change["finish_stock"] - change["issued_qty"]}})

                # print(gap_new_dict)

    # primary_item = find_primary_item()
    # for j in primary_item:
    #     # print(i['spare_item'])
    #     gap_calculator.update_one({"parts": j['spare_item']},
    #                               {"$set": {'primary_item': j['primary_items']}})
    #
    # final_gap_cal()  # function call cumlatives


# edit_particular_data([{'Machine': 'DYNAMIC BALANCING MACHINE(HDM-300)', 'quantity': '2'}])




def getting_data_gap_analysis(data):
    # print(data)
    record = []

    for i in range(0,len(data)):
        doc = part_production_plan.find({"machine_name": data[i]["Machine"]}, {"_id": 0})
        for k in doc:
            gap_data = gap_analysis.find({'parts': k['assembly_name']}, {"_id": 0})
        # gap_data = gap_analysis.find({'parts': data[i]["Machine"]}, {"_id": 0})
            for j in gap_data:
                record.append(j)
    # print(record)
    return record






def getting_gap_calculator(data):
    # print(data)
    record = []
    gap_data = gap_calculator.find({}, {"_id": 0})
    for j in gap_data:
        record.append(j)
    # pprint(record)
    return record

# getting_gap_calculator([{'Machine': 'DIGITAL ROCKWELL HARDNESS TESTER(RASNE-3)', 'quantity': '7'}, {'Machine': 'DIGITAL ROCKWELL HARDNESS TESTER(RASNEB-3)', 'quantity': '2'}, {'Machine': 'DIGITAL ROCKWELL HARDNESS TESTER(RASNET-3)', 'quantity': '4'}]
# )
# getting_gap_calculator([{'Machine': 'BRINELL HARDNESS TESTER B-3000 PC', 'quantity': '3'}])



def reset_machine_data(data):

    if production_plan.find({}).count() > 0:
        production_plan_function()
        part_production_plan.drop()
        data_part =reset_data_part_prduction_plan.find({})
        for i in data_part:
            part_production_plan.insert_one(i)
        print("production__part_plan done")


    if part_production_plan.find({}).count() > 0:
        print("gap_collection done")
        gap_analysis.drop()
        record = reset_data_gap.find({})
        for i in record:
            gap_analysis.insert_one(i)
        print("gap_collection done")
    return 0

# ============================ END ================================================
def datetimeformat():
    vart = "2-Apr-21"
    obj = datetime.strptime(vart, '%d-%b-%y')
    # test = obj =  datetime.strptime(obj, '%d-%b-%y')
    print(type(obj))




# -----------------------------------------------------------------------------------------------------
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% backup_data %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# -----------------------------------------------------------------------------------------------------
def backup_data_sales_order(data):
    record = sales_order.find({}, {'_id': False}).count()
    # writedata = data['data']
    if record == 0:
        pass
    else:
        dict = {}
        dict["timestamp"] = datetime.now()
        docs_count = sales_order_backup.find({}).count()
        dict["docs_count"] = docs_count
        dict["database_name"] = "sales_order"
        dict["sales_order"] = data['pending_so']

        if docs_count < 10:
            print("I AM IN IF ")
            sales_order_backup.insert_one(dict)
            print(docs_count)
        else:
            print("I AM IN ELSE PART")
            print(docs_count)
            sales_order_backup.delete_one({"docs_count": 0})
            for i in range(0, 9):
                print(i + 1, i)
                sales_order_backup.update_many({"docs_count": (i + 1)}, {"$set": {"docs_count": i}})

            dict["docs_count"] = 9
            sales_order_backup.insert_one(dict)


def backup_data_stock(data):
    record = stock.find({}, {'_id': False}).count()
    # writedata = data['data']
    if record == 0:
        pass
    else:
        dict = {}
        dict["timestamp"] = datetime.now()
        docs_count = stock_backup.find({}).count()
        dict["docs_count"] = docs_count
        dict["database_name"] = "stock"
        dict["machine_stocks"] = data['machine_stocks']

        if docs_count < 10:
            print("I AM IN IF ")
            stock_backup.insert_one(dict)
            print(docs_count)
        else:
            print("I AM IN ELSE PART")
            print(docs_count)
            stock_backup.delete_one({"docs_count": 0})
            for i in range(0, 9):
                # print(i + 1, i)
                stock_backup.update_many({"docs_count": (i + 1)}, {"$set": {"docs_count": i}})

            dict["docs_count"] = 9
            stock_backup.insert_one(dict)


def backup_data_machinery_components(data):
    record = machinery_components.find({}, {'_id': False}).count()
    # writedata = data['data']
    if record == 0:
        # print("backup pass")
        pass
    else:
        print("I AM IN IF ")
        # print(writedata)
        docs_count = machinery_components_backup.find({}).count()
        dict1 = {}
        dict1["timestamp"] = datetime.now()
        dict1["docs_count"] = docs_count
        dict1["database_name"] = "machinery_components"
        unique = list({each["machine_name"]:each for each in data['machinery_components']}.values())
        # print(unique)
        dict1["machinery_components"] = unique

        if docs_count < 10:
            print("I AM IN IF ")
            # print(type(dict1['machinery_components']))
            machinery_components_backup.insert_one(dict1)
            print(docs_count)
        else:
            print("I AM IN ELSE PART")
            # print(docs_count)
            # print(docs_count)
            machinery_components_backup.delete_one({"docs_count": 0})
            for i in range(0, 9):
                # print(i + 1, i)
                machinery_components_backup.update_many({"docs_count": (i + 1)}, {"$set": {"docs_count": i}})

            dict["docs_count"] = 9
            machinery_components_backup.insert_one(dict)


def backup_data_wip_stocks(data):
    record = wip.find({}, {'_id': False}).count()
    # writedata = data['data']
    if record == 0:
        pass
    else:
        dict = {}
        dict["timestamp"] = datetime.now()
        docs_count = wip_backup.find({}).count()
        dict["docs_count"] = docs_count
        dict["database_name"] = "wip"
        dict["wip"] = data['wip_stocks']

        if docs_count < 10:
            print("I AM IN IF ")
            wip_backup.insert_one(dict)
            print(docs_count)
        else:
            print("I AM IN ELSE PART")
            print(docs_count)
            wip_backup.delete_one({"docs_count": 0})
            for i in range(0, 9):
                # print(i + 1, i)
                wip_backup.update_many({"docs_count": (i + 1)}, {"$set": {"docs_count": i}})

            dict["docs_count"] = 9
            wip_backup.insert_one(dict)


def backup_data_vendor_details(data):
    record = vendor_details.find({}, {'_id': False}).count()
    # writedata = data['data']
    if record == 0:
        pass
    else:
        dict = {}
        dict["timestamp"] = datetime.now()
        docs_count = vendor_details_backup.find({}).count()
        dict["docs_count"] = docs_count
        dict["database_name"] = "vendor_details"
        dict["vendor_details"] = data['vendor_details']

        if docs_count < 10:
            print("I AM IN IF ")
            vendor_details_backup.insert_one(dict)
            print(docs_count)
        else:
            print("I AM IN ELSE PART")
            print(docs_count)
            vendor_details_backup.delete_one({"docs_count": 0})
            for i in range(0, 9):
                # print(i + 1, i)
                vendor_details_backup.update_many({"docs_count": (i + 1)}, {"$set": {"docs_count": i}})

            dict["docs_count"] = 9
            vendor_details_backup.insert_one(dict)



# -----------------------------------------------------------------------------------------------------
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% backup_data %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# -----------------------------------------------------------------------------------------------------