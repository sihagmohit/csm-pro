import pymongo
import copy
from datetime import datetime, timedelta
import constants
from pprint import pprint
from statistics import mean
import mail_api
import time
import otp_operations

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["PPAP_OEE"]
temp_production_orders = mydb["temp_production_orders"]
production_orders = mydb["production_orders"]
production_order_parameters = mydb["production_order_parameters"]
shift_records = mydb["shift_records"]
pqcr_records = mydb["pqcr_records"]

mydb1 = myclient['Anzen_3_0']
user_collection = mydb1['Users']
'''
=================================================================================================================
PRODUCTION ORDER CALCULATIONS
=================================================================================================================
'''


# to do add cycle time calculation chart
# plan vs actual as per production orders

def clear_temp_production_orders(session):
    myquery = {"phone": session["user"]}
    temp_production_orders.delete_many(myquery)
    return None


def temp_insert_production_orders(data, session):
    myquery = {"phone": session["user"]}
    temp_production_orders.delete_many(myquery)

    for record in data:
        record["phone"] = session["user"]
    temp_production_orders.insert_many(data)
    return True


def temp_get_production_orders(session):
    myquery = {"phone": session["user"]}
    data = temp_production_orders.find(myquery, {'_id': False})
    # print(data)
    return_orders = []
    for mydoc in data:
        return_orders.append(mydoc)
    # print(len(return_orders))
    return return_orders


def query_backend_database(part_number):
    myquery = {"PART NUMBER": part_number}
    data = production_order_parameters.find_one(myquery, {'_id': False})
    return data


def insert_production_orders(data):
    # production_orders.insert_many(data)
    for record in data:
        myquery = {"ORDER NUMBER (LEFT)": record["ORDER NUMBER (LEFT)"],
                   "ORDER NUMBER (RIGHT)": record["ORDER NUMBER (RIGHT)"]}
        count = production_orders.find(myquery, {'_id': False}).count()
        if count == 0:
            production_orders.insert_one(record)
    return True


def get_production_orders():
    myquery = {}
    data = production_orders.find(myquery, {'_id': False}).sort("PLANNED_START", -1)
    # print(data)
    return_orders = []
    for mydoc in data:
        return_orders.append(mydoc)
    # print(len(return_orders))
    return return_orders


def get_latest_production_orders():
    myquery = {}
    data = production_orders.find(myquery, {'_id': False}).sort("PLANNED_START", -1).limit(
        constants.production_plan_limit)
    # print(data)
    return_orders = []
    for mydoc in data:
        return_orders.append(mydoc)
    # print(len(return_orders))
    return return_orders


def update_production_orders(data):
    for production_order in data:
        myquery = {"ORDER NUMBER (LEFT)": production_order["ORDER NUMBER (LEFT)"],
                   "ORDER NUMBER (RIGHT)": production_order["ORDER NUMBER (RIGHT)"]}
        newvalues = {"$set": data}
        production_orders.update_one(myquery, newvalues)


def pause_production_order(data):
    myquery = {"ORDER NUMBER (LEFT)": data["ORDER NUMBER (LEFT)"],
               "ORDER NUMBER (RIGHT)": data["ORDER NUMBER (RIGHT)"]}

    order = production_orders.find_one(myquery, {'_id': False, 'kpi': False})
    order["ACTION"] = "Paused"

    history = {}
    history["start_time"] = datetime.now().strftime(constants.time_format)
    history["stop_time"] = "-"

    if "PAUSE HISTORY" in order:
        order["PAUSE HISTORY"].append(history)
    else:
        order["PAUSE HISTORY"] = []
        order["PAUSE HISTORY"].append(history)

    newvalues = {"$set": order}

    production_orders.update_one(myquery, newvalues)
    print("Pause history created!")


def resume_production_order(data):
    myquery = {"ORDER NUMBER (LEFT)": data["ORDER NUMBER (LEFT)"],
               "ORDER NUMBER (RIGHT)": data["ORDER NUMBER (RIGHT)"]}

    order = production_orders.find_one(myquery, {'_id': False, 'kpi': False})

    # pause history has to be there
    if "PAUSE HISTORY" in order:
        order["PAUSE HISTORY"][-1]["stop_time"] = datetime.now().strftime(constants.time_format)

    order["ACTION"] = "In Process"

    newvalues = {"$set": order}

    production_orders.update_one(myquery, newvalues)
    print("Production order was resumed!")


def update_specific_production_order(production_order):
    # print(production_order)
    myquery = {"ORDER NUMBER (LEFT)": production_order["ORDER NUMBER (LEFT)"],
               "ORDER NUMBER (RIGHT)": production_order["ORDER NUMBER (RIGHT)"]}
    newvalues = {"$set": production_order}

    production_orders.update_one(myquery, newvalues)


def check_if_production_order_is_paused(data):
    myquery = {
        "ORDER NUMBER (LEFT)": data["ORDER NUMBER (LEFT)"],
        "ORDER NUMBER (RIGHT)": data["ORDER NUMBER (RIGHT)"],
        "ACTION": "Paused"}
    data = production_orders.find(myquery, {'_id': False, 'kpi': False}).count()
    return data


def get_specific_production_order(data):
    # print(production_order)
    myquery = {"ORDER NUMBER (LEFT)": data["ORDER NUMBER (LEFT)"], "ORDER NUMBER (RIGHT)": data["ORDER NUMBER (RIGHT)"]}
    production_order = production_orders.find_one(myquery, {'_id': False})
    return production_order


def get_specific_production_order_spr(data):
    # print(production_order)
    myquery = {"ORDER NUMBER (LEFT)": data["ORDER NUMBER (LEFT)"], "ORDER NUMBER (RIGHT)": data["ORDER NUMBER (RIGHT)"]}
    production_order = production_orders.find_one(myquery, {'_id': False})
    return production_order


def get_production_order_details_by_machine(machine):
    myquery = {"MACHINE": machine, "ACTION": "In Process"}
    production_order = production_orders.find_one(myquery, {'_id': False, 'kpi': False})
    # print(production_order)
    found = False
    if production_order is not None:
        found = True
    return production_order, found


# ALL DONE PRODUCTION ORDERS >> DOWNTIME ANALYSIS HISTORY
def get_production_order_details_by_order_number(order_left, order_right):
    myquery = {"ORDER NUMBER (LEFT)": order_left, "ORDER NUMBER (RIGHT)": order_right}
    production_order = production_orders.find_one(myquery, {'_id': False, 'kpi': False})
    # print(production_order)
    found = False
    if production_order is not None:
        found = True
    return production_order, found


def get_shot_details_by_machine(machine):
    myquery = {"MACHINE": machine, "ACTION": "In Process"}
    production_order = production_orders.find_one(myquery, {'_id': False, 'kpi': False})
    found = False

    if production_order is not None:
        found = True
        current_time = datetime.now()
        start_time = production_order["ACTUAL_START"]
        duration = (current_time - start_time).total_seconds()
        try:
            production_order["EXPECTED SHOTS"] = int(duration / production_order["CYCLE TIME"])
        except:
            production_order["EXPECTED SHOTS"] = "NA"

        # add variable to shot data to find actual shot data
        try:
            for i in range(len(production_order["SHOT_DETAILS"])):
                if i == 0:
                    production_order["SHOT_DETAILS"][i]["CALCULATED CYCLE TIME"] = 0
                else:
                    start_time = datetime.strptime(production_order["SHOT_DETAILS"][i - 1]["timestamp"],
                                                   constants.time_format)
                    end_time = datetime.strptime(production_order["SHOT_DETAILS"][i]["timestamp"],
                                                 constants.time_format)
                    production_order["SHOT_DETAILS"][i]["CALCULATED CYCLE TIME"] = (
                            end_time - start_time).total_seconds()
        except:
            pass

    return production_order, found


# ALL DONE PRODUCTION ORDERS >> BASIC DETAILS
def get_shot_details_by_machine_history(order_left, order_right):
    print(order_left)
    print(order_right)
    # ADD ORDER NUMBERS TO QUERY ["ORDER_NUMBER (RIGHT)"] ["ORDER_NUMBER (LEFT)"]
    myquery = {"ORDER NUMBER (LEFT)": order_left, "ORDER NUMBER (RIGHT)": order_right}
    production_order = production_orders.find_one(myquery, {'_id': False, 'kpi': False})
    found = False

    if production_order is not None:
        found = True
        current_time = datetime.now()
        start_time = production_order["ACTUAL_START"]
        stop_time = production_order["ACTUAL_STOP"]
        duration = (stop_time - start_time).total_seconds()
        try:
            production_order["EXPECTED SHOTS"] = int(duration / production_order["CYCLE TIME"])
        except:
            production_order["EXPECTED SHOTS"] = "NA"

        # add variable to shot data to find actual shot data
        try:
            for i in range(len(production_order["SHOT_DETAILS"])):
                if i == 0:
                    production_order["SHOT_DETAILS"][i]["CALCULATED CYCLE TIME"] = 0
                else:
                    start_time = datetime.strptime(production_order["SHOT_DETAILS"][i - 1]["timestamp"],
                                                   constants.time_format)
                    end_time = datetime.strptime(production_order["SHOT_DETAILS"][i]["timestamp"],
                                                 constants.time_format)
                    production_order["SHOT_DETAILS"][i]["CALCULATED CYCLE TIME"] = (
                            end_time - start_time).total_seconds()
        except:
            pass

    return production_order, found


def get_all_active_production_orders():
    myquery = {"ACTION": "In Process"}
    data = production_orders.find(myquery, {'_id': False, 'kpi': False})
    return_orders = []
    # print(data)
    for mydoc in data:
        return_orders.append(mydoc)

    # print("return_orders",return_orders)
    return return_orders


def get_active_production_orders_at_specific_time(current_time):
    # Production Orders with Start Time and Stop Time present
    myquery = {
        "ACTUAL_START": {"$lte": current_time},
        "ACTUAL_STOP": {"$gt": current_time}
    }
    data = production_orders.find(myquery, {'_id': False})
    return_orders = []
    for mydoc in data:
        return_orders.append(mydoc)

    # If stop time is not present than stop time is "-"
    myquery = {
        "ACTUAL_START": {"$lte": current_time},
        "ACTUAL_STOP": "-"
    }
    data = production_orders.find(myquery, {'_id': False})
    for mydoc in data:
        return_orders.append(mydoc)

    return return_orders


def clean_production_orders():
    all_production_orders = get_production_orders()

    total_repetitions = 0
    single_orders = 0
    for production_order in all_production_orders:
        myquery = {"ORDER NUMBER (LEFT)": production_order["ORDER NUMBER (LEFT)"],
                   "ORDER NUMBER (RIGHT)": production_order["ORDER NUMBER (RIGHT)"]}
        count = production_orders.find(myquery, {'_id': False}).count()
        if count == 1:
            single_orders += 1

        if count > 1:
            total_repetitions += 1
            print("------------REPETITIVE ORDERS-----------------")
            print("ORDER NUMBER (LEFT) - ", production_order["ORDER NUMBER (LEFT)"])
            print("ORDER NUMBER (RIGHT) - ", production_order["ORDER NUMBER (RIGHT)"])

            repetition_count = 0

            while repetition_count is not 1:
                myquery = {"ORDER NUMBER (LEFT)": production_order["ORDER NUMBER (LEFT)"],
                           "ORDER NUMBER (RIGHT)": production_order["ORDER NUMBER (RIGHT)"]}
                production_orders.delete_one(myquery)

                myquery = {"ORDER NUMBER (LEFT)": production_order["ORDER NUMBER (LEFT)"],
                           "ORDER NUMBER (RIGHT)": production_order["ORDER NUMBER (RIGHT)"]}
                repetition_count = production_orders.find(myquery, {'_id': False}).count()

    print(total_repetitions)
    print(single_orders)


def get_rubbish_production_orders():
    all_production_orders = get_production_orders()
    for production_order in all_production_orders:
        if production_order["ACTUAL QTY"] == "BLACK":
            production_order["ACTUAL QTY"] == 0
            myquery = {"ORDER NUMBER (LEFT)": production_order["ORDER NUMBER (LEFT)"],
                       "ORDER NUMBER (RIGHT)": production_order["ORDER NUMBER (RIGHT)"]}
            newvalues = {"$set": production_order}
            production_orders.update_one(myquery, newvalues)


def get_active_production_orders_in_a_day(date, machine):
    start_time = date + ", " + constants.PQCR_start
    start_time = datetime.strptime(start_time, constants.time_format)
    stop_time = start_time + timedelta(hours=constants.PQCR_duration)

    print(start_time)
    print(stop_time)
    return_orders = []

    # Case 1 : start time less than day_start and stop time less than day_stop
    myquery = {
        "ACTUAL_START": {"$lte": start_time},
        "ACTUAL_STOP": {"$lte": stop_time, "$gte": start_time},
        "MACHINE": machine,
    }
    data = production_orders.find(myquery, {'_id': False})
    for mydoc in data:
        return_orders.append(mydoc)

    # Case 2 : start time greater than day_start and stop time less than day_stop
    myquery = {"ACTUAL_START": {"$gte": start_time}, "ACTUAL_STOP": {"$lte": stop_time}, "MACHINE": machine}
    data = production_orders.find(myquery, {'_id': False})
    for mydoc in data:
        return_orders.append(mydoc)

    # Case 3 : start time greater than day_start and stop time greater than day_stop
    myquery = {
        "ACTUAL_STOP": {"gte": stop_time},
        "ACTUAL_START": {"$lte": stop_time, "$gte": start_time},
        "MACHINE": machine,
    }
    data = production_orders.find(myquery, {'_id': False})
    for mydoc in data:
        return_orders.append(mydoc)

    # Case 4 : start time less than day_start and stop time greater than day_stop
    myquery = {
        "ACTUAL_START": {"$lte": start_time},
        "ACTUAL_STOP": {"$gte": stop_time},
        "MACHINE": machine,
    }
    data = production_orders.find(myquery, {'_id': False})
    for mydoc in data:
        return_orders.append(mydoc)

    # Case 5 : active order
    myquery = {
        "ACTUAL_START": {"$lte": stop_time},
        "ACTUAL_STOP": "-",
        "MACHINE": machine,
    }
    data = production_orders.find(myquery, {'_id': False})
    for mydoc in data:
        return_orders.append(mydoc)

    # return only names and order numbers for now
    numbers = []
    names = []
    print(return_orders)
    for order in return_orders:
        if order["ORDER NUMBER (LEFT)"] != "":
            print("=====APPENDED RIGHT ORDER NUMBER=============================")
            numbers.append(order["ORDER NUMBER (LEFT)"])
            names.append(order["PART NAME"])
        if order["ORDER NUMBER (RIGHT)"] != "":
            print("=====APPENDED LEFT ORDER NUMBER=============================")
            numbers.append(order["ORDER NUMBER (RIGHT)"])
            names.append(order["PART NAME"])

    return numbers, names


'''
=================================================================================================================
FOR CBM - CHARTS | GETTING ALL ORDERS WITH PARTNUMBER BETWEEN FROM - TO                    -VATSAL
=================================================================================================================
'''


def get_active_production_orders_from_to(from_time, to_time, machine):
    start_time = from_time
    start_time = datetime.strptime(start_time, constants.time_format)
    stop_time = to_time
    stop_time = datetime.strptime(stop_time, constants.time_format)

    print(start_time)
    print(stop_time)
    return_orders = []

    # Case 1 : start time less than day_start and stop time less than day_stop
    myquery = {
        "ACTUAL_START": {"$lte": start_time},
        "ACTUAL_STOP": {"$lte": stop_time, "$gte": start_time},
        "MACHINE": machine,
    }
    data = production_orders.find(myquery,
                                  {'_id': False, 'ACTUAL_START': True, 'ACTUAL_STOP': True, 'PART NUMBER': True})
    for mydoc in data:
        mydoc["appended by"] = "1"
        return_orders.append(mydoc)

    # Case 2 : start time greater than day_start and stop time less than day_stop
    myquery = {"ACTUAL_START": {"$gte": start_time}, "ACTUAL_STOP": {"$lte": stop_time}, "MACHINE": machine}
    data = production_orders.find(myquery,
                                  {'_id': False, 'ACTUAL_START': True, 'ACTUAL_STOP': True, 'PART NUMBER': True}).sort(
        'ACTUAL_START', 1)
    for mydoc in data:
        mydoc["appended by"] = "2"
        return_orders.append(mydoc)

    # Case 3 : start time greater than day_start and stop time greater than day_stop
    myquery = {
        "ACTUAL_STOP": {"gte": stop_time},
        "ACTUAL_START": {"$lte": stop_time, "$gte": start_time},
        "MACHINE": machine,
    }
    data = production_orders.find(myquery,
                                  {'_id': False, 'ACTUAL_START': True, 'ACTUAL_STOP': True, 'PART NUMBER': True})
    for mydoc in data:
        mydoc["appended by"] = "3"
        return_orders.append(mydoc)

    # Case 5 : active order
    myquery = {
        "ACTUAL_START": {"$lte": stop_time},
        "ACTUAL_STOP": "-",
        "MACHINE": machine,
    }
    data = production_orders.find(myquery,
                                  {'_id': False, 'ACTUAL_START': True, 'ACTUAL_STOP': True, 'PART NUMBER': True})
    for mydoc in data:
        mydoc["appended by"] = "5"
        return_orders.append(mydoc)

        # Case 4 : start time less than day_start and stop time greater than day_stop
    myquery = {
        "ACTUAL_START": {"$lte": start_time},
        "ACTUAL_STOP": {"$gte": stop_time},
        "MACHINE": machine,
    }
    data = production_orders.find(myquery,
                                  {'_id': False, 'ACTUAL_START': True, 'ACTUAL_STOP': True, 'PART NUMBER': True})
    for mydoc in data:
        mydoc["appended by"] = "4"
        return_orders.append(mydoc)

    # return only names and order numbers for now
    numbers = []
    names = []

    return return_orders


'''
=========================================================================================================
    FOR CBM - PQCR
=========================================================================================================    
'''


def get_active_production_orders_from_to_for_pqcr(from_time, to_time, machine):
    start_time = from_time
    start_time = datetime.strptime(start_time, constants.time_format)
    stop_time = to_time
    stop_time = datetime.strptime(stop_time, constants.time_format)

    print(start_time)
    print(stop_time)
    return_orders = []

    # Case 1 : start time less than day_start and stop time less than day_stop
    myquery = {
        "ACTUAL_START": {"$lte": start_time},
        "ACTUAL_STOP": {"$lte": stop_time, "$gte": start_time},
        "MACHINE": machine,
    }
    data = production_orders.find(myquery,
                                  {'_id': False, 'ACTUAL_START': True, 'ACTUAL_STOP': True, 'PART NUMBER': True,
                                   "PART NAME": True, "ORDER NUMBER (RIGHT)": True, "ORDER NUMBER (LEFT)": True})
    for mydoc in data:
        mydoc["appended by"] = "1"
        return_orders.append(mydoc)

    # Case 2 : start time greater than day_start and stop time less than day_stop
    myquery = {"ACTUAL_START": {"$gte": start_time}, "ACTUAL_STOP": {"$lte": stop_time}, "MACHINE": machine}
    data = production_orders.find(myquery,
                                  {'_id': False, 'ACTUAL_START': True, 'ACTUAL_STOP': True, 'PART NUMBER': True,
                                   "PART NAME": True, "ORDER NUMBER (RIGHT)": True, "ORDER NUMBER (LEFT)": True}).sort(
        'ACTUAL_START', 1)
    for mydoc in data:
        mydoc["appended by"] = "2"
        return_orders.append(mydoc)

    # Case 3 : start time greater than day_start and stop time greater than day_stop
    myquery = {
        "ACTUAL_STOP": {"gte": stop_time},
        "ACTUAL_START": {"$lte": stop_time, "$gte": start_time},
        "MACHINE": machine,
    }
    data = production_orders.find(myquery,
                                  {'_id': False, 'ACTUAL_START': True, 'ACTUAL_STOP': True, 'PART NUMBER': True,
                                   "PART NAME": True, "ORDER NUMBER (RIGHT)": True, "ORDER NUMBER (LEFT)": True})
    for mydoc in data:
        mydoc["appended by"] = "3"
        return_orders.append(mydoc)

    # Case 5 : active order
    myquery = {
        "ACTUAL_START": {"$lte": stop_time},
        "ACTUAL_STOP": "-",
        "MACHINE": machine,
    }
    data = production_orders.find(myquery,
                                  {'_id': False, 'ACTUAL_START': True, 'ACTUAL_STOP': True, 'PART NUMBER': True,
                                   "PART NAME": True, "ORDER NUMBER (RIGHT)": True, "ORDER NUMBER (LEFT)": True})
    for mydoc in data:
        mydoc["appended by"] = "5"
        return_orders.append(mydoc)

        # Case 4 : start time less than day_start and stop time greater than day_stop
    myquery = {
        "ACTUAL_START": {"$lte": start_time},
        "ACTUAL_STOP": {"$gte": stop_time},
        "MACHINE": machine,
    }
    data = production_orders.find(myquery,
                                  {'_id': False, 'ACTUAL_START': True, 'ACTUAL_STOP': True, 'PART NUMBER': True,
                                   "PART NAME": True, "ORDER NUMBER (RIGHT)": True, "ORDER NUMBER (LEFT)": True})
    for mydoc in data:
        mydoc["appended by"] = "4"
        return_orders.append(mydoc)

    return return_orders


def get_all_active_production_orders_from_to(from_time, to_time):
    start_time = from_time
    # start_time = datetime.strptime(start_time, constants.time_format)
    stop_time = to_time
    # stop_time = datetime.strptime(stop_time, constants.time_format)

    print(start_time)
    print(stop_time)
    return_orders = []

    # Case 1 : start time less than day_start and stop time less than day_stop
    myquery = {
        "ACTUAL_START": {"$lte": start_time},
        "ACTUAL_STOP": {"$lte": stop_time, "$gte": start_time},

    }
    data = production_orders.find(myquery, {'_id': False})
    for mydoc in data:
        mydoc["appended by"] = "1"
        return_orders.append(mydoc)

    # Case 2 : start time greater than day_start and stop time less than day_stop
    myquery = {"ACTUAL_START": {"$gte": start_time}, "ACTUAL_STOP": {"$lte": stop_time}}
    data = production_orders.find(myquery, {'_id': False}).sort('ACTUAL_START', 1)
    for mydoc in data:
        mydoc["appended by"] = "2"
        return_orders.append(mydoc)

    # Case 3 : start time greater than day_start and stop time greater than day_stop
    myquery = {
        "ACTUAL_STOP": {"gte": stop_time},
        "ACTUAL_START": {"$lte": stop_time, "$gte": start_time},

    }
    data = production_orders.find(myquery, {'_id': False})
    for mydoc in data:
        mydoc["appended by"] = "3"
        return_orders.append(mydoc)

    # Case 5 : active order
    myquery = {
        "ACTUAL_START": {"$lte": stop_time},
        "ACTUAL_STOP": "-",

    }
    data = production_orders.find(myquery, {'_id': False})
    for mydoc in data:
        mydoc["appended by"] = "5"
        return_orders.append(mydoc)

        # Case 4 : start time less than day_start and stop time greater than day_stop
    myquery = {
        "ACTUAL_START": {"$lte": start_time},
        "ACTUAL_STOP": {"$gte": stop_time},

    }
    data = production_orders.find(myquery, {'_id': False})

    for mydoc in data:
        mydoc["appended by"] = "4"
        return_orders.append(mydoc)

    return (return_orders)


def get_active_production_orders_from_to_for_charts(from_time, to_time, machine):
    start_time = from_time

    stop_time = to_time

    print(start_time)
    print(stop_time)
    return_orders = []

    # Case 1 : start time less than day_start and stop time less than day_stop
    myquery = {
        "ACTUAL_START": {"$lte": start_time},
        "ACTUAL_STOP": {"$lte": stop_time, "$gte": start_time},
        "MACHINE": machine,
    }
    data = production_orders.find(myquery, {'_id': False})
    for mydoc in data:
        mydoc["appended by"] = "1"
        return_orders.append(mydoc)

    # Case 2 : start time greater than day_start and stop time less than day_stop
    myquery = {"ACTUAL_START": {"$gte": start_time}, "ACTUAL_STOP": {"$lte": stop_time}, "MACHINE": machine}
    data = production_orders.find(myquery, {'_id': False})
    for mydoc in data:
        mydoc["appended by"] = "2"
        return_orders.append(mydoc)

    # Case 3 : start time greater than day_start and stop time greater than day_stop
    myquery = {
        "ACTUAL_STOP": {"gte": stop_time},
        "ACTUAL_START": {"$lte": stop_time, "$gte": start_time},
        "MACHINE": machine,
    }
    data = production_orders.find(myquery, {'_id': False})
    for mydoc in data:
        mydoc["appended by"] = "3"
        return_orders.append(mydoc)

    # Case 5 : active order
    myquery = {
        "ACTUAL_START": {"$lte": stop_time},
        "ACTUAL_STOP": "-",
        "MACHINE": machine,
    }
    data = production_orders.find(myquery, {'_id': False})
    for mydoc in data:
        mydoc["appended by"] = "5"
        return_orders.append(mydoc)

        # Case 4 : start time less than day_start and stop time greater than day_stop
    myquery = {
        "ACTUAL_START": {"$lte": start_time},
        "ACTUAL_STOP": {"$gte": stop_time},
        "MACHINE": machine,
    }
    data = production_orders.find(myquery,
                                  {'_id': False})
    for mydoc in data:
        mydoc["appended by"] = "4"
        return_orders.append(mydoc)

    return return_orders


'''
=================================================================================================================
PRODUCTION ORDERS PAGE 
=================================================================================================================
'''


# %d/%m/%Y

def get_active_production_orders():
    myquery = {"$or": [{"ACTION": "In Process"},
                       {"ACTION": "Paused"}]}
    data = production_orders.find(myquery, {'_id': False, 'kpi': False}).sort("PLANNED_START", -1);
    # print(data)
    return_orders = []
    for mydoc in data:
        return_orders.append(mydoc)

    # print(return_orders)
    return return_orders


def get_done_production_orders():
    current_time = datetime.now()
    bound = current_time - timedelta(days=7)
    myquery = {"ACTION": "Done", "PLANNED_START": {"$gte": bound}}

    data = production_orders.find(myquery, {'_id': False, 'kpi': False}).sort("PLANNED_START", -1).limit(
        constants.limit_orders)
    # print(data)
    return_orders = []
    for mydoc in data:
        return_orders.append(mydoc)
    # print(len(return_orders))
    return return_orders


def get_planned_production_orders():
    myquery = {"ACTION": "Start"}
    data = production_orders.find(myquery, {'_id': False, 'kpi': False}).sort("PLANNED_START", -1).limit(
        constants.limit_orders)
    # print(data)
    return_orders = []
    for mydoc in data:
        return_orders.append(mydoc)
    # print(len(return_orders))
    return return_orders


'''
=================================================================================================================
SHOT DATA - BASIC DETAILS
=================================================================================================================
'''


def filter_duplicate_shots(data):
    unique_shot_details = []
    production_order = get_production_order_from_machine(data)
    if production_order is not None:
        if "SHOT_DETAILS" in production_order:
            if len(data["shot_details"]) > 0:
                for shot_record in data["shot_details"]:
                    duplicate_found = 0
                    for shot in reversed(production_order["SHOT_DETAILS"]):
                        if shot['SHOT COUNT'] == shot_record["shot_count"]:
                            print("--------Duplicate shot found-------")
                            duplicate_found = 1
                            break
                        else:
                            pass
                    if duplicate_found == 0:
                        unique_shot_details.append(shot_record)

                data["shot_details"] = unique_shot_details
            else:
                pass
        else:
            pass
    else:
        pass

    return data


