import requests
import json
from pprint import pprint


# ----------------------------- sales_order_data ----------------------------------

# f = open('/home/amit-pc/software/fie/json_file/sales_order.json')
# data = json.load(f)
#
# # print(data)
#
# url = 'http://0.0.0.0:5000/sales_order_data'
# # url = 'http://34.125.50.203/sales_order_data'
# # pprint(data)
#
# x = requests.post(url, json = data)
#
# print(x.text)

# ---------------------stocks_data------------------------------------
#
# f = open('/home/amit-pc/software/fie/json_file/stocks.json')
# data = json.load(f)
#
# # print(data)
#
# url = 'http://0.0.0.0:5000/stocks_data'
# # pprint(data)
#
# x = requests.post(url, json = data)
#
# print(x.text)



# -------------------------  vendor_details_data  ----------------------------------

# f = open('/home/amit-pc/software/fie/json_file/vendors.json')
# data = json.load(f)
#
# # print(data)
#
# url = 'http://0.0.0.0:5000/vendor_details_data'
# # pprint(data)
#
# x = requests.post(url, json = data)
#
# print(x.text)

# -------------------------  wip_stocks_data  ----------------------------------

# f = open('/home/amit-pc/software/fie/json_file/wip.json')
# data = json.load(f)
#
# # print(data)
#
# url = 'http://0.0.0.0:5000/wip_stocks_data'
# # pprint(data)
#
# x = requests.post(url, json = data)
#
# print(x.text)


# ------------------------------  machinery_components ---------------------------------

f = open('/home/amit-pc/Documents/software/fie/MachineUpload.json')
data = json.load(f)

# print(data)

url = 'http://0.0.0.0:5000/machinery_components_data'
# pprint(data)new_collection
# url = 'http://34.125.50.203/machinery_components_data'

x = requests.post(url, json = data)

print(x.text)


#
# for i in range(1, 7):
#     for j in range(1, i + 1):
#         if (j == 1 or j == i):
#             print(1, end="")
#         else:
#             print(0, end="")
#     print('\n', end="")

#
# input_list = [[10,11],[10.30,12.30],[13,17],[14,16]]
#
# for i in range(len(input_list)):
#     try:
#         t = input_list[i + 1]
#         for j in range(len(input_list[i])):
#             if input_list[i][0] < t[j] and t[j] < input_list[i][1]:
#                 print("LIES")
#                 input_list.pop(i + 1)
#             else:
#                 print("NOT LIES")
#     except:
#             pass
#
# print(input_list)


# dict_any = {"asd": 14, "xyz": 20, "er": 30}
#
# new_dict = {}
#
# for i in dict_any:
#     x = dict_any[i]
#     # print(x)
#     new_dict[x] = i
#
# print(new_dict)