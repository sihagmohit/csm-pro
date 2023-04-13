import shutil

import pymongo
import copy
from datetime import datetime, timedelta

import requests

import constants
from pprint import pprint
from statistics import mean

import database_operations
import mail_api
import time
import otp_operations
import os

from bson.objectid import ObjectId

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["TWIN"]
active_orders = mydb["active_orders"]
design_activity_info = mydb["design_activity_info"]
production_activity_info = mydb["production_activity_info"]
purchase_activity_info = mydb["purchase_activity_info"]
testing_activity_info = mydb["testing_activity_info"]
dispatch_activity_info = mydb["dispatch_activity_info"]
customers = mydb["customers"]

# activities = mydb["activities"]
profile = mydb["profile"]
activity_presets = mydb['activity_presets']
'''=================================Active Orders========================================'''


def insert_order(order):
    rpo = order["RPO"]
    count = active_orders.find({"RPO": rpo}).count()
    if count == 0:
        active_orders.insert_one(order)

        generate_production_activities(order)
        generate_design_activities(order)
        generate_dispatch_activities(order)
        generate_purchase_activities(order)
        generate_testing_activities(order)

        return 0
    else:
        return 1



def query_active_projects():
    myquery = {"Project Status" : {"$nin":["CLOSED"]}}
    mydoc = active_orders.find(myquery)
    all_x = []
    for x in mydoc:
        x["_id"] = str(x["_id"])
        try:
            x["Delivery Date"] = str(x["Delivery Date"].strftime(constants.only_date))
            x["project_deadline"] = str(x["project_deadline"].strftime(constants.only_date))
            x["design_deadline"] = str(x["design_deadline"].strftime(constants.only_date))
            x["dispatch_deadline"] = str(x["dispatch_deadline"].strftime(constants.only_date))
            x["inventory_deadline"] = str(x["inventory_deadline"].strftime(constants.only_date))
            x["production_deadline"] = str(x["production_deadline"].strftime(constants.only_date))
            x["testing_deadline"] = str(x["testing_deadline"].strftime(constants.only_date))
        except:
            pass
        all_x.append(x)
    return all_x


def get_client_details(rpo):
    myquery = {'RPO': rpo}
    x1 = active_orders.find_one(myquery, {'_id': False})
    try:
        x1["closed_on"] = x1["closed_on"].strftime(constants.time_format)
    except:
        pass
    return x1

def get_specific_rpo(rpo_id):

    rpo = active_orders.find_one({'_id': ObjectId(rpo_id)})
    rpo["_id"] = str(rpo["_id"])

    return rpo

def edit_rpo_details(data):

    rpo_id = ObjectId(data["_id"])
    del data["_id"]
    updated_data = {"$set": data}
    active_orders.update_one({'_id': rpo_id}, updated_data)
    calculate_total_rpo_status(data["RPO"])

def delete_rpo(data):

    rpo = active_orders.find_one({'_id': ObjectId(data["_id"])})
    active_orders.delete_one({'_id': ObjectId(data["_id"])})
    production_activity_info.delete_many({"RPO": data["RPO"]})
    design_activity_info.delete_many({"RPO": data["RPO"]})
    testing_activity_info.delete_many({"RPO": data["RPO"]})
    purchase_activity_info.delete_many({"RPO": data["RPO"]})
    dispatch_activity_info.delete_many({"RPO": data["RPO"]})



    file_path = "rpo_images/" + rpo["RPO"]
    reports_path = "twin_reports/" + rpo["RPO"]
    try:
        shutil.rmtree(file_path)
    except:
        print("---------------------------------No images to delete.----------------------------------")
    try:
        shutil.rmtree(reports_path)
    except:
        print("---------------------------------No reports to delete.----------------------------------")
    print("RPO REMOVED - DATA CLEANED!")

'''==============================Design Activity================================'''


def insert_design_activity(activity):

    exists = design_activity_info.find({"RPO":activity["RPO"],"Activity No":activity["Activity No"]}).count()

    if exists == 0 :

        design_activity_info.insert_one(activity)
        rpo = activity["RPO"]
        update_design_weightage_percent(rpo)

        myquery = {"RPO": rpo}
        mydoc = design_activity_info.find(myquery)

        weightage_total_list = []
        for x in mydoc:
            status = x["Status"]
            if status == "Done":
                weightage_percent = x["Weightage %"]
                weightage_total_list.append(weightage_percent)

        if weightage_total_list:
            design_status_list = []
            for x in weightage_total_list:
                weightage_percent_str = x.replace("%", "")
                weightage_percent_float = float(weightage_percent_str)
                design_status_list.append(weightage_percent_float)
            design_status_percent = sum(design_status_list)
            design_status_percent_str = str(design_status_percent) # + "%"
            myquery2 = {"RPO": rpo}
            updated_data = {"$set": {"Design Status %": design_status_percent_str}}
            active_orders.update_one(myquery2, updated_data)

        calculate_total_rpo_status(rpo)

        return 1
    else:
        return 0


def query_design_activity_info(rpo):
    myquery = {"RPO": rpo}
    mydoc = design_activity_info.find(myquery, {'_id': False})
    all_x = []
    for x in mydoc:
        all_x.append(x)
    return all_x


def get_specific_design_activity_data(activity_no, rpo):
    myquery = {'RPO': rpo, 'Activity No': activity_no}
    x1 = design_activity_info.find_one(myquery, {'_id': False})
    return x1


def update_specific_design_activity_data(data):
    rpo = data["RPO"]
    activity_no = data["Activity No"]
    data["last_updated"] = datetime.now().strftime(constants.time_format)
    myquery = {'RPO': rpo, 'Activity No': activity_no}
    updated_data = {"$set": data}
    design_activity_info.update_one(myquery, updated_data)
    update_design_weightage_percent(rpo)

    myquery = {"RPO": rpo}
    mydoc = design_activity_info.find(myquery)

    weightage_total_list = []
    for x in mydoc:
        status = x["Status"]
        if status == "Done":
            weightage_percent = x["Weightage %"]
            weightage_total_list.append(weightage_percent)

    if weightage_total_list:
        design_status_list = []
        for x in weightage_total_list:
            weightage_percent_str = x.replace("%", "")
            weightage_percent_float = float(weightage_percent_str)
            design_status_list.append(weightage_percent_float)
        design_status_percent = sum(design_status_list)
        design_status_percent_str = str(design_status_percent) + "%"
        myquery2 = {"RPO": rpo}
        updated_data = {"$set": {"Design Status %": design_status_percent_str}}
        active_orders.update_one(myquery2, updated_data)
    else:
        design_status_percent_str = str(0) + "%"
        myquery3 = {"RPO": rpo}
        updated_data = {"$set": {"Design Status %": design_status_percent_str}}
        active_orders.update_one(myquery3, updated_data)

    calculate_total_rpo_status(rpo)


def delete_specific_design_activity_data(rpo, activity_no):
    myquery = {'RPO': rpo, 'Activity No': activity_no}
    design_activity_info.delete_one(myquery)
    update_design_weightage_percent(rpo)

    myquery = {"RPO": rpo}
    mydoc = design_activity_info.find(myquery)

    count = mydoc.count()
    if count == 0:
        design_status_percent_str = str(0) + "%"
        myquery3 = {"RPO": rpo}
        updated_data = {"$set": {"Design Status %": design_status_percent_str}}
        active_orders.update_one(myquery3, updated_data)
    else:
        weightage_total_list = []
        for x in mydoc:
            status = x["Status"]
            if status == "Done":
                weightage_percent = x["Weightage %"]
                weightage_total_list.append(weightage_percent)

        if weightage_total_list:
            design_status_list = []
            for x in weightage_total_list:
                weightage_percent_str = x.replace("%", "")
                weightage_percent_float = float(weightage_percent_str)
                design_status_list.append(weightage_percent_float)
            design_status_percent = sum(design_status_list)
            design_status_percent_str = str(design_status_percent) + "%"
            myquery2 = {"RPO": rpo}
            updated_data = {"$set": {"Design Status %": design_status_percent_str}}
            active_orders.update_one(myquery2, updated_data)
        else:
            design_status_percent_str = str(0) + "%"
            myquery3 = {"RPO": rpo}
            updated_data = {"$set": {"Design Status %": design_status_percent_str}}
            active_orders.update_one(myquery3, updated_data)

    calculate_total_rpo_status(rpo)


def update_design_weightage_percent(rpo):
    myquery1 = {'RPO': rpo}
    mydoc1 = design_activity_info.find(myquery1)
    total = []
    for x1 in mydoc1:
        time_taken = x1["Time Taken (Days)"]
        time_taken = float(time_taken)
        total.append(time_taken)

    sum_time_taken = sum(total)

    myquery2 = {'RPO': rpo}
    mydoc2 = design_activity_info.find(myquery2)

    for x2 in mydoc2:
        time_taken1 = x2["Time Taken (Days)"]
        activity_no = x2["Activity No"]

        myquery3 = {'RPO': rpo, 'Activity No': activity_no}

        time_taken1 = float(time_taken1)
        weightage_percent = (time_taken1 / sum_time_taken) * 100
        weightage_percent2 = str(weightage_percent) + "%"

        new_field = {"$set": {"Weightage %": weightage_percent2}}
        design_activity_info.update_one(myquery3, new_field)


'''==============================Production Activity================================'''


def insert_production_activity(activity):

    exists = production_activity_info.find({'RPO':activity['RPO'], "Activity No":activity["Activity No"]}).count()

    if exists == 0:

        production_activity_info.insert_one(activity)
        rpo = activity["RPO"]
        update_production_weightage_percent(rpo)

        myquery = {"RPO": rpo}
        mydoc = production_activity_info.find(myquery)
        weightage_total_list = []
        for x in mydoc:
            status = x["Status"]
            if status == "Done":
                weightage_percent = x["Weightage %"]
                weightage_total_list.append(weightage_percent)

        if weightage_total_list:
            production_status_list = []
            for x in weightage_total_list:
                weightage_percent_str = x.replace("%", "")
                weightage_percent_float = float(weightage_percent_str)
                production_status_list.append(weightage_percent_float)
            production_status_percent = sum(production_status_list)
            production_status_percent_str = str(production_status_percent) + "%"
            myquery2 = {"RPO": rpo}
            updated_data = {"$set": {"Production Status %": production_status_percent_str}}
            active_orders.update_one(myquery2, updated_data)

        calculate_total_rpo_status(rpo)
        return 1

    else:
        return 0


def query_production_activity_info(rpo):
    myquery = {"RPO": rpo}
    mydoc = production_activity_info.find(myquery, {'_id': False})
    all_x = []
    for x in mydoc:
        all_x.append(x)
    return all_x


def get_specific_production_activity_data(activity_no, rpo):
    myquery = {'RPO': rpo, 'Activity No': activity_no}
    x1 = production_activity_info.find_one(myquery, {'_id': False})
    print("specific prod activty")
    print(x1)
    return x1


