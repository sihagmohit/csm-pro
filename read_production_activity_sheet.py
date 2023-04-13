import pandas
import numpy as np
import pymongo
import json
from pprint import pprint
myclient1 = pymongo.MongoClient("mongodb://localhost:27017/")
mydb1 = myclient1['TWIN']
production_activity_presets = mydb1['activity_presets']

def read_mmd():
    # -------------------------------------- MMD ----------------------------------------------------------
    excel_data_df = pandas.read_excel('pr_activities.xlsx', sheet_name='MMD',index_col=None ,skiprows=[0])
    excel_data_df = excel_data_df.replace(np.nan, 0.0, regex=True)
    excel_data_df.columns = excel_data_df.columns.str.replace('\n','')
    data_dict = json.loads(excel_data_df.to_json(orient='records'))
    # -----------------------------------------------------------------------------------------------------
    # pprint(data_dict)

    all_data = []
    for data in data_dict:


        temp = {}
        temp["Domain"] = "Production"
        temp["Machine Type"] = "MMD"
        temp["Machine sub_type"] = data["Machine Type"]
        temp["Activity Type"] = "Assembly"
        temp["sub_type"] = 'Mechanical Assembly'
        temp["man_days"] = data['Mechanical Assembly']
        production_activity_presets.insert_one(temp)


        temp = {}
        temp["Domain"] = "Production"
        temp["Machine Type"] = "MMD"
        temp["Machine sub_type"] = data["Machine Type"]
        temp["Activity Type"] = "Assembly"
        temp["sub_type"] = 'Layout, Main Panel Wiring,Operator Panel Wiring'
        temp["man_days"] = data['Layout, Main Panel Wiring,Operator Panel Wiring']
        production_activity_presets.insert_one(temp)

        temp = {}
        temp["Domain"] = "Production"
        temp["Machine Type"] = "MMD"
        temp["Machine sub_type"] = data["Machine Type"]
        temp["Activity Type"] = "Trial"
        temp["sub_type"] = 'Machine Trial'
        temp["man_days"] = data['Machine Trial']
        production_activity_presets.insert_one(temp)

        temp = {}
        temp["Domain"] = "Production"
        temp["Machine Type"] = "MMD"
        temp["Machine sub_type"] = data["Machine Type"]
        temp["Activity Type"] = "Trial"
        temp["sub_type"] = 'Machine wiring,I/O Checking,Labeling,Parameter'
        temp["man_days"] = data['Machine wiring,I/O Checking,Labeling,Parameter Setting']
        production_activity_presets.insert_one(temp)

        temp = {}
        temp["Domain"] = "Production"
        temp["Machine Type"] = "MMD"
        temp["Machine sub_type"] = data["Machine Type"]
        temp["Activity Type"] = "Customer Pre Dispatch Inspection"
        temp["sub_type"] = 'Electrical'
        temp["man_days"] = data['Electrical']
        production_activity_presets.insert_one(temp)

        temp = {}
        temp["Domain"] = "Production"
        temp["Machine Type"] = "MMD"
        temp["Machine sub_type"] = data["Machine Type"]
        temp["Activity Type"] = "Customer Pre Dispatch Inspection"
        temp["sub_type"] = 'Mechanical'
        temp["man_days"] = data['Mechanical']
        production_activity_presets.insert_one(temp)

        temp = {}
        temp["Domain"] = "Production"
        temp["Machine Type"] = "MMD"
        temp["Machine sub_type"] = data["Machine Type"]
        temp["Activity Type"] = "MOMPoints, MachineCleaning & Dispatch activities"
        temp["sub_type"] = 'Electrical'
        temp["man_days"] = data['Electrical.1']
        production_activity_presets.insert_one(temp)

        temp = {}
        temp["Domain"] = "Production"
        temp["Machine Type"] = "MMD"
        temp["Machine sub_type"] = data["Machine Type"]
        temp["Activity Type"] = "MOMPoints, MachineCleaning & Dispatch activities"
        temp["sub_type"] = 'Mechanical'
        temp["man_days"] = data['Mechanical.1']
        production_activity_presets.insert_one(temp)


