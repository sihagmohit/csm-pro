import pandas as pd
import numpy as np
import pymongo
import os
import sys

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["TWIN"]
activity_presets = mydb['activity_presets']

df = pd.read_excel('preset_database.xlsx', sheet_name='Sheet1',index_col=None ,skiprows=[])
from pprint import pprint


df = df.fillna(method='ffill')

df = df.replace(np.nan, '', regex=True)
df = df.replace('\n','', regex=True)

pd.set_option("display.max_rows", None, "display.max_columns", None)

database_dict = df.to_dict(orient='record')

#pprint(database_dict)
new_presets = []

for temp in database_dict:
    preset = {}
    preset["Domain"] = temp["Milestone"]
    preset["Machine Type"] = temp["Machine Type"]
    preset["Machine sub_type"] = temp["Machine Subtype"]
    preset["Activity Type"] = temp["Activity Type"]
    preset["sub_type"] = temp["Activity Subtype"]
    preset["man_days"] = temp["Mandays"]
    pprint(preset)
    print("----------------------------------------------------------------------")
    new_presets.append(preset)

activity_presets.drop()
activity_presets.insert_many(new_presets)

print(str(len(new_presets)) + " new activities imported successfully.")
print("DATABASE UPDATED.")