def update_specific_production_activity_data(data):
    rpo = data["RPO"]
    activity_no = data["Activity No"]
    data["last_updated"] = datetime.now().strftime(constants.time_format)
    myquery = {'RPO': rpo, 'Activity No': activity_no}
    updated_data = {"$set": data}
    production_activity_info.update_one(myquery, updated_data)
    update_production_weightage_percent(rpo)

    myquery = {"RPO": rpo}
    mydoc = production_activity_info.find(myquery)

    weightage_total_list = []
    for x in mydoc:
        status = x["Status"]
        if status == "Done":
            weightage_percent = x["Weightage %"]
            weightage_total_list.append(weightage_percent)

    if weightage_total_list:
        production_status_list = []
        for x in weightage_total_list:
            weightage_percent_str = x.replace("%", "")
            weightage_percent_float = float(weightage_percent_str)
            production_status_list.append(weightage_percent_float)
        production_status_percent = sum(production_status_list)
        production_status_percent_str = str(production_status_percent) + "%"
        myquery2 = {"RPO": rpo}
        updated_data = {"$set": {"Production Status %": production_status_percent_str}}
        active_orders.update_one(myquery2, updated_data)
    else:
        production_status_percent_str = str(0) + "%"
        myquery3 = {"RPO": rpo}
        updated_data = {"$set": {"Production Status %": production_status_percent_str}}
        active_orders.update_one(myquery3, updated_data)

    calculate_total_rpo_status(rpo)


def delete_specific_production_activity_data(rpo, activity_no):
    myquery = {'RPO': rpo, 'Activity No': activity_no}
    production_activity_info.delete_one(myquery)
    update_production_weightage_percent(rpo)

    myquery = {"RPO": rpo}
    mydoc = production_activity_info.find(myquery)

    count = mydoc.count()
    if count == 0:
        production_status_percent_str = str(0) + "%"
        myquery3 = {"RPO": rpo}
        updated_data = {"$set": {"Production Status %": production_status_percent_str}}
        active_orders.update_one(myquery3, updated_data)
    else:
        weightage_total_list = []
        for x in mydoc:
            status = x["Status"]
            if status == "Done":
                weightage_percent = x["Weightage %"]
                weightage_total_list.append(weightage_percent)

        if weightage_total_list:
            production_status_list = []
            for x in weightage_total_list:
                weightage_percent_str = x.replace("%", "")
                weightage_percent_float = float(weightage_percent_str)
                production_status_list.append(weightage_percent_float)
            production_status_percent = sum(production_status_list)
            production_status_percent_str = str(production_status_percent) + "%"
            myquery2 = {"RPO": rpo}
            updated_data = {"$set": {"Production Status %": production_status_percent_str}}
            active_orders.update_one(myquery2, updated_data)
        else:
            production_status_percent_str = str(0) + "%"
            myquery3 = {"RPO": rpo}
            updated_data = {"$set": {"Production Status %": production_status_percent_str}}
            active_orders.update_one(myquery3, updated_data)

    calculate_total_rpo_status(rpo)


def update_production_weightage_percent(rpo):
    myquery1 = {'RPO': rpo}
    mydoc1 = production_activity_info.find(myquery1)
    total = []
    for x1 in mydoc1:
        time_taken = x1["Time Taken (Days)"]
        time_taken = float(time_taken)
        total.append(time_taken)

    sum_time_taken = sum(total)

    myquery2 = {'RPO': rpo}
    mydoc2 = production_activity_info.find(myquery2)

    for x2 in mydoc2:
        time_taken1 = x2["Time Taken (Days)"]
        activity_no = x2["Activity No"]

        myquery3 = {'RPO': rpo, 'Activity No': activity_no}

        time_taken1 = float(time_taken1)
        weightage_percent = (time_taken1 / sum_time_taken) * 100
        weightage_percent2 = str(weightage_percent) + "%"

        new_field = {"$set": {"Weightage %": weightage_percent2}}
        production_activity_info.update_one(myquery3, new_field)


'''==============================Purchase Activity================================'''


def insert_purchase_activity(activity):

    exists = purchase_activity_info.find({"RPO": activity["RPO"], "Activity No": activity["Activity No"]}).count()


    if exists == 0:
        purchase_activity_info.insert_one(activity)
        rpo = activity["RPO"]
        update_purchase_weightage_percent(rpo)

        myquery = {"RPO": rpo}
        mydoc = purchase_activity_info.find(myquery)

        weightage_total_list = []
        for x in mydoc:
            status = x["Status"]
            if status == "Done":
                weightage_percent = x["Weightage %"]
                weightage_total_list.append(weightage_percent)

        if weightage_total_list:
            purchase_status_list = []
            for x in weightage_total_list:
                weightage_percent_str = x.replace("%", "")
                weightage_percent_float = float(weightage_percent_str)
                purchase_status_list.append(weightage_percent_float)
            purchase_status_percent = sum(purchase_status_list)
            purchase_status_percent_str = str(purchase_status_percent) + "%"
            myquery2 = {"RPO": rpo}
            updated_data = {"$set": {"Purchase Status %": purchase_status_percent_str}}
            active_orders.update_one(myquery2, updated_data)

        calculate_total_rpo_status(rpo)
        return 1
    else:
        return 0


def query_purchase_activity_info(rpo):
    myquery = {"RPO": rpo}
    mydoc = purchase_activity_info.find(myquery, {'_id': False})
    all_x = []
    for x in mydoc:
        all_x.append(x)
    return all_x


def get_specific_purchase_activity_data(activity_no, rpo):
    myquery = {'RPO': rpo, 'Activity No': activity_no}
    x1 = purchase_activity_info.find_one(myquery, {'_id': False})
    return x1


def update_specific_purchase_activity_data(data):
    rpo = data["RPO"]
    activity_no = data["Activity No"]
    data["last_updated"] = datetime.now().strftime(constants.time_format)
    myquery = {'RPO': rpo, 'Activity No': activity_no}
    updated_data = {"$set": data}
    purchase_activity_info.update_one(myquery, updated_data)
    update_purchase_weightage_percent(rpo)

    myquery = {"RPO": rpo}
    mydoc = purchase_activity_info.find(myquery)

    weightage_total_list = []
    for x in mydoc:
        status = x["Status"]
        if status == "Done":
            weightage_percent = x["Weightage %"]
            weightage_total_list.append(weightage_percent)

    if weightage_total_list:
        purchase_status_list = []
        for x in weightage_total_list:
            weightage_percent_str = x.replace("%", "")
            weightage_percent_float = float(weightage_percent_str)
            purchase_status_list.append(weightage_percent_float)
        purchase_status_percent = sum(purchase_status_list)
        purchase_status_percent_str = str(purchase_status_percent) + "%"
        myquery2 = {"RPO": rpo}
        updated_data = {"$set": {"Purchase Status %": purchase_status_percent_str}}
        active_orders.update_one(myquery2, updated_data)
    else:
        purchase_status_percent_str = str(0) + "%"
        myquery3 = {"RPO": rpo}
        updated_data = {"$set": {"Purchase Status %": purchase_status_percent_str}}
        active_orders.update_one(myquery3, updated_data)

    calculate_total_rpo_status(rpo)


def delete_specific_purchase_activity_data(rpo, activity_no):
    myquery = {'RPO': rpo, 'Activity No': activity_no}
    purchase_activity_info.delete_one(myquery)
    update_purchase_weightage_percent(rpo)

    myquery = {"RPO": rpo}
    mydoc = purchase_activity_info.find(myquery)

    count = mydoc.count()
    if count == 0:
        purchase_status_percent_str = str(0) + "%"
        myquery3 = {"RPO": rpo}
        updated_data = {"$set": {"Purchase Status %": purchase_status_percent_str}}
        active_orders.update_one(myquery3, updated_data)
    else:
        weightage_total_list = []
        for x in mydoc:
            status = x["Status"]
            if status == "Done":
                weightage_percent = x["Weightage %"]
                weightage_total_list.append(weightage_percent)

        if weightage_total_list:
            purchase_status_list = []
            for x in weightage_total_list:
                weightage_percent_str = x.replace("%", "")
                weightage_percent_float = float(weightage_percent_str)
                purchase_status_list.append(weightage_percent_float)
            purchase_status_percent = sum(purchase_status_list)
            purchase_status_percent_str = str(purchase_status_percent) + "%"
            myquery2 = {"RPO": rpo}
            updated_data = {"$set": {"Purchase Status %": purchase_status_percent_str}}
            active_orders.update_one(myquery2, updated_data)
        else:
            purchase_status_percent_str = str(0) + "%"
            myquery3 = {"RPO": rpo}
            updated_data = {"$set": {"Purchase Status %": purchase_status_percent_str}}
            active_orders.update_one(myquery3, updated_data)

    calculate_total_rpo_status(rpo)


def update_purchase_weightage_percent(rpo):
    try:
        myquery1 = {'RPO': rpo}
        mydoc1 = purchase_activity_info.find(myquery1)
        total = []
        for x1 in mydoc1:
            time_taken = x1["Time Taken (Days)"]
            time_taken = float(time_taken)
            total.append(time_taken)

        sum_time_taken = sum(total)

        myquery2 = {'RPO': rpo}
        mydoc2 = purchase_activity_info.find(myquery2)

        for x2 in mydoc2:
            time_taken1 = x2["Time Taken (Days)"]
            activity_no = x2["Activity No"]

            myquery3 = {'RPO': rpo, 'Activity No': activity_no}

            time_taken1 = float(time_taken1)
            weightage_percent = (time_taken1 / sum_time_taken) * 100
            weightage_percent2 = str(weightage_percent)

            new_field = {"$set": {"Weightage %": weightage_percent2}}
            purchase_activity_info.update_one(myquery3, new_field)
    except:
        print("--------------- Error Occurred while Updating Production Percentage ---------------")


'''=============================testing activity===================================='''



def insert_testing_activity(activity):

    exists = testing_activity_info.find({"RPO": activity["RPO"], "Activity No": activity["Activity No"]}).count()


    if exists == 0:
        testing_activity_info.insert_one(activity)
        rpo = activity["RPO"]
        update_testing_weightage_percent(rpo)

        myquery = {"RPO": rpo}
        mydoc = testing_activity_info.find(myquery)

        weightage_total_list = []
        for x in mydoc:
            status = x["Status"]
            if status == "Done":
                weightage_percent = x["Weightage %"]
                weightage_total_list.append(weightage_percent)

        if weightage_total_list:
            testing_status_list = []
            for x in weightage_total_list:
                weightage_percent_str = x.replace("%", "")
                weightage_percent_float = float(weightage_percent_str)
                testing_status_list.append(weightage_percent_float)
            testing_status_percent = sum(testing_status_list)
            testing_status_percent_str = str(testing_status_percent) + "%"
            myquery2 = {"RPO": rpo}
            updated_data = {"$set": {"Testing Status %": testing_status_percent_str}}
            active_orders.update_one(myquery2, updated_data)

        calculate_total_rpo_status(rpo)
        return 1
    else:
        return 0