def read_filling():
    # -------------------------------------- Filling ----------------------------------------------------------
    excel_data_df = pandas.read_excel('pr_activities.xlsx', sheet_name='Filling', index_col=None, skiprows=[0])
    excel_data_df = excel_data_df.replace(np.nan, 0.0, regex=True)
    excel_data_df.columns = excel_data_df.columns.str.replace('\n', '')
    data_dict = json.loads(excel_data_df.to_json(orient='records'))
    # -----------------------------------------------------------------------------------------------------
    # pprint(data_dict)

    all_data = []
    for data in data_dict:
        temp = {}
        temp["Domain"] = "Production"
        temp["Machine Type"] = "Filling"
        temp["Machine sub_type"] = data["Machine Type"]
        temp["Activity Type"] = "Assembly"
        temp["sub_type"] = 'Mechanical Assembly'
        temp["man_days"] = data['Mechanical Assembly']
        production_activity_presets.insert_one(temp)

        temp = {}
        temp["Domain"] = "Production"
        temp["Machine Type"] = "Filling"
        temp["Machine sub_type"] = data["Machine Type"]
        temp["Activity Type"] = "Assembly"
        temp["sub_type"] = 'Layout, Main Panel Wiring,Operator Panel Wiring'
        temp["man_days"] = data['Layout, Main Panel Wiring,Operator Panel Wiring']
        production_activity_presets.insert_one(temp)

        temp = {}
        temp["Domain"] = "Production"
        temp["Machine Type"] = "Filling"
        temp["Machine sub_type"] = data["Machine Type"]
        temp["Activity Type"] = "Trial"
        temp["sub_type"] = 'Machine Trial'
        temp["man_days"] = data['Machine Trial']
        production_activity_presets.insert_one(temp)

        temp = {}
        temp["Domain"] = "Production"
        temp["Machine Type"] = "Filling"
        temp["Machine sub_type"] = data["Machine Type"]
        temp["Activity Type"] = "Trial"
        temp["sub_type"] = 'Machine wiring,I/O Checking,Labeling,Parameter'
        temp["man_days"] = data['Machine wiring,I/O Checking,Labeling,Parameter Setting']
        production_activity_presets.insert_one(temp)

        temp = {}
        temp["Domain"] = "Production"
        temp["Machine Type"] = "Filling"
        temp["Machine sub_type"] = data["Machine Type"]
        temp["Activity Type"] = "Customer Pre Dispatch Inspection"
        temp["sub_type"] = 'Electrical'
        temp["man_days"] = data['Electrical']
        production_activity_presets.insert_one(temp)

        temp = {}
        temp["Domain"] = "Production"
        temp["Machine Type"] = "Filling"
        temp["Machine sub_type"] = data["Machine Type"]
        temp["Activity Type"] = "Customer Pre Dispatch Inspection"
        temp["sub_type"] = 'Mechanical'
        temp["man_days"] = data['Mechanical']
        production_activity_presets.insert_one(temp)

        temp = {}
        temp["Domain"] = "Production"
        temp["Machine Type"] = "Filling"
        temp["Machine sub_type"] = data["Machine Type"]
        temp["Activity Type"] = "MOMPoints, MachineCleaning & Dispatch activities"
        temp["sub_type"] = 'Electrical'
        temp["man_days"] = data['Electrical.1']
        production_activity_presets.insert_one(temp)

        temp = {}
        temp["Domain"] = "Production"
        temp["Machine Type"] = "Filling"
        temp["Machine sub_type"] = data["Machine Type"]
        temp["Activity Type"] = "MOMPoints, MachineCleaning & Dispatch activities"
        temp["sub_type"] = 'Mechanical'
        temp["man_days"] = data['Mechanical.1']
        production_activity_presets.insert_one(temp)