def update_shot_data(data):
    # Convert Timestamp to datettime
    ##format_str = '%d-%m-%Y %H-%M-%S'  # The format
    format_str = constants.time_format
    timestamp = datetime.strptime(data["timestamp"], format_str)

    # check if there is order is in a timestamp
    myquery = {"$and": [{"ACTUAL_START": {"$lte": timestamp}}, {"ACTUAL_STOP": "-"}], "MACHINE": data["machine"]}
    production_order = production_orders.find_one(myquery, {'_id': False})
    if production_order is not None:
        production_order_count = 0
        if production_order["ORDER NUMBER (LEFT)"] is not "":
            production_order_count = production_order_count + 1
        if production_order["ORDER NUMBER (RIGHT)"] is not "":
            production_order_count = production_order_count + 1

        try:
            production_order["NUMBER OF CAVITIES"] = int(production_order["NUMBER OF CAVITIES"])
        except:
            production_order["NUMBER OF CAVITIES"] = int(production_order_count)  # 1 removed

        if production_order["ACTUAL QTY"] == "":
            # multiplier = int(production_order["NUMBER OF CAVITIES"]) / production_order_count
            production_order["ACTUAL QTY"] = 0 + int(data["new_shots"])  # * multiplier
        else:
            # multiplier = int(production_order["NUMBER OF CAVITIES"]) / production_order_count
            production_order["ACTUAL QTY"] = int(production_order["ACTUAL QTY"]) + int(
                data["new_shots"])  # * multiplier

        # Update Production Order
        # update_specific_production_order(production_order)

        # print("New Qty for Machine : ", data["machine"], "  =", production_order["ACTUAL QTY"])
        # print("Updated Production Order Qty !")

    else:
        print("Production Order Not Found !")


def update_shot_details(data):
    # print(production_order)
    myquery = {"ORDER NUMBER (LEFT)": str(data["ORDER NUMBER (LEFT)"]),
               "ORDER NUMBER (RIGHT)": str(data["ORDER NUMBER (RIGHT)"])}
    production_order = production_orders.find_one(myquery, {'_id': False})
    if production_order is not None:
        to_append = {

            'SHOT COUNT': data['shot_count'],
            'CYCLE TIME': data['cycle_time'],
            'timestamp': data['timestamp'],
            'status': data['status'],
        }

        if "SHOT_DETAILS" in production_order:
            production_order["SHOT_DETAILS"].append(to_append)
        else:
            production_order["SHOT_DETAILS"] = []
            production_order["SHOT_DETAILS"].append(to_append)

        newvalues = {"$set": production_order}
        production_orders.update_one(myquery, newvalues)
        print("SHOT DATA RECORDED")

        # ====================================================================================
        if production_order["ACTUAL QTY"] == "":
            production_order["ACTUAL QTY"] = 0 + 1  # * multiplier
        else:
            production_order["ACTUAL QTY"] = int(production_order["ACTUAL QTY"]) + 1  # * multiplier

        # Update Production Order
        update_specific_production_order(production_order)

        # print("New Qty for Machine : ", data["machine"], "  =", production_order["ACTUAL QTY"])
        print("Updated Production Order Qty !")
        # =======================================================================================
    else:
        print("NO PRODUCTION ORDER FOUND !")


'''
=================================================================================================================
KPI CRON JOB 
=================================================================================================================
'''


def update_minor_stops(data):
    print("Calculating Minor Stops if any..")
    myquery = {"ORDER NUMBER (LEFT)": str(data["ORDER NUMBER (LEFT)"]),
               "ORDER NUMBER (RIGHT)": str(data["ORDER NUMBER (RIGHT)"])}
    production_order = production_orders.find_one(myquery, {'_id': False})
    if production_order is not None:
        '''to_append = {

            'SHOT COUNT': data['shot_count'],
            'CYCLE TIME': data['cycle_time'],
            'timestamp': data['timestamp'],
            'status': data['status'],
        }'''
        shot_timestamp = datetime.strptime(data['timestamp'], constants.time_format)
        # print(shot_timestamp)
        if "CURRENT_DOWNTIME_STATUS" in production_order and len(production_order["SHOT_DETAILS"]) > 1:
            if production_order["CURRENT_DOWNTIME_STATUS"]["downtime_status"] == "false":
                if "SHOT_DETAILS" in production_order:
                    # print("------------LAST SHOT FROM DATABASE-----------------")
                    # print(production_order["SHOT_DETAILS"][-2])
                    # print("----------------------------------------------------")
                    last_known_shot = datetime.strptime(production_order["SHOT_DETAILS"][-2]["timestamp"],
                                                        constants.time_format)
                    # print(production_order["CYCLE TIME"])
                    # print("----------------------------------------------------")
                    # print(shot_timestamp)
                    # print(last_known_shot)
                    # print((shot_timestamp - last_known_shot).total_seconds())
                    if (shot_timestamp - last_known_shot).seconds > production_order["CYCLE TIME"]:
                        print("Downtime possible")
                        dt_start = last_known_shot + timedelta(seconds=production_order["CYCLE TIME"])
                        dt_stop = shot_timestamp
                        downtime_to_append = {
                            "start_time"
                            :
                                dt_start.strftime(constants.time_format),
                            "stop_time"
                            :
                                dt_stop.strftime(constants.time_format),
                            "reasonlist"
                            :
                                "Minor Stops",
                            "Mode"
                            :
                                "Software",
                            "details"
                            :
                                "Cycle time Exceeded.",
                            "status"
                            :
                                "Accept"
                        }
                        # print("DOWNTIME" in production_order)
                        if "DOWNTIME" in production_order:
                            production_order["DOWNTIME"].append(downtime_to_append)
                            # print(downtime_to_append)
                        else:
                            production_order["DOWNTIME"] = []
                            production_order["DOWNTIME"].append(downtime_to_append)
                            # print(downtime_to_append)
                    else:
                        pass
                else:
                    pass

                newvalues = {"$set": production_order}
                production_orders.update_one(myquery, newvalues)
                print("SHOT DELAY DOWNTIME RECORDED.")
        else:
            if "SHOT_DETAILS" in production_order and len(production_order["SHOT_DETAILS"]) > 1:
                last_known_shot = datetime.strptime(production_order["SHOT_DETAILS"][-2]["timestamp"],
                                                    constants.time_format)
                if (shot_timestamp - last_known_shot).total_seconds() > production_order["CYCLE TIME"]:

                    dt_start = last_known_shot + timedelta(seconds=production_order["CYCLE TIME"])
                    dt_stop = shot_timestamp
                    downtime_to_append = {
                        "start_time"
                        :
                            dt_start.strftime(constants.time_format),
                        "stop_time"
                        :
                            dt_stop.strftime(constants.time_format),
                        "reasonlist"
                        :
                            "Minor Stops",
                        "Mode"
                        :
                            "Software",
                        "details"
                        :
                            "Cycle time Exceeded.",
                        "status"
                        :
                            "Accept"
                    }
                    if "DOWNTIME" in production_order:
                        production_order["DOWNTIME"].append(downtime_to_append)
                    else:
                        production_order["DOWNTIME"] = []
                        production_order["DOWNTIME"].append(downtime_to_append)
                else:
                    pass
            else:
                pass

            newvalues = {"$set": production_order}
            production_orders.update_one(myquery, newvalues)
            print("SHOT DELAY DOWNTIME RECORDED.")


    else:
        print("NO PRODUCTION ORDER FOUND !")


def get_line_rejection_qty(order_details):
    total_line_rejections = 0
    shift = get_current_shift_details()
    # Calculation for Total Line Rejections for active shift

    if "REJECTION ANALYSIS" in order_details:
        for rejection in order_details["REJECTION ANALYSIS"]:
            if shift["SHIFT START TIME"] < datetime.strptime(rejection["timestamp"], constants.time_format) < shift[
                "SHIFT STOP TIME"]:
                if rejection["TYPE"] == "LINE REJECTION":
                    total_line_rejections += int(rejection["QUANTITY"])
                else:
                    pass
            else:
                pass
    else:
        pass

    return total_line_rejections


def get_line_rejection_weight(order_details):
    total_line_rejections = 0
    shift = get_current_shift_details()
    # Calculation for Total Line Rejections for active shift
    if shift is not None:
        if "REJECTION ANALYSIS" in order_details:
            for rejection in order_details["REJECTION ANALYSIS"]:
                if shift["SHIFT START TIME"] < datetime.strptime(rejection["timestamp"], constants.time_format) < shift[
                    "SHIFT STOP TIME"]:
                    if rejection["TYPE"] == "LINE REJECTION":
                        total_line_rejections += float(rejection["WEIGHT"])
                    else:
                        pass
                else:
                    pass
        else:
            pass

    return round(total_line_rejections, 2)


def get_rejection_weight(order_details):
    total_rejection_weight = 0
    shift = get_current_shift_details()
    # print(shift)
    if shift is not None:
        if "REJECTION ANALYSIS" in order_details:
            for rejection in order_details["REJECTION ANALYSIS"]:
                if shift["SHIFT START TIME"] < datetime.strptime(rejection["timestamp"], constants.time_format) < shift[
                    "SHIFT STOP TIME"]:
                    weight = float(rejection["WEIGHT"])
                    total_rejection_weight += weight
                else:
                    pass
        else:
            pass

    return total_rejection_weight


def get_downtime_overlaps(order_details):
    correct_downtimes = []
    if "DOWNTIME" in order_details:
        # CONVERT TO TIMESTAMPS ,CHECK ONLY ACCEPTED DOWNTIMES , FILTER OUT BAD ONES OR EMPTY STRINGS
        downtimes = []
        for downtime in order_details["DOWNTIME"]:
            temp_downtime = copy.deepcopy(downtime)
            if temp_downtime["status"] == "Accept" and ("reasonlist" in temp_downtime):
                if temp_downtime["reasonlist"] != "Minor Stops" and temp_downtime["Mode"] != "Software":
                    try:
                        temp_downtime["start_time"] = datetime.strptime(temp_downtime["start_time"],
                                                                        constants.time_format)
                        temp_downtime["stop_time"] = datetime.strptime(temp_downtime["stop_time"],
                                                                       constants.time_format)
                        downtimes.append(temp_downtime)
                    except:
                        pass

        # Arrange Downtimes in ascending order of start time
        downtimes = sorted(downtimes, key=lambda x: (x['start_time']))

        # print("=================================")
        # print(order_details["ORDER NUMBER (LEFT)"])
        # print("PRE - CLEANING DONWTIMES")
        for downtime in downtimes:
            # if "reasonlist" not in downtime:
            #    print(downtime)

            if downtime["reasonlist"] == "Mould Change":
                print(downtime)

        # FIND OVERLAPPING DOWNTIMES
        for i in range(len(downtimes)):
            start_time = downtimes[i]["start_time"]
            stop_time = downtimes[i]["stop_time"]
            if len(correct_downtimes) == 0:
                details = ""
                details = downtimes[i]["reasonlist"] + " - "
                details += downtimes[i]["start_time"].strftime(constants.time_format)
                details += " TO " + downtimes[i]["stop_time"].strftime(constants.time_format)
                downtimes[i]["details"] = details
                correct_downtimes.append(downtimes[i])

            else:
                flag_overlap = 0
                # print("=====================================")
                j = 0
                k = -1
                while j < len(correct_downtimes):
                    # for j in range(len(correct_downtimes)):
                    # print(j)
                    to_check_start_time = correct_downtimes[j]["start_time"]
                    to_check_stop_time = correct_downtimes[j]["stop_time"]
                    if j == k:
                        j = j + 1
                    elif to_check_start_time < start_time and to_check_stop_time < start_time:
                        j = j + 1
                    elif to_check_start_time > stop_time and to_check_stop_time > stop_time:
                        j = j + 1
                    elif to_check_start_time == start_time and to_check_stop_time == stop_time:
                        j = j + 1
                        flag_overlap += 1  # ignore completely
                    else:
                        # print("Downtime Overlap Occured")
                        # print(downtime["reasonlist"] ,to_check_start_time,to_check_stop_time )
                        # print(j,"=>",correct_downtimes[j]["reasonlist"],start_time,stop_time)
                        k = j
                        temp = {}

                        # GET THE MINIMUM OF START TIME AND MAXIMUM OF STOP TIME
                        if to_check_start_time < start_time:
                            temp["start_time"] = to_check_start_time
                        else:
                            temp["start_time"] = start_time
                        if to_check_stop_time > stop_time:
                            temp["stop_time"] = to_check_stop_time
                        else:
                            temp["stop_time"] = stop_time

                        if "reasonlist" in correct_downtimes[j]:
                            temp["reasonlist"] = correct_downtimes[j]["reasonlist"]
                        else:
                            temp["reasonlist"] = "NA"

                        # Append to reasonlists
                        if downtimes[i]["Mode"] == "Operator Input":
                            temp["reasonlist"] = downtimes[i]["reasonlist"]
                            # print("CHANGED REASON -" ,downtimes[i]["reasonlist"] )

                        '''if downtimes[i]["reasonlist"] != "Software" :
                            temp["reasonlist"] = downtimes[i]["reasonlist"]'''

                        temp["Mode"] = "Software"
                        temp["status"] = "Accept"
                        details = downtimes[i]["reasonlist"] + " - "
                        details += downtimes[i]["start_time"].strftime(constants.time_format)
                        details += " TO " + downtimes[i]["stop_time"].strftime(constants.time_format)
                        temp["details"] = correct_downtimes[j]["details"] + " , " + details

                        correct_downtimes[j] = temp

                        flag_overlap += 1
                        j = 0

                # print("=====================================")

                if flag_overlap == 0:
                    details = ""
                    details = downtimes[i]["reasonlist"] + " - "
                    details += downtimes[i]["start_time"].strftime(constants.time_format)
                    details += " TO " + downtimes[i]["stop_time"].strftime(constants.time_format)
                    downtimes[i]["details"] = details
                    correct_downtimes.append(downtimes[i])
                    # print("NO OVERLAP OCCURED. ADDING")
                    # print(downtime["reasonlist"], to_check_start_time, to_check_stop_time)
                    k = -1
                # print("TOTAL LENGTH = ", len(correct_downtimes))

        for downtime in correct_downtimes:
            if downtime["status"] == "Accept":
                try:
                    downtime["start_time"] = downtime["start_time"].strftime(constants.time_format)
                    downtime["stop_time"] = downtime["stop_time"].strftime(constants.time_format)
                    downtimes.append(downtime)
                except:
                    pass

    # print("POST - CLEANING DONWTIMES")
    '''for i in range(len(correct_downtimes)):
        #if "reasonlist" not in downtime :
        #    print(downtime)
        if correct_downtimes[i]["reasonlist"] == "Mould Change":

            print(i," => ",correct_downtimes[i])'''
    # print(correct_downtimes)
    return correct_downtimes


def get_runtime_overlaps(shift, machine):
    shift_details = get_all_active_production_orders_from_to(shift["SHIFT START TIME"], shift["SHIFT STOP TIME"])
    correct_runtimes = []
    # FIND OVERLAPPING DOWNTIMES
    for i in range(len(shift_details)):

        # get po start and stop within the required shift.
        start_time, stop_time = get_times_for_order_in_shift(shift_details[i], shift)
        print("---------------------------------------------")
        print(start_time)
        print(stop_time)
        if len(correct_runtimes) == 0:
            '''details = ""
            details = shift_details[i]["reasonlist"] + " - "
            details += shift_details[i]["ACTUAL_START"].strftime(constants.time_format)
            details += " TO " + downtimes[i]["ACTUAL_STOP"].strftime(constants.time_format)
            downtimes[i]["details"] = details'''
            temp = {}
            temp["start_time"] = start_time
            temp["stop_time"] = stop_time

            correct_runtimes.append(temp)
        else:
            flag_overlap = 0
            for j in range(len(correct_runtimes)):
                to_check_start_time = correct_runtimes[j]["start_time"]
                to_check_stop_time = correct_runtimes[j]["stop_time"]

                if to_check_start_time < start_time and to_check_stop_time < start_time:
                    pass
                elif to_check_start_time > stop_time and to_check_stop_time > stop_time:
                    pass
                else:
                    print("Overlap Occurred")
                    temp = {}

                    # GET THE MINIMUM OF START TIME AND MAXIMUM OF STOP TIME
                    if to_check_start_time < start_time:
                        temp["start_time"] = to_check_start_time
                    else:
                        temp["start_time"] = start_time

                    if to_check_stop_time > stop_time:
                        temp["stop_time"] = to_check_stop_time
                    else:
                        temp["stop_time"] = stop_time

                    '''# Append to reasonlists
                    if downtimes[i]["Mode"] == "Operator Input":
                        temp["reasonlist"] = downtimes[i]["reasonlist"]
                    temp["Mode"] = "Software"
                    temp["status"] = "Accept"
                    details = downtimes[i]["reasonlist"] + " - "
                    details += downtimes[i]["start_time"].strftime(constants.time_format)
                    details += " TO " + downtimes[i]["stop_time"].strftime(constants.time_format)
                    temp["details"] = correct_downtimes[j]["details"] + " , " + details'''

                    correct_runtimes[j] = temp
                    flag_overlap += 1
                    j = 0

            if flag_overlap == 0:
                '''details = ""
                details = downtimes[i]["reasonlist"] + " - "
                details += downtimes[i]["start_time"].strftime(constants.time_format)
                details += " TO " + downtimes[i]["stop_time"].strftime(constants.time_format)
                downtimes[i]["details"] = details'''
                temp = {}
                temp["start_time"] = start_time
                temp["stop_time"] = stop_time
                correct_runtimes.append(temp)
    '''for downtime in correct_downtimes:
        if downtime["status"] == "Accept":
            try:
                downtime["start_time"] = downtime["start_time"].strftime(constants.time_format)
                downtime["stop_time"] = downtime["stop_time"].strftime(constants.time_format)
                downtimes.append(downtime)
            except:
                pass'''
    print(correct_runtimes)

    return correct_runtimes


def get_total_downtime(order_details):
    total_downtime = 0
    correct_downtimes = get_downtime_overlaps(order_details)
    # print(len(correct_downtimes))
    # print(correct_downtimes)
    # convert to timestamps
    for downtime in correct_downtimes:
        temp_downtime = copy.deepcopy(downtime)
        temp_downtime["start_time"] = datetime.strptime(temp_downtime["start_time"], constants.time_format)
        temp_downtime["stop_time"] = datetime.strptime(temp_downtime["stop_time"], constants.time_format)
        duration = temp_downtime["stop_time"] - temp_downtime["start_time"]
        # print(duration)
        total_downtime += duration.total_seconds()

    total_downtime = round(total_downtime / 60, 2)
    return total_downtime


# GET TOTAL DOWNTIME FOR CURRENT SHIFT
def get_total_downtime1(order_details):
    # print(order_details["MACHINE"])
    total_downtime = 0
    correct_downtimes = get_downtime_overlaps(order_details)
    # print(len(correct_downtimes))
    # print(correct_downtimes)
    # convert to timestamps
    shift = get_current_shift_details()
    # print(correct_downtimes)
    # print("--------------------------------")
    for downtime in correct_downtimes:
        if "reasonlist" in downtime:  # got key error for reasonlist.
            if downtime["reasonlist"] != "Minor Stops":
                if (shift["SHIFT START TIME"] < datetime.strptime(downtime["start_time"], constants.time_format) <
                    shift["SHIFT STOP TIME"]) or \
                        (shift["SHIFT START TIME"] < datetime.strptime(downtime["stop_time"], constants.time_format) <
                         shift["SHIFT STOP TIME"]) or \
                        (shift["SHIFT START TIME"] > datetime.strptime(downtime["start_time"],
                                                                       constants.time_format) and shift[
                             "SHIFT STOP TIME"] < datetime.strptime(downtime["stop_time"], constants.time_format)):

                    temp_downtime = copy.deepcopy(downtime)
                    temp_downtime["start_time"] = datetime.strptime(temp_downtime["start_time"], constants.time_format)
                    temp_downtime["stop_time"] = datetime.strptime(temp_downtime["stop_time"], constants.time_format)
                    start_time = temp_downtime["start_time"]
                    stop_time = temp_downtime["stop_time"]

                    if temp_downtime["start_time"] < shift["SHIFT START TIME"]:
                        start_time = shift["SHIFT START TIME"]
                    else:
                        pass

                    if temp_downtime["stop_time"] > shift["SHIFT STOP TIME"]:
                        stop_time = shift["SHIFT STOP TIME"]
                    else:
                        pass

                    duration = stop_time - start_time
                    # print(duration)
                    total_downtime += duration.total_seconds()
        else:
            if (shift["SHIFT START TIME"] < datetime.strptime(downtime["start_time"], constants.time_format) < shift[
                "SHIFT STOP TIME"]) or \
                    (shift["SHIFT START TIME"] < datetime.strptime(downtime["stop_time"], constants.time_format) <
                     shift["SHIFT STOP TIME"]) or \
                    (shift["SHIFT START TIME"] > datetime.strptime(downtime["start_time"], constants.time_format) and
                     shift["SHIFT STOP TIME"] < datetime.strptime(downtime["stop_time"], constants.time_format)):

                temp_downtime = copy.deepcopy(downtime)
                temp_downtime["start_time"] = datetime.strptime(temp_downtime["start_time"], constants.time_format)
                temp_downtime["stop_time"] = datetime.strptime(temp_downtime["stop_time"], constants.time_format)
                start_time = temp_downtime["start_time"]
                stop_time = temp_downtime["stop_time"]

                if temp_downtime["start_time"] < shift["SHIFT START TIME"]:
                    start_time = shift["SHIFT START TIME"]
                else:
                    pass

                if temp_downtime["stop_time"] > shift["SHIFT STOP TIME"]:
                    stop_time = shift["SHIFT STOP TIME"]
                else:
                    pass

                duration = stop_time - start_time
                # print(duration)
                total_downtime += duration.total_seconds()

    total_downtime = round(total_downtime / 60, 2)
    # print("i ran successfully")
    return total_downtime


def kpi_cron_job(current_time):
    get_current_times = current_time
    give = get_all_active_production_orders()
    # kpi_calculated_data={"Oee":50.0,"Productivity":60.0,"Quality":60.0,"Availability":30.0,"Total Ok Part weight(Kgs)":30.0,"Total Raw Material Used":40.0,"Actual Material Consumption per part":35.6,"Energy Consumption Total":45.50,"Parts per KwH":70.30,"Rejection":40.30,"Scrap":20.10,"Yeild":40.20,"PPM":90.10,"Time":get_current_time}
    kpi_raw_data = {"Oee": "NA", "Productivity": "NA", "Quality": "NA", "Availability": "NA",
                    "Total Ok Part weight(Kgs)": "NA", "Total Raw Material Used": "NA",
                    "Actual Material Consumption per part": "NA", "Energy Consumption Total": "NA",
                    "Parts per KwH": "NA", "Rejection": "NA", "Scrap": "NA", "Yeild": "NA", "PPM": "NA",
                    "Time": get_current_times.strftime(constants.time_format)}

    # ------------------------------------------- V A T S A L ------------------------------------------------------------------------

    # get current shift
    shift = get_current_shift_details()

    # ----------------  GOES TO SHIFT RECORD (LATER USED FOR CHARTS) ----------------------
    kpi_all = {}
    kpi_all["Oee"] = []
    kpi_all["Productivity"] = []
    kpi_all["Availability"] = []
    kpi_all["Quality"] = []
    kpi_all["timestamp"] = current_time
    # -------------------------------------------------------------------------------------
    for i in give:
        # print("#######################################################################################")

        # print(i['MACHINE'])

        # print("#######################################################################################")
        given_p_key_left = i['ORDER NUMBER (LEFT)']
        given_p_key_right = i['ORDER NUMBER (RIGHT)']
        given_p_key_machine = i['MACHINE']
        temp = copy.deepcopy(kpi_raw_data)

        planned_downtime = i["START UP TIME (MIN)"] + i["MOULD CHANGE TIME (MIN)"]
        # print('planned Downtime :', planned_downtime)
        # downtime = get_total_downtime1(i)
        try:
            # print("total_time_cal:",(get_current_times - shift["SHIFT START TIME"]).total_seconds())
            total_time = round(
                ((get_current_times - shift["SHIFT START TIME"]).total_seconds() / 60) - planned_downtime, 2)
            downtime = get_total_downtime1(i)
            # print('downtime raw : ', downtime)
            if downtime > planned_downtime:
                downtime = downtime - planned_downtime
            runtime = total_time - downtime
            # print(total_time)
            # print(runtime)
        except:
            # print("xxxxxxxxxxxxxxxxxxxxxxx machine in except block XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
            # print(i['MACHINE'])

            total_time = 0
            runtime = 0
        # print('total time : ',total_time)
        # print('runtime : ', runtime)

        try:
            # Filter shots for the shift
            all_cycle_time = []
            shot_counter = 0
            for shot in i["SHOT_DETAILS"]:
                if shift["SHIFT START TIME"] < datetime.strptime(shot["timestamp"], constants.time_format) < shift[
                    "SHIFT STOP TIME"]:
                    shot_counter += 1
                    all_cycle_time.append(float(shot['CYCLE TIME']))

            total_shots = shot_counter
            average_cycle_time = sum(all_cycle_time) / len(all_cycle_time)
        except:
            total_shots = 0

        # function to calculate total rejection weight

        total_rejection_weight = get_rejection_weight(i)
        # print('total_rejection_weight : ',total_rejection_weight)

        # function to calculate total rejection qty
        total_line_rejection_weight = get_line_rejection_weight(i)
        total_rejection_qty = get_line_rejection_qty(i)

        try:
            total_ok_shots = total_shots - total_rejection_qty
        except:
            total_ok_shots = 0

        # print("total_ok_shots : ", total_ok_shots)

        try:
            temp["Availability"] = round((runtime / total_time) * 100, 2)
            # print("Availibilty ",temp["Availability"])
            # appending to all availility
            kpi_all["Availability"].append(round((runtime / total_time) * 100, 2))
        except:
            pass

        try:
            Achieved_Shot_Rate_per_hour_cal = (3600 * total_shots) / total_time
        except:
            Achieved_Shot_Rate_per_hour_cal = 0

        try:
            temp["Productivity"] = (average_cycle_time / i["CYCLE TIME"]) * 100
            # print("productivity :",temp["Productivity"])
            if temp["Productivity"] > 100:
                print("Productivity Clipped to 100")
                temp["Productivity"] = 100

            kpi_all["Productivity"].append(round(temp["Productivity"], 2))
        except:
            pass

        try:
            temp["Total Ok Part weight(Kgs)"] = (total_ok_shots * float(i["PART WEIGHT"])) / 1000
        except:
            pass

        try:
            temp["Total Raw Material Used"] = total_rejection_weight + temp["Total Ok Part weight(Kgs)"]
        except:
            pass

        try:
            temp["Quality"] = round((total_ok_shots / total_shots) * 100, 2)
            # print("quality ",temp["Quality"])
            kpi_all["Quality"].append(round((total_ok_shots / total_shots) * 100, 2))
        except:
            pass

        try:
            temp["Oee"] = (temp["Quality"] * temp["Availability"] * temp["Productivity"]) / (100 * 100)
            # appending OEE to all Oee
            kpi_all["Oee"].append(
                round((temp["Quality"] * temp["Availability"] * temp["Productivity"]) / (100 * 100), 2))


        except:
            pass

        try:
            temp["Actual Material Consumption per  part"] = temp["Total Raw Material Used"] / total_ok_shots
        except:
            pass
        try:
            temp["Rejection"] = (total_line_rejection_weight / temp["Total Raw Material Used"]) * 100
        except:
            pass

        try:
            temp["Scrap"] = (total_rejection_weight / temp["Total Raw Material Used"]) * 100

        except:
            pass

        try:
            temp["Yeild"] = (temp["Total Ok Part weight(Kgs)"] / temp["Total Raw Material Used"]) * 100
        except:
            pass

        try:
            temp["Energy Consumption Total"] = temp["ENERGY DETAILS"]["energy_difference"]
        except:
            pass

        try:
            temp["KwH per Part"] = temp["Energy Consumption Total"] / total_ok_shots
        except:
            pass

        # if available convert them into round 2

        try:
            temp["Oee"] = round(temp["Oee"], 2)
        except:
            pass
        try:
            temp["Productivity"] = round(temp["Productivity"], 2)
        except:
            pass
        try:
            temp["Quality"] = round(temp["Quality"], 2)
        except:
            pass
        try:
            temp["Availability"] = round(temp["Availability"], 2)
        except:
            pass
        try:
            temp["Total Ok Part weight(Kgs)"] = round(temp["Total Ok Part weight(Kgs)"], 2)
        except:
            pass
        try:
            temp["Total Raw Material Used"] = round(temp["Total Raw Material Used"], 2)
        except:
            pass
        try:
            temp["Actual Material Consumption per part"] = round(temp["Actual Material Consumption per part"], 2)
        except:
            pass
        try:
            temp["Energy Consumption Total"] = round(temp["Energy Consumption Total"], 2)
        except:
            pass
        try:
            temp["Parts per KwH"] = round(temp["Parts per KwH"], 2)
        except:
            pass
        try:
            temp["Rejection"] = round(temp["Rejection"], 2)
        except:
            pass
        try:
            temp["Scrap"] = round(temp["Scrap"], 2)
        except:
            pass
        try:
            temp["Yeild"] = round(temp["Yeild"], 2)
        except:
            pass

        if "kpi" in i:
            i["kpi"].append(temp)
        else:
            i["kpi"] = []
            i["kpi"].append(temp)
        # print("----------KPI CRON JOB------------")
        # print(i["MACHINE"])
        # print(temp)
        # print("-----------------------------")
        update_specific_production_order(i)
        # pprint(temp)
    # print(kpi_all)
    if len(kpi_all['Oee']) != 0:
        kpi_all['Oee'] = round(sum(kpi_all['Oee']) / len(kpi_all['Oee']), 2)  # average
    else:
        kpi_all['Oee'] = 0

    if len(kpi_all['Productivity']) != 0:
        kpi_all['Productivity'] = round(sum(kpi_all['Productivity']) / len(kpi_all['Productivity']), 2)  # average
    else:
        kpi_all['Productivity'] = 0

    if len(kpi_all['Availability']) != 0:
        kpi_all['Availability'] = round(sum(kpi_all['Availability']) / len(kpi_all['Availability']), 2)  # average
    else:
        kpi_all['Availability'] = 0

    if len(kpi_all['Quality']) != 0:
        kpi_all['Quality'] = round(sum(kpi_all['Quality']) / len(kpi_all['Quality']), 2)  # average
    else:
        kpi_all['Quality'] = 0

    append_kpi_to_shift_record(kpi_all)
    print("KPI DETAILS UPDATED TO SHIFT RECORDS")
    # time.sleep(10)
    # print(kpi_all)