def query_testing_activity_info(rpo):
    myquery = {"RPO": rpo}
    mydoc = testing_activity_info.find(myquery, {'_id': False})
    all_x = []
    for x in mydoc:
        all_x.append(x)
    return all_x


def get_specific_testing_activity_data(activity_no, rpo):
    myquery = {'RPO': rpo, 'Activity No': activity_no}
    x1 = testing_activity_info.find_one(myquery, {'_id': False})
    return x1


def update_specific_testing_activity_data(data):
    rpo = data["RPO"]
    activity_no = data["Activity No"]
    data["last_updated"] = datetime.now().strftime(constants.time_format)
    myquery = {'RPO': rpo, 'Activity No': activity_no}
    updated_data = {"$set": data}
    testing_activity_info.update_one(myquery, updated_data)
    update_testing_weightage_percent(rpo)

    myquery = {"RPO": rpo}
    mydoc = testing_activity_info.find(myquery)

    weightage_total_list = []
    for x in mydoc:
        status = x["Status"]
        if status == "Done":
            weightage_percent = x["Weightage %"]
            weightage_total_list.append(weightage_percent)

    if weightage_total_list:
        testing_status_list = []
        for x in weightage_total_list:
            weightage_percent_str = x.replace("%", "")
            weightage_percent_float = float(weightage_percent_str)
            testing_status_list.append(weightage_percent_float)
        testing_status_percent = sum(testing_status_list)
        testing_status_percent_str = str(testing_status_percent) + "%"
        myquery2 = {"RPO": rpo}
        updated_data = {"$set": {"Testing Status %": testing_status_percent_str}}
        active_orders.update_one(myquery2, updated_data)
    else:
        testing_status_percent_str = str(0) + "%"
        myquery3 = {"RPO": rpo}
        updated_data = {"$set": {"Testing Status %": testing_status_percent_str}}
        active_orders.update_one(myquery3, updated_data)

    calculate_total_rpo_status(rpo)


def delete_specific_testing_activity_data(rpo, activity_no):
    myquery = {'RPO': rpo, 'Activity No': activity_no}
    testing_activity_info.delete_one(myquery)
    update_testing_weightage_percent(rpo)

    myquery = {"RPO": rpo}
    mydoc = testing_activity_info.find(myquery)

    count = mydoc.count()
    if count == 0:
        testing_status_percent_str = str(0) + "%"
        myquery3 = {"RPO": rpo}
        updated_data = {"$set": {"Testing Status %": testing_status_percent_str}}
        active_orders.update_one(myquery3, updated_data)
    else:
        weightage_total_list = []
        for x in mydoc:
            status = x["Status"]
            if status == "Done":
                weightage_percent = x["Weightage %"]
                weightage_total_list.append(weightage_percent)

        if weightage_total_list:
            testing_status_list = []
            for x in weightage_total_list:
                weightage_percent_str = x.replace("%", "")
                weightage_percent_float = float(weightage_percent_str)
                testing_status_list.append(weightage_percent_float)
            testing_status_percent = sum(testing_status_list)
            testing_status_percent_str = str(testing_status_percent) + "%"
            myquery2 = {"RPO": rpo}
            updated_data = {"$set": {"Testing Status %": testing_status_percent_str}}
            active_orders.update_one(myquery2, updated_data)
        else:
            testing_status_percent_str = str(0) + "%"
            myquery3 = {"RPO": rpo}
            updated_data = {"$set": {"Testing Status %": testing_status_percent_str}}
            active_orders.update_one(myquery3, updated_data)

    calculate_total_rpo_status(rpo)


def update_testing_weightage_percent(rpo):
    try:
        myquery1 = {'RPO': rpo}
        mydoc1 = testing_activity_info.find(myquery1)
        total = []
        for x1 in mydoc1:
            time_taken = x1["Time Taken (Days)"]
            time_taken = float(time_taken)
            total.append(time_taken)

        sum_time_taken = sum(total)

        myquery2 = {'RPO': rpo}
        mydoc2 = testing_activity_info.find(myquery2)

        for x2 in mydoc2:
            time_taken1 = x2["Time Taken (Days)"]
            activity_no = x2["Activity No"]

            myquery3 = {'RPO': rpo, 'Activity No': activity_no}

            time_taken1 = float(time_taken1)
            weightage_percent = (time_taken1 / sum_time_taken) * 100
            weightage_percent2 = str(weightage_percent)

            new_field = {"$set": {"Weightage %": weightage_percent2}}
            testing_activity_info.update_one(myquery3, new_field)
    except:
        print("--------------- Error Occurred while Updating Production Percentage ---------------")



'''==============================dispatch activities=============================='''


def insert_dispatch_activity(activity):

    exists = dispatch_activity_info.find({"RPO": activity["RPO"], "Activity No": activity["Activity No"]}).count()


    if exists == 0:
        dispatch_activity_info.insert_one(activity)
        rpo = activity["RPO"]
        update_dispatch_weightage_percent(rpo)

        myquery = {"RPO": rpo}
        mydoc = dispatch_activity_info.find(myquery)

        weightage_total_list = []
        for x in mydoc:
            status = x["Status"]
            if status == "Done":
                weightage_percent = x["Weightage %"]
                weightage_total_list.append(weightage_percent)

        if weightage_total_list:
            dispatch_status_list = []
            for x in weightage_total_list:
                weightage_percent_str = x.replace("%", "")
                weightage_percent_float = float(weightage_percent_str)
                dispatch_status_list.append(weightage_percent_float)
            dispatch_status_percent = sum(dispatch_status_list)
            dispatch_status_percent_str = str(dispatch_status_percent) + "%"
            myquery2 = {"RPO": rpo}
            updated_data = {"$set": {"Dispatch Status %": dispatch_status_percent_str}}
            active_orders.update_one(myquery2, updated_data)

        calculate_total_rpo_status(rpo)
        return 1
    else:
        return 0


def query_dispatch_activity_info(rpo):
    myquery = {"RPO": rpo}
    mydoc = dispatch_activity_info.find(myquery, {'_id': False})
    all_x = []
    for x in mydoc:
        all_x.append(x)
    return all_x


def get_specific_dispatch_activity_data(activity_no, rpo):
    myquery = {'RPO': rpo, 'Activity No': activity_no}
    x1 = dispatch_activity_info.find_one(myquery, {'_id': False})
    return x1


def update_specific_dispatch_activity_data(data):
    rpo = data["RPO"]
    activity_no = data["Activity No"]

    data["last_updated"] = datetime.now().strftime(constants.time_format)
    myquery = {'RPO': rpo, 'Activity No': activity_no}
    updated_data = {"$set": data}
    dispatch_activity_info.update_one(myquery, updated_data)
    update_dispatch_weightage_percent(rpo)

    myquery = {"RPO": rpo}
    mydoc = dispatch_activity_info.find(myquery)

    weightage_total_list = []
    for x in mydoc:
        status = x["Status"]
        if status == "Done":
            weightage_percent = x["Weightage %"]
            weightage_total_list.append(weightage_percent)

    if weightage_total_list:
        dispatch_status_list = []
        for x in weightage_total_list:
            weightage_percent_str = x.replace("%", "")
            weightage_percent_float = float(weightage_percent_str)
            dispatch_status_list.append(weightage_percent_float)
        dispatch_status_percent = sum(dispatch_status_list)
        dispatch_status_percent_str = str(dispatch_status_percent) + "%"
        myquery2 = {"RPO": rpo}
        updated_data = {"$set": {"Dispatch Status %": dispatch_status_percent_str}}
        active_orders.update_one(myquery2, updated_data)
    else:
        dispatch_status_percent_str = str(0) + "%"
        myquery3 = {"RPO": rpo}
        updated_data = {"$set": {"Dispatch Status %": dispatch_status_percent_str}}
        active_orders.update_one(myquery3, updated_data)

    calculate_total_rpo_status(rpo)


def delete_specific_dispatch_activity_data(rpo, activity_no):
    myquery = {'RPO': rpo, 'Activity No': activity_no}
    dispatch_activity_info.delete_one(myquery)
    update_dispatch_weightage_percent(rpo)

    myquery = {"RPO": rpo}
    mydoc = dispatch_activity_info.find(myquery)

    count = mydoc.count()
    if count == 0:
        dispatch_status_percent_str = str(0) + "%"
        myquery3 = {"RPO": rpo}
        updated_data = {"$set": {"Dispatch Status %": dispatch_status_percent_str}}
        active_orders.update_one(myquery3, updated_data)
    else:
        weightage_total_list = []
        for x in mydoc:
            status = x["Status"]
            if status == "Done":
                weightage_percent = x["Weightage %"]
                weightage_total_list.append(weightage_percent)

        if weightage_total_list:
            dispatch_status_list = []
            for x in weightage_total_list:
                weightage_percent_str = x.replace("%", "")
                weightage_percent_float = float(weightage_percent_str)
                dispatch_status_list.append(weightage_percent_float)
            dispatch_status_percent = sum(dispatch_status_list)
            dispatch_status_percent_str = str(dispatch_status_percent) + "%"
            myquery2 = {"RPO": rpo}
            updated_data = {"$set": {"Dispatch Status %": dispatch_status_percent_str}}
            active_orders.update_one(myquery2, updated_data)
        else:
            dispatch_status_percent_str = str(0) + "%"
            myquery3 = {"RPO": rpo}
            updated_data = {"$set": {"Dispatch Status %": dispatch_status_percent_str}}
            active_orders.update_one(myquery3, updated_data)

    calculate_total_rpo_status(rpo)


def update_dispatch_weightage_percent(rpo):
    try:
        myquery1 = {'RPO': rpo}
        mydoc1 = dispatch_activity_info.find(myquery1)
        total = []
        for x1 in mydoc1:
            time_taken = x1["Time Taken (Days)"]
            time_taken = float(time_taken)
            total.append(time_taken)

        sum_time_taken = sum(total)

        myquery2 = {'RPO': rpo}
        mydoc2 = dispatch_activity_info.find(myquery2)

        for x2 in mydoc2:
            time_taken1 = x2["Time Taken (Days)"]
            activity_no = x2["Activity No"]

            myquery3 = {'RPO': rpo, 'Activity No': activity_no}

            time_taken1 = float(time_taken1)
            weightage_percent = (time_taken1 / sum_time_taken) * 100
            weightage_percent2 = str(weightage_percent)

            new_field = {"$set": {"Weightage %": weightage_percent2}}
            dispatch_activity_info.update_one(myquery3, new_field)
    except:
        print("--------------- Error Occurred while Updating Production Percentage ---------------")


'''==============================Weightage per RPO================================'''


def validate_rpo(rpo):
    myquery = {"RPO": rpo}
    count = active_orders.find(myquery).count()
    if count == 0:
        return 1
    else:
        return 2


def get_design_status_for_rpo(rpo):
    myquery = {"RPO": rpo}
    count = design_activity_info.find(myquery).count()
    if count == 0:
        return 0
    else:
        status_total = []
        mydoc = design_activity_info.find(myquery)
        for x in mydoc:
            status = x["Status"]
            if status == "Done":
                weightage_percent = x["Weightage %"]
                weightage_percent = weightage_percent.replace('%', '')
                weightage_percent = float(weightage_percent)
                status_total.append(weightage_percent)

        total = sum(status_total)
        return total


