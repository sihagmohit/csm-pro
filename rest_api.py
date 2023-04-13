import new_database_operations
import constants
import requests


def send_active_production_orders():
    active_orders = new_database_operations.get_active_production_orders()

    for record in active_orders:
        try:
            record["PLANNED_START"] = record["PLANNED_START"].strftime(constants.time_format)
            record["PLANNED_STOP"] = record["PLANNED_STOP"].strftime(constants.time_format)
            record["ACTUAL_START"] = record["ACTUAL_START"].strftime(constants.time_format)
            record["ACTUAL_STOP"] = record["ACTUAL_STOP"].strftime(constants.time_format)
        except:
            pass

    # -------------------------------------------------------------
    #                 POST TO CBM - ACTIVE POS
    # -------------------------------------------------------------
    # API_ENDPOINT = "http://15.207.74.145/POST_PO"   #ACTIVATE BEFOR PUSH

    API_ENDPOINT = constants.cbm_api_endpoint + "/POST_PO"  # LOCAL
    print("API ENDPOINT FOR ACTIVE ORDERS", API_ENDPOINT)
    # res = requests.post(url=API_ENDPOINT, json=active_orders)
    print("====== Sent Planned Production Orders ======")
    # print(res.text)
    print("============================================")


def send_planned_production_orders():


    active_orders = new_database_operations.get_planned_production_orders()

    for record in active_orders:
        try:
            record["PLANNED_START"] = record["PLANNED_START"].strftime(constants.time_format)
            record["PLANNED_STOP"] = record["PLANNED_STOP"].strftime(constants.time_format)
            record["ACTUAL_START"] = record["ACTUAL_START"].strftime(constants.time_format)
            record["ACTUAL_STOP"] = record["ACTUAL_STOP"].strftime(constants.time_format)
        except:
            pass

    API_ENDPOINT = constants.trace_api_endpoint + "/POST_PO"  # LOCAL
    print("API ENDPOINT FOR ACTIVE ORDERS", API_ENDPOINT)
    res = requests.post(url=API_ENDPOINT, json=active_orders)
    print("====== Sent Planned Production Orders ======")
    print(res.text)
    print("============================================")