def retrive_kpi_data(dt):
    # print("selected machines", dt['m_name'])
    n = 10
    oee_val = []
    productivity_val = []
    quality_val = []
    availability_val = []
    total_ok_part_weight_val = []
    total_raw_material_used_val = []
    actual_material_consumption_per_part_val = []
    energy_consumption_total_val = []
    parts_per_val = []
    rejection_val = []
    scrap_val = []
    yeild_val = []
    PPM_val = []
    kpi_data = {}
    # myquery = {"MACHINE": "JSW 450T-III", "ACTION": "In Process"}
    myquery = {"MACHINE": dt['m_name'], "ACTION": "In Process"}
    dt = production_orders.find_one(myquery, {'_id': False})
    machin_kpi_list = dt['kpi']
    main_list = []
    for a in machin_kpi_list:
        if (a["Oee"] == "NA" or a["Productivity"] == "NA" or a["Quality"] == "NA" or a["Availability"] == "NA" or a[
            "Total Ok Part weight(Kgs)"] == "NA" or a["Total Raw Material Used"] == "NA" or a[
            "Actual Material Consumption per part"] == "NA" or a["Energy Consumption Total"] == "NA" or a[
            "Parts per KwH"] == "NA" or a["Rejection"] == "NA" or a["Scrap"] == "NA" or a["Yeild"] == "NA" or a[
            "PPM"] == "NA"):
            pass
        else:
            main_list.append(a)
    latest_kpi = ""
    selected_machin_kpi = main_list
    if len(selected_machin_kpi) > 1:
        latest_kpi = selected_machin_kpi[-1]
    if len(selected_machin_kpi) == 1:
        latest_kpi = selected_machin_kpi

    last_updated = selected_machin_kpi[-n:]
    if (len(last_updated) == 0):
        # print("last updated=",last_updated)
        kpi_data['oee'] = oee_val
        kpi_data['productivity'] = productivity_val
        kpi_data['quality'] = quality_val
        kpi_data['availability'] = availability_val
        kpi_data['total_ok_part_weight'] = total_ok_part_weight_val
        kpi_data['total_raw_material_used'] = total_raw_material_used_val
        kpi_data['actual_material_consumption_per_part'] = actual_material_consumption_per_part_val
        kpi_data['energy_consumption_total'] = energy_consumption_total_val
        kpi_data['parts_per'] = parts_per_val
        kpi_data['rejection'] = rejection_val
        kpi_data['scrap'] = scrap_val
        kpi_data['yeild'] = yeild_val
        kpi_data['PPM'] = PPM_val

    if (len(last_updated) > 0):
        # print("last updated=",last_updated)
        for i in last_updated:
            oee_val.append(i['Oee'])
            productivity_val.append(i['Productivity'])
            quality_val.append(i['Quality'])
            availability_val.append(i['Availability'])
            total_ok_part_weight_val.append(i['Total Ok Part weight(Kgs)'])
            total_raw_material_used_val.append(i['Total Raw Material Used'])
            actual_material_consumption_per_part_val.append(i['Actual Material Consumption per part'])
            energy_consumption_total_val.append(i['Energy Consumption Total'])
            parts_per_val.append(i['Parts per KwH'])
            rejection_val.append(i['Rejection'])
            scrap_val.append(i['Scrap'])
            yeild_val.append(i['Yeild'])
            PPM_val.append(i['PPM'])
            kpi_data['oee'] = oee_val
            kpi_data['productivity'] = productivity_val
            kpi_data['quality'] = quality_val
            kpi_data['availability'] = availability_val
            kpi_data['total_ok_part_weight'] = total_ok_part_weight_val
            kpi_data['total_raw_material_used'] = total_raw_material_used_val
            kpi_data['actual_material_consumption_per_part'] = actual_material_consumption_per_part_val
            kpi_data['energy_consumption_total'] = energy_consumption_total_val
            kpi_data['parts_per'] = parts_per_val
            kpi_data['rejection'] = rejection_val
            kpi_data['scrap'] = scrap_val
            kpi_data['yeild'] = yeild_val
            kpi_data['PPM'] = PPM_val

    kpi_data['latest_kpi_val'] = latest_kpi
    kpi_data['target_oee'] = 100
    kpi_data['target_prod'] = 100
    kpi_data['target_qual'] = 100
    kpi_data['target_aval'] = 100
    kpi_data['change_oee'] = -100
    kpi_data['change_prod'] = -100
    kpi_data['change_qual'] = -100
    kpi_data['change_aval'] = -100

    # print("kpi_data=",kpi_data)
    return kpi_data


'''
=================================================================================================================
DOWNTIME
=================================================================================================================
'''


def get_production_order_from_machine(data):
    # Convert Timestamp to datettime
    timestamp = datetime.strptime(data["timestamp"], constants.time_format)

    # check if there is order is in a timestamp
    # myquery = {"$and": [{"ACTUAL_START": {"$lte": timestamp}}, {"ACTUAL_STOP": "-"}], "MACHINE": data["machine"]}
    myquery = {"MACHINE": data["machine"], "ACTION": "In Process"}
    production_order = production_orders.find_one(myquery, {'_id': False, "kpi": False})
    # production_order = production_orders.find_one(myquery, {'_id': False,'kpi':False})
    if production_order is not None:
        return production_order
    else:
        return None


def get_production_order_with_KPI(data):
    # Convert Timestamp to datettime
    # timestamp = datetime.strptime(data["timestamp"], constants.time_format)

    # check if there is order is in a timestamp
    # myquery = {"$and": [{"ACTUAL_START": {"$lte": timestamp}}, {"ACTUAL_STOP": "-"}], "MACHINE": data["machine"]}
    myquery = {"MACHINE": data["machine"], "ACTION": "In Process"}
    production_order = production_orders.find_one(myquery, {'_id': False})
    # production_order = production_orders.find_one(myquery, {'_id': False,'kpi':False})
    if production_order is not None:
        return production_order
    else:
        return None


def start_current_downtime_status(data, downtime_status):
    # print(production_order)
    myquery = {"ORDER NUMBER (LEFT)": str(data["ORDER NUMBER (LEFT)"]),
               "ORDER NUMBER (RIGHT)": str(data["ORDER NUMBER (RIGHT)"])}
    production_order = production_orders.find_one(myquery, {'_id': False, 'kpi': False})
    if production_order is not None:
        production_order["CURRENT_DOWNTIME_STATUS"] = copy.deepcopy(downtime_status)
        newvalues = {"$set": production_order}
        production_orders.update_one(myquery, newvalues)
        print("CURRENT DOWNTIME STATUS RECORDED")


def stop_current_downtime_status(data, downtime_status):
    # print(production_order)
    myquery = {"ORDER NUMBER (LEFT)": str(data["ORDER NUMBER (LEFT)"]),
               "ORDER NUMBER (RIGHT)": str(data["ORDER NUMBER (RIGHT)"])}
    production_order = production_orders.find_one(myquery, {'_id': False, 'kpi': False})
    if production_order is not None:
        production_order["CURRENT_DOWNTIME_STATUS"]["downtime_stop"] = downtime_status["downtime_stop"]
        production_order["CURRENT_DOWNTIME_STATUS"]["downtime_type"] = downtime_status["downtime_type"]
        newvalues = {"$set": production_order}
        production_orders.update_one(myquery, newvalues)
        print("CURRENT DOWNTIME STATUS RECORDED")


def get_current_downtime_status(data):
    myquery = {"ORDER NUMBER (LEFT)": str(data["ORDER NUMBER (LEFT)"]),
               "ORDER NUMBER (RIGHT)": str(data["ORDER NUMBER (RIGHT)"])}
    production_order = production_orders.find_one(myquery, {'_id': False, 'kpi': False})
    status = 0
    to_return = {}
    if production_order is not None:
        if "CURRENT_DOWNTIME_STATUS" in production_order:
            status = 1
            to_return = production_order["CURRENT_DOWNTIME_STATUS"]
    if status == 0:
        to_return = {
            "downtime_start": "",
            "downtime_stop": "",
            "downtime_status": "false",
            "downtime_type": ""}
        start_current_downtime_status(data, to_return)
    return to_return


def update_downtime(data):
    # print(production_order)
    myquery = {"ORDER NUMBER (LEFT)": str(data["ORDER NUMBER (LEFT)"]),
               "ORDER NUMBER (RIGHT)": str(data["ORDER NUMBER (RIGHT)"])}
    production_order = production_orders.find_one(myquery, {'_id': False, 'kpi': False})
    if production_order is not None:
        print(data)
        to_append = {

            'start_time': data['start_time'],
            'stop_time': data['stop_time'],
            'reasonlist': data['reasonlist'],
            'details': data['details'],
            'Mode': data['Mode'],
            'status': data['status']
        }

        if "DOWNTIME" in production_order:
            production_order["DOWNTIME"].append(to_append)
        else:
            production_order["DOWNTIME"] = []
            production_order["DOWNTIME"].append(to_append)

        newvalues = {"$set": production_order}
        production_orders.update_one(myquery, newvalues)
        to_return = production_order
        state = True
        print("DOWNTIME RECORDED")
    else:
        to_return = {}
        state = False
        print("NO PRODUCTION ORDER FOUND")

    return to_return, state


def update_downtime_charts(data):
    # print(production_order)
    myquery = {"ORDER NUMBER (LEFT)": str(data["ORDER NUMBER (LEFT)"]),
               "ORDER NUMBER (RIGHT)": str(data["ORDER NUMBER (RIGHT)"])}
    production_order = production_orders.find_one(myquery, {'_id': False, 'kpi': False})

    to_send_downtime_chart = {
        "downtime_types": constants.downtime_type,
        "downtime_time": constants.downtime_time,
        "pie_chart_data": [
            {"value": 0, "name": 'Total Time'},
            {"value": 0, "name": 'Total Downtime'},
            {"value": 0, "name": 'Total Runtime'},

        ]
    }

    if production_order is not None:

        # =============================================================================================================
        # Get 2 arrays as a summation of the downtimes
        # DOWNTIME ANALYSIS CODE
        if "DOWNTIME" in production_order:
            data = production_order["DOWNTIME"]
            downtime_types = constants.downtime_type
            downtime_time = constants.downtime_time
            total_downtime = 0

            for record in data:
                # print(record)
                for downtime_type in range(len(downtime_types)):
                    if record["reasonlist"] == downtime_types[downtime_type]:
                        # print(record["reasonlist"])
                        format_str = constants.time_format  # The format
                        start_time = datetime.strptime(record["start_time"], format_str)
                        stop_time = datetime.strptime(record["stop_time"], format_str)
                        downtime = round((stop_time - start_time).total_seconds() / 60.0, 2)
                        downtime_time[downtime_type] = round(downtime_time[downtime_type] + downtime, 2)
                        total_downtime = total_downtime + downtime

            # print(downtime_types)
            # print(downtime_time)

            # =============================================================================================================
            # RUNTIME ANALYSIS CODE
            # Current Time - Actual Shift Start Time  = Total Time
            # Total Time - Downtime = Run Time

            # PRD / HR = Total Qty - Rejected Qty / (Total Run Time / 60 )
            # Cycle Time = Total Time / (Total Qty - Rejected Qty)
            # Achieved Shots =  Total Qty / (Total Run Time / 60 )
            # Ideal Achieved Shots =  ( 3600 ) / (Cycle Time)

            current_time = datetime.now() + timedelta(seconds=constants.timezone_offset)
            production_order["DOWNTIME_ANALYSIS"] = {
                "TOTAL_TIME": 0,
                "DOWN_TIME": 0,
                "RUN_TIME": 0,

            }

            try:
                production_order["DOWNTIME_ANALYSIS"]["TOTAL_TIME"] = round(
                    (current_time - production_order["ACTUAL_START"]).total_seconds() / 60.0, 2)
                production_order["DOWNTIME_ANALYSIS"]["DOWN_TIME"] = round(total_downtime, 2)
                production_order["DOWNTIME_ANALYSIS"]["RUN_TIME"] = round(
                    production_order["DOWNTIME_ANALYSIS"]["TOTAL_TIME"] - production_order["DOWNTIME_ANALYSIS"][
                        "DOWN_TIME"], 2)

            except:
                production_order["DOWNTIME_ANALYSIS"]["TOTAL_TIME"] = 0
                production_order["DOWNTIME_ANALYSIS"]["DOWN_TIME"] = 0
                production_order["DOWNTIME_ANALYSIS"]["RUN_TIME"] = 0

            to_send_downtime_chart = {
                "downtime_types": downtime_types,
                "downtime_time": downtime_time,
                "pie_chart_data": [
                    {"value": production_order["DOWNTIME_ANALYSIS"]["DOWN_TIME"], "name": 'Total Downtime'},
                    {"value": production_order["DOWNTIME_ANALYSIS"]["RUN_TIME"], "name": 'Total Runtime'},

                ]
            }
            print(to_send_downtime_chart)

            newvalues = {"$set": production_order}
            production_orders.update_one(myquery, newvalues)
            print("DOWNTIME RECORDED")

    return to_send_downtime_chart


def update_downtime_status(data):
    # print(production_order)
    myquery = {"ORDER NUMBER (LEFT)": str(data["ORDER NUMBER (LEFT)"]),
               "ORDER NUMBER (RIGHT)": str(data["ORDER NUMBER (RIGHT)"])}
    production_order = production_orders.find_one(myquery, {'_id': False, 'kpi': False})
    if production_order is not None:
        if "DOWNTIME" in production_order:
            for record in production_order["DOWNTIME"]:
                # print (record["start_time"])
                if record["start_time"] == data["start_time"] and record["stop_time"] == data["stop_time"]:
                    record["status"] = data["status"]
                    print("DOWNTIME RECORD FOUND AND UPDATED !")
                    newvalues = {"$set": production_order}
                    production_orders.update_one(myquery, newvalues)
                    print("DOWNTIME RECORDED")


def update_downtime_type(data):
    # print(production_order)
    myquery = {"ORDER NUMBER (LEFT)": str(data["ORDER NUMBER (LEFT)"]),
               "ORDER NUMBER (RIGHT)": str(data["ORDER NUMBER (RIGHT)"])}
    production_order = production_orders.find_one(myquery, {'_id': False, 'kpi': False})
    if production_order is not None:
        if "DOWNTIME" in production_order:
            for record in production_order["DOWNTIME"]:
                # print (record["start_time"])
                if record["start_time"] == data["start_time"] and record["stop_time"] == data["stop_time"]:
                    record["reasonlist"] = data["reasonlist"]
                    print("DOWNTIME RECORD FOUND AND UPDATED !")
                    newvalues = {"$set": production_order}
                    production_orders.update_one(myquery, newvalues)
                    print("DOWNTIME RECORDED")


'''
=================================================================================================================
REJECTION
=================================================================================================================
'''


def update_rejection(data):
    # print(production_order)

    myquery = {"ORDER NUMBER (LEFT)": str(data["ORDER NUMBER (LEFT)"]),
               "ORDER NUMBER (RIGHT)": str(data["ORDER NUMBER (RIGHT)"])}
    production_order = production_orders.find_one(myquery, {'_id': False, 'kpi': False})
    print(data)

    if production_order is not None:
        to_append = {

            'REJECTION_QUANTITY': data["REJECTION_QUANTITY"],
            'REJECTION_WEIGHT_MANUAL': data["REJECTION_WEIGHT_MANUAL"],
            'reasonlist': data["reasonlist"],
            'details': data["details"],
            'Mode': data["Mode"],
            'status': data['status'],
            'ORDER MODE': data["ORDER MODE"],
            "timestamp": datetime.now().strftime(constants.time_format),
            "Input By": data["Input By"],
        }

        if "REJECTION ANALYSIS" in production_order:
            if "REJECTION" in production_order["REJECTION ANALYSIS"]:
                production_order["REJECTION ANALYSIS"]["REJECTION"].append(to_append)
            else:
                production_order["REJECTION ANALYSIS"]["REJECTION"] = []
                production_order["REJECTION ANALYSIS"]["REJECTION"].append(to_append)
        else:
            production_order["REJECTION ANALYSIS"] = {}
            production_order["REJECTION ANALYSIS"]["REJECTION"] = []
            production_order["REJECTION ANALYSIS"]["REJECTION"].append(to_append)

        newvalues = {"$set": production_order}
        production_orders.update_one(myquery, newvalues)
        print("REJECTION RECORDED")
    else:
        print("NO PRODUCTION ORDER FOUND")

    # =============================================================================================================
    # Get 2 arrays as a summation of the downtimes
    # REJECTION ANALYSIS CODE
    to_send_rejection_chart = {
        "rejection_types": constants.rejection_type,
        "rejection_qty": constants.rejection_qty,
        "status": "Cannot Update Chart. Value Input Error."
    }
    if "REJECTION ANALYSIS" in production_order:
        if "REJECTION" in production_order["REJECTION ANALYSIS"]:
            data = production_order["REJECTION ANALYSIS"]["REJECTION"]
            rejection_types = constants.rejection_type
            rejection_qty = constants.rejection_qty

            total_rejection_weight = 0
            total_rejection_qty = 0
            rejection_qty_right = 0
            rejection_qty_left = 0
            try:
                for record in data:
                    # print(record)
                    for rejection_type in range(len(rejection_types)):
                        if record["reasonlist"] == rejection_types[rejection_type]:
                            # print(record["reasonlist"])
                            # downtime_time[downtime_type] = round(downtime_time[downtime_type] + downtime, 2)
                            rejection_qty[rejection_type] = int(
                                rejection_qty[rejection_type] + int(record['REJECTION_QUANTITY']))
                            total_rejection_weight = total_rejection_weight + float(record['REJECTION_WEIGHT_MANUAL'])
                            total_rejection_qty = total_rejection_qty + int(record['REJECTION_QUANTITY'])
                            if "ORDER MODE" in record:
                                if record["ORDER MODE"] == "RIGHT":
                                    print("Found Right")
                                    rejection_qty_right = rejection_qty_right + int(record['REJECTION_QUANTITY'])
                                elif record["ORDER MODE"] == "LEFT":
                                    print("Found Left")
                                    rejection_qty_left = rejection_qty_left + int(record['REJECTION_QUANTITY'])

                to_send_rejection_chart = {
                    "rejection_types": rejection_types,
                    "rejection_qty": rejection_qty,
                    "status": "Chart successfully updated."
                }
                print(to_send_rejection_chart)

                production_order["REJECTION ANALYSIS"]["TOTAL_LINE_REJECTION_WEIGHT"] = total_rejection_weight
                production_order["REJECTION ANALYSIS"]["TOTAL_LINE_REJECTION_QTY"] = total_rejection_qty
                production_order["REJECTION ANALYSIS"]["TOTAL_LINE_REJECTION_QTY (RIGHT)"] = rejection_qty_right
                production_order["REJECTION ANALYSIS"]["TOTAL_LINE_REJECTION_QTY (LEFT)"] = rejection_qty_left

                newvalues = {"$set": production_order}
                production_orders.update_one(myquery, newvalues)
                print("LINE REJECTION RECORDED")
            except:
                pass
    return to_send_rejection_chart


def update_rejection_chart(data):
    # print(production_order)
    to_send_rejection_chart = {}
    myquery = {"ORDER NUMBER (LEFT)": str(data["ORDER NUMBER (LEFT)"]),
               "ORDER NUMBER (RIGHT)": str(data["ORDER NUMBER (RIGHT)"])}
    production_order = production_orders.find_one(myquery, {'_id': False, 'kpi': False})
    to_send_rejection_chart = {
        "rejection_types": copy.deepcopy(constants.rejection_type),
        "rejection_qty": copy.deepcopy(constants.rejection_qty),
        "status": "Cannot Update Chart. Value Input Error."
    }

    if production_order is not None:
        # =============================================================================================================
        # Get 2 arrays as a summation of the downtimes
        # REJECTION ANALYSIS CODE

        if "REJECTION ANALYSIS" in production_order:
            if "REJECTION" in production_order["REJECTION ANALYSIS"]:
                data = production_order["REJECTION ANALYSIS"]["REJECTION"]
                rejection_types = constants.rejection_type
                rejection_qty = constants.rejection_qty

                total_rejection_weight = 0

                for record in data:
                    # print(record)
                    for rejection_type in range(len(rejection_types)):
                        if record["reasonlist"] == rejection_types[rejection_type]:
                            # print(record["reasonlist"])
                            # downtime_time[downtime_type] = round(downtime_time[downtime_type] + downtime, 2)
                            rejection_qty[rejection_type] = int(
                                rejection_qty[rejection_type] + int(record['REJECTION_QUANTITY']))
                            total_rejection_weight = float(record['REJECTION_WEIGHT_MANUAL'])

                to_send_rejection_chart = {
                    "rejection_types": rejection_types,
                    "rejection_qty": rejection_qty,
                    "status": "Chart successfully updated!"
                }
                print(to_send_rejection_chart)
            else:
                to_send_rejection_chart = {
                    "rejection_types": copy.deepcopy(constants.rejection_type),
                    "rejection_qty": [0, 0, 0, 0, 0, 0, 0,
                                      0, 0, 0, 0, 0, 0,
                                      0, 0, 0, 0],
                    "status": "No Line Rejection Record Found."
                }
                print(to_send_rejection_chart)
                print("------IN this loop---------")
        else:
            to_send_rejection_chart = {
                "rejection_types": copy.deepcopy(constants.rejection_type),
                "rejection_qty": [0, 0, 0, 0, 0, 0, 0,
                                  0, 0, 0, 0, 0, 0,
                                  0, 0, 0, 0],
                "status": "No Line Rejection Record Found."
            }
            print(to_send_rejection_chart)
            print("------IN this loop---------")
    # except:
    #    pass

    return to_send_rejection_chart


def update_rejection_piechart(data):
    # print(production_order)

    myquery = {"ORDER NUMBER (LEFT)": str(data["ORDER NUMBER (LEFT)"]),
               "ORDER NUMBER (RIGHT)": str(data["ORDER NUMBER (RIGHT)"])}
    production_order = production_orders.find_one(myquery, {'_id': False, 'kpi': False})

    to_send_rejection_chart = {
        "status": "Cannot Update Chart. Value Input Error.",
        "data": [
            {'value': 0, 'name': 'Total Rejections'},
            {'value': 0, 'name': 'Process Scrap'},
            {'value': 0, 'name': 'Total Startup'},

        ]
    }
    try:
        if production_order is not None:
            # =============================================================================================================

            total_rejection_kg = 0
            process_scrap_kg = 0
            startup_kg = 0
            if "REJECTION ANALYSIS" in production_order:
                if "TOTAL_LINE_REJECTION_WEIGHT" in production_order["REJECTION ANALYSIS"]:
                    total_rejection_kg = production_order["REJECTION ANALYSIS"]["TOTAL_LINE_REJECTION_WEIGHT"]
                if "PROCESS_SCRAP" in production_order["REJECTION ANALYSIS"]:
                    process_scrap_kg = production_order["REJECTION ANALYSIS"]["PROCESS_SCRAP"]
                if "STARTUP_REJECTION" in production_order["REJECTION ANALYSIS"]:
                    startup_kg = production_order["REJECTION ANALYSIS"]["STARTUP_REJECTION"][
                        "TOTAL_STARTUP_REJECTION_KG"]

                to_send_rejection_chart = {

                    "data": [{'value': total_rejection_kg, 'name': 'Total Rejections (Kg)'},
                             {'value': process_scrap_kg, 'name': 'Process Scrap (Kg)'},
                             {'value': startup_kg, 'name': 'Total Startup (Kg)'}],
                    "status": "Chart Successfully updated!"

                }

                print(to_send_rejection_chart)
            else:
                to_send_rejection_chart = {
                    "status": "No Rejection Record found.",
                    "data": [
                        {'value': 0, 'name': 'Total Rejections'},
                        {'value': 0, 'name': 'Process Scrap'},
                        {'value': 0, 'name': 'Total Startup'},

                    ]
                }
        else:
            to_send_rejection_chart = {
                "status": "No Rejection Record found.",
                "data": [
                    {'value': 0, 'name': 'Total Rejections'},
                    {'value': 0, 'name': 'Process Scrap'},
                    {'value': 0, 'name': 'Total Startup'},

                ]
            }

    except:
        pass

    return to_send_rejection_chart


def update_startup_rejection(data):
    myquery = {"ORDER NUMBER (LEFT)": str(data["ORDER NUMBER (LEFT)"]),
               "ORDER NUMBER (RIGHT)": str(data["ORDER NUMBER (RIGHT)"])}
    production_order = production_orders.find_one(myquery, {'_id': False, 'kpi': False})

    # If any of the 4 fields is blank convert to 0

    if data["STARTUP_REJECTION_KG (LEFT)"] == "":
        data["STARTUP_REJECTION_KG (LEFT)"] = 0

    if data['STARTUP_SCRAP_KG (LEFT)'] == "":
        data["STARTUP_SCRAP_KG (LEFT)"] = 0

    if data["STARTUP_REJECTION_KG (RIGHT)"] == "":
        data["STARTUP_REJECTION_KG (RIGHT)"] = 0

    if data['STARTUP_SCRAP_KG (RIGHT)'] == "":
        data["STARTUP_SCRAP_KG (RIGHT)"] = 0

    if production_order is not None:
        to_insert = {

            'STARTUP_REJECTION_KG (LEFT)': round(float(data["STARTUP_REJECTION_KG (LEFT)"]), 2),
            'STARTUP_SCRAP_KG (LEFT)': round(float(data["STARTUP_SCRAP_KG (LEFT)"]), 2),

            'STARTUP_REJECTION_KG (RIGHT)': round(float(data["STARTUP_REJECTION_KG (RIGHT)"]), 2),
            'STARTUP_SCRAP_KG (RIGHT)': round(float(data["STARTUP_SCRAP_KG (RIGHT)"]), 2),

            "TOTAL_STARTUP_REJECTION_KG": round(
                float(data["STARTUP_REJECTION_KG (LEFT)"]) + float(data["STARTUP_SCRAP_KG (LEFT)"]) + float(
                    data["STARTUP_REJECTION_KG (RIGHT)"]) + float(data["STARTUP_SCRAP_KG (RIGHT)"]), 2)
        }

        if "REJECTION ANALYSIS" in production_order:
            if "STARTUP_REJECTION" in production_order["REJECTION ANALYSIS"]:
                production_order["REJECTION ANALYSIS"]["STARTUP_REJECTION"] = to_insert
            else:
                production_order["REJECTION ANALYSIS"]["STARTUP_REJECTION"] = to_insert
        else:
            production_order["REJECTION ANALYSIS"] = {}
            production_order["REJECTION ANALYSIS"]["STARTUP_REJECTION"] = to_insert

        newvalues = {"$set": production_order}
        production_orders.update_one(myquery, newvalues)
        print("STARTUP REJECTION  RECORDED")
        print(to_insert)

        return to_insert
    else:
        print("NO PRODUCTION ORDER FOUND")
        to_insert = {
            'STARTUP_REJECTION_KG (LEFT)': 0,
            'STARTUP_SCRAP_KG (LEFT)': 0,
            'STARTUP_REJECTION_KG (RIGHT)': 0,
            'STARTUP_SCRAP_KG (RIGHT)': 0,
            "TOTAL_STARTUP_REJECTION_KG": 0,
        }
        return to_insert