def get_production_status_for_rpo(rpo):
    myquery = {"RPO": rpo}
    count = production_activity_info.find(myquery).count()
    if count == 0:
        return 0
    else:
        status_total = []
        mydoc = production_activity_info.find(myquery)
        for x in mydoc:
            status = x["Status"]
            if status == "Done":
                weightage_percent = x["Weightage %"]
                weightage_percent = weightage_percent.replace('%', '')
                weightage_percent = float(weightage_percent)
                status_total.append(weightage_percent)

        total = sum(status_total)
        return total


def get_purchase_status_for_rpo(rpo):
    myquery = {"RPO": rpo}
    count = purchase_activity_info.find(myquery).count()
    if count == 0:
        return 0
    else:
        status_total = []
        mydoc = purchase_activity_info.find(myquery)
        for x in mydoc:
            status = x["Status"]
            if status == "Done":
                weightage_percent = x["Weightage %"]
                weightage_percent = weightage_percent.replace('%', '')
                weightage_percent = float(weightage_percent)
                status_total.append(weightage_percent)

        total = sum(status_total)
        return total


'''======================================Total RPO Status==============================='''


def calculate_total_rpo_status(rpo):
    myquery = {"RPO": rpo}
    x = active_orders.find_one(myquery)

    total_weightage1 = []
    design_weightage = x["Design Weightage"]
    design_weightage = int(design_weightage)
    total_weightage1.append(design_weightage)

    production_weightage = x["Production Weightage"]
    production_weightage = int(production_weightage)
    total_weightage1.append(production_weightage)

    purchase_weightage = x["Purchase Weightage"]
    purchase_weightage = int(purchase_weightage)
    total_weightage1.append(purchase_weightage)

    testing_weightage = x["Testing Weightage"]
    testing_weightage = int(testing_weightage)
    total_weightage1.append(testing_weightage)

    dispatch_weightage = x["Dispatch Weightage"]
    dispatch_weightage = int(dispatch_weightage)
    total_weightage1.append(dispatch_weightage)

    total_weightage2 = sum(total_weightage1)

    design1 = design_weightage / total_weightage2 * 100
    production1 = production_weightage / total_weightage2 * 100
    purchase1 = purchase_weightage / total_weightage2 * 100
    testing1 = testing_weightage / total_weightage2 * 100
    dispatch1 = dispatch_weightage / total_weightage2 * 100

    design_status_str = x["Design Status %"]
    design_status_str = design_status_str.replace("%", "")
    design_status_float = float(design_status_str)
    total_design_status = design_status_float / 100 * design1

    production_status_str = x["Production Status %"]
    production_status_str = production_status_str.replace("%", "")
    production_status_float = float(production_status_str)
    total_production_status = production_status_float / 100 * production1

    purchase_status_str = x["Purchase Status %"]
    purchase_status_str = purchase_status_str.replace("%", "")
    purchase_status_float = float(purchase_status_str)
    total_purchase_status = purchase_status_float / 100 * purchase1

    testing_status_str = x["Testing Status %"]
    testing_status_str = testing_status_str.replace("%", "")
    testing_status_float = float(testing_status_str)
    total_testing_status = testing_status_float / 100 * testing1

    dispatch_status_str = x["Purchase Status %"]
    dispatch_status_str = dispatch_status_str.replace("%", "")
    dispatch_status_float = float(dispatch_status_str)
    total_dispatch_status = dispatch_status_float / 100 * dispatch1

    total_rpo_status_percent = total_design_status + total_production_status + total_purchase_status + total_dispatch_status + total_testing_status

    x["Total Status %"] = total_rpo_status_percent

    if total_rpo_status_percent > 99:
        if x["notifications"]["100_percent"] == 0:
            send_percent_wise_mails(x)
            x["notifications"]["100_percent"] = 1

    elif total_rpo_status_percent > 75:
        if x["notifications"]["75_percent"] == 0:
            send_percent_wise_mails(x)
            x["notifications"]["75_percent"] = 1

    elif total_rpo_status_percent > 50:
        if x["notifications"]["50_percent"] == 0:
            send_percent_wise_mails(x)
            x["notifications"]["50_percent"] = 1

    elif total_rpo_status_percent > 25:
        if x["notifications"]["25_percent"] == 0:
            send_percent_wise_mails(x)
            x["notifications"]["25_percent"] = 1

    total_rpo_status_percent = str(total_rpo_status_percent)
    total_rpo_status_percent_str = total_rpo_status_percent + "%"
    print("--------------------------------------------------------")
    print("             TOTAL COMPLETION PERCENT                   ")
    print("--------------------------------------------------------")
    print(total_rpo_status_percent_str)
    print("--------------------------------------------------------")

    myquery2 = {"RPO": rpo}
    updated_data = {"$set": {"Total Status %": total_rpo_status_percent_str ,"notifications" : x["notifications"] }}
    active_orders.update_one(myquery2, updated_data)


def get_rpo_status(rpo):
    myquery = {"RPO": rpo}
    x = active_orders.find_one(myquery)
    total_status = x["Total Status %"]
    return total_status


'''======================================Dispatch Details==============================='''


def insert_dispatch_details(data):
    rpo = data["RPO"]
    myquery = {"RPO": rpo}
    updated_data = {"$set": data}
    active_orders.update_one(myquery, updated_data)


def get_dispatch_details(rpo):
    myquery = {"RPO": rpo}
    mydoc = active_orders.find_one(myquery, {'_id': False})
    return mydoc


'''======================================Additional Notes==============================='''


def insert_additional_notes(data):
    details_for_mail = copy.deepcopy(data)
    print("--------------updating additional notes------------------")
    print(data)
    print("---------------------------------------------------------")
    rpo = data["RPO"]
    myquery = {"RPO": rpo}
    updated_data = {"$set": {"Project Status" : data["Project Status"],"Additional Notes": data["Additional Notes"]}}
    active_orders.update_one(myquery, updated_data)
    del data["RPO"] # Cleaning
    data["updated_on"] = datetime.now().strftime(constants.time_format)
    active_orders.update(myquery, {"$push": {"STATUS LOG": data}})
    send_mails_on_notes(details_for_mail)


def get_additional_notes(rpo):
    myquery = {"RPO": rpo}
    mydoc = active_orders.find_one(myquery, {'_id': False})
    return mydoc


'''======================================Profile========================================='''


def insert_profile(data):
    org_id = data["Organization ID"]
    myquery = {"Organization ID": org_id}
    count = profile.find(myquery).count()
    if count == 0:
        profile.insert_one(data)
    else:
        updated_data = {"$set": data}
        profile.update_one(myquery, updated_data)


'''======================================Reports========================================='''


def delete_report(data):
    query = {"RPO": data["RPO"]}
    rpo = active_orders.find_one(query, {'_id': False})
    if rpo is not None:
        if "reports" in rpo:
            for i in range(len(rpo["reports"])):
                if rpo["reports"][i]['report_name'] == data["file_name"] and rpo["reports"][i]['timestamp'] == data[
                    "timestamp"]:
                    os.remove(rpo["reports"][i]['path'])
                    del rpo["reports"][i]
                    break
            updated_data = {"$set": rpo}
            active_orders.update_one(query, updated_data)
            print("REPORT DELETED")
            return 1
        else:
            pass
    else:
        pass


def insert_report_details(data):
    print(data)
    timestamp = datetime.now().strftime(constants.time_format)
    data["timestamp"] = timestamp
    query = {"RPO": data["RPO"]}

    rpo = active_orders.find_one(query, {'_id': False})

    if rpo is not None:
        if "Reports" in rpo:
            rpo["Reports"].append(data)
        else:
            rpo["Reports"] = []
            rpo["Reports"].append(data)

        updated_data = {"$set": rpo}
        active_orders.update_one(query, updated_data)
    print("------------------ REPORT SAVED SUCCESSFULLY -------------------------")


def get_report_name_data(rpo):
    myquery1 = {"RPO": rpo, "Reports": {"$exists": True}}
    mydoc1 = active_orders.find_one(myquery1)

    if mydoc1:
        report_name_list = []
        array1 = mydoc1["Reports"]
        for x in array1:
            report_name = x["Report Name"]
            report_name_list.append(report_name)
        return report_name_list
    else:
        report_name_list = []
        return report_name_list


def get_report_note_data(rpo):
    myquery1 = {"RPO": rpo, "Reports": {"$exists": True}}
    mydoc1 = active_orders.find_one(myquery1)

    if mydoc1:
        report_note_list = []
        array1 = mydoc1["Reports"]
        for x in array1:
            report_note = x["Report Note"]
            report_note_list.append(report_note)
        return report_note_list
    else:
        report_note_list = []
        return report_note_list


def get_report_data_for_display(rpo):
    myquery1 = {"RPO": rpo, "Reports": {"$exists": True}}
    mydoc1 = active_orders.find_one(myquery1, {'_id': False})

    if mydoc1:
        return mydoc1
    else:
        report_note_list = []
        return report_note_list


def get_activity_presets():
    presets = []
    all_presets = activity_presets.find({})
    for preset in all_presets:
        preset["_id"] = str(preset["_id"])
        presets.append(preset)

    return presets


def get_machine_types_from_activity_preset():
    all_presets = activity_presets.distinct('Machine Type')
    print(type(all_presets))
    print(type(all_presets[0]))
    return all_presets


def get_activity_types_for_new_activity_preset():
    activity_types = activity_presets.distinct('Activity Type')

    return activity_types


def get_subtypes_for_machine_type(machine_type):
    subtypes = activity_presets.find({"Machine Type": machine_type}).distinct("Machine sub_type")

    return subtypes


def generate_production_activities(order):
    pprint(order)
    all_activities = activity_presets.find(
        {"Machine Type": order["Machine Type"], "Machine sub_type": order["Machine Subtype"], "Domain": "Production"})
    print("------activities------")
    print(all_activities)

    counter = 1
    for activity in all_activities:
        production_activity = {}
        production_activity["RPO"] = order["RPO"]
        production_activity["Client Name"] = order["Client Name"]
        production_activity["Activity No"] = str(counter)
        production_activity["Activity Type"] = activity["Activity Type"]
        production_activity["sub_type"] = activity["sub_type"]
        production_activity["Activity"] = ""
        production_activity["Time Taken (Days)"] = activity["man_days"]
        production_activity["Note"] = ""
        production_activity["Status"] = "Not Started"
        production_activity["last_updated"] = ""

        insert_production_activity(production_activity)
        counter += 1

    print("PRODUCTION ACTIVITIES WERE GENERATED.")