def read_robotics():
    # -------------------------------------- Robotics ----------------------------------------------------------
    excel_data_df = pandas.read_excel('pr_activities.xlsx', sheet_name='Robotics', index_col=None, skiprows=[0])
    excel_data_df = excel_data_df.replace(np.nan, 0.0, regex=True)
    excel_data_df.columns = excel_data_df.columns.str.replace('\n', '')
    data_dict = json.loads(excel_data_df.to_json(orient='records'))
    # -----------------------------------------------------------------------------------------------------
    # pprint(data_dict)

    all_data = []
    for data in data_dict:
        temp = {}
        temp["Domain"] = "Production"
        temp["Machine Type"] = "Robotics"
        temp["Machine sub_type"] = data["Machine Type"]
        temp["Activity Type"] = "Assembly"
        temp["sub_type"] = 'Mechanical Assembly'
        temp["man_days"] = data['Mechanical Assembly']
        production_activity_presets.insert_one(temp)

        temp = {}
        temp["Domain"] = "Production"
        temp["Machine Type"] = "Robotics"
        temp["Machine sub_type"] = data["Machine Type"]
        temp["Activity Type"] = "Assembly"
        temp["sub_type"] = 'Layout, Main Panel Wiring,Operator Panel Wiring'
        temp["man_days"] = data['Layout, Main Panel Wiring,Operator Panel Wiring']
        production_activity_presets.insert_one(temp)

        temp = {}
        temp["Domain"] = "Production"
        temp["Machine Type"] = "Robotics"
        temp["Machine sub_type"] = data["Machine Type"]
        temp["Activity Type"] = "Trial"
        temp["sub_type"] = 'Machine Trial'
        temp["man_days"] = data['Machine Trial']
        production_activity_presets.insert_one(temp)

        temp = {}
        temp["Domain"] = "Production"
        temp["Machine Type"] = "Robotics"
        temp["Machine sub_type"] = data["Machine Type"]
        temp["Activity Type"] = "Trial"
        temp["sub_type"] = 'Machine wiring,I/O Checking,Labeling,Parameter'
        temp["man_days"] = data['Machine wiring,I/O Checking,Labeling,Parameter Setting']
        production_activity_presets.insert_one(temp)

        temp = {}
        temp["Domain"] = "Production"
        temp["Machine Type"] = "Robotics"
        temp["Machine sub_type"] = data["Machine Type"]
        temp["Activity Type"] = "Customer Pre Dispatch Inspection"
        temp["sub_type"] = 'Electrical'
        temp["man_days"] = data['Electrical']
        production_activity_presets.insert_one(temp)

        temp = {}
        temp["Domain"] = "Production"
        temp["Machine Type"] = "Robotics"
        temp["Machine sub_type"] = data["Machine Type"]
        temp["Activity Type"] = "Customer Pre Dispatch Inspection"
        temp["sub_type"] = 'Mechanical'
        temp["man_days"] = data['Mechanical']
        production_activity_presets.insert_one(temp)

        temp = {}
        temp["Domain"] = "Production"
        temp["Machine Type"] = "Robotics"
        temp["Machine sub_type"] = data["Machine Type"]
        temp["Activity Type"] = "MOMPoints, MachineCleaning & Dispatch activities"
        temp["sub_type"] = 'Electrical'
        temp["man_days"] = data['Electrical.1']
        production_activity_presets.insert_one(temp)

        temp = {}
        temp["Domain"] = "Production"
        temp["Machine Type"] = "Robotics"
        temp["Machine sub_type"] = data["Machine Type"]
        temp["Activity Type"] = "MOMPoints, MachineCleaning & Dispatch activities"
        temp["sub_type"] = 'Mechanical'
        temp["man_days"] = data['Mechanical.1']
        production_activity_presets.insert_one(temp)



