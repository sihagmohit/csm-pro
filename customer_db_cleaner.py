import pandas as pd
import numpy as np
import pymongo
import os
import sys
import json

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["TWIN"]
customers = mydb['customers']

df = pd.read_excel('customer_database.xlsx', sheet_name='Sheet1',index_col=None ,skiprows=[])
df = df.replace(np.nan, '', regex=True)
df = df.replace('\n','', regex=True)

print(df.to_json(orient='records'))




data_dict = json.loads(df.to_json(orient='records'))

counter= 1
for a in data_dict:
    length = len(str(counter))
    c_id = ("0" * (4 - length)) + str(counter)
    a["client_id"] = c_id
    counter+=1



print(data_dict)
customers.insert_many(data_dict)