def generate_design_activities(order):
    pprint(order)
    all_activities = activity_presets.find(
        {"Machine Type": order["Machine Type"], "Machine sub_type": order["Machine Subtype"], "Domain": "Design"})
    print("------activities------")
    print(all_activities)

    counter = 1
    for activity in all_activities:
        design_activity = {}
        design_activity["RPO"] = order["RPO"]
        design_activity["Client Name"] = order["Client Name"]
        design_activity["Activity No"] = str(counter)
        design_activity["Activity Type"] = activity["Activity Type"]
        design_activity["sub_type"] = activity["sub_type"]
        design_activity["Activity"] = ""
        design_activity["Time Taken (Days)"] = activity["man_days"]
        design_activity["Note"] = ""
        design_activity["Status"] = "Not Started"
        design_activity["last_updated"] = ""
        insert_design_activity(design_activity)
        counter += 1

    print("DESIGN ACTIVITIES WERE GENERATED.")

def generate_testing_activities(order):
    pprint(order)
    all_activities = activity_presets.find(
        {"Machine Type": order["Machine Type"], "Machine sub_type": order["Machine Subtype"], "Domain": "Testing"})
    print("------activities------")
    print(all_activities)

    counter = 1
    for activity in all_activities:
        testing_activity = {}
        testing_activity["RPO"] = order["RPO"]
        testing_activity["Client Name"] = order["Client Name"]
        testing_activity["Activity No"] = str(counter)
        testing_activity["Activity Type"] = activity["Activity Type"]
        testing_activity["sub_type"] = activity["sub_type"]
        testing_activity["Activity"] = ""
        testing_activity["Time Taken (Days)"] = activity["man_days"]
        testing_activity["Note"] = ""
        testing_activity["Status"] = "Not Started"
        testing_activity["last_updated"] = ""

        insert_testing_activity(testing_activity)
        counter += 1

    print("TESTING ACTIVITIES WERE GENERATED.")

def generate_dispatch_activities(order):
    pprint(order)
    all_activities = activity_presets.find(
        {"Machine Type": order["Machine Type"], "Machine sub_type": order["Machine Subtype"], "Domain": "Dispatch"})
    print("------activities------")
    print(all_activities)

    counter = 1
    for activity in all_activities:
        dispatch_activity = {}
        dispatch_activity["RPO"] = order["RPO"]
        dispatch_activity["Client Name"] = order["Client Name"]
        dispatch_activity["Activity No"] = str(counter)
        dispatch_activity["Activity Type"] = activity["Activity Type"]
        dispatch_activity["sub_type"] = activity["sub_type"]
        dispatch_activity["Activity"] = ""
        dispatch_activity["Time Taken (Days)"] = activity["man_days"]
        dispatch_activity["Note"] = ""
        dispatch_activity["Status"] = "Not Started"
        dispatch_activity["last_updated"] = ""

        insert_dispatch_activity(dispatch_activity)
        counter += 1

    print("DISPATCH ACTIVITIES WERE GENERATED.")


def generate_purchase_activities(order):
    pprint(order)
    all_activities = activity_presets.find(
        {"Machine Type": order["Machine Type"], "Machine sub_type": order["Machine Subtype"], "Domain": "Purchase"})
    print("------activities------")
    print(all_activities)

    counter = 1
    for activity in all_activities:
        purchase_activity = {}
        purchase_activity["RPO"] = order["RPO"]
        purchase_activity["Client Name"] = order["Client Name"]
        purchase_activity["Activity No"] = str(counter)
        purchase_activity["Activity Type"] = activity["Activity Type"]
        purchase_activity["sub_type"] = activity["sub_type"]
        purchase_activity["Activity"] = ""
        purchase_activity["Time Taken (Days)"] = activity["man_days"]
        purchase_activity["Note"] = ""
        purchase_activity["Status"] = "Not Started"
        purchase_activity["last_updated"] = ""

        insert_purchase_activity(purchase_activity)
        counter += 1

    print("PURCHASE ACTIVITIES WERE GENERATED.")


def approve1_rpo(data):
    rpo = active_orders.find_one({"RPO": data["rpo"]}, {"_id": False})

    rpo["approval1_status"] = "Approved"
    rpo["approved1_by"] = data["user"]
    updated_data = {"$set": rpo}
    active_orders.update_one({"RPO": data["rpo"]}, updated_data)


def approve2_rpo(data):
    rpo = active_orders.find_one({"RPO": data["rpo"]}, {"_id": False})

    rpo["approval2_status"] = "Approved"
    rpo["approved2_by"] = data["user"]
    updated_data = {"$set": rpo}
    active_orders.update_one({"RPO": data["rpo"]}, updated_data)


def approve3_rpo(data):
    rpo = active_orders.find_one({"RPO": data["rpo"]}, {"_id": False})

    rpo["approval3_status"] = "Approved"
    rpo["approved3_by"] = data["user"]
    updated_data = {"$set": rpo}
    active_orders.update_one({"RPO": data["rpo"]}, updated_data)


def get_rpos_ready_to_dispatch():
    rpos = active_orders.find({"Project Status": "READY TO DISPATCH"}, {"_id": False})
    all_rpos = []
    for a in rpos:
        all_rpos.append(a)

    return all_rpos


def get_closed_rpos():
    rpos = active_orders.find({"Project Status": "CLOSED"}, {"_id": False})
    all_rpos = []
    for a in rpos:
        all_rpos.append(a)

    return all_rpos

def close_rpo(data):
    print(data)
    active_orders.update_one({"RPO": data["rpo"]}, {"$set": {"Project Status": "CLOSED" ,"closed_by" : data["user"], "closed_on": datetime.now()}})
    print("RPO CLOSED")
    send_rpo_to_dsm(data)

def send_rpo_to_dsm(data):

    # keys mapped to dsm

    rpo = active_orders.find_one({"RPO": data["rpo"]})
    client = customers.find_one({"client_id": rpo["Client ID"]})

    to_send = {}
    to_send["order_number"] = rpo["RPO"]
    to_send["client_id"] = rpo["Client ID"]
    to_send["client_name"] = rpo["Client Name"]
    to_send["machine_type"] = rpo["Machine Type"]
    to_send["machine_subtype"] = rpo["Machine Subtype"]
    to_send["twin_poc"] = rpo["POC"]
    to_send["invoice_date"] = rpo["invoice_date"]
    to_send["warranty"] = rpo["warranty"]
    to_send["warranty_date"] = rpo["warranty_date"]
    to_send["expiry_date"] = rpo["expiry_date"]
    to_send["address"] = rpo["address"]
    to_send["phone"] = rpo["phone"]
    to_send["email"] = rpo["email"]
    to_send["customer_poc"] = rpo["POC"]
    to_send["location"] = rpo["location"]
    to_send["client_type"] = rpo["Client Type"]
    to_send["documents"] = []

    # POST TO DSM
    try:
        res = requests.post(url=constants.dsm_new_rpo_endpoint, json=to_send)
        return "Sent to DSM Successfully"
    except:
        return "Failed to reach DSM Server."

def add_new_preset(data):
    print(data)
    # check for machine type, machine subtype, activity subtype
    exists = activity_presets.find({"$and": [{'Domain': data["Domain"],
                                              "Machine Type": data["Machine Type"],
                                              'Machine sub_type': data["Machine sub_type"],
                                              'Activity Type': data['Activity Type'],
                                              'sub_type': data['sub_type']
                                              }]}).count()
    found = activity_presets.find({'Domain': data["Domain"],
                                   "Machine Type": data["Machine Type"],
                                   'Machine sub_type': data["Machine sub_type"],
                                   'Activity Type': data['Activity Type'],
                                   'sub_type': data['sub_type']
                                   }).count()
    print("-_____________")
    print(found)
    print("--------------------")

    if exists == 0:
        print("adding new preset")
        activity_presets.insert_one(data)
        return 1
    else:
        print("already exists")
        return 0


def delete_preset(data):

    activity_presets.delete_one({'_id': ObjectId(data)})
    print("------------------------ Preset deleted -------------------------------")