def update_process_scrap(data):
    myquery = {"ORDER NUMBER (LEFT)": str(data["ORDER NUMBER (LEFT)"]),
               "ORDER NUMBER (RIGHT)": str(data["ORDER NUMBER (RIGHT)"])}
    production_order = production_orders.find_one(myquery, {'_id': False, 'kpi': False})

    if production_order is not None:
        if "REJECTION ANALYSIS" in production_order:
            production_order["REJECTION ANALYSIS"]["PROCESS_SCRAP"] = round(float(data["PROCESS_SCRAP"]), 2)
        else:
            production_order["REJECTION ANALYSIS"] = {}
            production_order["REJECTION ANALYSIS"]["PROCESS_SCRAP"] = round(float(data["PROCESS_SCRAP"]), 2)

        newvalues = {"$set": production_order}
        production_orders.update_one(myquery, newvalues)
        print("PROCESS RECORDED")

    else:
        print("NO PRODUCTION ORDER FOUND")


def update_rejection_status(data):
    # print(production_order)
    myquery = {"ORDER NUMBER (LEFT)": str(data["ORDER NUMBER (LEFT)"]),
               "ORDER NUMBER (RIGHT)": str(data["ORDER NUMBER (RIGHT)"])}
    production_order = production_orders.find_one(myquery, {'_id': False, 'kpi': False})
    if production_order is not None:
        if "REJECTION ANALYSIS" in production_order:
            if "REJECTION" in production_order["REJECTION ANALYSIS"]:
                for record in production_order["REJECTION ANALYSIS"]["REJECTION"]:
                    # print (record["start_time"])
                    if str(record["REJECTION_QUANTITY"]) == data["REJECTION_QUANTITY"] and record["reasonlist"] == data[
                        "reasonlist"]:
                        record["status"] = data["status"]
                        print("REJECTION RECORD FOUND AND UPDATED !")
                        newvalues = {"$set": production_order}
                        production_orders.update_one(myquery, newvalues)
                        print("REJECTION RECORDED")


# -Vatsal

def add_new_rejection_record(data):
    my_query = data["query"]
    production_order = production_orders.find_one(my_query, {'_id': False, 'kpi': False})
    if production_order is not None:
        data["payload"]["timestamp"] = datetime.now().strftime(constants.time_format)
        if "REJECTION ANALYSIS" in production_order:
            production_order["REJECTION ANALYSIS"].append(data["payload"])
        else:
            production_order["REJECTION ANALYSIS"] = [data["payload"]]
        newvalues = {"$set": production_order}
        production_orders.update_one(my_query, newvalues)
        to_return = production_order
        state = True
    else:
        state = False
        to_return = {}
    print("REJECTION ORDER UPDATED!")

    return state, to_return


def add_compound_detail(data):
    my_query = data["query"]
    production_order = production_orders.find_one(my_query, {'_id': False, 'kpi': False})
    if production_order is not None:
        data["payload"]["timestamp"] = datetime.now().strftime(constants.time_format)
        if "COMPOUND ANALYSIS" in production_order:
            production_order["COMPOUND ANALYSIS"].append(data["payload"])
        else:
            production_order["COMPOUND ANALYSIS"] = [data["payload"]]
        newvalues = {"$set": production_order}
        production_orders.update_one(my_query, newvalues)
        to_return = production_order
        state = True
    else:
        state = False
        to_return = {}
    print("ADDED COMPOUND DETAILS")

    return state, to_return


# ADD LAST UPDATE VALUE IN DICT.
# ======================================

def insert_process_scrap(data):
    myquery = {"ORDER NUMBER (LEFT)": str(data["ORDER NUMBER (LEFT)"]),
               "ORDER NUMBER (RIGHT)": str(data["ORDER NUMBER (RIGHT)"])}
    current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    data1 = {
        "PROCESS_SCRAP": {
            'KG(S)': data["kgs"],
            "status": "ACCEPTED",
            "timestamp": current_time
        }
    }
    # print(data1)
    production_order = production_orders.update(myquery, {'$push': {"REJECTION_ANALYSIS": data1}})
    return 1


def find_process_scrap(data):
    myquery = {"ORDER NUMBER (LEFT)": str(data["ORDER NUMBER (LEFT)"]),
               "ORDER NUMBER (RIGHT)": str(data["ORDER NUMBER (RIGHT)"])}

    data2 = production_orders.find_one(myquery, {'_id': False, "REJECTION_ANALYSIS": True})
    print(data2)
    return data2


'''
=================================================================================================================
SHIFT CALCULATIONS 
=================================================================================================================
'''


def create_shift_plan(start_time="12/11/2018", stop_time="13/11/2018"):
    start_timestamp = datetime.strptime((start_time + " " + constants.A_shift_start_time), "%d/%m/%Y %H:%M:%S")
    stop_timestamp = datetime.strptime((stop_time + " " + constants.A_shift_start_time), "%d/%m/%Y %H:%M:%S")

    current_shift_start_time = start_timestamp

    while current_shift_start_time < stop_timestamp:
        # ======= UPDATE SHIFT A   ========

        myquery = {"SHIFT DATE": current_shift_start_time.strftime("%d/%m/%Y"), "SHIFT ID": "A", }
        count = shift_records.find(myquery).count()

        if count == 0:
            shift_record = {
                "TEAM LEADER": "",
                "TEAM MEMBERS": [],
                "GROUP LEADER": "",
                "DEPARTMENT HEAD": "",
                "SHIFT START TIME": current_shift_start_time,
                "SHIFT STOP TIME": current_shift_start_time + timedelta(minutes=constants.shift_duration),
                "SHIFT DATE": current_shift_start_time.strftime("%d/%m/%Y"),
                "SHIFT ID": "A",
                "PRODUCTION ORDERS": [],
                "MAIL SENT": "NO"
            }
            shift_records.insert_one(shift_record)
        current_shift_start_time = current_shift_start_time + timedelta(minutes=constants.shift_duration)

        myquery = {"SHIFT DATE": current_shift_start_time.strftime("%d/%m/%Y"), "SHIFT ID": "B", }
        count = shift_records.find(myquery).count()
        if count == 0:
            shift_record = {
                "TEAM LEADER": "",
                "TEAM MEMBERS": [],
                "GROUP LEADER": "",
                "DEPARTMENT HEAD": "",
                "SHIFT START TIME": current_shift_start_time,
                "SHIFT STOP TIME": current_shift_start_time + timedelta(minutes=constants.shift_duration),
                "SHIFT DATE": current_shift_start_time.strftime("%d/%m/%Y"),
                "SHIFT ID": "B",
                "PRODUCTION ORDERS": [],
                "MAIL SENT": "NO"
            }
            shift_records.insert_one(shift_record)
        current_shift_start_time = current_shift_start_time + timedelta(minutes=constants.shift_duration)

        myquery = {"SHIFT DATE": current_shift_start_time.strftime("%d/%m/%Y"), "SHIFT ID": "C", }
        count = shift_records.find(myquery).count()
        if count == 0:
            shift_record = {
                "TEAM LEADER": "",
                "TEAM MEMBERS": [],
                "GROUP LEADER": "",
                "DEPARTMENT HEAD": "",
                "SHIFT START TIME": current_shift_start_time,
                "SHIFT STOP TIME": current_shift_start_time + timedelta(minutes=constants.shift_duration),
                "SHIFT DATE": current_shift_start_time.strftime("%d/%m/%Y"),
                "SHIFT ID": "C",
                "PRODUCTION ORDERS": [],
                "MAIL SENT": "NO"
            }
            shift_records.insert_one(shift_record)
        current_shift_start_time = current_shift_start_time + timedelta(minutes=constants.shift_duration)


def get_shift_records(dates):
    print(dates)
    from_date = datetime.strptime(dates["from_date"], "%Y-%m-%d")
    to_date = datetime.strptime(dates["to_date"], "%Y-%m-%d")
    print(type(from_date))
    print(type(to_date))
    myquery = {"SHIFT START TIME":
                   {"$gte": from_date,
                    "$lt": to_date
                    }
               }
    data = shift_records.find(myquery, {'_id': False})
    # print(data)
    return_orders = []
    for mydoc in data:
        return_orders.append(mydoc)
    # print(len(return_orders))
    return return_orders


def get_shift_records_without_kpi(dates):
    print(dates)
    from_date = datetime.strptime(dates["from_date"], "%Y-%m-%d")
    to_date = datetime.strptime(dates["to_date"], "%Y-%m-%d")
    print(type(from_date))
    print(type(to_date))
    myquery = {"SHIFT START TIME":
                   {"$gte": from_date,
                    "$lt": to_date
                    }
               }
    data = shift_records.find(myquery, {'_id': False, 'kpi': False})
    # print(data)
    return_orders = []
    for mydoc in data:
        return_orders.append(mydoc)
    # print(len(return_orders))
    return return_orders


def update_shift_records(data):
    myquery = {"SHIFT ID": data["SHIFT ID"], "SHIFT DATE": data["SHIFT DATE"]}
    newvalues = {"$set": data}
    shift_records.update_one(myquery, newvalues)


def get_specific_shift_record(data):
    myquery = {"SHIFT ID": data["SHIFT ID"], "SHIFT DATE": data["SHIFT DATE"]}
    data = shift_records.find_one(myquery, {'_id': False})
    return data


def update_shift_production_orders(production_order_number):
    # Get Current Shift
    current_time = datetime.now() + timedelta(constants.timezone_offset)
    myquery = {"$and": [{"SHIFT START TIME": {"$lte": current_time}},
                        {"SHIFT STOP TIME": {"$gt": current_time}}
                        ]}

    shift = shift_records.find_one(myquery, {'_id': False})

    # Add Production Order if not already added
    flag_to_append = 0

    if len(shift["PRODUCTION ORDERS"]) is not 0:
        for order in shift["PRODUCTION ORDERS"]:
            if "ORDER NUMBER (LEFT)" in order:
                if order["ORDER NUMBER (LEFT)"] == production_order_number["ORDER NUMBER (LEFT)"]:
                    if order["ORDER NUMBER (RIGHT)"] == production_order_number["ORDER NUMBER (RIGHT)"]:
                        flag_to_append = 1
        if flag_to_append == 0:
            print("-----------------------------------")
            print("Production Order Appended !")
            print("-----------------------------------")
            shift["PRODUCTION ORDERS"].append(production_order_number)
    else:
        print("APPENDING SHIFT ORDERS FOR FIRST TIME.")
        shift["PRODUCTION ORDERS"].append(production_order_number)

    # shift["PRODUCTION ORDERS"].append(production_order_number)

    # Save changes to Database
    myquery = {"SHIFT ID": shift["SHIFT ID"], "SHIFT DATE": shift["SHIFT DATE"]}
    newvalues = {"$set": shift}
    shift_records.update_one(myquery, newvalues)


# SPR HELPING FUNCTIONS

def compound_analysis_spr(production_order, shift):
    batch_left = "-"
    weight_left = 0
    batch_right = "-"
    weight_right = 0
    try:
        if "COMPOUND ANALYSIS" in production_order:
            if len(production_order["COMPOUND ANALYSIS"]):
                batch_left = []
                weight_left = 0
                batch_right = []
                weight_right = 0
                for compound in production_order["COMPOUND ANALYSIS"]:
                    compound_timestamp = datetime.strptime(compound["timestamp"], constants.time_format)
                    if shift["SHIFT START TIME"] < compound_timestamp < shift["SHIFT STOP TIME"]:
                        if compound["ORDER NUMBER"] == "LEFT":
                            batch_left.append(compound["COMPOUND BATCH"])
                            try:
                                weight_left += float(compound["COMPOUND WEIGHT"])
                            except:
                                pass
                        else:
                            batch_right.append(compound["COMPOUND BATCH"])
                            try:
                                weight_right += float(compound["COMPOUND WEIGHT"])
                            except:
                                pass
                        weight_left = round(weight_left, 2)
                        weight_right = round(weight_right, 2)
    except:
        pass
    return batch_left, weight_left, batch_right, weight_right


def get_times_for_order_in_shift(production_order, shift):
    try:
        current_time = datetime.now()
        stop_time = production_order["ACTUAL_STOP"]
        stop_as_shift_stop = 0
        if isinstance(production_order["ACTUAL_STOP"], str):

            # in case the production order is running and within shift.
            if current_time < shift["SHIFT STOP TIME"]:
                stop_time = current_time
            else:
                stop_as_shift_stop = 1

        elif isinstance(production_order["ACTUAL_STOP"], datetime):
            if production_order["ACTUAL_STOP"] > shift["SHIFT STOP TIME"]:
                stop_as_shift_stop = 1
            else:
                stop_as_shift_stop = 0

        if stop_as_shift_stop == 1:
            stop_time = shift["SHIFT STOP TIME"]

        start_time = production_order["ACTUAL_START"]
        start_as_shift_time = 0
        if isinstance(production_order["ACTUAL_START"], str):
            # THIS CONDITION WILL NEVER ARISE
            start_as_shift_time = 1
        elif isinstance(production_order["ACTUAL_START"], datetime):
            if production_order["ACTUAL_START"] < shift["SHIFT START TIME"]:
                start_as_shift_time = 1
            else:
                start_as_shift_time = 0

        if start_as_shift_time == 1:
            start_time = shift["SHIFT START TIME"]

        return start_time, stop_time
    except:
        return 0, 0


def get_planned_qty_in_shift_for_a_production_order(production_order, shift, runtime):
    try:
        print("---------------------------------------------------------")
        print(production_order["PART NUMBER"])
        print("runtime ", runtime)
        print("cycletime ", production_order["CYCLE TIME"])
        planned_qty = int(runtime * 60 / production_order["CYCLE TIME"])
        time.sleep(10)
    except:
        planned_qty = 0
    return planned_qty


def get_actual_done_in_shift_for_a_production_order(production_order, shift):
    start_time, stop_time = get_times_for_order_in_shift(production_order, shift)
    actual_qty = 0
    print("OLD START TIME IS :", start_time)
    try:
        if start_time != 0:
            # check if mould change  or start time exists
            try:
                if "DOWNTIME" in production_order:
                    for downtime in production_order["DOWNTIME"]:
                        if shift["SHIFT START TIME"] < datetime.strptime(downtime["stop_time"], constants.time_format) < \
                                shift["SHIFT STOP TIME"]:

                            if "reasonlist" in downtime:
                                if downtime["reasonlist"] == "Startup Time":
                                    start_time = datetime.strptime(downtime["stop_time"], constants.time_format)
                                elif downtime["reasonlist"] == "Mould Change":
                                    start_time = datetime.strptime(downtime["stop_time"], constants.time_format)
                                else:
                                    pass
            except:
                print("ERROR WHILE CONSIDERING MOULD/STARTUP TIME AS START TIME.")

            print("NEW START TIME IS :", start_time)

            records = production_order["SHOT_DETAILS"]
            for record in records:
                shot_time = datetime.strptime(record["timestamp"], constants.time_format)
                if start_time < shot_time < stop_time:
                    actual_qty += 1
    except:
        pass
    return actual_qty


def get_rejection_qty_in_for_a_production_order(production_order, shift):
    total_rejections_left = 0
    total_rejections_right = 0
    start_time, stop_time = get_times_for_order_in_shift(production_order, shift)
    try:
        records = production_order["REJECTION ANALYSIS"]
        if start_time != 0:
            for record in records:
                if "TYPE" in record and record["TYPE"] == "LINE REJECTION":
                    if "timestamp" in record:
                        rejection_time = datetime.strptime(record["timestamp"], constants.time_format)
                    else:
                        rejection_time = stop_time - timedelta(minutes=5)
                    if start_time < rejection_time < stop_time:
                        if record['ORDER MODE'] == "LEFT":
                            try:
                                total_rejections_left += int(record['QUANTITY'])
                            except:
                                pass
                        if record['ORDER MODE'] == "RIGHT":
                            try:
                                total_rejections_right += int(record['QUANTITY'])
                            except:
                                pass
    except:
        pass

    return total_rejections_left, total_rejections_right


def get_rejection_wt_in_for_a_production_order(production_order, shift):
    total_rejections_left = 0
    total_rejections_right = 0
    start_time, stop_time = get_times_for_order_in_shift(production_order, shift)
    try:
        records = production_order["REJECTION ANALYSIS"]
        if start_time != 0:
            for record in records:
                if "TYPE" in record and record["TYPE"] == "LINE REJECTION":
                    if "timestamp" in record:
                        rejection_time = datetime.strptime(record["timestamp"], constants.time_format)
                    else:
                        rejection_time = stop_time - timedelta(minutes=5)
                    if start_time < rejection_time < stop_time:
                        if record['ORDER MODE'] == "LEFT":
                            try:
                                total_rejections_left += float(record['WEIGHT'])
                            except:
                                pass
                        if record['ORDER MODE'] == "RIGHT":
                            try:
                                total_rejections_right += float(record['WEIGHT'])
                            except:
                                pass
    except:
        pass
    return round(total_rejections_left, 2), round(total_rejections_right, 2)


def get_startup_rejection_wt_in_for_a_production_order(production_order, shift):
    startup_rejection_wt_left = 0
    startup_rejection_wt_right = 0
    start_time, stop_time = get_times_for_order_in_shift(production_order, shift)
    try:
        records = production_order["REJECTION ANALYSIS"]
        if start_time != 0:
            for record in records:
                if "TYPE" in record and record["TYPE"] == "STARTUP REJECTION":
                    if "timestamp" in record:
                        rejection_time = datetime.strptime(record["timestamp"], constants.time_format)
                    else:
                        rejection_time = stop_time - timedelta(minutes=5)
                    if start_time < rejection_time < stop_time:
                        if record['ORDER MODE'] == "LEFT":
                            try:
                                startup_rejection_wt_left += float(record['WEIGHT'])
                            except:
                                pass
                        if record['ORDER MODE'] == "RIGHT":
                            try:
                                startup_rejection_wt_right += float(record['WEIGHT'])
                            except:
                                pass
    except:
        pass
    return round(startup_rejection_wt_left, 2), round(startup_rejection_wt_right, 2)


def get_startup_scrap_wt_in_for_a_production_order(production_order, shift):
    startup_scrap_wt = 0
    start_time, stop_time = get_times_for_order_in_shift(production_order, shift)
    try:
        records = production_order["REJECTION ANALYSIS"]
        if start_time != 0:
            for record in records:
                if "TYPE" in record and record["TYPE"] == "STARTUP SCRAP":
                    if "timestamp" in record:
                        rejection_time = datetime.strptime(record["timestamp"], constants.time_format)
                    else:
                        rejection_time = stop_time - timedelta(minutes=5)
                    if start_time < rejection_time < stop_time:
                        try:
                            startup_scrap_wt += float(record['WEIGHT'])
                        except:
                            pass
    except:
        pass
    return round(startup_scrap_wt, 2)


def get_process_scrap_wt_in_for_a_production_order(production_order, shift):
    process_scrap_wt = 0
    start_time, stop_time = get_times_for_order_in_shift(production_order, shift)
    try:
        records = production_order["REJECTION ANALYSIS"]
        if start_time != 0:
            for record in records:
                if "TYPE" in record and record["TYPE"] == "PROCESS SCRAP":
                    if "timestamp" in record:
                        rejection_time = datetime.strptime(record["timestamp"], constants.time_format)
                    else:
                        rejection_time = stop_time - timedelta(minutes=5)
                    if start_time < rejection_time < stop_time:
                        try:
                            process_scrap_wt += float(record['WEIGHT'])
                        except:
                            pass
    except:
        pass
    return round(process_scrap_wt, 2)


def get_total_downtime_for_a_production_order_in_shift(production_order, shift):
    total_downtime = 0
    correct_downtimes = get_downtime_overlaps(production_order)
    try:
        for downtime in correct_downtimes:
            if (shift["SHIFT START TIME"] < datetime.strptime(downtime["start_time"], constants.time_format) < shift[
                "SHIFT STOP TIME"]) or \
                    (shift["SHIFT START TIME"] < datetime.strptime(downtime["stop_time"], constants.time_format) <
                     shift["SHIFT STOP TIME"]):

                temp_downtime = copy.deepcopy(downtime)
                if temp_downtime["reasonlist"] != "Minor Stops":
                    temp_downtime["start_time"] = datetime.strptime(temp_downtime["start_time"], constants.time_format)
                    temp_downtime["stop_time"] = datetime.strptime(temp_downtime["stop_time"], constants.time_format)
                    start_time = temp_downtime["start_time"]
                    stop_time = temp_downtime["stop_time"]

                    if temp_downtime["start_time"] < shift["SHIFT START TIME"]:
                        start_time = shift["SHIFT START TIME"]
                    else:
                        pass

                    if temp_downtime["stop_time"] > shift["SHIFT STOP TIME"]:
                        stop_time = shift["SHIFT STOP TIME"]
                    else:
                        pass

                    duration = stop_time - start_time
                    # print(duration)
                    total_downtime += duration.total_seconds()

        total_downtime = round(total_downtime / 60, 2)
    except:
        pass
    return total_downtime


def get_shift_runtime(shift_production_order_times):
    downtimes = shift_production_order_times
    correct_downtimes = []

    # FIND OVERLAPPING DOWNTIMES
    for i in range(len(downtimes)):
        start_time = downtimes[i]["start_time"]
        stop_time = downtimes[i]["stop_time"]
        if len(correct_downtimes) == 0:
            details = ""
            details = downtimes[i]["production_order"] + " - "
            details += downtimes[i]["start_time"].strftime(constants.time_format)
            details += " TO " + downtimes[i]["stop_time"].strftime(constants.time_format)
            downtimes[i]["details"] = details
            correct_downtimes.append(downtimes[i])
        else:
            flag_overlap = 0
            for j in range(len(correct_downtimes)):
                to_check_start_time = correct_downtimes[j]["start_time"]
                to_check_stop_time = correct_downtimes[j]["stop_time"]

                if to_check_start_time < start_time and to_check_stop_time < start_time:
                    pass
                elif to_check_start_time > stop_time and to_check_stop_time > stop_time:
                    pass
                else:
                    # print("Downtime Overlap Occured")
                    temp = {}

                    # GET THE MINIMUM OF START TIME AND MAXIMUM OF STOP TIME
                    if to_check_start_time < start_time:
                        temp["start_time"] = to_check_start_time
                    else:
                        temp["start_time"] = start_time
                    if to_check_stop_time > stop_time:
                        temp["stop_time"] = to_check_stop_time
                    else:
                        temp["stop_time"] = stop_time
                    # Append to reasonlists
                    details = downtimes[i]["production_order"] + " - "
                    details += downtimes[i]["start_time"].strftime(constants.time_format)
                    details += " TO " + downtimes[i]["stop_time"].strftime(constants.time_format)
                    temp["details"] = correct_downtimes[j]["details"] + " , " + details
                    correct_downtimes[j] = temp
                    flag_overlap += 1
                    j = 0

            if flag_overlap == 0:
                details = ""
                details = downtimes[i]["production_order"] + " - "
                details += downtimes[i]["start_time"].strftime(constants.time_format)
                details += " TO " + downtimes[i]["stop_time"].strftime(constants.time_format)
                downtimes[i]["details"] = details
                correct_downtimes.append(downtimes[i])
    for downtime in correct_downtimes:
        try:
            downtime["start_time"] = downtime["start_time"].strftime(constants.time_format)
            downtime["stop_time"] = downtime["stop_time"].strftime(constants.time_format)
            downtimes.append(downtime)
        except:
            pass

    return correct_downtimes


def get_runtime_in_shift(shift):
    start = shift["SHIFT START TIME"]
    stop = shift["SHIFT STOP TIME"]
    current_time = datetime.now()
    if stop > current_time > start:
        stop = current_time
    runtime_in_shift = round((stop - start).total_seconds() / 60, 2)
    return runtime_in_shift


def get_runtime_for_production_order(production_order, shift):
    start_time, stop_time = get_times_for_order_in_shift(production_order, shift)
    runtime = round(((stop_time - start_time).total_seconds()) / 60, 2)  # expected runtime
    total_pause_time = 0

    if "PAUSE HISTORY" in production_order:
        for history in production_order["PAUSE HISTORY"]:
            # print("-----------------------------")
            # print(history["start_time"])
            # print(history["stop_time"])
            # Handling currently paused orders
            if history["stop_time"] == "-":
                history["stop_time"] = datetime.now().strftime(constants.time_format)
                print("Order Still paused. Considering current time")
            else:
                pass

            if (start_time < datetime.strptime(history["start_time"], constants.time_format) < stop_time) or \
                    (start_time < datetime.strptime(history["stop_time"], constants.time_format) <
                     stop_time) or (start_time > datetime.strptime(history["start_time"],
                                                                   constants.time_format) and stop_time < datetime.strptime(
                history["stop_time"], constants.time_format)):

                temp_history = copy.deepcopy(history)
                pause_start_time = datetime.strptime(temp_history["start_time"], constants.time_format)
                pause_stop_time = datetime.strptime(temp_history["stop_time"], constants.time_format)

                if pause_start_time < start_time:
                    pause_start_time = start_time
                else:
                    pass

                if pause_stop_time > stop_time:
                    pause_stop_time = stop_time
                else:
                    pass

                duration = pause_stop_time - pause_start_time
                # print(duration)
                total_pause_time += duration.total_seconds()
    '''print("#################################RUNTIME CALCULATIONS########################################")
    print("start_time : ", start_time)
    print("stop_time: ", stop_time)
    print("runtime:" , runtime)
    print("pause time:",total_pause_time )
    print("##########################################################################")'''
    runtime = round(runtime - (total_pause_time / 60), 2)

    return runtime


def get_paused_details_for_production_order_in_shift(production_order, shift):
    start_time, stop_time = get_times_for_order_in_shift(production_order, shift)

    total_pause_time = 0
    all_pauses = []

    if "PAUSE HISTORY" in production_order:
        for history in production_order["PAUSE HISTORY"]:
            print("-----------------------------")
            print(history["start_time"])
            print(history["stop_time"])
            # Handling currently paused orders
            if history["stop_time"] == "-":
                history["stop_time"] = datetime.now().strftime(constants.time_format)
                print("Order Still paused. Considering current time")
            else:
                pass

            if (start_time < datetime.strptime(history["start_time"], constants.time_format) < stop_time) or \
                    (start_time < datetime.strptime(history["stop_time"], constants.time_format) <
                     stop_time) or (start_time > datetime.strptime(history["start_time"],
                                                                   constants.time_format) and stop_time < datetime.strptime(
                history["stop_time"], constants.time_format)):

                temp_history = copy.deepcopy(history)
                pause_start_time = datetime.strptime(temp_history["start_time"], constants.time_format)
                pause_stop_time = datetime.strptime(temp_history["stop_time"], constants.time_format)

                if pause_start_time < start_time:
                    pause_start_time = start_time
                else:
                    pass

                if pause_stop_time > stop_time:
                    pause_stop_time = stop_time
                else:
                    pass

                duration = pause_stop_time - pause_start_time
                # print(duration)
                total_pause_time += duration.total_seconds()

                # Getting paused history in spr downtime format
                temp_record = {}
                temp_record["START TIME"] = pause_start_time.strftime(constants.spr_time_format)
                temp_record["STOP TIME"] = pause_stop_time.strftime(constants.spr_time_format)
                temp_record["PROBLEM"] = "PAUSED | " + production_order["ORDER NUMBER (LEFT)"] + " | " + \
                                         production_order["ORDER NUMBER (RIGHT)"]
                temp_record["TIME MINS"] = round(duration.total_seconds() / 60, 2)

                all_pauses.append(temp_record)

    return all_pauses