def read_SPM():
    # -------------------------------------- MMD ----------------------------------------------------------
    excel_data_df = pandas.read_excel('pr_activities.xlsx', sheet_name='SPM', index_col=None, skiprows=[0])
    excel_data_df = excel_data_df.replace(np.nan, 0.0, regex=True)
    excel_data_df.columns = excel_data_df.columns.str.replace('\n', '')
    data_dict = json.loads(excel_data_df.to_json(orient='records'))
    # -----------------------------------------------------------------------------------------------------
    # pprint(data_dict)

    all_data = []
    for data in data_dict:
        temp = {}
        temp["Domain"] = "Production"
        temp["Machine Type"] = "SPM"
        temp["Machine sub_type"] = data["Machine Type"]
        temp["Activity Type"] = "Assembly"
        temp["sub_type"] = 'Mechanical Assembly'
        temp["man_days"] = data['Mechanical Assembly']
        production_activity_presets.insert_one(temp)

        temp = {}
        temp["Domain"] = "Production"
        temp["Machine Type"] = "SPM"
        temp["Machine sub_type"] = data["Machine Type"]
        temp["Activity Type"] = "Assembly"
        temp["sub_type"] = 'Layout, Main Panel Wiring,Operator Panel Wiring'
        temp["man_days"] = data['Layout, Main Panel Wiring,Operator Panel Wiring']
        production_activity_presets.insert_one(temp)

        temp = {}
        temp["Domain"] = "Production"
        temp["Machine Type"] = "SPM"
        temp["Machine sub_type"] = data["Machine Type"]
        temp["Activity Type"] = "Trial"
        temp["sub_type"] = 'Machine Trial'
        temp["man_days"] = data['Machine Trial']
        production_activity_presets.insert_one(temp)

        temp = {}
        temp["Domain"] = "Production"
        temp["Machine Type"] = "SPM"
        temp["Machine sub_type"] = data["Machine Type"]
        temp["Activity Type"] = "Trial"
        temp["sub_type"] = 'Machine wiring,I/O Checking,Labeling,Parameter'
        temp["man_days"] = data['Machine wiring,I/O Checking,Labeling,Parameter Setting']
        production_activity_presets.insert_one(temp)

        temp = {}
        temp["Domain"] = "Production"
        temp["Machine Type"] = "SPM"
        temp["Machine sub_type"] = data["Machine Type"]
        temp["Activity Type"] = "Customer Pre Dispatch Inspection"
        temp["sub_type"] = 'Electrical'
        temp["man_days"] = data['Electrical']
        production_activity_presets.insert_one(temp)

        temp = {}
        temp["Domain"] = "Production"
        temp["Machine Type"] = "SPM"
        temp["Machine sub_type"] = data["Machine Type"]
        temp["Activity Type"] = "Customer Pre Dispatch Inspection"
        temp["sub_type"] = 'Mechanical'
        temp["man_days"] = data['Mechanical']
        production_activity_presets.insert_one(temp)

        temp = {}
        temp["Domain"] = "Production"
        temp["Machine Type"] = "SPM"
        temp["Machine sub_type"] = data["Machine Type"]
        temp["Activity Type"] = "MOMPoints, MachineCleaning & Dispatch activities"
        temp["sub_type"] = 'Electrical'
        temp["man_days"] = data['Electrical.1']
        production_activity_presets.insert_one(temp)

        temp = {}
        temp["Domain"] = "Production"
        temp["Machine Type"] = "SPM"
        temp["Machine sub_type"] = data["Machine Type"]
        temp["Activity Type"] = "MOMPoints, MachineCleaning & Dispatch activities"
        temp["sub_type"] = 'Mechanical'
        temp["man_days"] = data['Mechanical.1']
        production_activity_presets.insert_one(temp)

read_mmd()
read_filling()
read_robotics()
read_SPM()