def get_customer_page_data(rpo):


    print("here")
    myquery = {"RPO": rpo}
    x = active_orders.find_one(myquery)

    total_weightage1 = []
    design_weightage = x["Design Weightage"]
    design_weightage = int(design_weightage)
    total_weightage1.append(design_weightage)

    production_weightage = x["Production Weightage"]
    production_weightage = int(production_weightage)
    total_weightage1.append(production_weightage)

    purchase_weightage = x["Purchase Weightage"]
    purchase_weightage = int(purchase_weightage)
    total_weightage1.append(purchase_weightage)

    testing_weightage = x["Testing Weightage"]
    testing_weightage = int(testing_weightage)
    total_weightage1.append(testing_weightage)

    dispatch_weightage = x["Dispatch Weightage"]
    dispatch_weightage = int(dispatch_weightage)
    total_weightage1.append(dispatch_weightage)

    total_weightage2 = sum(total_weightage1)

    design1 = design_weightage / total_weightage2 * 100
    production1 = production_weightage / total_weightage2 * 100
    purchase1 = purchase_weightage / total_weightage2 * 100
    testing1 = testing_weightage / total_weightage2 * 100
    dispatch1 = dispatch_weightage / total_weightage2 * 100







    all_activities = []

    order =  active_orders.find_one({"RPO": rpo},{"_id":False})
    client_type = order["Client Type"]
    order["Design Status %"] = order["Design Status %"] .replace("%","")
    order["Production Status %"] = order["Production Status %"].replace("%", "")
    order["Purchase Status %"] = order["Purchase Status %"].replace("%", "")
    order["Testing Status %"] = order["Testing Status %"].replace("%", "")
    order["Dispatch Status %"] = order["Dispatch Status %"].replace("%", "")

    if float(order["Design Status %"]) >= design1:

        design = design_activity_info.find({"RPO": rpo}, {'_id': False})
        date_list = []
        for act in design:
            if "last_updated" in act:
                try:
                    date_list.append(datetime.strptime(act["last_updated"], constants.time_format))
                except:
                    pass

        sorted_list = sorted(date_list)

        milestione = {}
        milestione["domain"] = "Design"
        try:
            milestione["date"] = sorted_list[-1].strftime(constants.only_date)
        except:
            milestione["date"] = "-"
        milestione["status"] = "Done"

        # print("Done")
    elif float(order["Design Status %"]) > 0:
        milestione = {}
        milestione["domain"] = "Design"
        milestione["date"] = "-"
        milestione["status"] = "In Progress"
        # print("In Progress")
    else:
        milestione = {}
        milestione["domain"] = "Design"
        milestione["date"] = "-"
        milestione["status"] = "Not started"
        # print("Not started")

    all_activities.append(milestione)
    # ---------------------------------------------------------------------------------

    if float(order["Purchase Status %"]) >= purchase1:
        # print("Done")
        purchase = purchase_activity_info.find({"RPO": rpo}, {'_id': False})
        date_list = []
        for act in purchase:
            if "last_updated" in act:
                print("-------------------------")
                print(act["last_updated"])
                print("-------------------------")
                try:
                    date_list.append(datetime.strptime(act["last_updated"], constants.time_format))
                except:
                    pass

        sorted_list = sorted(date_list)

        milestione = {}
        milestione["domain"] = "Purchase"
        try:
            milestione["date"] = sorted_list[-1].strftime(constants.only_date)
        except:
            milestione["date"] = "-"
        milestione["status"] = "Done"

    elif float(order["Purchase Status %"]) > 0:
        # print("In Progress")
        milestione = {}
        milestione["domain"] = "Purchase"
        milestione["date"] = "-"
        milestione["status"] = "In Progress"
        # print("In Progress")
    else:
        # print("Not started")
        milestione = {}
        milestione["domain"] = "Purchase"
        milestione["date"] = "-"
        milestione["status"] = "In Progress"
        # print("In Progress")
    all_activities.append(milestione)
    # ---------------------------------------------------------------------------------

    if float(order["Production Status %"]) >= production1:
        production = production_activity_info.find({"RPO": rpo}, {'_id': False})
        date_list = []
        for act in production:
            if "last_updated" in act:
                try:
                    date_list.append(datetime.strptime(act["last_updated"], constants.time_format))
                except:
                    pass

        sorted_list = sorted(date_list)

        milestione = {}
        milestione["domain"] = "Production"
        try:
            milestione["date"] = sorted_list[-1].strftime(constants.only_date)
        except:
            milestione["date"] = "-"
        milestione["status"] = "Done"
        # print("Done")
    elif float(order["Production Status %"]) > 0:
        milestione = {}
        milestione["domain"] = "Production"
        milestione["date"] = "-"
        milestione["status"] = "In Progress"
        # print("In Progress")

    else:
        milestione = {}
        milestione["domain"] = "Production"
        milestione["date"] = "-"
        milestione["status"] = "Not started"
        # print("In Progress")


        print("Not started")
    all_activities.append(milestione)
    # ---------------------------------------------------------------------------------



    if float(order["Testing Status %"]) >= testing1:
        testing = testing_activity_info.find({"RPO": rpo}, {'_id': False})
        date_list =[]
        for act in testing:
            if "last_updated" in act:
                try:
                    date_list.append(datetime.strptime(act["last_updated"], constants.time_format))
                except:
                    pass

        sorted_list = sorted(date_list)

        milestione = {}
        milestione["domain"] = "Testing"
        try:
            milestione["date"] = sorted_list[-1].strftime(constants.only_date)
        except:
            milestione["date"] = "-"
        milestione["status"] = "Done"
        # print("Done")
    elif float(order["Testing Status %"]) > 0:
        # print("In Progress")
        milestione = {}
        milestione["domain"] = "Testing"
        milestione["date"] = "-"
        milestione["status"] = "In Progress"

    else:
        milestione = {}
        milestione["domain"] = "Testing"
        milestione["date"] = "-"
        milestione["status"] = "Not started"
        print("Not started")
    all_activities.append(milestione)
    # ---------------------------------------------------------------------------------


    if float(order["Dispatch Status %"]) >= dispatch1:
        dispatch = dispatch_activity_info.find({"RPO": rpo}, {'_id': False})
        date_list = []
        for act in dispatch:
            if "last_updated" in act:
                try:
                    date_list.append(datetime.strptime(act["last_updated"], constants.time_format))
                except:
                    pass

        sorted_list = sorted(date_list)

        milestione = {}
        milestione["domain"] = "Dispatch"
        try:
            milestione["date"] = sorted_list[-1].strftime(constants.only_date)
        except:
            milestione["date"] = "-"
        milestione["status"] = "Done"

        # print("Done")
    elif float(order["Dispatch Status %"]) > 0:
        milestione = {}
        milestione["domain"] = "Dispatch"
        milestione["date"] = "-"
        milestione["status"] = "In Progress"
        # print("In Progress")
    else:
        milestione = {}
        milestione["domain"] = "Dispatch"
        milestione["date"] = "-"
        milestione["status"] = "Not started"
        # print("Not started")

    all_activities.append(milestione)

    pprint(all_activities)

    return all_activities


def get_customer_page_data_old(rpo):

    all_activities = []

    counter = 1
    design = design_activity_info.find({"RPO": rpo}, {'_id': False})

    design1 = []
    for a in design:
        design1.append(a)

    for i in range(len(design1)):
        if i == 0:
            design1[i]["Domain"] = "Design"
            design1[i]["sr"] = counter
            counter +=1
        else:
            design1[i]["Domain"] = ""
            design1[i]["sr"] = ""

        all_activities.append(design1[i])

    purchase = purchase_activity_info.find({"RPO": rpo}, {'_id': False})

    purchase1 = []
    for a in purchase:
        purchase1.append(a)

    for i in range(len(purchase1)):
        if i == 0:
            purchase1[i]["Domain"] = "Purchase"
            purchase1[i]["sr"] = counter
            counter += 1
        else:
            purchase1[i]["Domain"] = ""
            purchase1[i]["sr"] = ""

        all_activities.append(purchase1[i])

    production = production_activity_info.find({"RPO": rpo}, {'_id': False})

    production1 = []
    for a in production:
        production1.append(a)

    for i in range(len(production1)):
        if i == 0:
            production1[i]["Domain"] = "Production"
            production1[i]["sr"] = counter
            counter += 1
        else:
            production1[i]["Domain"] = ""
            production1[i]["sr"] = ""

        all_activities.append(production1[i])


    testing = testing_activity_info.find({"RPO": rpo}, {'_id': False})

    testing1 = []
    for a in testing:
        testing1.append(a)

    for i in range(len(testing1)):
        if i == 0:
            testing1[i]["Domain"] = "Testing"
            testing1[i]["sr"] = counter
            counter += 1
        else:
            testing1[i]["Domain"] = ""
            testing1[i]["sr"] = ""

        all_activities.append(testing1[i])


    dispatch = dispatch_activity_info.find({"RPO": rpo}, {'_id': False})

    dispatch1 = []
    for a in dispatch:
        dispatch1.append(a)

    for i in range(len(dispatch1)):
        if i == 0:
            dispatch1[i]["Domain"] = "Dispatch"
            dispatch1[i]["sr"] = counter
            counter += 1
        else:
            dispatch1[i]["Domain"] = ""
            dispatch1[i]["sr"] = ""

        all_activities.append(dispatch1[i])
    return all_activities