# to be subtracted from runtime during calculating the planned quantity.
def check_for_existing_downtimes_for_planned_downtimes(production_order, shift):
    correct_downtimes = get_downtime_overlaps(production_order)
    mould_change_found = 0
    start_up_found = 0
    mould_change_to_subtract = 0
    start_up_to_subtract = 0
    planned_mould_change = production_order["MOULD CHANGE TIME (MIN)"]
    planned_start_up = production_order["START UP TIME (MIN)"]
    try:
        for downtime in correct_downtimes:
            if (shift["SHIFT START TIME"] < datetime.strptime(downtime["start_time"], constants.time_format) < shift[
                "SHIFT STOP TIME"]) or \
                    (shift["SHIFT START TIME"] < datetime.strptime(downtime["stop_time"], constants.time_format) <
                     shift["SHIFT STOP TIME"]):

                if "reasonlist" in downtime:
                    if downtime["reasonlist"] == "Mould Change":
                        print("=====================================================================================")
                        print("Mould_start : ", downtime["start_time"])
                        print("Mould stop: ", downtime["stop_time"])
                        print("======================================================================================")
                        mould_change_found = 1
                        # Logic for subtracting:
                        if (shift["SHIFT START TIME"] < datetime.strptime(downtime["start_time"],
                                                                          constants.time_format) < shift[
                                "SHIFT STOP TIME"]) and \
                                (shift["SHIFT START TIME"] < datetime.strptime(downtime["stop_time"],
                                                                               constants.time_format) < shift[
                                     "SHIFT STOP TIME"]):

                            # subtract planned mould change directly.
                            mould_change_to_subtract = planned_mould_change

                        elif shift["SHIFT START TIME"] < datetime.strptime(downtime["start_time"],
                                                                           constants.time_format) < shift[
                            "SHIFT STOP TIME"]:

                            actual_mould_change = (shift["SHIFT STOP TIME"] - downtime[
                                "start_time"]).total_seconds() / 60
                            if actual_mould_change > planned_mould_change:
                                mould_change_to_subtract = planned_mould_change
                            else:
                                mould_change_to_subtract = actual_mould_change  # mould change lying in current shift

                        elif shift["SHIFT START TIME"] < datetime.strptime(downtime["stop_time"],
                                                                           constants.time_format) < shift[
                            "SHIFT STOP TIME"]:

                            actual_mould_change = (shift["SHIFT START TIME"] - downtime[
                                "start_time"]).total_seconds() / 60  # mould change lying in previous shift
                            difference = planned_mould_change - actual_mould_change
                            if difference < 0:
                                mould_change_to_subtract = 0
                            else:
                                mould_change_to_subtract = difference
                            # Also check if the difference is not less than 0.
                            # if less then 0, mould_change to subtract remains 0.

                        else:
                            pass

                    elif downtime["reasonlist"] == "Startup Time":
                        start_up_found = 1
                        print("=====================================================================================")
                        print("startup_start : ", downtime["start_time"])
                        print("startup stop: ", downtime["stop_time"])
                        print("======================================================================================")
                        # Logic for subtracting:
                        if (shift["SHIFT START TIME"] < datetime.strptime(downtime["start_time"],
                                                                          constants.time_format) < shift[
                                "SHIFT STOP TIME"]) and \
                                (shift["SHIFT START TIME"] < datetime.strptime(downtime["stop_time"],
                                                                               constants.time_format) < shift[
                                     "SHIFT STOP TIME"]):

                            start_up_to_subtract = planned_start_up

                        elif shift["SHIFT START TIME"] < datetime.strptime(downtime["start_time"],
                                                                           constants.time_format) < shift[
                            "SHIFT STOP TIME"]:

                            actual_start_up = (shift["SHIFT STOP TIME"] - downtime["start_time"]).total_seconds() / 60
                            difference = planned_start_up - actual_start_up  # startup lying in current shift

                            if actual_start_up > planned_start_up:
                                start_up_to_subtract = planned_start_up
                            else:
                                start_up_to_subtract = actual_start_up  # mould change lying in current shift
                            # Also check if the difference is not less than 0.
                            # if less than 0 subtract the total planned directly.

                        elif shift["SHIFT START TIME"] < datetime.strptime(downtime["stop_time"],
                                                                           constants.time_format) < shift[
                            "SHIFT STOP TIME"]:

                            actual_start_up = (shift["SHIFT START TIME"] - downtime[
                                "start_time"]).total_seconds() / 60  # startup lying in previous shift
                            difference = planned_start_up - actual_start_up
                            # Also check if the difference is not less than 0.
                            # if less then 0, start_up_to_subtract remains 0.
                            if difference < 0:
                                start_up_to_subtract = 0
                            else:
                                start_up_to_subtract = difference

                        else:
                            pass
                else:
                    pass

            else:
                pass

            if mould_change_found == 1 and start_up_found == 1:
                break



    except:
        print("######################### EXCEPT BLOCK FOR MOULD CHANGE SUBTRACTION############################")

    print("=============================================================")
    print("mould change subtracted : ", mould_change_to_subtract)
    print("Start up subtracted: ", start_up_to_subtract)
    print("==============================================================")
    time.sleep(10)
    return mould_change_to_subtract, start_up_to_subtract


def get_total_downtime_of_type_for_a_production_order_in_shift(production_order, shift, downtime_type):
    total_downtime = 0

    correct_downtimes = get_downtime_overlaps(production_order)

    downtime_instances = 0
    try:
        for downtime in correct_downtimes:
            if (shift["SHIFT START TIME"] < datetime.strptime(downtime["start_time"], constants.time_format) < shift[
                "SHIFT STOP TIME"]) or \
                    (shift["SHIFT START TIME"] < datetime.strptime(downtime["stop_time"], constants.time_format) <
                     shift["SHIFT STOP TIME"]):

                temp_downtime = copy.deepcopy(downtime)
                if temp_downtime["reasonlist"] == downtime_type:
                    downtime_instances += 1
                    temp_downtime["start_time"] = datetime.strptime(temp_downtime["start_time"], constants.time_format)
                    temp_downtime["stop_time"] = datetime.strptime(temp_downtime["stop_time"], constants.time_format)
                    start_time = temp_downtime["start_time"]
                    stop_time = temp_downtime["stop_time"]

                    if temp_downtime["start_time"] < shift["SHIFT START TIME"]:
                        start_time = shift["SHIFT START TIME"]
                    else:
                        pass

                    if temp_downtime["stop_time"] > shift["SHIFT STOP TIME"]:
                        stop_time = shift["SHIFT STOP TIME"]
                    else:
                        pass

                    duration = stop_time - start_time
                    # print(duration)
                    total_downtime += duration.total_seconds()

        total_downtime = round(total_downtime / 60, 2)
    except:
        pass
    return total_downtime, downtime_instances


def get_downtimes_in_spr_format(production_order, shift):
    all_downtimes = []
    correct_downtimes = get_downtime_overlaps(production_order)
    try:
        for downtime in correct_downtimes:
            if (shift["SHIFT START TIME"] < datetime.strptime(downtime["start_time"], constants.time_format) < shift[
                "SHIFT STOP TIME"]) or \
                    (shift["SHIFT START TIME"] < datetime.strptime(downtime["stop_time"], constants.time_format) <
                     shift[
                         "SHIFT STOP TIME"]):

                temp_downtime = copy.deepcopy(downtime)
                temp_downtime["start_time"] = datetime.strptime(temp_downtime["start_time"], constants.time_format)
                temp_downtime["stop_time"] = datetime.strptime(temp_downtime["stop_time"], constants.time_format)
                start_time = temp_downtime["start_time"]
                stop_time = temp_downtime["stop_time"]

                if temp_downtime["start_time"] < shift["SHIFT START TIME"]:
                    start_time = shift["SHIFT START TIME"]
                else:
                    pass

                if temp_downtime["stop_time"] > shift["SHIFT STOP TIME"]:
                    stop_time = shift["SHIFT STOP TIME"]
                else:
                    pass

                temp_record = {}
                temp_record["START TIME"] = start_time.strftime(constants.spr_time_format)
                temp_record["STOP TIME"] = stop_time.strftime(constants.spr_time_format)
                temp_record["PROBLEM"] = temp_downtime["reasonlist"]
                temp_record["TIME MINS"] = round(
                    (stop_time - start_time).total_seconds() / 60.0, 2)

                if temp_record["PROBLEM"] != "Minor Stops":
                    all_downtimes.append(temp_record)
    except:
        pass
    return all_downtimes


def get_shots_for_production_order(production_order, shift):
    # SHOT COUNT LOGIC ===================================================================================================
    start_time, stop_time = get_times_for_order_in_shift(production_order, shift)
    start_shot_count = 0
    stop_shot_count = 0
    total_ok_shots = 0

    try:
        # check if mould change  or start time exists
        try:
            if "DOWNTIME" in production_order:
                for downtime in production_order["DOWNTIME"]:
                    if shift["SHIFT START TIME"] < datetime.strptime(downtime["stop_time"], constants.time_format) < \
                            shift["SHIFT STOP TIME"]:

                        if "reasonlist" in downtime:
                            if downtime["reasonlist"] == "Startup Time":
                                start_time = datetime.strptime(downtime["stop_time"], constants.time_format)
                            elif downtime["reasonlist"] == "Mould Change":
                                start_time = datetime.strptime(downtime["stop_time"], constants.time_format)
                            else:
                                pass
        except:
            print("ERROR WHILE CONSIDERING MOULD/STARTUP TIME AS START TIME.")

        records = production_order["SHOT_DETAILS"]
        start_shot_count = 0
        stop_shot_count = 0
        total_ok_shots = 0
        for record in records:
            if "timestamp" in record:
                shot_time = datetime.strptime(record["timestamp"], constants.time_format)
            else:
                shot_time = stop_time - timedelta(minutes=5)

            if start_time < shot_time <= stop_time:
                total_ok_shots = total_ok_shots + 1
                if total_ok_shots == 1:
                    start_shot_count = int(record["SHOT COUNT"])
                stop_shot_count = int(record["SHOT COUNT"])

    except:
        pass
    return start_shot_count, stop_shot_count, total_ok_shots


def get_line_rejection_details_in_for_a_production_order(production_order, shift):
    start_time, stop_time = get_times_for_order_in_shift(production_order, shift)
    line_rejection_details = []

    order_left = production_order["ORDER NUMBER (LEFT)"]
    order_right = production_order["ORDER NUMBER (RIGHT)"]
    try:
        records = production_order["REJECTION ANALYSIS"]
        if start_time != 0:
            for record in records:
                if "TYPE" in record and record["TYPE"] == "LINE REJECTION":
                    if "timestamp" in record:
                        rejection_time = datetime.strptime(record["timestamp"], constants.time_format)
                    else:
                        rejection_time = stop_time - timedelta(minutes=5)
                    if start_time < rejection_time < stop_time:
                        temp_record = {}
                        if record["ORDER MODE"] == "LEFT":
                            temp_record["PART NAME"] = production_order["PART NAME"] + "|" + order_left
                            temp_record["MODE"] = "LEFT"
                        else:
                            temp_record["PART NAME"] = production_order["PART NAME"] + "|" + order_right
                            temp_record["MODE"] = "RIGHT"
                        temp_record["REJECTED QTY"] = int(record["QUANTITY"])
                        temp_record["REJECTION REASON"] = record["reasonlist"]

                        line_rejection_details.append(temp_record)
    except:
        pass

    line_rejection_details1 = sorted(line_rejection_details, key=lambda k: k['MODE'], reverse=True)

    print(line_rejection_details1)
    return line_rejection_details1


def get_energy_details(production_order, shift):
    start_energy = 0
    stop_energy = 0
    total_energy = 0
    # VATSAL
    shift_start, shift_stop = get_times_for_order_in_shift(production_order, shift)

    if "ENERGY DETAILS" in production_order:
        try:
            for detail in production_order["ENERGY DETAILS"]:
                timestamp = datetime.strptime(detail["timestamp"], constants.time_format)
                if shift_start < timestamp < shift_stop:
                    start_energy = round(float(detail["energy_start"]), 2)
                    stop_energy = round(float(detail["energy_end"]), 2)
                    total_energy = round(float(detail["energy_difference"]), 2)
        except:
            pass

    '''print("-------------------Energy-----------------------")
    print(start_energy)
    print(stop_energy)
    print(total_energy)
    print("-------------------------------------------------")'''
    return start_energy, stop_energy, total_energy


def add_energy_details(data):
    myquery = {"ORDER NUMBER (LEFT)": data["ORDER NUMBER (LEFT)"],
               "ORDER NUMBER (RIGHT)": data["ORDER NUMBER (RIGHT)"]}

    order = production_orders.find_one(myquery, {'_id': False, 'kpi': False})
    print(order)
    current_time = datetime.now().strftime(constants.time_format)
    energy_details = data["energy_details"]
    energy_details["timestamp"] = current_time
    if "ENERGY DETAILS" in order:
        order["ENERGY DETAILS"].append(energy_details)
    else:
        order["ENERGY DETAILS"] = []
        order["ENERGY DETAILS"].append(energy_details)

    newvalues = {"$set": order}

    production_orders.update_one(myquery, newvalues)


# CODE FOR SPR
def get_shift_report(data):
    myquery = {"SHIFT ID": data["SHIFT ID"], "SHIFT DATE": data["SHIFT DATE"]}

    shift = shift_records.find_one(myquery, {'_id': False, 'kpi': False})
    pprint(shift)
    # print("Shift Query Complete ")

    shift_to_send = {}
    shift_to_send["SHIFT START TIME"] = shift["SHIFT START TIME"]
    shift_to_send["SHIFT STOP TIME"] = shift["SHIFT STOP TIME"]

    # get total runtime for shift.
    get_runtime_overlaps(shift_to_send, data["MACHINE"])

    # print(data)

    if shift is not None:
        SPR_DATA = {
            "DATE": data["SHIFT DATE"],
            "SHIFT": data["SHIFT ID"],
            "MACHINE": data["MACHINE"],
            "TEAM MEMBERS": "",
            "PLANT": "PLANT III",
            "DEPARTMENT HEAD": "",
            "PRODUCTION ORDER DETAILS": [],
            "SUM PRODUCTION ORDER DETAILS": {},
            "LINE REJECTION DETAILS": [],
            "GAP DETAILS": [],
            "TEAM LEADER": []
        }

        if "TEAM MEMBERS" in shift:
            SPR_DATA["TEAM MEMBERS"] = shift["TEAM MEMBERS"]
        if "DEPARTMENT HEAD" in shift:
            SPR_DATA["DEPARTMENT HEAD"] = shift["DEPARTMENT HEAD"]
        if "GROUP LEADER" in shift:
            SPR_DATA["GROUP LEADER"] = shift["GROUP LEADER"]

        # ========================       SPR PART 1         ================================================

        if "PRODUCTION ORDERS" in shift:
            # print(shift["PRODUCTION ORDERS"])
            # SUMMATION OF ALL QUANTITIES OF PRODUCTION ORDER DETAILS
            sum_details = {}
            sum_details["PLAN QTY"] = 0
            sum_details["ACTUAL QTY"] = 0
            sum_details["GAP QTY"] = 0
            sum_details["STARTUP_REJECTION_KG"] = 0
            sum_details["STARTUP_SCRAP_KG"] = 0
            sum_details["TOTAL_STARTUP_REJECTION_KG"] = 0
            sum_details["TOTAL_LINE_REJECTION_QTY"] = 0
            sum_details["TOTAL_LINE_REJECTION_WEIGHT"] = 0
            sum_details["PROCESS SCRAP"] = 0
            sum_details["POWER CUT NOS"] = 0
            sum_details["POWER CUT MINS"] = 0
            sum_details["RUN TIME MINS"] = 0
            sum_details["CHANGE OVER TIME MINS"] = 0
            sum_details["SETUP TIME MINS"] = 0
            sum_details["BREAKDOWN MINS"] = 0
            sum_details["SHOT DETAILS START"] = "-"
            sum_details["SHOT DETAILS STOP"] = "-"
            sum_details["SHOT DETAILS GAP"] = 0
            sum_details["ENERGY KWH START"] = "-"
            sum_details["ENERGY KWH STOP"] = "-"
            sum_details["ENERGY KWH GAP"] = 0
            sum_details["PER PRODUCTION ORDER DOWNTIME"] = 0
            for record in shift["PRODUCTION ORDERS"]:
                production_order = get_specific_production_order_spr(record)

                if production_order is not None:
                    if production_order["MACHINE"] == data["MACHINE"]:
                        # print("FOUND MACHINE !")
                        # print("==================PRODUCTION ORDERS==============")
                        # print("------------------------------------------------")
                        # print(shift["PRODUCTION ORDERS"])
                        # print("------------------------------------------------")

                        if "MACHINE INCHARGE" in production_order:
                            if production_order["MACHINE INCHARGE"] not in SPR_DATA["TEAM MEMBERS"]:
                                SPR_DATA["TEAM MEMBERS"].append(production_order["MACHINE INCHARGE"])
                        if "QC INCHARGE" in production_order:
                            if production_order["QC INCHARGE"] not in SPR_DATA["TEAM MEMBERS"]:
                                SPR_DATA["TEAM MEMBERS"].append(production_order["QC INCHARGE"])
                        if "LINE INCHARGE" in production_order:
                            if production_order["LINE INCHARGE"] not in SPR_DATA["TEAM LEADER"]:
                                SPR_DATA["TEAM LEADER"].append(production_order["LINE INCHARGE"])

                        production_order_details = {}
                        production_order_details["PART NAME"] = production_order["PART NAME"]

                        # ========================== CAN REMOVE LATER =============================================
                        production_order_details["PART NAME"] += "<br> START : "
                        if (isinstance(production_order["ACTUAL_START"], datetime)):
                            production_order_details["PART NAME"] += datetime.strftime(production_order["ACTUAL_START"],
                                                                                       constants.time_format)
                        else:
                            production_order_details["PART NAME"] += "NA"

                        production_order_details["PART NAME"] += "<br>STOP : "
                        if (isinstance(production_order["ACTUAL_STOP"], datetime)):
                            production_order_details["PART NAME"] += datetime.strftime(production_order["ACTUAL_STOP"],
                                                                                       constants.time_format)
                        else:
                            production_order_details["PART NAME"] += "NA"

                        # ==============================================================================================

                        production_order_details["MATERIAL"] = production_order["MATERIAL"]
                        production_order_details["ORDER_NUMBER (RIGHT)"] = production_order["ORDER NUMBER (RIGHT)"]
                        production_order_details["ORDER_NUMBER (LEFT)"] = production_order["ORDER NUMBER (LEFT)"]

                        batch_left, weight_left, batch_right, weight_right = compound_analysis_spr(production_order,
                                                                                                   shift)
                        production_order_details["COMPOUND BATCH (LEFT)"] = batch_left
                        production_order_details["COMPOUND BATCH (RIGHT)"] = batch_right
                        production_order_details["COMPOUND KGS (LEFT)"] = weight_left
                        production_order_details["COMPOUND KGS (RIGHT)"] = weight_right
                        # ==============================================================================================================
                        # CODE FOR QUANTITY ANALYSIS
                        # ==============================================================================================================
                        runtime_for_po = get_runtime_for_production_order(production_order, shift)
                        mould_change, start_up = check_for_existing_downtimes_for_planned_downtimes(production_order,
                                                                                                    shift)
                        runtime_without_planned_downtimes = runtime_for_po - mould_change - start_up
                        planned_qty = get_planned_qty_in_shift_for_a_production_order(production_order, shift,
                                                                                      runtime_without_planned_downtimes)
                        acheived_shots = get_actual_done_in_shift_for_a_production_order(production_order, shift)
                        total_rejections_left, total_rejections_right = get_rejection_qty_in_for_a_production_order(
                            production_order, shift)

                        if production_order_details["ORDER_NUMBER (RIGHT)"] is not "":
                            production_order_details["PLAN QTY (RIGHT)"] = planned_qty
                        else:
                            production_order_details["PLAN QTY (RIGHT)"] = 0

                        if production_order_details["ORDER_NUMBER (LEFT)"] is not "":
                            production_order_details["PLAN QTY (LEFT)"] = planned_qty
                        else:
                            production_order_details["PLAN QTY (LEFT)"] = 0

                        if production_order_details["ORDER_NUMBER (RIGHT)"] is not "":
                            production_order_details["ACTUAL QTY (RIGHT)"] = acheived_shots - total_rejections_right

                        else:
                            production_order_details["ACTUAL QTY (RIGHT)"] = 0
                        if production_order_details["ORDER_NUMBER (LEFT)"] is not "":
                            production_order_details["ACTUAL QTY (LEFT)"] = acheived_shots - total_rejections_left
                        else:
                            production_order_details["ACTUAL QTY (LEFT)"] = 0

                        production_order_details["GAP (RIGHT)"] = production_order_details["PLAN QTY (RIGHT)"] - \
                                                                  production_order_details["ACTUAL QTY (RIGHT)"]

                        production_order_details["GAP (LEFT)"] = production_order_details["PLAN QTY (LEFT)"] - \
                                                                 production_order_details["ACTUAL QTY (LEFT)"]

                        sum_details["PLAN QTY"] += production_order_details["PLAN QTY (RIGHT)"]
                        sum_details["ACTUAL QTY"] += production_order_details["ACTUAL QTY (RIGHT)"]
                        sum_details["GAP QTY"] += production_order_details["GAP (RIGHT)"]

                        sum_details["PLAN QTY"] += production_order_details["PLAN QTY (LEFT)"]
                        sum_details["ACTUAL QTY"] += production_order_details["ACTUAL QTY (LEFT)"]
                        sum_details["GAP QTY"] += production_order_details["GAP (LEFT)"]

                        # ==============================================================================================================
                        # CODE FOR STARTUP ANALYSIS
                        # ==============================================================================================================

                        production_order_details["STARTUP_REJECTION_KG (LEFT)"], production_order_details[
                            "STARTUP_REJECTION_KG (RIGHT)"] = get_startup_rejection_wt_in_for_a_production_order(
                            production_order, shift)
                        sum_details["STARTUP_REJECTION_KG"] += (
                                    production_order_details["STARTUP_REJECTION_KG (LEFT)"] + production_order_details[
                                "STARTUP_REJECTION_KG (RIGHT)"])

                        production_order_details["STARTUP_SCRAP_KG"] = get_startup_scrap_wt_in_for_a_production_order(
                            production_order, shift)
                        sum_details["STARTUP_SCRAP_KG"] += production_order_details["STARTUP_SCRAP_KG"]

                        production_order_details["TOTAL_STARTUP_SCRAP_KG"] = round((production_order_details[
                                                                                        "STARTUP_REJECTION_KG (LEFT)"] +
                                                                                    production_order_details[
                                                                                        "STARTUP_REJECTION_KG (RIGHT)"] +
                                                                                    production_order_details[
                                                                                        "STARTUP_SCRAP_KG"]), 2)
                        sum_details["TOTAL_STARTUP_REJECTION_KG"] += production_order_details["TOTAL_STARTUP_SCRAP_KG"]

                        # ==============================================================================================================
                        # CODE FOR LINE REJECTION ANALYSIS
                        # ==============================================================================================================

                        total_rejections_left, total_rejections_right = get_rejection_qty_in_for_a_production_order(
                            production_order, shift)
                        production_order_details[
                            "TOTAL_LINE_REJECTION_QTY"] = total_rejections_left + total_rejections_right
                        sum_details["TOTAL_LINE_REJECTION_QTY"] += production_order_details["TOTAL_LINE_REJECTION_QTY"]

                        total_rejections_left, total_rejections_right = get_rejection_wt_in_for_a_production_order(
                            production_order, shift)
                        production_order_details[
                            "TOTAL_LINE_REJECTION_WEIGHT"] = total_rejections_left + total_rejections_right
                        sum_details["TOTAL_LINE_REJECTION_WEIGHT"] += production_order_details[
                            "TOTAL_LINE_REJECTION_WEIGHT"]

                        # ==============================================================================================================
                        # CODE FOR PROCESS SCRAP ANALYSIS
                        # ==============================================================================================================
                        production_order_details["PROCESS SCRAP"] = get_process_scrap_wt_in_for_a_production_order(
                            production_order, shift)
                        sum_details["PROCESS SCRAP"] += production_order_details["PROCESS SCRAP"]

                        # ADD LINE REJECTION DETAILS TO SPR
                        line_rejection_details = get_line_rejection_details_in_for_a_production_order(production_order,
                                                                                                      shift)

                        if len(line_rejection_details) > 0:
                            SPR_DATA["LINE REJECTION DETAILS"].extend(line_rejection_details)

                        # GET PRODUCTION ORDER RUNTIME
                        production_order_details["RUN TIME MINS"] = get_runtime_for_production_order(production_order,
                                                                                                     shift)
                        total_downtime_in_shift = get_total_downtime_for_a_production_order_in_shift(production_order,
                                                                                                     shift)
                        production_order_details["RUN TIME MINS"] = round(
                            production_order_details["RUN TIME MINS"] - total_downtime_in_shift, 2)
                        sum_details["RUN TIME MINS"] += production_order_details["RUN TIME MINS"]
                        # find net downtime in shift
                        sum_details["PER PRODUCTION ORDER DOWNTIME"] += total_downtime_in_shift

                        # GET INDIVIDUAL DOWNTIMES
                        production_order_details["POWER CUT MINS"], production_order_details["POWER CUT NOS"] = \
                            get_total_downtime_of_type_for_a_production_order_in_shift(production_order, shift,
                                                                                       "Power Cut")

                        production_order_details["CHANGE OVER TIME MINS"], production_order_details[
                            "CHANGE OVER TIME NOS"] = \
                            get_total_downtime_of_type_for_a_production_order_in_shift(production_order, shift,
                                                                                       "Mould Change")

                        # print(production_order_details["CHANGE OVER TIME MINS"], production_order_details["CHANGE OVER TIME NOS"])

                        production_order_details["SETUP TIME MINS"], production_order_details[
                            "SETUP TIME NOS"] = \
                            get_total_downtime_of_type_for_a_production_order_in_shift(production_order, shift,
                                                                                       "Startup Time")
                        temp_setup_time_mins, temp_setup_time_nos = \
                            get_total_downtime_of_type_for_a_production_order_in_shift(production_order, shift,
                                                                                       "Holiday Startup")
                        production_order_details["SETUP TIME MINS"] += temp_setup_time_mins
                        production_order_details["SETUP TIME NOS"] += temp_setup_time_nos

                        production_order_details["SETUP TIME MINS"] = round(production_order_details["SETUP TIME MINS"],
                                                                            2)
                        production_order_details["SETUP TIME NOS"] = round(production_order_details["SETUP TIME NOS"],
                                                                           2)

                        production_order_details["BREAKDOWN MINS"], production_order_details[
                            "BREAKDOWN NOS"] = \
                            get_total_downtime_of_type_for_a_production_order_in_shift(production_order, shift,
                                                                                       "Breakdown")

                        # DOWNTIME SUMMATION
                        sum_details["POWER CUT NOS"] += production_order_details["POWER CUT NOS"]
                        sum_details["POWER CUT MINS"] += production_order_details["POWER CUT MINS"]
                        sum_details["CHANGE OVER TIME MINS"] += production_order_details["CHANGE OVER TIME MINS"]
                        sum_details["SETUP TIME MINS"] += production_order_details["SETUP TIME MINS"]
                        sum_details["BREAKDOWN MINS"] += production_order_details["BREAKDOWN MINS"]

                        # ADD DOWNTIMES IN SPR FORMAT
                        all_downtimes = get_downtimes_in_spr_format(production_order, shift)
                        if len(all_downtimes) > 0:
                            SPR_DATA["GAP DETAILS"].extend(all_downtimes)

                        # ADD PAUSES TO DOWNTIMES LIST
                        all_pauses = get_paused_details_for_production_order_in_shift(production_order, shift)
                        if len(all_pauses) > 0:
                            SPR_DATA["GAP DETAILS"].extend(all_pauses)

                        # ADD SHOT COUNTS TO SPR
                        start_shot_count, stop_shot_count, total_ok_shots = get_shots_for_production_order(
                            production_order, shift)
                        production_order_details["SHOT DETAILS START"] = start_shot_count
                        production_order_details["SHOT DETAILS STOP"] = stop_shot_count
                        production_order_details["SHOT DETAILS GAP"] = total_ok_shots

                        # sum_details["SHOT DETAILS START"] += production_order_details["SHOT DETAILS START"]
                        # sum_details["SHOT DETAILS STOP"] += production_order_details["SHOT DETAILS STOP"]
                        sum_details["SHOT DETAILS GAP"] += production_order_details["SHOT DETAILS GAP"]

                        production_order_details["ENERGY KWH START"], production_order_details["ENERGY KWH STOP"], \
                        production_order_details["ENERGY KWH GAP"] = get_energy_details(production_order, shift)

                        # sum_details["ENERGY KWH START"] += production_order_details["ENERGY KWH START"]
                        # sum_details["ENERGY KWH STOP"] += production_order_details["ENERGY KWH STOP"]
                        sum_details["ENERGY KWH GAP"] += production_order_details["ENERGY KWH GAP"]

                        SPR_DATA["PRODUCTION ORDER DETAILS"].append(production_order_details)

            # FINAL ROUND OFF
            sum_details["RUN TIME MINS"] = round(sum_details["RUN TIME MINS"], 2)
            sum_details["STARTUP_REJECTION_KG"] = round(sum_details["STARTUP_REJECTION_KG"], 2)
            sum_details["STARTUP_SCRAP_KG"] = round(sum_details["STARTUP_SCRAP_KG"], 2)
            sum_details["TOTAL_STARTUP_REJECTION_KG"] = round(sum_details["TOTAL_STARTUP_REJECTION_KG"], 2)
            sum_details["TOTAL_LINE_REJECTION_WEIGHT"] = round(sum_details["TOTAL_LINE_REJECTION_WEIGHT"], 2)
            sum_details["PROCESS SCRAP"] = round(sum_details["PROCESS SCRAP"], 2)
            sum_details["POWER CUT MINS"] = round(sum_details["POWER CUT MINS"], 2)
            sum_details["RUN TIME MINS"] = round(sum_details["RUN TIME MINS"], 2)
            sum_details["CHANGE OVER TIME MINS"] = round(sum_details["CHANGE OVER TIME MINS"], 2)
            sum_details["SETUP TIME MINS"] = round(sum_details["SETUP TIME MINS"], 2)
            sum_details["BREAKDOWN MINS"] = round(sum_details["BREAKDOWN MINS"], 2)

            SPR_DATA["SUM PRODUCTION ORDER DETAILS"] = sum_details
            SPR_DATA["PRODUCTION SUMMARY"] = []
            SPR_DATA["PRODUCTION SUMMARY"].append("TOTAL PLANNED QTY - " + str(sum_details["PLAN QTY"]))
            SPR_DATA["PRODUCTION SUMMARY"].append("TOTAL ACHIEVED QTY - " + str(sum_details["ACTUAL QTY"]))

            try:
                total_downtime = 0
                total_downtime = sum_details["PER PRODUCTION ORDER DOWNTIME"]
                SPR_DATA["PRODUCTION SUMMARY"].append("TOTAL DOWNTIME (MINS) - " + str(total_downtime))
            except:
                SPR_DATA["PRODUCTION SUMMARY"].append("TOTAL DOWNTIME (MINS) -  NA")

            # print(sum_details)
        else:
            pass

        return SPR_DATA