def get_customer_page_data2(rpo):
    all_activities = []

    counter = 1
    order = active_orders.find_one({"RPO": rpo})

    design_distinct = design_activity_info.find({"RPO": rpo}, {'_id': False}).distinct("Activity Type")
    print(design_distinct)
    if order["Client Type"] != "Standard":
        for pd in range(len(design_distinct)):
            milestone_data = {}
            all_pd = design_activity_info.find({"RPO": rpo, "Activity Type": design_distinct[pd]}, {'_id': False}).count()
            not_started = design_activity_info.find(
                {"RPO": rpo, "Activity Type": design_distinct[pd], "Status": "Not Started"}, {'_id': False}).count()
            all_done = design_activity_info.find({"RPO": rpo, "Activity Type": design_distinct[pd], "Status": "Done"},
                                                 {'_id': False}).count()
            if pd == 0:
                if all_pd == not_started:
                    milestone_data["sr"] = counter
                    milestone_data["date"] = "-"
                    milestone_data["milestone"] = "Design"
                    milestone_data["activity"] = design_distinct[pd]
                    milestone_data["status"] = "Not started"
                    print("Not started")
                elif all_pd == all_done:
                    milestone_data["sr"] = counter
                    milestone_data["milestone"] = "Design"
                    milestone_data["activity"] = design_distinct[pd]
                    milestone_data["status"] = "Done"
                    date_list = []
                    for act in design_activity_info.find({"RPO": rpo, "Activity Type": design_distinct[pd]}, {'_id': False}):
                        if "last_updated" in act:
                            try:
                                date_list.append(datetime.strptime(act["last_updated"], constants.time_format))
                            except:
                                pass
                    print(date_list)
                    sorted_list = sorted(date_list)
                    print(sorted_list)
                    milestone_data["date"] = sorted_list[-1].strftime(constants.only_date)


                    print("Done")
                else:
                    milestone_data["date"] = "-"
                    milestone_data["sr"] = counter
                    milestone_data["milestone"] = "Design"
                    milestone_data["activity"] = design_distinct[pd]
                    milestone_data["status"] = "In Progress"
                    print("In Progress")

                counter += 1
            else:
                if all_pd == not_started:
                    milestone_data["sr"] = ""
                    milestone_data["milestone"] = ""
                    milestone_data["activity"] = design_distinct[pd]
                    milestone_data["status"] = "Not started"
                    milestone_data["date"] = "-"
                    print("Not started")
                elif all_pd == all_done:
                    milestone_data["sr"] = ""
                    milestone_data["milestone"] = ""
                    milestone_data["activity"] = design_distinct[pd]
                    milestone_data["status"] = "Done"
                    date_list = []
                    for act in design_activity_info.find({"RPO": rpo, "Activity Type": design_distinct[pd]}, {'_id': False}):
                        if "last_updated" in act:
                            try:
                                date_list.append(datetime.strptime(act["last_updated"], constants.time_format))
                            except:
                                pass
                    print(date_list)
                    sorted_list = sorted(date_list)
                    print(sorted_list)
                    try:
                        milestone_data["date"] = sorted_list[-1].strftime(constants.only_date)
                    except:
                        milestone_data["date"] = "-"
                    print("Done")
                else:
                    milestone_data["date"] = "-"
                    milestone_data["sr"] = ""
                    milestone_data["milestone"] = ""
                    milestone_data["activity"] = design_distinct[pd]
                    milestone_data["status"] = "In Progress"
                    print("In Progress")

            print(milestone_data)
            all_activities.append(milestone_data)

    # ---------------------------------------------------------------------------------------------------
    purchase_distinct = purchase_activity_info.find({"RPO": rpo}, {'_id': False}).distinct("Activity Type")
    print(purchase_distinct)

    for pd in range(len(purchase_distinct)):
        milestone_data = {}
        all_pd = purchase_activity_info.find({"RPO": rpo, "Activity Type": purchase_distinct[pd]},
                                             {'_id': False}).count()
        not_started = purchase_activity_info.find(
            {"RPO": rpo, "Activity Type": purchase_distinct[pd], "Status": "Not Started"}, {'_id': False}).count()
        all_done = purchase_activity_info.find({"RPO": rpo, "Activity Type": purchase_distinct[pd], "Status": "Done"},
                                               {'_id': False}).count()
        if pd == 0:
            if all_pd == not_started:
                milestone_data["sr"] = counter
                milestone_data["date"] = "-"
                milestone_data["milestone"] = "Purchase"
                milestone_data["activity"] = purchase_distinct[pd]
                milestone_data["status"] = "Not started"
                print("Not started")
            elif all_pd == all_done:
                milestone_data["sr"] = counter
                milestone_data["milestone"] = "Purchase"
                milestone_data["activity"] = purchase_distinct[pd]
                milestone_data["status"] = "Done"
                date_list = []
                for act in purchase_activity_info.find({"RPO": rpo, "Activity Type": purchase_distinct[pd]}, {'_id': False}):
                    if "last_updated" in act:
                        try:
                            date_list.append(datetime.strptime(act["last_updated"], constants.time_format))
                        except:
                            pass
                print(date_list)
                sorted_list = sorted(date_list)
                print(sorted_list)
                try:
                    milestone_data["date"] = sorted_list[-1].strftime(constants.only_date)
                except:
                    milestone_data["date"] = "-"
                print("Done")
            else:
                milestone_data["date"] = "-"
                milestone_data["sr"] = counter
                milestone_data["milestone"] = "Purchase"
                milestone_data["activity"] = purchase_distinct[pd]
                milestone_data["status"] = "In Progress"
                print("In Progress")

            counter += 1
        else:
            if all_pd == not_started:
                milestone_data["sr"] = ""
                milestone_data["milestone"] = ""
                milestone_data["activity"] = purchase_distinct[pd]
                milestone_data["status"] = "Not started"
                milestone_data["date"] = "-"
                print("Not started")
            elif all_pd == all_done:
                milestone_data["sr"] = ""
                milestone_data["milestone"] = ""
                milestone_data["activity"] = purchase_distinct[pd]
                milestone_data["status"] = "Done"
                date_list = []
                for act in purchase_activity_info.find({"RPO": rpo, "Activity Type": purchase_distinct[pd]}, {'_id': False}):
                    if "last_updated" in act:
                        try:
                            date_list.append(datetime.strptime(act["last_updated"], constants.time_format))
                        except:
                            pass
                print(date_list)
                sorted_list = sorted(date_list)
                print(sorted_list)
                try:
                    milestone_data["date"] = sorted_list[-1].strftime(constants.only_date)
                except:
                    milestone_data["date"] = "-"
                print("Done")
            else:
                milestone_data["date"] = "-"
                milestone_data["sr"] = ""
                milestone_data["milestone"] = ""
                milestone_data["activity"] = purchase_distinct[pd]
                milestone_data["status"] = "In Progress"
                print("In Progress")

        print(milestone_data)
        all_activities.append(milestone_data)

    # -----------------------------------------------------------------------------------------------------------

    production_distinct = production_activity_info.find({"RPO": rpo}, {'_id': False}).distinct("Activity Type")
    print(production_distinct)

    for pd in range(len(production_distinct)):
        milestone_data = {}
        all_pd = production_activity_info.find({"RPO": rpo,"Activity Type" : production_distinct[pd]}, {'_id': False}).count()
        not_started = production_activity_info.find({"RPO": rpo,"Activity Type" : production_distinct[pd] ,"Status": "Not Started" }, {'_id': False}).count()
        all_done = production_activity_info.find({"RPO": rpo,"Activity Type" : production_distinct[pd] ,"Status": "Done" }, {'_id': False}).count()
        if pd == 0:
            if all_pd == not_started:
                milestone_data["sr"] = counter
                milestone_data["date"] = "-"
                milestone_data["milestone"] = "Production"
                milestone_data["activity"] = production_distinct[pd]
                milestone_data["status"] = "Not started"
                print("Not started")
            elif all_pd == all_done:
                milestone_data["sr"] = counter
                milestone_data["milestone"] = "Production"
                milestone_data["activity"] = production_distinct[pd]
                milestone_data["status"] = "Done"
                date_list = []
                for act in production_activity_info.find({"RPO": rpo, "Activity Type": production_distinct[pd]}, {'_id': False}):
                    if "last_updated" in act:
                        try:
                            date_list.append(datetime.strptime(act["last_updated"], constants.time_format))
                        except:
                            pass

                print(date_list)
                sorted_list = sorted(date_list)
                print(sorted_list)
                try:
                    milestone_data["date"] = sorted_list[-1].strftime(constants.only_date)
                except:
                    milestone_data["date"] = "-"

                print("Done")
            else:
                milestone_data["date"] = "-"
                milestone_data["sr"] = counter
                milestone_data["milestone"] = "Production"
                milestone_data["activity"] = production_distinct[pd]
                milestone_data["status"] = "In Progress"
                print("In Progress")

            counter += 1
        else:
            if all_pd == not_started:
                milestone_data["sr"] = ""
                milestone_data["milestone"] = ""
                milestone_data["activity"] = production_distinct[pd]
                milestone_data["status"] = "Not started"
                milestone_data["date"] = "-"
                print("Not started")
            elif all_pd == all_done:
                milestone_data["sr"] = ""
                milestone_data["milestone"] = ""
                milestone_data["activity"] = production_distinct[pd]
                milestone_data["status"] = "Done"
                date_list = []
                for act in production_activity_info.find({"RPO": rpo, "Activity Type": production_distinct[pd]}, {'_id': False}):
                    if "last_updated" in act:
                        try:
                            date_list.append(datetime.strptime(act["last_updated"], constants.time_format))
                        except:
                            pass
                print(date_list)
                sorted_list = sorted(date_list)
                print(sorted_list)
                try:
                    milestone_data["date"] = sorted_list[-1].strftime(constants.only_date)
                except:
                    milestone_data["date"] = "-"
                print("Done")
            else:
                milestone_data["date"] = "-"
                milestone_data["sr"] = ""
                milestone_data["milestone"] = ""
                milestone_data["activity"] = production_distinct[pd]
                milestone_data["status"] = "In Progress"
                print("In Progress")

        print(milestone_data)
        all_activities.append(milestone_data)
    # -------------------------------------------------------------------------------------------------

    dispatch_distinct = dispatch_activity_info.find({"RPO": rpo}, {'_id': False}).distinct("Activity Type")
    print(dispatch_distinct)

    for pd in range(len(dispatch_distinct)):
        milestone_data = {}
        all_pd = dispatch_activity_info.find({"RPO": rpo, "Activity Type": dispatch_distinct[pd]},
                                             {'_id': False}).count()
        not_started = dispatch_activity_info.find(
            {"RPO": rpo, "Activity Type": dispatch_distinct[pd], "Status": "Not Started"}, {'_id': False}).count()
        all_done = dispatch_activity_info.find({"RPO": rpo, "Activity Type": dispatch_distinct[pd], "Status": "Done"},
                                               {'_id': False}).count()
        if pd == 0:
            if all_pd == not_started:
                milestone_data["sr"] = counter
                milestone_data["date"] = "-"
                milestone_data["milestone"] = "Dispatch"
                milestone_data["activity"] = dispatch_distinct[pd]
                milestone_data["status"] = "Not started"
                print("Not started")
            elif all_pd == all_done:
                milestone_data["sr"] = counter
                milestone_data["milestone"] = "Dispatch"
                milestone_data["activity"] = dispatch_distinct[pd]
                milestone_data["status"] = "Done"
                date_list = []
                for act in dispatch_activity_info.find({"RPO": rpo, "Activity Type": dispatch_distinct[pd]}, {'_id': False}):
                    if "last_updated" in act:
                        try:
                            date_list.append(datetime.strptime(act["last_updated"], constants.time_format))
                        except:
                            pass
                print(date_list)
                sorted_list = sorted(date_list)
                print(sorted_list)
                try:
                    milestone_data["date"] = sorted_list[-1].strftime(constants.only_date)
                except:
                    milestone_data["date"] = "-"
                print("Done")
            else:
                milestone_data["date"] = "-"
                milestone_data["sr"] = counter
                milestone_data["milestone"] = "Dispatch"
                milestone_data["activity"] = dispatch_distinct[pd]
                milestone_data["status"] = "In Progress"
                print("In Progress")

            counter += 1
        else:
            if all_pd == not_started:
                milestone_data["sr"] = ""
                milestone_data["milestone"] = ""
                milestone_data["activity"] = dispatch_distinct[pd]
                milestone_data["status"] = "Not started"
                milestone_data["date"] = "-"
                print("Not started")
            elif all_pd == all_done:
                milestone_data["sr"] = ""
                milestone_data["milestone"] = ""
                milestone_data["activity"] = dispatch_distinct[pd]
                milestone_data["status"] = "Done"
                date_list = []
                for act in dispatch_activity_info.find({"RPO": rpo, "Activity Type": dispatch_distinct[pd]}, {'_id': False}):
                    if "last_updated" in act:
                        try:
                            date_list.append(datetime.strptime(act["last_updated"], constants.time_format))
                        except:
                            pass
                print(date_list)
                sorted_list = sorted(date_list)
                print(sorted_list)
                try:
                    milestone_data["date"] = sorted_list[-1].strftime(constants.only_date)
                except:
                    milestone_data["date"] = "-"
                print("Done")
            else:
                milestone_data["date"] = "-"
                milestone_data["sr"] = ""
                milestone_data["milestone"] = ""
                milestone_data["activity"] = dispatch_distinct[pd]
                milestone_data["status"] = "In Progress"
                print("In Progress")

        print(milestone_data)
        all_activities.append(milestone_data)

    # -------------------------------------------------------------------------------------------

    testing_distinct = testing_activity_info.find({"RPO": rpo}, {'_id': False}).distinct("Activity Type")
    print(testing_distinct)

    for pd in range(len(testing_distinct)):
        milestone_data = {}
        all_pd = testing_activity_info.find({"RPO": rpo, "Activity Type": testing_distinct[pd]}, {'_id': False}).count()
        not_started = testing_activity_info.find(
            {"RPO": rpo, "Activity Type": testing_distinct[pd], "Status": "Not Started"}, {'_id': False}).count()
        all_done = testing_activity_info.find({"RPO": rpo, "Activity Type": testing_distinct[pd], "Status": "Done"},
                                              {'_id': False}).count()
        if pd == 0:
            if all_pd == not_started:
                milestone_data["sr"] = counter
                milestone_data["date"] = "-"
                milestone_data["milestone"] = "Testing"
                milestone_data["activity"] = testing_distinct[pd]
                milestone_data["status"] = "Not started"
                print("Not started")
            elif all_pd == all_done:
                milestone_data["sr"] = counter
                milestone_data["milestone"] = "Testing"
                milestone_data["activity"] = testing_distinct[pd]
                milestone_data["status"] = "Done"
                date_list = []
                for act in testing_activity_info.find({"RPO": rpo, "Activity Type": testing_distinct[pd]}, {'_id': False}):
                    if "last_updated" in act:
                        try:
                            date_list.append(datetime.strptime(act["last_updated"], constants.time_format))
                        except:
                            pass
                print(date_list)
                sorted_list = sorted(date_list)
                print(sorted_list)
                try:
                    milestone_data["date"] = sorted_list[-1].strftime(constants.only_date)
                except:
                    milestone_data["date"] = "-"
                print("Done")
            else:
                milestone_data["date"] = "-"
                milestone_data["sr"] = counter
                milestone_data["milestone"] = "Testing"
                milestone_data["activity"] = testing_distinct[pd]
                milestone_data["status"] = "In Progress"
                print("In Progress")

            counter += 1
        else:
            if all_pd == not_started:
                milestone_data["sr"] = ""
                milestone_data["milestone"] = ""
                milestone_data["activity"] = testing_distinct[pd]
                milestone_data["status"] = "Not started"
                milestone_data["date"] = "-"
                print("Not started")
            elif all_pd == all_done:
                milestone_data["sr"] = ""
                milestone_data["milestone"] = ""
                milestone_data["activity"] = testing_distinct[pd]
                milestone_data["status"] = "Done"
                date_list = []
                for act in testing_activity_info.find({"RPO": rpo, "Activity Type": testing_distinct[pd]}, {'_id': False}):
                    if "last_updated" in act:
                        try:
                            date_list.append(datetime.strptime(act["last_updated"], constants.time_format))
                        except:
                            pass
                print(date_list)
                sorted_list = sorted(date_list)
                print(sorted_list)
                try:
                    milestone_data["date"] = sorted_list[-1].strftime(constants.only_date)
                except:
                    milestone_data["date"] = "-"
                print("Done")
            else:
                milestone_data["date"] = "-"
                milestone_data["sr"] = ""
                milestone_data["milestone"] = ""
                milestone_data["activity"] = testing_distinct[pd]
                milestone_data["status"] = "In Progress"
                print("In Progress")

        print(milestone_data)
        all_activities.append(milestone_data)

    print(all_activities)
    return all_activities