def append_kpi_to_shift_record(kpi):
    # Get Current Shift
    current_time = datetime.now() + timedelta(constants.timezone_offset)
    myquery = {"$and": [{"SHIFT START TIME": {"$lte": current_time}},
                        {"SHIFT STOP TIME": {"$gt": current_time}}
                        ]}

    shift = shift_records.find_one(myquery, {'_id': False})

    if 'kpi' in shift:
        shift['kpi'].append(kpi)
    else:
        shift['kpi'] = [kpi]

    query = {"$and": [{"SHIFT START TIME": shift['SHIFT START TIME']},
                      {"SHIFT STOP TIME": shift["SHIFT STOP TIME"]}
                      ]}
    newvalues = {"$set": shift}
    shift_records.update_one(query, newvalues)
    print("kpi details updated to database.")


def cron_job(time):
    # get live shift
    current_time = time
    myquery = {
        "SHIFT START TIME": {"$lte": current_time},
        "SHIFT STOP TIME": {"$gt": current_time}
    }
    current_shift = shift_records.find_one(myquery, {'_id': False})
    # change status as Live, Planned or Done
    current_shift["STATUS"] = "Live"
    update_shift_records(current_shift)

    # make the old shifts as Done
    myquery = {"SHIFT STOP TIME": {"$lt": current_time}}

    old_shifts_cursor = shift_records.find(myquery, {'_id': False})
    for shift in old_shifts_cursor:
        shift["STATUS"] = "Done"
        update_shift_records(shift)

    # ------------------------- SEND NOTIFICATIONS ------------------------
    if constants.mail_auto_send:
        shift_for_spr = shift_records.find({"$and": [{"MAIL SENT": "NO"}, {"SHIFT STOP TIME": {"$lt": current_time}}]},
                                           {'_id': False})

        for shift in shift_for_spr:
            # ---------------------------------------------------------------
            send_oee_via_sms(shift)
            # ---------------------------------------------------------------
            spr_date = datetime.strftime(shift["SHIFT START TIME"], "%d-%m-%Y")
            spr_shift_id = shift["SHIFT ID"]
            send_spr_mails(spr_date, spr_shift_id, shift)
            # ---------------------------------------------------------------
            pqcr_date = datetime.strftime(shift["SHIFT START TIME"], "%Y-%m-%d")
            send_pqcr_mails(pqcr_date)

            shift["MAIL SENT"] = "YES"

            newvalues = {"$set": shift}
            shift_records.update_one({"$and": [{"MAIL SENT": "NO"}, {"SHIFT STOP TIME": {"$lt": current_time}}]},
                                     newvalues)
            print("mail_sent was turned to YES")

    # ---------------------------------------------------------------

    # get all current production orders and append to shift records
    production_orders = get_all_active_production_orders()
    # print(production_orders)

    for production_order in production_orders:
        to_append = {
            "ORDER NUMBER (LEFT)": production_order["ORDER NUMBER (LEFT)"],
            "ORDER NUMBER (RIGHT)": production_order["ORDER NUMBER (RIGHT)"]
        }
        flag_to_append = 0
        if len(current_shift["PRODUCTION ORDERS"]) is not 0:
            for order in current_shift["PRODUCTION ORDERS"]:
                if "ORDER NUMBER (LEFT)" in order:
                    if order["ORDER NUMBER (LEFT)"] == to_append["ORDER NUMBER (LEFT)"]:
                        if order["ORDER NUMBER (RIGHT)"] == to_append["ORDER NUMBER (RIGHT)"]:
                            flag_to_append = 1
            if flag_to_append == 0:
                print("-----------------------------------")
                print("Production Order Appended !")
                print("-----------------------------------")
                current_shift["PRODUCTION ORDERS"].append(to_append)
        else:
            print("APPENDING SHIFT ORDERS FOR FIRST TIME.")
            current_shift["PRODUCTION ORDERS"].append(to_append)

    update_shift_records(current_shift)

    # create tomorrows shifts if needed

    start_time = current_time + timedelta(days=1)
    start_time_string = start_time.strftime(constants.only_date)
    stop_time = current_time + timedelta(days=2)
    stop_time_string = stop_time.strftime(constants.only_date)
    create_shift_plan(start_time=start_time_string, stop_time=stop_time_string)




def get_current_shift_details():
    current_time = datetime.now() + timedelta(constants.timezone_offset)
    myquery = {"$and": [{"SHIFT START TIME": {"$lte": current_time}},
                        {"SHIFT STOP TIME": {"$gt": current_time}}
                        ]}

    shift = shift_records.find_one(myquery, {'_id': False})

    return shift


'''
###############################################################################################################
                                FUNCTIONS FOR CHARTS ON SHIFT ANALYSIS PAGE
###############################################################################################################                      
'''


def get_downtime_chart_sum(req_date, shift_id):
    # generating time bounds for shifts

    # current_time = datetime.now()
    # ct = datetime.strftime(current_time, "%d/%m/%Y, ")

    ct2 = datetime.strptime(req_date + ", 6:00:00", constants.time_format)
    shiftA_start = ct2
    shiftA_stop = shiftA_start + timedelta(minutes=480)
    shiftB_start = shiftA_stop
    shiftB_stop = shiftB_start + timedelta(minutes=480)
    shiftC_start = shiftB_stop
    shiftC_stop = shiftC_start + timedelta(minutes=480)

    if shift_id == "A":
        current_shift_start = shiftA_start
        current_shift_stop = shiftA_stop
        # print("first shift active")

    elif shift_id == "B":
        current_shift_start = shiftB_start
        current_shift_stop = shiftB_stop
        # print("sec shift active")

    elif shift_id == "C":
        current_shift_start = shiftC_start
        current_shift_stop = shiftC_stop
        # print("third shift active")

    '''
    # Determining Current shift.
    if shiftA_start <= current_time < shiftA_stop:

        current_shift_start = shiftA_start
        current_shift_stop = shiftA_stop
        print("first shift active")

    elif shiftB_start <= current_time < shiftB_stop:

        current_shift_start = shiftB_start
        current_shift_stop = shiftB_stop
        print("sec shift active")

    elif shiftC_start <= current_time < shiftC_stop:

        current_shift_start = shiftC_start
        current_shift_stop = shiftC_stop
        print("third shift active")
    '''

    shift_info = get_all_active_production_orders_from_to(current_shift_start, current_shift_stop)

    downtime_reasons = ["Startup Time", "Mould Change", "Power Cut", "Holiday Startup", "Breakdown", "Trial",
                        "No Plan", "Minor Stops"];
    all_downtimes = []
    planned_mould_change = 0
    planned_start_up = 0
    # pass each rec in downtime_overlaps function

    for rec in shift_info:
        # take sum of mould change and startup
        planned_mould_change += rec["MOULD CHANGE TIME (MIN)"]
        planned_start_up += rec["START UP TIME (MIN)"]

        rec = get_downtime_overlaps(rec)  # calculating downtime overlaps.
        # print(rec)

        all_downtimes.extend(rec)

    # pprint(all_downtimes)
    # print(len(all_downtimes))
    downtime_sum_list = []
    value = 0
    for dr in downtime_reasons:
        value = 0
        for dt in all_downtimes:

            if "stop_time" in dt:
                if (current_shift_start < datetime.strptime(dt["start_time"],
                                                            constants.time_format) < current_shift_stop) or \
                        (current_shift_start < datetime.strptime(dt["start_time"],
                                                                 constants.time_format) < current_shift_stop):

                    try:
                        if dt["reasonlist"] == dr:
                            start_time = datetime.strptime(dt["start_time"], constants.time_format)
                            stop_time = datetime.strptime(dt["stop_time"], constants.time_format)
                            delta = (stop_time - start_time).seconds / 60

                            # print(dt["reasonlist"])
                            value += delta
                    except:
                        pass

        downtime_sum_list.append(round(value, 2))

    # print(downtime_sum_list)
    planned_downtimes = [planned_start_up, planned_mould_change, 0, 0, 0, 0, 0, 0]
    downtime_data = {}
    downtime_data["actual"] = downtime_sum_list
    downtime_data["planned"] = planned_downtimes
    return downtime_data


# PLANT ANALYSIS
def get_downtime_chart_by_machine(req_date, shift_id, machine):
    # generating time bounds for shifts
    ct2 = datetime.strptime(req_date + ", 6:00:00", constants.time_format)
    shiftA_start = ct2
    shiftA_stop = shiftA_start + timedelta(minutes=480)
    shiftB_start = shiftA_stop
    shiftB_stop = shiftB_start + timedelta(minutes=480)
    shiftC_start = shiftB_stop
    shiftC_stop = shiftC_start + timedelta(minutes=480)

    if shift_id == "A":
        current_shift_start = shiftA_start
        current_shift_stop = shiftA_stop
        # print("first shift active")

    elif shift_id == "B":
        current_shift_start = shiftB_start
        current_shift_stop = shiftB_stop
        # print("sec shift active")

    elif shift_id == "C":
        current_shift_start = shiftC_start
        current_shift_stop = shiftC_stop
        # print("third shift active")

    '''
    # Determining Current shift.
    if shiftA_start <= current_time < shiftA_stop:

        current_shift_start = shiftA_start
        current_shift_stop = shiftA_stop
        print("first shift active")

    elif shiftB_start <= current_time < shiftB_stop:

        current_shift_start = shiftB_start
        current_shift_stop = shiftB_stop
        print("sec shift active")

    elif shiftC_start <= current_time < shiftC_stop:

        current_shift_start = shiftC_start
        current_shift_stop = shiftC_stop
        print("third shift active")
    '''
    shift_info = get_active_production_orders_from_to_for_charts(current_shift_start, current_shift_stop, machine)

    downtime_reasons = ["Startup Time", "Mould Change", "Power Cut", "Holiday Startup", "Breakdown", "Trial",
                        "No Plan", "Minor Stops"];
    all_downtimes = []
    planned_mould_change = 0
    planned_start_up = 0

    for rec in shift_info:
        # take sum of mould change and startup
        planned_mould_change += rec["MOULD CHANGE TIME (MIN)"]
        planned_start_up += rec["START UP TIME (MIN)"]

        rec = get_downtime_overlaps(rec)  # calculating downtime overlaps.

        all_downtimes.extend(rec)

    # pprint(all_downtimes)
    # print(len(all_downtimes))
    downtime_sum_list = []
    value = 0
    for dr in downtime_reasons:
        value = 0
        for dt in all_downtimes:
            if "stop_time" in dt:
                if (current_shift_start < datetime.strptime(dt["start_time"],
                                                            constants.time_format) < current_shift_stop) or \
                        (current_shift_start < datetime.strptime(dt["start_time"],
                                                                 constants.time_format) < current_shift_stop):

                    try:
                        if dt["reasonlist"] == dr:
                            start_time = datetime.strptime(dt["start_time"], constants.time_format)
                            stop_time = datetime.strptime(dt["stop_time"], constants.time_format)
                            delta = (stop_time - start_time).seconds / 60

                            # print(dt["reasonlist"])
                            value += delta
                    except:
                        pass
        downtime_sum_list.append(round(value, 2))

    planned_downtimes = [planned_start_up, planned_mould_change, 0, 0, 0, 0, 0, 0]
    # print(planned_downtimes)
    downtime_data = {}
    downtime_data["actual"] = downtime_sum_list
    downtime_data["planned"] = planned_downtimes
    return downtime_data


def get_line_rejection_sum(req_date, shift_id):
    # generating time bounds for shifts
    ct2 = datetime.strptime(req_date + ", 6:00:00", constants.time_format)
    shiftA_start = ct2
    shiftA_stop = shiftA_start + timedelta(minutes=480)
    shiftB_start = shiftA_stop
    shiftB_stop = shiftB_start + timedelta(minutes=480)
    shiftC_start = shiftB_stop
    shiftC_stop = shiftC_start + timedelta(minutes=480)

    if shift_id == "A":
        current_shift_start = shiftA_start
        current_shift_stop = shiftA_stop
        # print("first shift active")

    elif shift_id == "B":
        current_shift_start = shiftB_start
        current_shift_stop = shiftB_stop
    # print("sec shift active")

    elif shift_id == "C":
        current_shift_start = shiftC_start
        current_shift_stop = shiftC_stop
        # print("third shift active")

    '''
    # Determining Current shift.
    if shiftA_start <= current_time < shiftA_stop:

        current_shift_start = shiftA_start
        current_shift_stop = shiftA_stop
        print("first shift active")

    elif shiftB_start <= current_time < shiftB_stop:

        current_shift_start = shiftB_start
        current_shift_stop = shiftB_stop
        print("sec shift active")

    elif shiftC_start <= current_time < shiftC_stop:

        current_shift_start = shiftC_start
        current_shift_stop = shiftC_stop
        print("third shift active")
    '''

    shift_info = get_all_active_production_orders_from_to(current_shift_start, current_shift_stop)

    category_options = ["AIR BUBBLE", "GAS MARK", "BLACK DOT", "PATCH MARK", "PIN MARK", "SCRATCH", "MOISTURE",
                        "BLACK FLOW", "BLACK MARK", "WILD LINE", "POWER CUT REJECTION", "SHORT MOLDING", "SILVER",
                        "SINK MARK", "BURN MARK", "OIL MARK", "FLOW MARK"];
    # print(len(shift_info))
    all_line_rejections = []
    for rec in shift_info:
        if "REJECTION ANALYSIS" in rec:
            all_line_rejections.extend(rec["REJECTION ANALYSIS"])

    # pprint(all_line_rejections)

    rejection_sum_list = []
    value = 0
    for op in category_options:
        value = 0
        for lr in all_line_rejections:
            if current_shift_start < datetime.strptime(lr["timestamp"], constants.time_format) < current_shift_stop:

                if lr["TYPE"] == "LINE REJECTION":
                    if lr["reasonlist"] == op:
                        # print(lr["reasonlist"])
                        weight = float(lr["WEIGHT"])
                        value += weight
        rejection_sum_list.append(value)

    # print(rejection_sum_list)
    return rejection_sum_list


# get line rejection by machine - PLANT ANALYSIS PAGE
def get_line_rejection_by_machine(req_date, shift_id, machine):
    # generating time bounds for shifts
    ct2 = datetime.strptime(req_date + ", 6:00:00", constants.time_format)
    shiftA_start = ct2
    shiftA_stop = shiftA_start + timedelta(minutes=480)
    shiftB_start = shiftA_stop
    shiftB_stop = shiftB_start + timedelta(minutes=480)
    shiftC_start = shiftB_stop
    shiftC_stop = shiftC_start + timedelta(minutes=480)

    if shift_id == "A":
        current_shift_start = shiftA_start
        current_shift_stop = shiftA_stop
        # print("first shift active")

    elif shift_id == "B":
        current_shift_start = shiftB_start
        current_shift_stop = shiftB_stop
    # print("sec shift active")

    elif shift_id == "C":
        current_shift_start = shiftC_start
        current_shift_stop = shiftC_stop
    # print("third shift active")

    '''
    # Determining Current shift.
    if shiftA_start <= current_time < shiftA_stop:

        current_shift_start = shiftA_start
        current_shift_stop = shiftA_stop
        print("first shift active")

    elif shiftB_start <= current_time < shiftB_stop:

        current_shift_start = shiftB_start
        current_shift_stop = shiftB_stop
        print("sec shift active")

    elif shiftC_start <= current_time < shiftC_stop:

        current_shift_start = shiftC_start
        current_shift_stop = shiftC_stop
        print("third shift active")
    '''
    shift_info = get_active_production_orders_from_to_for_charts(current_shift_start, current_shift_stop, machine)

    category_options = ["AIR BUBBLE", "GAS MARK", "BLACK DOT", "PATCH MARK", "PIN MARK", "SCRATCH", "MOISTURE",
                        "BLACK FLOW", "BLACK MARK", "WILD LINE", "POWER CUT REJECTION", "SHORT MOLDING", "SILVER",
                        "SINK MARK", "BURN MARK", "OIL MARK", "FLOW MARK"];

    all_line_rejections = []
    for rec in shift_info:
        if "REJECTION ANALYSIS" in rec:
            all_line_rejections.extend(rec["REJECTION ANALYSIS"])

    # pprint(all_line_rejections)

    rejection_sum_list = []
    value = 0
    for op in category_options:
        value = 0
        for lr in all_line_rejections:
            if current_shift_start < datetime.strptime(lr["timestamp"], constants.time_format) < current_shift_stop:
                if lr["TYPE"] == "LINE REJECTION":
                    if lr["reasonlist"] == op:
                        # print(lr["reasonlist"])
                        weight = float(lr["WEIGHT"])
                        value += weight
        rejection_sum_list.append(value)

    # print(rejection_sum_list)
    return rejection_sum_list


def get_rejection_sum(req_date, shift_id):
    # generating time bounds for shifts
    ct2 = datetime.strptime(req_date + ", 6:00:00", constants.time_format)
    shiftA_start = ct2
    shiftA_stop = shiftA_start + timedelta(minutes=480)
    shiftB_start = shiftA_stop
    shiftB_stop = shiftB_start + timedelta(minutes=480)
    shiftC_start = shiftB_stop
    shiftC_stop = shiftC_start + timedelta(minutes=480)

    if shift_id == "A":
        current_shift_start = shiftA_start
        current_shift_stop = shiftA_stop
        # print("first shift active")

    elif shift_id == "B":
        current_shift_start = shiftB_start
        current_shift_stop = shiftB_stop
        # print("sec shift active")

    elif shift_id == "C":
        current_shift_start = shiftC_start
        current_shift_stop = shiftC_stop
        # print("third shift active")

    '''
    # Determining Current shift.
    if shiftA_start <= current_time < shiftA_stop:

        current_shift_start = shiftA_start
        current_shift_stop = shiftA_stop
        print("first shift active")

    elif shiftB_start <= current_time < shiftB_stop:

        current_shift_start = shiftB_start
        current_shift_stop = shiftB_stop
        print("sec shift active")

    elif shiftC_start <= current_time < shiftC_stop:

        current_shift_start = shiftC_start
        current_shift_stop = shiftC_stop
        print("third shift active")
    '''
    shift_info = get_all_active_production_orders_from_to(current_shift_start, current_shift_stop)

    rejection_types = ["LINE REJECTION", "PROCESS SCRAP", "STARTUP SCRAP", "STARTUP REJECTION"];
    # print(len(shift_info))
    all_rejections = []
    for rec in shift_info:
        if "REJECTION ANALYSIS" in rec:
            all_rejections.extend(rec["REJECTION ANALYSIS"])

    # pprint(all_line_rejections)

    rejection_sum_list = []
    value = 0
    for op in rejection_types:
        value = 0
        input_dict = {}
        for r in all_rejections:
            if current_shift_start < datetime.strptime(r["timestamp"], constants.time_format) < current_shift_stop:
                if r["TYPE"] == op:
                    weight = float(r["WEIGHT"])
                    value += weight
        input_dict["name"] = op
        input_dict["value"] = value
        rejection_sum_list.append(input_dict)

    # print(rejection_sum_list)
    return rejection_sum_list


def get_rejection_by_machine(req_date, shift_id, machine):
    # generating time bounds for shifts
    ct2 = datetime.strptime(req_date + ", 6:00:00", constants.time_format)
    shiftA_start = ct2
    shiftA_stop = shiftA_start + timedelta(minutes=480)
    shiftB_start = shiftA_stop
    shiftB_stop = shiftB_start + timedelta(minutes=480)
    shiftC_start = shiftB_stop
    shiftC_stop = shiftC_start + timedelta(minutes=480)

    if shift_id == "A":
        current_shift_start = shiftA_start
        current_shift_stop = shiftA_stop
        # print("first shift active")

    elif shift_id == "B":
        current_shift_start = shiftB_start
        current_shift_stop = shiftB_stop
        # print("sec shift active")

    elif shift_id == "C":
        current_shift_start = shiftC_start
        current_shift_stop = shiftC_stop
        # print("third shift active")

    '''
    # Determining Current shift.
    if shiftA_start <= current_time < shiftA_stop:

        current_shift_start = shiftA_start
        current_shift_stop = shiftA_stop
        print("first shift active")

    elif shiftB_start <= current_time < shiftB_stop:

        current_shift_start = shiftB_start
        current_shift_stop = shiftB_stop
        print("sec shift active")

    elif shiftC_start <= current_time < shiftC_stop:

        current_shift_start = shiftC_start
        current_shift_stop = shiftC_stop
        print("third shift active")
    '''

    shift_info = get_active_production_orders_from_to_for_charts(current_shift_start, current_shift_stop, machine)

    rejection_types = ["LINE REJECTION", "PROCESS SCRAP", "STARTUP SCRAP", "STARTUP REJECTION"];
    # print(shift_info)
    all_rejections = []
    for rec in shift_info:

        if "REJECTION ANALYSIS" in rec:
            pprint(rec["REJECTION ANALYSIS"])
            all_rejections.extend(rec["REJECTION ANALYSIS"])

    # pprint(all_line_rejections)

    rejection_sum_list = []
    value = 0
    for op in rejection_types:
        value = 0
        input_dict = {}
        for r in all_rejections:
            if r["TYPE"] == op:
                weight = float(r["WEIGHT"])
                value += weight
        input_dict["name"] = op
        input_dict["value"] = value
        rejection_sum_list.append(input_dict)

    # print(rejection_sum_list)
    return rejection_sum_list


def get_kpi_chart(req_date, shift_id):
    current_time = datetime.now()
    ct2 = datetime.strptime(req_date + ", 6:00:00", constants.time_format)
    shiftA_start = ct2
    shiftA_stop = shiftA_start + timedelta(minutes=480)
    shiftB_start = shiftA_stop
    shiftB_stop = shiftB_start + timedelta(minutes=480)
    shiftC_start = shiftB_stop
    shiftC_stop = shiftC_start + timedelta(minutes=480)

    if shift_id == "A":
        current_shift_start = shiftA_start
        current_shift_stop = shiftA_stop
        # print("first shift active")

    elif shift_id == "B":
        current_shift_start = shiftB_start
        current_shift_stop = shiftB_stop
        # print("sec shift active")

    elif shift_id == "C":
        current_shift_start = shiftC_start
        current_shift_stop = shiftC_stop
        # print("third shift active")

    myquery = {"$and": [{"SHIFT START TIME": current_shift_start},
                        {"SHIFT STOP TIME": current_shift_stop}
                        ]}
    values_for_graph = {}
    values_for_graph["Oee"] = []
    values_for_graph["Productivity"] = []
    values_for_graph["Availability"] = []
    values_for_graph["Quality"] = []
    values_for_graph["timestamp"] = []

    shift = shift_records.find_one(myquery, {'_id': False})

    trend_limit = int(((current_shift_stop - current_shift_start).total_seconds()) // 60)
    time_step = 60.00
    from_time = current_shift_start
    to_time = current_shift_start + timedelta(seconds=time_step)
    last_known_prod = 0
    last_known_oee = 0
    last_known_avl = 0
    last_known_quality = 0
    for i in range(0, trend_limit):

        found_flag = 0
        mean_time = (from_time + timedelta(seconds=(time_step / 2))).strftime(constants.time_format)

        for kpi in shift["kpi"]:
            if found_flag == 0:
                if from_time <= kpi["timestamp"] < to_time:
                    values_for_graph["Oee"].append(kpi["Oee"])
                    values_for_graph["Productivity"].append(kpi["Productivity"])
                    values_for_graph["Availability"].append(kpi["Availability"])
                    values_for_graph["Quality"].append(kpi["Quality"])
                    values_for_graph["timestamp"].append(mean_time)
                    last_known_prod = kpi["Productivity"]
                    last_known_oee = kpi["Oee"]
                    last_known_avl = kpi["Availability"]
                    last_known_quality = kpi["Quality"]
                    found_flag = 1
                    break
        if found_flag == 0:
            values_for_graph["Oee"].append(last_known_oee)
            values_for_graph["Productivity"].append(last_known_prod)
            values_for_graph["Availability"].append(last_known_avl)
            values_for_graph["Quality"].append(last_known_quality)
            values_for_graph["timestamp"].append(mean_time)

        # increment time
        from_time = to_time
        to_time = to_time + timedelta(seconds=time_step)

    return values_for_graph


def production_plan_analysis_for_shift(req_date, shift_id):
    ct2 = datetime.strptime(req_date + ", 6:00:00", constants.time_format)
    shiftA_start = ct2
    shiftA_stop = shiftA_start + timedelta(minutes=480)
    shiftB_start = shiftA_stop
    shiftB_stop = shiftB_start + timedelta(minutes=480)
    shiftC_start = shiftB_stop
    shiftC_stop = shiftC_start + timedelta(minutes=480)

    if shift_id == "A":
        current_shift_start = shiftA_start
        current_shift_stop = shiftA_stop
        # print("first shift active")

    elif shift_id == "B":
        current_shift_start = shiftB_start
        current_shift_stop = shiftB_stop
        # print("sec shift active")

    elif shift_id == "C":
        current_shift_start = shiftC_start
        current_shift_stop = shiftC_stop
        # print("third shift active")

    shift_details = get_all_active_production_orders_from_to(current_shift_start, current_shift_stop)

    all_shot_details = []
    for order in shift_details:

        actual_shots_counter = 0  # reset for each PO
        shot_details = {}

        if "SHOT_DETAILS" in order:
            for shot in order["SHOT_DETAILS"]:
                shot_timestamp = datetime.strptime(shot["timestamp"], constants.time_format)
                if current_shift_start < shot_timestamp < current_shift_stop:
                    actual_shots_counter += 1  # SHOTS LYING WITHIN THE SHIFT.

        # subtracting rejections
        line_rejection = 0
        if "REJECTION ANALYSIS" in order:

            for rejection in order["REJECTION ANALYSIS"]:
                rejection_timestamp = datetime.strptime(rejection["timestamp"], constants.time_format)
                if rejection[
                    "TYPE"] == 'LINE REJECTION' and current_shift_start < rejection_timestamp < current_shift_stop:
                    line_rejection += int(rejection["QUANTITY"])

        shot_details["rejection"] = line_rejection

        actual_shots_counter -= line_rejection

        # CALCULATE EXPECTED SHOTS

        start_time = current_shift_start
        stop_time = datetime.now()  # current_shift_stop
        actual_start_time = order["ACTUAL_START"]
        if current_shift_start < actual_start_time:
            start_time = actual_start_time

        if order["ACTUAL_STOP"] != "-":
            actual_stop_time = order["ACTUAL_STOP"]

            if current_shift_stop > actual_stop_time:
                stop_time = actual_stop_time

        total_duration = (stop_time - start_time).seconds

        planned_shots = total_duration // order["CYCLE TIME"]
        shot_details["duration"] = total_duration
        # shot_details["start"] = start_time
        # shot_details["stop"] = stop_time
        shot_details["planned_shots"] = planned_shots
        shot_details["cycle_time"] = order["CYCLE TIME"]
        shot_details["actual_shot_count"] = actual_shots_counter
        shot_details["machine"] = order["MACHINE"]
        shot_details["po_right"] = order["ORDER NUMBER (RIGHT)"]
        shot_details["po_left"] = order["ORDER NUMBER (LEFT)"]
        all_shot_details.append(shot_details)

    # pprint(all_shot_details)
    return all_shot_details


def get_energy_consumption_for_shift(req_date, shift_id):
    # time.sleep(10)
    ct2 = datetime.strptime(req_date + ", 6:00:00", constants.time_format)
    shiftA_start = ct2
    shiftA_stop = shiftA_start + timedelta(minutes=480)
    shiftB_start = shiftA_stop
    shiftB_stop = shiftB_start + timedelta(minutes=480)
    shiftC_start = shiftB_stop
    shiftC_stop = shiftC_start + timedelta(minutes=480)

    if shift_id == "A":
        current_shift_start = shiftA_start
        current_shift_stop = shiftA_stop
        # print("first shift active")

    elif shift_id == "B":
        current_shift_start = shiftB_start
        current_shift_stop = shiftB_stop
        # print("sec shift active")

    elif shift_id == "C":
        current_shift_start = shiftC_start
        current_shift_stop = shiftC_stop
        # print("third shift active")

    shift_details = get_all_active_production_orders_from_to(current_shift_start, current_shift_stop)
    all_chart_data = []
    machine_list = ['JSW 350T', "JSW 650T", "JSW 550T-II", "JSW 450T-II", "JSW 550T-I", "JSW 450T-III", "JSW 450T"]
    unique_machines = []
    final = {}
    final["machines"] = machine_list
    final["energy"] = []

    for machine in machine_list:
        found_flag = 0
        energy_diff = 0

        for sd in shift_details:
            if machine == sd["MACHINE"]:
                # print("##################################################################################")
                # print(sd["MACHINE"])
                # print(sd["ORDER NUMBER (LEFT)"])

                if "ENERGY DETAILS" in sd:
                    try:
                        for detail in sd["ENERGY DETAILS"]:

                            detail_timestamp = datetime.strptime(detail["timestamp"], constants.time_format)
                            if current_shift_start < detail_timestamp < current_shift_stop:
                                print(float(detail["energy_difference"]))
                                print(detail["timestamp"])
                                energy_diff += float(detail["energy_difference"])
                                found_flag = 1
                            else:
                                pass
                    except:
                        pass
                else:
                    pass

        if found_flag == 1:
            final["energy"].append(energy_diff)

        else:
            final["energy"].append(0)

    return final


'''
###############################################################################################################
                      HIERARCHY PAGE 
###############################################################################################################                      
'''


def get_json_for_heirarchy_chart():
    data = {
        "name": "PPAP",
        "itemStyle": {
            "borderColor": "orange"
        },
        "children": [
            {
                "name": "PLANT I",
                "itemStyle": {
                    "borderColor": "gray"
                },
                "children": []
            },
            {
                "name": "PLANT II",
                "itemStyle": {
                    "borderColor": "gray"
                },
                "children": []
            },
            {
                "name": "PLANT III",
                "itemStyle": {
                    "borderColor": "green"
                },
                "children": []
            },
            {
                "name": "PLANT IV",
                "itemStyle": {
                    "borderColor": "gray"
                },
                "children": []
            },
            {
                "name": "PLANT V",
                "itemStyle": {
                    "borderColor": "gray"
                },
                "children": []
            },
            {
                "name": "PLANT VI",
                "itemStyle": {
                    "borderColor": "gray"
                },
                "children": []
            }, {
                "name": "PLANT VII",
                "itemStyle": {
                    "borderColor": "gray"
                },
                "children": []
            },
            {
                "name": "PTI I",
                "itemStyle": {
                    "borderColor": "gray"
                },
                "children": []
            }, {
                "name": "PTI II",
                "itemStyle": {
                    "borderColor": "gray"
                },
                "children": []
            }

        ]

    }
    machine_template = {
        "name": "JSW 450T-I",
        "itemStyle": {
            "borderColor": "gray"
        },
        "children": []
    }
    parameter_template = {
        "name": "OEE : --",
        "value": 0,
        "itemStyle": {
            "borderColor": "gray"
        }
    }

    # print(data["children"][2])

    # APPEND DATA TO THIS FUNCTION

    all_machines = ["JSW 550T-I", "JSW 550T-II", "JSW 450T-I", "JSW 450T-II", "JSW 450T-III", "JSW 650T", "JSW 350T"]

    for machine in all_machines:
        machine_json = copy.deepcopy(machine_template)
        machine_json["name"] = machine
        order_data = get_production_order_with_KPI({"machine": machine})
        try:
            machine_json["part_name"] = "PART :" + order_data["PART NAME"]
        except:
            machine_json["part_name"] = "PART : --"

        if order_data == None:
            pass
        else:
            try:
                if order_data["CURRENT_DOWNTIME_STATUS"]["downtime_status"] == 'true':
                    machine_json["itemStyle"]["borderColor"] = "red"
                else:
                    machine_json["itemStyle"]["borderColor"] = "green"
            except:
                machine_json["itemStyle"]["borderColor"] = "grey"

            parameter_template_new = copy.deepcopy(parameter_template)
            parameter_template_new["name"] = "OEE : " + str(order_data["kpi"][-1]["Oee"]) + " %"
            parameter_template_new["value"] = order_data["kpi"][-1]["Oee"]
            try:
                if constants.OEE > float(order_data["kpi"][-1]["Oee"]):
                    parameter_template_new["itemStyle"]["borderColor"] = "orange"
                else:
                    parameter_template_new["itemStyle"]["borderColor"] = "green"
            except:
                parameter_template_new["itemStyle"]["borderColor"] = "grey"

            machine_json["children"].append(parameter_template_new)

            parameter_template_new = copy.deepcopy(parameter_template)
            parameter_template_new["name"] = "Availability : " + str(order_data["kpi"][-1]["Availability"]) + " %"
            parameter_template_new["value"] = order_data["kpi"][-1]["Availability"]
            try:
                if constants.A > float(order_data["kpi"][-1]["Availability"]):
                    parameter_template_new["itemStyle"]["borderColor"] = "orange"
                else:
                    parameter_template_new["itemStyle"]["borderColor"] = "green"
            except:
                parameter_template_new["itemStyle"]["borderColor"] = "grey"

            machine_json["children"].append(parameter_template_new)

            parameter_template_new = copy.deepcopy(parameter_template)
            parameter_template_new["name"] = "Productivity : " + str(order_data["kpi"][-1]["Productivity"]) + " %"
            parameter_template_new["value"] = order_data["kpi"][-1]["Productivity"]
            try:
                if constants.P > float(order_data["kpi"][-1]["Productivity"]):
                    parameter_template_new["itemStyle"]["borderColor"] = "orange"
                else:
                    parameter_template_new["itemStyle"]["borderColor"] = "green"
            except:
                parameter_template_new["itemStyle"]["borderColor"] = "grey"
            machine_json["children"].append(parameter_template_new)

            parameter_template_new = copy.deepcopy(parameter_template)
            parameter_template_new["name"] = "Quality : " + str(order_data["kpi"][-1]["Quality"]) + " %"
            parameter_template_new["value"] = order_data["kpi"][-1]["Quality"]

            try:
                if constants.Q > float(order_data["kpi"][-1]["Quality"]):
                    parameter_template_new["itemStyle"]["borderColor"] = "orange"
                else:
                    parameter_template_new["itemStyle"]["borderColor"] = "green"
            except:
                parameter_template_new["itemStyle"]["borderColor"] = "grey"

            machine_json["children"].append(parameter_template_new)

        data["children"][2]["children"].append(machine_json)

    print("GENERATION OF HEIRARCHY DATA COMPLETE.")
    return data


def get_shift_timeline(req_date, shift_id, machine):
    # Shift Definitions.
    ct2 = datetime.strptime(req_date + ", 6:00:00", constants.time_format)
    shiftA_start = ct2
    shiftA_stop = shiftA_start + timedelta(minutes=480)
    shiftB_start = shiftA_stop
    shiftB_stop = shiftB_start + timedelta(minutes=480)
    shiftC_start = shiftB_stop
    shiftC_stop = shiftC_start + timedelta(minutes=480)

    if shift_id == "A":
        current_shift_start = shiftA_start
        current_shift_stop = shiftA_stop
        # print("first shift active")

    elif shift_id == "B":
        current_shift_start = shiftB_start
        current_shift_stop = shiftB_stop
        # print("sec shift active")

    elif shift_id == "C":
        current_shift_start = shiftC_start
        current_shift_stop = shiftC_stop
        # print("third shift active")

    shift_details = get_active_production_orders_from_to_for_charts(current_shift_start, current_shift_stop, machine)

    shift_to_send = {}
    shift_to_send["SHIFT START TIME"] = current_shift_start
    shift_to_send["SHIFT STOP TIME"] = current_shift_stop

    timeline_data = []

    po_counter = 0
    tl_start = 0
    tl_stop = 0

    tl_start_value = 0
    tl_stop_value = 0
    tl_delta = 0

    for po in shift_details:

        if po_counter == 0:
            po_start, po_stop = get_times_for_order_in_shift(po, shift_to_send)
            # print("####################################")
            # print(po_start)
            # print(po_stop)
            # print((po_stop - po_start).seconds)
            # print("####################################")

            tl_start = current_shift_start
            tl_stop = current_shift_stop
            downtime_flag = 0
            tl_start_value = 0
            tl_stop_value = 0
            tl_delta = 0

            # data_template = { "name": "RunTime", "value": [0, tl_start_value, tl_stop_value, tl_delta], "itemStyle": {
            # "normal": { "color": "#007E31" } } }
            # ============================================================================================
            # Idle time between shift start and first order if any.
            if po_start > current_shift_start:
                # tl_instance for idle time
                # --------------------------------------------------------------------------------------

                tl_stop = po_start
                tl_delta = (tl_stop - tl_start).seconds
                tl_stop_value = tl_delta + tl_start_value

                tl_instance = {"name": "Idle", "value": [0, tl_start_value, tl_stop_value, tl_delta],
                               "itemStyle": {"normal": {"color": "#888888"}}}

                timeline_data.append(tl_instance)
                # re-assign tl_start_value and tl_start to previous stop.
                tl_start_value = tl_stop_value
                tl_start = tl_stop
            # ============================================================================================
            if "DOWNTIME" in po:

                # print("Downtimes found")
                downtimes1 = get_downtime_overlaps(po)
                downtimes = get_downtimes_within_shift(downtimes1, shift_to_send)
                # pprint(downtimes)
                # Correct downtimes.
                if len(downtimes) > 0:

                    downtime_flag = 1
                    for i in range(0, len(downtimes)):
                        try:
                            downtime_reason = downtimes[i]["reasonlist"]
                        except:
                            downtime_reason = "Downtime"
                        # print("i am in loop 1")

                        if po_start < datetime.strptime(downtimes[i]["start_time"], constants.time_format):
                            # print("i entered loop 2")

                            if i == 0:
                                # print("i entered loop 3")
                                # tl_instance from order start to first downtime.
                                # --------------------------------------------------------------------------------------------------
                                tl_stop = datetime.strptime(downtimes[i]["start_time"], constants.time_format)
                                tl_delta = (tl_stop - tl_start).seconds
                                tl_stop_value = tl_delta + tl_start_value

                                tl_instance = {"name": "RunTime", "value": [0, tl_start_value, tl_stop_value, tl_delta],
                                               "itemStyle": {"normal": {"color": "green"}}}

                                timeline_data.append(tl_instance)

                                # re-assign tl_start_value and tl_start to previous stop.
                                tl_start_value = tl_stop_value
                                tl_start = tl_stop

                                # tl_instance for first downtime.
                                # ---------------------------------------------------------------------------------------
                                if po_stop > datetime.strptime(downtimes[i]["stop_time"], constants.time_format):

                                    # downtime stops within shift
                                    tl_stop = datetime.strptime(downtimes[i]["stop_time"], constants.time_format)
                                    tl_delta = (tl_stop - tl_start).seconds
                                    tl_stop_value = tl_delta + tl_start_value

                                    tl_instance = {"name": downtime_reason,
                                                   "value": [0, tl_start_value, tl_stop_value, tl_delta],
                                                   "itemStyle": {"normal": {"color": "#8B0000"}}}

                                    timeline_data.append(tl_instance)
                                    # re-assign tl_start_value and tl_start to previous stop.
                                    tl_start_value = tl_stop_value
                                    tl_start = tl_stop
                                else:
                                    # downtime exceeds shift time. -- exit --
                                    tl_stop = po_stop
                                    tl_delta = (tl_stop - tl_start).seconds
                                    tl_stop_value = tl_delta + tl_start_value

                                    tl_instance = {"name": downtime_reason,
                                                   "value": [0, tl_start_value, tl_stop_value, tl_delta],
                                                   "itemStyle": {"normal": {"color": "#8B0000"}}}

                                    timeline_data.append(tl_instance)
                                    # re-assign tl_start_value and tl_start to previous stop.
                                    tl_start_value = tl_stop_value
                                    tl_start = tl_stop

                            elif po_stop > datetime.strptime(downtimes[i]["stop_time"], constants.time_format):
                                # more than one downtime.
                                # Check for Runtime between two downtimes and append if any.
                                if (datetime.strptime(downtimes[i]["start_time"],
                                                      constants.time_format) - tl_stop).seconds != 0:
                                    # Run time found between downtimes.
                                    tl_stop = datetime.strptime(downtimes[i]["start_time"], constants.time_format)
                                    tl_delta = (tl_stop - tl_start).seconds
                                    tl_stop_value = tl_delta + tl_start_value
                                    tl_instance = {"name": "RunTime",
                                                   "value": [0, tl_start_value, tl_stop_value, tl_delta],
                                                   "itemStyle": {"normal": {"color": "green"}}}

                                    timeline_data.append(tl_instance)

                                    # re-assign tl_start_value and tl_start to previous stop.
                                    tl_start_value = tl_stop_value
                                    tl_start = tl_stop
                                    # tl_instance for runtime between downtimes.

                                # tl_instance for second downtime onwards.
                                # --------------------------------------------------------------------------------------
                                # downtime stops within shift
                                tl_stop = datetime.strptime(downtimes[i]["stop_time"], constants.time_format)
                                tl_delta = (tl_stop - tl_start).seconds
                                tl_stop_value = tl_delta + tl_start_value

                                tl_instance = {"name": downtime_reason,
                                               "value": [0, tl_start_value, tl_stop_value, tl_delta],
                                               "itemStyle": {"normal": {"color": "#8B0000"}}}

                                timeline_data.append(tl_instance)
                                # re-assign tl_start_value and tl_start to previous stop.
                                tl_start_value = tl_stop_value
                                tl_start = tl_stop

                            else:
                                # downtime exceeds shift time. -- exit --
                                tl_stop = po_stop
                                tl_delta = (tl_stop - tl_start).seconds
                                tl_stop_value = tl_delta + tl_start_value

                                tl_instance = {"name": downtime_reason,
                                               "value": [0, tl_start_value, tl_stop_value, tl_delta],
                                               "itemStyle": {"normal": {"color": "#8B0000"}}}

                                timeline_data.append(tl_instance)
                                # re-assign tl_start_value and tl_start to previous stop.
                                tl_start_value = tl_stop_value
                                tl_start = tl_stop

                        else:  # downtime out of shift boundaries.
                            tl_stop = po_stop
                            tl_delta = (tl_stop - tl_start).seconds
                            tl_stop_value = tl_delta + tl_start_value

                            tl_instance = {"name": downtime_reason,
                                           "value": [0, tl_start_value, tl_stop_value, tl_delta],
                                           "itemStyle": {"normal": {"color": "#8B0000"}}}

                            timeline_data.append(tl_instance)
                            # re-assign tl_start_value and tl_start to previous stop.
                            tl_start_value = tl_stop_value
                            tl_start = tl_stop
                else:
                    print("NO DOWNTIMES FOUND")
                    tl_stop = po_stop
                    tl_delta = (tl_stop - tl_start).seconds
                    tl_stop_value = tl_delta + tl_start_value

                    tl_instance = {"name": "Runtime", "value": [0, tl_start_value, tl_stop_value, tl_delta],
                                   "itemStyle": {"normal": {"color": "green"}}}

                    timeline_data.append(tl_instance)
                    # re-assign tl_start_value and tl_start to previous stop.
                    tl_start_value = tl_stop_value
                    tl_start = tl_stop

                if downtime_flag == 1:
                    # check for remaining running times after all downtimes
                    tl_stop = po_stop
                    tl_delta = (tl_stop - tl_start).seconds
                    tl_stop_value = tl_delta + tl_start_value

                    tl_instance = {"name": "Runtime", "value": [0, tl_start_value, tl_stop_value, tl_delta],
                                   "itemStyle": {"normal": {"color": "green"}}}

                    timeline_data.append(tl_instance)
                    # re-assign tl_start_value and tl_start to previous stop.
                    tl_start_value = tl_stop_value
                    tl_start = tl_stop

            else:  # No Downtimes - Calculate total runtime for po.
                # print("NO DOWNTIMES FOUND")
                tl_stop = po_stop
                tl_delta = (tl_stop - tl_start).seconds
                tl_stop_value = tl_delta + tl_start_value

                tl_instance = {"name": "Runtime", "value": [0, tl_start_value, tl_stop_value, tl_delta],
                               "itemStyle": {"normal": {"color": "green"}}}

                timeline_data.append(tl_instance)
                # re-assign tl_start_value and tl_start to previous stop.
                tl_start_value = tl_stop_value
                tl_start = tl_stop

            # After checking downtimes
            # If no downtimes : Check
            # If downtimes : Check for the running time after downtime.
            po_counter = 1

        else:
            # print("second po exists")
            # SECOND PO | CONSIDER PREVIOUS TL_STOP AND CHECK IF IDLE TIME EXISTS

            po_start, po_stop = get_times_for_order_in_shift(po, shift_to_send)
            # print("------------------------------------")
            # print(po_start)
            # print(po_stop)
            # print((po_stop - po_start).seconds)
            # print("------------------------------------")

            tl_start = tl_stop  # using previous tl_stop for continuation.
            tl_stop = po_stop
            downtime_flag = 0
            # NOT initiating start stop values | Carry from previous PO
            '''tl_start_value = 0
            tl_stop_value = 0
            tl_delta = 0'''
            # ==========================================================================================
            # Check if Idle time exists. tl_start used in condition below is previous tl_stop
            # Check difference between po start and previous tl_stop

            if (po_start - tl_start).seconds != 0:
                # print("FOUND IDLE TIME BETWEEN POS") # This condition will always arise
                # tl_instance for idle time
                # --------------------------------------------------------------------------------------

                tl_stop = po_start
                tl_delta = (tl_stop - tl_start).seconds
                tl_stop_value = tl_delta + tl_start_value

                tl_instance = {"name": "Idle", "value": [0, tl_start_value, tl_stop_value, tl_delta],
                               "itemStyle": {"normal": {"color": "#888888"}}}

                timeline_data.append(tl_instance)
                # re-assign tl_start_value and tl_start to previous stop.
                tl_start_value = tl_stop_value
                tl_start = tl_stop

            # ==========================================================================================

            if "DOWNTIME" in po:

                downtimes1 = get_downtime_overlaps(po)
                downtimes = get_downtimes_within_shift(downtimes1, shift_to_send)
                # pprint(downtimes)
                # Correct downtimes.
                if len(downtimes) > 0:

                    downtime_flag = 1
                    for i in range(0, len(downtimes)):
                        try:
                            downtime_reason = downtimes[i]["reasonlist"]
                        except:
                            downtime_reason = "Downtime"
                        # print("i am in loop 1")

                        if po_start < datetime.strptime(downtimes[i]["start_time"], constants.time_format):
                            # print("i entered loop 2")

                            if i == 0:
                                # print("i entered loop 3")
                                # tl_instance from order start to first downtime.
                                # --------------------------------------------------------------------------------------------------
                                tl_stop = datetime.strptime(downtimes[i]["start_time"], constants.time_format)
                                tl_delta = (tl_stop - tl_start).seconds
                                tl_stop_value = tl_delta + tl_start_value

                                tl_instance = {"name": "RunTime", "value": [0, tl_start_value, tl_stop_value, tl_delta],
                                               "itemStyle": {"normal": {"color": "green"}}}

                                timeline_data.append(tl_instance)

                                # re-assign tl_start_value and tl_start to previous stop.
                                tl_start_value = tl_stop_value
                                tl_start = tl_stop

                                # tl_instance for first downtime.
                                # ---------------------------------------------------------------------------------------
                                if po_stop > datetime.strptime(downtimes[i]["stop_time"], constants.time_format):

                                    # downtime stops within shift
                                    tl_stop = datetime.strptime(downtimes[i]["stop_time"], constants.time_format)
                                    tl_delta = (tl_stop - tl_start).seconds
                                    tl_stop_value = tl_delta + tl_start_value

                                    tl_instance = {"name": downtime_reason,
                                                   "value": [0, tl_start_value, tl_stop_value, tl_delta],
                                                   "itemStyle": {"normal": {"color": "#8B0000"}}}

                                    timeline_data.append(tl_instance)
                                    # re-assign tl_start_value and tl_start to previous stop.
                                    tl_start_value = tl_stop_value
                                    tl_start = tl_stop
                                else:
                                    # downtime exceeds shift time. -- exit --
                                    tl_stop = po_stop
                                    tl_delta = (tl_stop - tl_start).seconds
                                    tl_stop_value = tl_delta + tl_start_value

                                    tl_instance = {"name": downtime_reason,
                                                   "value": [0, tl_start_value, tl_stop_value, tl_delta],
                                                   "itemStyle": {"normal": {"color": "#8B0000"}}}

                                    timeline_data.append(tl_instance)
                                    # re-assign tl_start_value and tl_start to previous stop.
                                    tl_start_value = tl_stop_value
                                    tl_start = tl_stop

                            elif po_stop > datetime.strptime(downtimes[i]["stop_time"], constants.time_format):
                                # more than one downtime.

                                # Check for Runtime between two downtimes and append if any.
                                if (datetime.strptime(downtimes[i]["start_time"],
                                                      constants.time_format) - tl_stop).seconds != 0:
                                    # Run time found between downtimes.
                                    tl_stop = datetime.strptime(downtimes[i]["start_time"], constants.time_format)
                                    tl_delta = (tl_stop - tl_start).seconds
                                    tl_stop_value = tl_delta + tl_start_value
                                    tl_instance = {"name": "RunTime",
                                                   "value": [0, tl_start_value, tl_stop_value, tl_delta],
                                                   "itemStyle": {"normal": {"color": "green"}}}

                                    timeline_data.append(tl_instance)

                                    # re-assign tl_start_value and tl_start to previous stop.
                                    tl_start_value = tl_stop_value
                                    tl_start = tl_stop
                                    # tl_instance for runtime between downtimes.

                                # tl_instance for second downtime onwards.
                                # --------------------------------------------------------------------------------------
                                # downtime stops within shift
                                tl_stop = datetime.strptime(downtimes[i]["stop_time"], constants.time_format)
                                tl_delta = (tl_stop - tl_start).seconds
                                tl_stop_value = tl_delta + tl_start_value

                                tl_instance = {"name": downtime_reason,
                                               "value": [0, tl_start_value, tl_stop_value, tl_delta],
                                               "itemStyle": {"normal": {"color": "#8B0000"}}}

                                timeline_data.append(tl_instance)
                                # re-assign tl_start_value and tl_start to previous stop.
                                tl_start_value = tl_stop_value
                                tl_start = tl_stop
                            else:
                                # downtime exceeds shift time. -- exit --
                                tl_stop = po_stop
                                tl_delta = (tl_stop - tl_start).seconds
                                tl_stop_value = tl_delta + tl_start_value

                                tl_instance = {"name": downtime_reason,
                                               "value": [0, tl_start_value, tl_stop_value, tl_delta],
                                               "itemStyle": {"normal": {"color": "#8B0000"}}}

                                timeline_data.append(tl_instance)
                                # re-assign tl_start_value and tl_start to previous stop.
                                tl_start_value = tl_stop_value
                                tl_start = tl_stop

                        else:  # downtime out of shift boundaries.
                            tl_stop = po_stop
                            tl_delta = (tl_stop - tl_start).seconds
                            tl_stop_value = tl_delta + tl_start_value

                            tl_instance = {"name": downtime_reason,
                                           "value": [0, tl_start_value, tl_stop_value, tl_delta],
                                           "itemStyle": {"normal": {"color": "#8B0000"}}}

                            timeline_data.append(tl_instance)
                            # re-assign tl_start_value and tl_start to previous stop.
                            tl_start_value = tl_stop_value
                            tl_start = tl_stop
                else:
                    # No Downtimes
                    tl_stop = po_stop
                    tl_delta = (tl_stop - tl_start).seconds
                    tl_stop_value = tl_delta + tl_start_value

                    tl_instance = {"name": "Runtime", "value": [0, tl_start_value, tl_stop_value, tl_delta],
                                   "itemStyle": {"normal": {"color": "green"}}}

                    timeline_data.append(tl_instance)
                    # re-assign tl_start_value and tl_start to previous stop.
                    tl_start_value = tl_stop_value
                    tl_start = tl_stop

                if downtime_flag == 1:
                    tl_stop = po_stop
                    tl_delta = (tl_stop - tl_start).seconds
                    tl_stop_value = tl_delta + tl_start_value

                    tl_instance = {"name": "Runtime", "value": [0, tl_start_value, tl_stop_value, tl_delta],
                                   "itemStyle": {"normal": {"color": "green"}}}

                    timeline_data.append(tl_instance)
                    # re-assign tl_start_value and tl_start to previous stop.
                    tl_start_value = tl_stop_value
                    tl_start = tl_stop

            else:  # No Downtimes - Calculate total runtime for po.
                tl_stop = po_stop
                tl_delta = (tl_stop - tl_start).seconds
                tl_stop_value = tl_delta + tl_start_value

                tl_instance = {"name": "Runtime", "value": [0, tl_start_value, tl_stop_value, tl_delta],
                               "itemStyle": {"normal": {"color": "green"}}}

                timeline_data.append(tl_instance)
                # re-assign tl_start_value and tl_start to previous stop.
                tl_start_value = tl_stop_value
                tl_start = tl_stop

    x_axis_labels = []
    # generate x axis labels:

    # pprint(timeline_data)
    return timeline_data


# vatsal
def get_downtimes_within_shift(downtimes, shift):
    filtered_downtimes = []
    for dt in downtimes:
        if (shift["SHIFT START TIME"] < datetime.strptime(dt["start_time"], constants.time_format) < shift[
            "SHIFT STOP TIME"]) or \
                (shift["SHIFT START TIME"] < datetime.strptime(dt["start_time"], constants.time_format) < shift[
                    "SHIFT STOP TIME"]):
            filtered_downtimes.append(dt)
        else:
            pass

    return filtered_downtimes


# get_shift_timeline('30/01/2021', 'B', 'JSW 550T-II')
def get_timelines_for_all_machines(req_date, shift_id):
    final_data = []
    machine_list = ['JSW 350T', "JSW 650T", "JSW 550T-II", "JSW 450T-II", "JSW 550T-I", "JSW 450T-III", "JSW 450T"]
    seq = 0
    for machine in machine_list:
        try:
            data = get_timelines(req_date, shift_id, machine, seq)
            final_data.extend(data)
        except:
            pass
        seq += 1

    # pprint(final_data)
    return final_data


def get_timelines(req_date, shift_id, machine, seq):
    # Shift Definitions.
    ct2 = datetime.strptime(req_date + ", 6:00:00", constants.time_format)
    shiftA_start = ct2
    shiftA_stop = shiftA_start + timedelta(minutes=480)
    shiftB_start = shiftA_stop
    shiftB_stop = shiftB_start + timedelta(minutes=480)
    shiftC_start = shiftB_stop
    shiftC_stop = shiftC_start + timedelta(minutes=480)

    if shift_id == "A":
        current_shift_start = shiftA_start
        current_shift_stop = shiftA_stop
        # print("first shift active")

    elif shift_id == "B":
        current_shift_start = shiftB_start
        current_shift_stop = shiftB_stop
        # print("sec shift active")

    elif shift_id == "C":
        current_shift_start = shiftC_start
        current_shift_stop = shiftC_stop
        # print("third shift active")

    shift_details = get_active_production_orders_from_to_for_charts(current_shift_start, current_shift_stop, machine)

    shift_to_send = {}
    shift_to_send["SHIFT START TIME"] = current_shift_start
    shift_to_send["SHIFT STOP TIME"] = current_shift_stop

    timeline_data = []

    po_counter = 0
    tl_start = 0
    tl_stop = 0

    tl_start_value = 0
    tl_stop_value = 0
    tl_delta = 0

    for po in shift_details:

        if po_counter == 0:
            po_start, po_stop = get_times_for_order_in_shift(po, shift_to_send)
            # print("####################################")
            # print(po_start)
            # print(po_stop)
            # print((po_stop - po_start).seconds)
            # print("####################################")

            tl_start = current_shift_start
            tl_stop = current_shift_stop
            downtime_flag = 0
            tl_start_value = 0
            tl_stop_value = 0
            tl_delta = 0

            # data_template = { "name": "RunTime", "value": [0, tl_start_value, tl_stop_value, tl_delta], "itemStyle": {
            # "normal": { "color": "#007E31" } } }
            # ============================================================================================
            # Idle time between shift start and first order if any.
            if po_start > current_shift_start:
                # tl_instance for idle time
                # --------------------------------------------------------------------------------------

                tl_stop = po_start
                tl_delta = (tl_stop - tl_start).seconds
                tl_stop_value = tl_delta + tl_start_value

                tl_instance = {"name": "Idle", "value": [seq, tl_start_value, tl_stop_value, tl_delta],
                               "itemStyle": {"normal": {"color": "#888888"}}}

                timeline_data.append(tl_instance)
                # re-assign tl_start_value and tl_start to previous stop.
                tl_start_value = tl_stop_value
                tl_start = tl_stop
            # ============================================================================================
            if "DOWNTIME" in po:

                print("Downtimes found")
                downtimes1 = get_downtime_overlaps(po)
                downtimes = get_downtimes_within_shift(downtimes1, shift_to_send)
                # pprint(downtimes)
                # Correct downtimes.
                if len(downtimes) > 0:

                    downtime_flag = 1
                    for i in range(0, len(downtimes)):
                        try:
                            downtime_reason = downtimes[i]["reasonlist"]
                        except:
                            downtime_reason = "Downtime"
                        # print("i am in loop 1")

                        if po_start < datetime.strptime(downtimes[i]["start_time"], constants.time_format):
                            # print("i entered loop 2")

                            if i == 0:
                                # print("i entered loop 3")
                                # tl_instance from order start to first downtime.
                                # --------------------------------------------------------------------------------------------------
                                tl_stop = datetime.strptime(downtimes[i]["start_time"], constants.time_format)
                                tl_delta = (tl_stop - tl_start).seconds
                                tl_stop_value = tl_delta + tl_start_value

                                tl_instance = {"name": "RunTime",
                                               "value": [seq, tl_start_value, tl_stop_value, tl_delta],
                                               "itemStyle": {"normal": {"color": "green"}}}

                                timeline_data.append(tl_instance)

                                # re-assign tl_start_value and tl_start to previous stop.
                                tl_start_value = tl_stop_value
                                tl_start = tl_stop

                                # tl_instance for first downtime.
                                # ---------------------------------------------------------------------------------------
                                if po_stop > datetime.strptime(downtimes[i]["stop_time"], constants.time_format):

                                    # downtime stops within shift
                                    tl_stop = datetime.strptime(downtimes[i]["stop_time"], constants.time_format)
                                    tl_delta = (tl_stop - tl_start).seconds
                                    tl_stop_value = tl_delta + tl_start_value

                                    tl_instance = {"name": downtime_reason,
                                                   "value": [seq, tl_start_value, tl_stop_value, tl_delta],
                                                   "itemStyle": {"normal": {"color": "#8B0000"}}}

                                    timeline_data.append(tl_instance)
                                    # re-assign tl_start_value and tl_start to previous stop.
                                    tl_start_value = tl_stop_value
                                    tl_start = tl_stop
                                else:
                                    # downtime exceeds shift time. -- exit --
                                    tl_stop = po_stop
                                    tl_delta = (tl_stop - tl_start).seconds
                                    tl_stop_value = tl_delta + tl_start_value

                                    tl_instance = {"name": downtime_reason,
                                                   "value": [seq, tl_start_value, tl_stop_value, tl_delta],
                                                   "itemStyle": {"normal": {"color": "#8B0000"}}}

                                    timeline_data.append(tl_instance)
                                    # re-assign tl_start_value and tl_start to previous stop.
                                    tl_start_value = tl_stop_value
                                    tl_start = tl_stop

                            elif po_stop > datetime.strptime(downtimes[i]["stop_time"], constants.time_format):
                                # more than one downtime.
                                # Check for Runtime between two downtimes and append if any.
                                if (datetime.strptime(downtimes[i]["start_time"],
                                                      constants.time_format) - tl_stop).seconds != 0:
                                    # Run time found between downtimes.
                                    tl_stop = datetime.strptime(downtimes[i]["start_time"], constants.time_format)
                                    tl_delta = (tl_stop - tl_start).seconds
                                    tl_stop_value = tl_delta + tl_start_value
                                    tl_instance = {"name": "RunTime",
                                                   "value": [seq, tl_start_value, tl_stop_value, tl_delta],
                                                   "itemStyle": {"normal": {"color": "green"}}}

                                    timeline_data.append(tl_instance)

                                    # re-assign tl_start_value and tl_start to previous stop.
                                    tl_start_value = tl_stop_value
                                    tl_start = tl_stop
                                    # tl_instance for runtime between downtimes.

                                # tl_instance for second downtime onwards.
                                # --------------------------------------------------------------------------------------
                                # downtime stops within shift
                                tl_stop = datetime.strptime(downtimes[i]["stop_time"], constants.time_format)
                                tl_delta = (tl_stop - tl_start).seconds
                                tl_stop_value = tl_delta + tl_start_value

                                tl_instance = {"name": downtime_reason,
                                               "value": [seq, tl_start_value, tl_stop_value, tl_delta],
                                               "itemStyle": {"normal": {"color": "#8B0000"}}}

                                timeline_data.append(tl_instance)
                                # re-assign tl_start_value and tl_start to previous stop.
                                tl_start_value = tl_stop_value
                                tl_start = tl_stop

                            else:
                                # downtime exceeds shift time. -- exit --
                                tl_stop = po_stop
                                tl_delta = (tl_stop - tl_start).seconds
                                tl_stop_value = tl_delta + tl_start_value

                                tl_instance = {"name": downtime_reason,
                                               "value": [seq, tl_start_value, tl_stop_value, tl_delta],
                                               "itemStyle": {"normal": {"color": "#8B0000"}}}

                                timeline_data.append(tl_instance)
                                # re-assign tl_start_value and tl_start to previous stop.
                                tl_start_value = tl_stop_value
                                tl_start = tl_stop

                        else:  # downtime out of shift boundaries.
                            tl_stop = po_stop
                            tl_delta = (tl_stop - tl_start).seconds
                            tl_stop_value = tl_delta + tl_start_value

                            tl_instance = {"name": downtime_reason,
                                           "value": [seq, tl_start_value, tl_stop_value, tl_delta],
                                           "itemStyle": {"normal": {"color": "#8B0000"}}}

                            timeline_data.append(tl_instance)
                            # re-assign tl_start_value and tl_start to previous stop.
                            tl_start_value = tl_stop_value
                            tl_start = tl_stop
                else:
                    # print("NO DOWNTIMES FOUND")
                    tl_stop = po_stop
                    tl_delta = (tl_stop - tl_start).seconds
                    tl_stop_value = tl_delta + tl_start_value

                    tl_instance = {"name": "Runtime", "value": [seq, tl_start_value, tl_stop_value, tl_delta],
                                   "itemStyle": {"normal": {"color": "green"}}}

                    timeline_data.append(tl_instance)
                    # re-assign tl_start_value and tl_start to previous stop.
                    tl_start_value = tl_stop_value
                    tl_start = tl_stop

                if downtime_flag == 1:
                    # check for remaining running times after all downtimes
                    tl_stop = po_stop
                    tl_delta = (tl_stop - tl_start).seconds
                    tl_stop_value = tl_delta + tl_start_value

                    tl_instance = {"name": "Runtime", "value": [seq, tl_start_value, tl_stop_value, tl_delta],
                                   "itemStyle": {"normal": {"color": "green"}}}

                    timeline_data.append(tl_instance)
                    # re-assign tl_start_value and tl_start to previous stop.
                    tl_start_value = tl_stop_value
                    tl_start = tl_stop

            else:  # No Downtimes - Calculate total runtime for po.
                # print("NO DOWNTIMES FOUND")
                tl_stop = po_stop
                tl_delta = (tl_stop - tl_start).seconds
                tl_stop_value = tl_delta + tl_start_value

                tl_instance = {"name": "Runtime", "value": [seq, tl_start_value, tl_stop_value, tl_delta],
                               "itemStyle": {"normal": {"color": "green"}}}

                timeline_data.append(tl_instance)
                # re-assign tl_start_value and tl_start to previous stop.
                tl_start_value = tl_stop_value
                tl_start = tl_stop

            # After checking downtimes
            # If no downtimes : Check
            # If downtimes : Check for the running time after downtime.
            po_counter = 1

        else:
            # print("second po exists")
            # SECOND PO | CONSIDER PREVIOUS TL_STOP AND CHECK IF IDLE TIME EXISTS

            po_start, po_stop = get_times_for_order_in_shift(po, shift_to_send)
            # print("------------------------------------")
            # print(po_start)
            # print(po_stop)
            # print((po_stop - po_start).seconds)
            # print("------------------------------------")

            tl_start = tl_stop  # using previous tl_stop for continuation.
            tl_stop = po_stop
            downtime_flag = 0
            # NOT initiating start stop values | Carry from previous PO
            '''tl_start_value = 0
            tl_stop_value = 0
            tl_delta = 0'''
            # ==========================================================================================
            # Check if Idle time exists. tl_start used in condition below is previous tl_stop
            # Check difference between po start and previous tl_stop

            if (po_start - tl_start).seconds != 0:
                print("FOUND IDLE TIME BETWEEN POS")  # This condition will always arise
                # tl_instance for idle time
                # --------------------------------------------------------------------------------------

                tl_stop = po_start
                tl_delta = (tl_stop - tl_start).seconds
                tl_stop_value = tl_delta + tl_start_value

                tl_instance = {"name": "Idle", "value": [seq, tl_start_value, tl_stop_value, tl_delta],
                               "itemStyle": {"normal": {"color": "#888888"}}}

                timeline_data.append(tl_instance)
                # re-assign tl_start_value and tl_start to previous stop.
                tl_start_value = tl_stop_value
                tl_start = tl_stop

            # ==========================================================================================

            if "DOWNTIME" in po:

                downtimes1 = get_downtime_overlaps(po)
                downtimes = get_downtimes_within_shift(downtimes1, shift_to_send)
                # pprint(downtimes)
                # Correct downtimes.
                if len(downtimes) > 0:

                    downtime_flag = 1
                    for i in range(0, len(downtimes)):
                        try:
                            downtime_reason = downtimes[i]["reasonlist"]
                        except:
                            downtime_reason = "Downtime"
                        # print("i am in loop 1")

                        if po_start < datetime.strptime(downtimes[i]["start_time"], constants.time_format):
                            # print("i entered loop 2")

                            if i == 0:
                                # print("i entered loop 3")
                                # tl_instance from order start to first downtime.
                                # --------------------------------------------------------------------------------------------------
                                tl_stop = datetime.strptime(downtimes[i]["start_time"], constants.time_format)
                                tl_delta = (tl_stop - tl_start).seconds
                                tl_stop_value = tl_delta + tl_start_value

                                tl_instance = {"name": "RunTime",
                                               "value": [seq, tl_start_value, tl_stop_value, tl_delta],
                                               "itemStyle": {"normal": {"color": "green"}}}

                                timeline_data.append(tl_instance)

                                # re-assign tl_start_value and tl_start to previous stop.
                                tl_start_value = tl_stop_value
                                tl_start = tl_stop

                                # tl_instance for first downtime.
                                # ---------------------------------------------------------------------------------------
                                if po_stop > datetime.strptime(downtimes[i]["stop_time"], constants.time_format):

                                    # downtime stops within shift
                                    tl_stop = datetime.strptime(downtimes[i]["stop_time"], constants.time_format)
                                    tl_delta = (tl_stop - tl_start).seconds
                                    tl_stop_value = tl_delta + tl_start_value

                                    tl_instance = {"name": downtime_reason,
                                                   "value": [seq, tl_start_value, tl_stop_value, tl_delta],
                                                   "itemStyle": {"normal": {"color": "#8B0000"}}}

                                    timeline_data.append(tl_instance)
                                    # re-assign tl_start_value and tl_start to previous stop.
                                    tl_start_value = tl_stop_value
                                    tl_start = tl_stop
                                else:
                                    # downtime exceeds shift time. -- exit --
                                    tl_stop = po_stop
                                    tl_delta = (tl_stop - tl_start).seconds
                                    tl_stop_value = tl_delta + tl_start_value

                                    tl_instance = {"name": downtime_reason,
                                                   "value": [seq, tl_start_value, tl_stop_value, tl_delta],
                                                   "itemStyle": {"normal": {"color": "#8B0000"}}}

                                    timeline_data.append(tl_instance)
                                    # re-assign tl_start_value and tl_start to previous stop.
                                    tl_start_value = tl_stop_value
                                    tl_start = tl_stop

                            elif po_stop > datetime.strptime(downtimes[i]["stop_time"], constants.time_format):
                                # more than one downtime.

                                # Check for Runtime between two downtimes and append if any.
                                if (datetime.strptime(downtimes[i]["start_time"],
                                                      constants.time_format) - tl_stop).seconds != 0:
                                    # Run time found between downtimes.
                                    tl_stop = datetime.strptime(downtimes[i]["start_time"], constants.time_format)
                                    tl_delta = (tl_stop - tl_start).seconds
                                    tl_stop_value = tl_delta + tl_start_value
                                    tl_instance = {"name": "RunTime",
                                                   "value": [seq, tl_start_value, tl_stop_value, tl_delta],
                                                   "itemStyle": {"normal": {"color": "green"}}}

                                    timeline_data.append(tl_instance)

                                    # re-assign tl_start_value and tl_start to previous stop.
                                    tl_start_value = tl_stop_value
                                    tl_start = tl_stop
                                    # tl_instance for runtime between downtimes.

                                # tl_instance for second downtime onwards.
                                # --------------------------------------------------------------------------------------
                                # downtime stops within shift
                                tl_stop = datetime.strptime(downtimes[i]["stop_time"], constants.time_format)
                                tl_delta = (tl_stop - tl_start).seconds
                                tl_stop_value = tl_delta + tl_start_value

                                tl_instance = {"name": downtime_reason,
                                               "value": [seq, tl_start_value, tl_stop_value, tl_delta],
                                               "itemStyle": {"normal": {"color": "#8B0000"}}}

                                timeline_data.append(tl_instance)
                                # re-assign tl_start_value and tl_start to previous stop.
                                tl_start_value = tl_stop_value
                                tl_start = tl_stop
                            else:
                                # downtime exceeds shift time. -- exit --
                                tl_stop = po_stop
                                tl_delta = (tl_stop - tl_start).seconds
                                tl_stop_value = tl_delta + tl_start_value

                                tl_instance = {"name": downtime_reason,
                                               "value": [seq, tl_start_value, tl_stop_value, tl_delta],
                                               "itemStyle": {"normal": {"color": "#8B0000"}}}

                                timeline_data.append(tl_instance)
                                # re-assign tl_start_value and tl_start to previous stop.
                                tl_start_value = tl_stop_value
                                tl_start = tl_stop

                        else:  # downtime out of shift boundaries.
                            tl_stop = po_stop
                            tl_delta = (tl_stop - tl_start).seconds
                            tl_stop_value = tl_delta + tl_start_value

                            tl_instance = {"name": downtime_reason,
                                           "value": [seq, tl_start_value, tl_stop_value, tl_delta],
                                           "itemStyle": {"normal": {"color": "#8B0000"}}}

                            timeline_data.append(tl_instance)
                            # re-assign tl_start_value and tl_start to previous stop.
                            tl_start_value = tl_stop_value
                            tl_start = tl_stop
                else:
                    # No Downtimes
                    tl_stop = po_stop
                    tl_delta = (tl_stop - tl_start).seconds
                    tl_stop_value = tl_delta + tl_start_value

                    tl_instance = {"name": "Runtime", "value": [seq, tl_start_value, tl_stop_value, tl_delta],
                                   "itemStyle": {"normal": {"color": "green"}}}

                    timeline_data.append(tl_instance)
                    # re-assign tl_start_value and tl_start to previous stop.
                    tl_start_value = tl_stop_value
                    tl_start = tl_stop

                if downtime_flag == 1:
                    tl_stop = po_stop
                    tl_delta = (tl_stop - tl_start).seconds
                    tl_stop_value = tl_delta + tl_start_value

                    tl_instance = {"name": "Runtime", "value": [seq, tl_start_value, tl_stop_value, tl_delta],
                                   "itemStyle": {"normal": {"color": "green"}}}

                    timeline_data.append(tl_instance)
                    # re-assign tl_start_value and tl_start to previous stop.
                    tl_start_value = tl_stop_value
                    tl_start = tl_stop

            else:  # No Downtimes - Calculate total runtime for po.
                tl_stop = po_stop
                tl_delta = (tl_stop - tl_start).seconds
                tl_stop_value = tl_delta + tl_start_value

                tl_instance = {"name": "Runtime", "value": [seq, tl_start_value, tl_stop_value, tl_delta],
                               "itemStyle": {"normal": {"color": "green"}}}

                timeline_data.append(tl_instance)
                # re-assign tl_start_value and tl_start to previous stop.
                tl_start_value = tl_stop_value
                tl_start = tl_stop

    x_axis_labels = []
    # generate x axis labels:
    # pprint(timeline_data)
    return timeline_data


# get_timelines_for_all_machines('29/01/2021', "B")

def send_spr_mails(date, shift, shift_data):
    # Generating machine links
    machine_list = ['JSW 350T', "JSW 650T", "JSW 550T-II", "JSW 450T-II", "JSW 550T-I", "JSW 450T-III", "JSW 450T"]

    # Get user info

    query = {"role": {"$in": constants.spr_roles}}

    users = user_collection.find(query, {'_id': False})
    recipients = []
    for user in users:
        if "email_id" in user:
            if user["email_id"] != "":
                recipients.append(user["email_id"])

    spr_mail_header = """ \
    	<head>
    		<title>
    		</title>
    		<!-- Latest compiled and minified CSS -->
    		<style>
    #mytable {
      font-family: Arial, Helvetica, sans-serif;
      border-collapse: collapse;
      width: 100%;
    }
    #mytable td, #mytable th {
      border: 1px solid #ddd;
      padding: 8px;
    }
    #mytable tr:nth-child(even){background-color: #f2f2f2;}
    #mytable tr:hover {background-color: #ddd;}
    #mytable th {
      padding-top: 12px;
      padding-bottom: 12px;
      text-align: left;
      background-color: #69051e;
      color: white;
    }
    .button {
      background-color: #69051e; 
      border: none;
      color: white;
      padding: 10px;
      text-align: center;
      text-decoration: none;
      display: inline-block;
      font-size: 12px;
      margin: 1px 1px;
      cursor: pointer;
      border-radius: 3px;
    }
    </style>
    </head>
    <body>
    <center>
    <div><img src="http://cyrocal.xyz/cyronics_iot_logo.png" style="height:40px"></div>

    """

    shift_date_heading = '</h3></div><center><div><br><h3 style="text-align:center;"> Shift Performance Report(SPR) for ' + date + '(SHIFT - ' + shift + ')</h3><br></div></center><center><div><h3>'

    table_header = '</h3></div><div class="container" style="width:300px" ><table id="mytable"><tr><th > MACHINE </th><th > REPORT </th></tr>'

    all_tr = ""

    spr_mail_footer = '</table></div></center></body>'

    all_oee = []

    if "kpi" in shift_data:
        print("found1")
        for i in range(0, len(shift_data["kpi"])):
            all_oee.append(shift_data["kpi"][i]["Oee"])

        average_oee = sum(all_oee) / len(all_oee)
        oee_message = "Plant Overall Efficiency during the shift was " + str(round(average_oee, 2)) + "%."
    else:
        print("No KPI data available")
        oee_message = "Plant Overall Efficiency during the shift was ---%."

    temp = ["vardan@ppapco.com"]
    for machine in machine_list:
        machine1 = machine.replace(" ", "%20")
        path = constants.oee_api_endpoint + "/SPR_view/" + date + "/" + shift + "/" + machine1

        part_1 = '<tr><td>' + machine
        part_2 = '</td><td><a href="' + path + '"><button type="button" '
        part_3 = ""
        part_4 = 'class="button">VIEW</button></a></td></tr>'

        tr_element = part_1 + part_2 + part_3 + part_4

        all_tr += tr_element

        print(path)
    final_html = spr_mail_header + shift_date_heading + oee_message + table_header + all_tr + spr_mail_footer
    mail_api.send_mail_via_smtp(constants.temporary_mail_list, "CYRONICS SOFTWARE - SPR", final_html)
    mail_api.send_mail(constants.temporary_mail_list, "CYRONICS SOFTWARE - SPR", final_html)

    # mail_api.send_mail_via_smtp(temp, "CYRONICS SOFTWARE - SPR",final_html)
    # print(final_html)
    print("SPR MAILS SENT!")


# send_spr_mails("31-01-2021","B")

def send_pqcr_mails(date):
    print(date)
    print("TRYING TO GENERATE PQCR MAIL DATA")
    # Generating machine links
    machine_list = ['JSW 350T', "JSW 650T", "JSW 550T-II", "JSW 450T-II", "JSW 550T-I", "JSW 450T-III", "JSW 450T"]

    # Get user info
    query = {"role": {"$in": constants.pqcr_roles}}

    users = user_collection.find(query, {'_id': False})
    recipients = []
    for user in users:
        if "email_id" in user:
            if user["email_id"] != "":
                recipients.append(user["email_id"])

    spr_mail_header = """ \
    	<head>
    		<title>
    		</title>
    		<!-- Latest compiled and minified CSS -->
    		<style>
    #mytable {
      font-family: Arial, Helvetica, sans-serif;
      border-collapse: collapse;
      width: 100%;
    }
    #mytable td, #mytable th {
      border: 1px solid #ddd;
      padding: 8px;
    }
    #mytable tr:nth-child(even){background-color: #f2f2f2;}
    #mytable tr:hover {background-color: #ddd;}
    #mytable th {
      padding-top: 12px;
      padding-bottom: 12px;
      text-align: left;
      background-color: #69051e;
      color: white;
    }
    .button {
      background-color: #69051e; 
      border: none;
      color: white;
      padding: 10px;
      text-align: center;
      text-decoration: none;
      display: inline-block;
      font-size: 12px;
      margin: 1px 1px;
      cursor: pointer;
      border-radius: 3px;
    }
    </style>
    </head>
    <body>
    <center>
    <div><img src="http://cyrocal.xyz/cyronics_iot_logo.png" style="height:40px"></div>
    """

    shift_date_heading = '<center></div><br><h3 style="text-align:center;"> Process Quality Control Report(PQCR) for ' + date + '</h3><br></center>'

    table_header = '<center><div class="container" style="width:300px" ><table id="mytable"><tr><th > MACHINE </th><th > REPORT </th></tr>'

    all_tr = ""

    spr_mail_footer = '</table></div></center></body>'

    for machine in machine_list:
        machine1 = machine.replace(" ", "%20")
        path = constants.cbm_api_endpoint + "/PQCR_view/" + date + "/" + machine1
        print(path)
        part_1 = '<tr><td>' + machine
        part_2 = '</td><td><a href="' + path + '"><button type="button" '
        part_3 = ""
        part_4 = 'class="button">VIEW</button></a></td></tr>'

        tr_element = part_1 + part_2 + part_3 + part_4

        all_tr += tr_element

    final_html = spr_mail_header + shift_date_heading + table_header + all_tr + spr_mail_footer
    # print(recipients)
    mail_api.send_mail(constants.temporary_mail_list, "CYRONICS SOFTWARE - PQCR", final_html)
    # print(final_html)
    print("PQCR MAILS SENT")


def send_oee_via_sms(shift):
    # fetching users
    print("------------------------------------------- Sending messages now! --------------------------------------")

    # time.sleep(5)
    query = {"role": {"$in": constants.spr_roles}}
    users = user_collection.find(query, {'_id': False})
    recipients = []
    for user in users:
        if "phone" in user:
            recipients.append(user["phone"])

    recipients.append("7066822892")  # test
    print(recipients)

    all_oee = []
    current_date = datetime.strftime(shift["SHIFT START TIME"], "%d-%m-%Y")
    if "kpi" in shift:
        print("############################### KPI FOUND#####################################")
        for i in range(0, len(shift["kpi"])):
            all_oee.append(shift["kpi"][i]["Oee"])

        average_oee = sum(all_oee) / len(all_oee)
        message = "Plant Overall Efficiency for " + current_date + " - SHIFT(" + shift["SHIFT ID"] + ") was " + str(
            round(average_oee, 2)) + "%."
        print(message)
        for i in range(0, len(recipients)):
            templist = []
            templist.append(recipients[i])
            otp_operations.send_custom_message(str(message), templist)

    else:
        print("NO KPI DATA AVAILABLE.")
    # print("---------------------------- MESSAGES WERE SENT --------------------------------------------------------------")


def tester():
    current_shift = shift_records.find_one({"STATUS": "Live"}, {'_id': False})
    spr_date = datetime.strftime(current_shift["SHIFT START TIME"], "%d-%m-%Y")
    spr_shift_id = current_shift["SHIFT ID"]
    send_spr_mails(spr_date, spr_shift_id, current_shift)