def send_eod():
    date = datetime.now().strftime(constants.only_date)
    # Get user info



    users = database_operations.twin_superadmins_emails()

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
      background-color: #0768a6;
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
    <div><img src="https://www.twinengineers.com/wp-content/uploads/2019/02/twin-engineers-logo.png" style="height:40px"></div>

    """

    shift_date_heading = '</h3></div><center><div><br><h2 style="text-align:center; font-family: sans-serif;"> Daily Report for ' + date + '</h2><br></div></center><center>'

    table_header = '<div class="container" style="width:100%;padding-left:20px;padding-right:10vw;" ><table id="mytable" style="margin-right:10px;"><tr><th > RPO  </th><th > CLIENT NAME </th><th >MACHINE CATEGORY</th><th >MACHINE TYPE</th><th >MACHINE SUBTYPE</th><th>STATUS</th><th >COMPLETED PERCENTAGE</th><th >DELIVERY DATE</th><th >POC</th></tr>'

    all_tr = ""

    spr_mail_footer = '</table><br><hr>For more details please visit <a href="http://114.143.212.138:83/">Twin 4.0 - Order Tracking Software</a>.</div></center></body>'

    all_oee = []
    orders = query_active_projects()

    for order in orders:

        try:
            order["Total Status %"] = order["Total Status %"].replace("%","")

            total_status = str(round(float(order["Total Status %"]), 2))
        except:
            total_status = "NA"


        row = '<tr><td>' + order["RPO"] + '</td><td>' + order["Client Name"] +'</td><td>' + order["Client Type"] +'</td><td>' + order["Machine Type"] +'</td><td>' + order["Machine Subtype"] +'</td><td><b>' + order["Project Status"] +'</b></td><td><b>' + total_status +'</b></td><td>' + order["Delivery Date"]+'</td><td>' + order["POC"]+'</td></tr>'

        tr_element = row

        all_tr += tr_element


    mail_ids = ["vatsalrana14@gmail.com"]
    final_html = spr_mail_header + shift_date_heading  + table_header + all_tr + spr_mail_footer
    #mail_api.send_mail_via_smtp(constants.temporary_mail_list, "CYRONICS SOFTWARE - SPR", final_html)


    users.append("sanchita@twinengineers.com")

    mail_api.send_mail(users, "TWIN 4.0 - Daily Reports", final_html)

    # mail_api.send_mail_via_smtp(temp, "CYRONICS SOFTWARE - SPR",final_html)
    # print(final_html)



def temp_notification_keys():
    notifications = {"25_percent": 0,
                     "50_percent": 0,
                     "75_percent": 0,
                     "100_percent": 0,
                     }

    active_orders.update_many({},{"$set": {"notifications": notifications }})



def send_percent_wise_mails(data):

    header = """ \
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
          background-color: #0768a6;
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
        <div><img src="https://www.twinengineers.com/wp-content/uploads/2019/02/twin-engineers-logo.png" style="height:40px"></div></center>

        """

    greetings = "<p><br><br>Greetings from <span style='font-weight:bold;'>Twin Engineers Pvt. Ltd.</span><br><br></p>"

    status = "<p>Your RPO Number. <span style='font-weight:bold;'>" +data["RPO"] + "</span> for <span style='font-weight:bold;'>" +data["Machine Subtype"] + "</span> is in process.<br> This is to notify that the machine is <span style='font-weight:bold;'>" + str(round(data["Total Status %"], 2)) + "%</span> complete.<br><br></p>"

    help = "For more information on your order visit <a href='http://114.143.212.138:83/customer_home'>Twin 4.0 - Customer Support</a>. "

    content = header +  greetings + status + help

    customer = customers.find_one({"client_id":data["Client ID"]},{'_id': False})
    customer_email = customer["email"]

    mails_list = []
    mails_list.append(customer_email)
    mails_list.append("info_iot@cyronics.com")
    print(mails_list)

    #mail_api.send_mail(clients=constants.twin_mail_temp, subject='Twin 4.0 - Project Status',html_content=content)
    mail_api.send_mail(clients=mails_list, subject='Twin 4.0 - Project Status', html_content=content)


def send_mails_on_notes(data):
    header = """ \
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
          background-color: #0768a6;
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
        <div><img src="https://www.twinengineers.com/wp-content/uploads/2019/02/twin-engineers-logo.png" style="height:40px"></div></center>

        """

    greetings = "<p><br><br>Greetings from <span style='font-weight:bold;'>Twin Engineers Pvt. Ltd.</span><br><br></p>"

    rpo = active_orders.find_one({"RPO": data["RPO"]})
    total_status = round(float(rpo["Total Status %"].replace("%","")),2)



    if rpo["Project Status"] == 'WORK IN PROGRESS':
        status = "<p>Your RPO Number. <span style='font-weight:bold;'>" + rpo[
            "RPO"] + "</span> for <span style='font-weight:bold;'>" + rpo[
                     "Machine Subtype"] + "</span> is <span style='font-weight:bold;'>in process</span>.<br> This is to notify that the machine is <span style='font-weight:bold;'>" + str(
            total_status) + "%</span> complete.<br><br></p>"

    elif rpo["Project Status"] == 'PROJECT HALT':
        status = "<p>Your RPO Number. <span style='font-weight:bold;'>" + rpo[
            "RPO"] + "</span> for <span style='font-weight:bold;'>" + rpo[
                     "Machine Subtype"] + "</span> is <span style='font-weight:bold;'>delayed</span>.<br> This is to notify that the machine is <span style='font-weight:bold;'>" + str(
            total_status) + "%</span> complete.<br><br></p>"

    elif rpo["Project Status"] == 'READY TO DISPATCH':
        status = "<p>Your RPO Number. <span style='font-weight:bold;'>" + rpo[
            "RPO"] + "</span> for <span style='font-weight:bold;'>" + rpo[
                     "Machine Subtype"] + "</span> is <span style='font-weight:bold;'>ready to dispatch</span>.<br> This is to notify that the machine is <span style='font-weight:bold;'>" + str(
            total_status) + "%</span> complete.<br><br></p>"




    remark = "<p><span style='font-weight:bold;'>Remark: </span>" + rpo["STATUS LOG"][-1]["Additional Notes"] + "<br><br></p>"

    help = "For more information on your order visit <a href='http://114.143.212.138:83/customer_home'>Twin 4.0 - Customer Support</a>. "

    content = header + greetings + status + remark +  help

    customer = customers.find_one({"client_id": rpo["Client ID"]}, {'_id': False})
    customer_email = customer["email"]

    mails_list = []
    mails_list.append(customer_email)
    mails_list.append("info_iot@cyronics.com")
    print(mails_list)

    #mail_api.send_mail(clients=constants.twin_mail_temp, subject='Twin 4.0 - Project Status',html_content=content)
    mail_api.send_mail(clients=mails_list, subject='Twin 4.0 - Project Status', html_content=content)

    test_data = {'RPO': 'RPO-0003063', 'Project Status': 'WORK IN PROGRESS', 'Additional Notes': 'started', 'updated_by': 'Siddharth Bhonge'}


def add_new_twin_report(order_number, report_name, note, path):
    today = datetime.today()
    timestamp = today.strftime('%d/%m/%Y, %H:%M:%S')
    active_orders.update_one({"RPO":order_number},{
        '$push':{
            "reports":{
                'report_name': report_name,
                'report_note': note,
                'timestamp' : timestamp,
                'path':path
            }
        }
    },upsert = True)


def get_customers_table():
    myquery = {}
    mydoc = customers.find(myquery, {'_id': False})
    all_x = []
    for x in mydoc:
        all_x.append(x)
    return all_x


def create_new_customer(data):
    customers.insert_one(data)


def get_specific_customer(data):
    mydoc = customers.find_one({"client_id":data["client_id"]}, {'_id': False})
    return mydoc


def update_specific_customer(data):
    myquery = {"client_name": data["client_name"]}
    newvalues = {"$set": {"client_id": data["client_id"],
                          "address": data["address"],
                          "location": data["location"],
                          "poc": data["poc"],
                          "phone": data["phone"],
                          "email": data["email"]}}
    customers.update_one(myquery, newvalues)


def check_customer_id_database(data):
    mydoc = customers.find_one({"client_id":data["client_id"]}, {'_id': False})
    if mydoc is None:
        return 1
    else:
        return mydoc


def check_rpo_database(data):
    rpo = active_orders.find_one({"RPO":data["RPO"]},{'_id':False})
    if rpo is None:
        return 1
    else:
        return 2


def get_customer_details_table(data):
    mydoc = active_orders.find({"Client ID":data["client_id"]}, {'_id': False})
    all_x = []
    for x in mydoc:
        all_x.append(x)
    return all_x


def get_specific_customer_details_data(data):
    mydoc = active_orders.find_one({"RPO":data["RPO"]}, {'_id': False})
    return mydoc


def update_specific_customer_detail(data):
    myquery = {"RPO": data["RPO"]}
    newvalues = {"$set": {"Machine Type": data["Machine Type"],
                          "Machine Subtype": data["Machine Subtype"],
                          "invoice_date": data["invoice_date"],
                          "warranty": data["warranty"],
                          "warranty_date": data["warranty_date"],
                          "expiry_date": data["expiry_date"]}}
    active_orders.update_one(myquery, newvalues)


def get_specific_customer_data_for_rpo(client_id):
    mydoc = customers.find_one({"client_id":client_id}, {'_id': False})
    return mydoc

def update_customer_details_to_old_db():
    all_customers = get_customers_table()

    for customer in all_customers:
        to_update = {}
        to_update["address"] = customer["address"]
        to_update["phone"] = customer["phone"]
        to_update["POC"] = customer["poc"]
        to_update["Client ID"] = customer["client_id"]
        to_update["location"] = customer["location"]
        to_update["email"] = customer["email"]

        active_orders.update_one({"Client Name" : customer["client_name"]},{"$set" : to_update})

    print("UPDATE COMPLETE")

if __name__ == "__main__":
    pass
        # temp_notification_keys()
