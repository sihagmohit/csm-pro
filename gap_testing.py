import json

import pymongo


myclient1 = pymongo.MongoClient("mongodb://localhost:27017/")
# myclient1  = pymongo.MongoClient("mongodb://cyronics:cipl1234@35.184.20.184:27017/Anzen_1_0?authSource=Anzen_1_0")
mydb1 = myclient1['fie_data']
part_production_plan = mydb1["part_production_plan"]
wip = mydb1['wip']

mydb2 = myclient1['test1']
gap = mydb2['gap']

gap.drop()
def alogrith():
    # f = open("/home/amit-pc/Documents/software/fie/MachineUpload.json", 'r')
    # data = json.load(f)
    # check = gap.insert(data["machinery_components"])
    # # writedata = data['data']
    # # print(data)
    # bm = {'total': 1}
    data = {"machinery_components": [
        {
            "serial_no": 1,
            "bom_level": 1,
            "machine_name": "Auto Broaching Machine Model:PRO-BROACH+",
            "machine_code": "PRO-BROACH (PLUS)",
            "base_units": "No.",
            "bom_qty": 0,
            "avl_qty": 7,
            "machinery_components": [
                {
                    "bom_level": 2,
                    "assembly_name": "Broaching Machine-Auto",
                    "base_units": "No.",
                    "bom_qty": 1,
                    "avl_qty": 8
                },
                {
                    "bom_level": 2,
                    "assembly_name": "V  NOTCH BROACH",
                    "base_units": "No.",
                    "bom_qty": 1,
                    "avl_qty": 4
                },
                {
                    "bom_level": 2,
                    "assembly_name": "IT30 AUTO-STD-497 S/C",
                    "base_units": "No.",
                    "bom_qty": 1,
                    "avl_qty": 0,
                    "machinery_components": [{
                                "bom_level": 3,
                                "spare_name": "B-3000 H/O,250/TWIN MAIN NUT HANDEL",
                                "base_units": "No.",
                                "bom_qty": 4,
                                "avl_qty": 56
                            },
                            {
                                "bom_level": 3,
                                "spare_name": "B-3000 O MAIN LEVER (FIN)",
                                "base_units": "No.",
                                "bom_qty": 1,
                                "avl_qty": -10,
                                "machinery_components": [
                                    {
                                        "bom_level": 4,
                                        "spare_name": "B-3000 O MAIN LEVER",
                                        "base_units": "No.",
                                        "bom_qty": 1,
                                        "avl_qty": 0,
                                        "machinery_components": [
                                            {
                                                "bom_level": 5,
                                                "spare_name": "B-3000 O MAIN LEVER [WELD]",
                                                "base_units": "No.",
                                                "bom_qty": 1,
                                                "avl_qty": 47,
                                                "machinery_components": [
                                                    {
                                                        "bom_level": 6,
                                                        "spare_name": "B-3000 O MAIN LEVER BLOCK",
                                                        "base_units": "No.",
                                                        "bom_qty": 1,
                                                        "avl_qty": 3,
                                                        "machinery_components": [
                                                            {
                                                                "bom_level": 7,
                                                                "spare_name": "B-3000 O MAIN LEVER BLOCK [STEEL CAST]",
                                                                "base_units": "No.",
                                                                "bom_qty": 1,
                                                                "avl_qty": 0
                                                            }
                                                        ]
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            },
                        {"bom_level": 3,
                                "spare_name": "B-3000 O11111 MAIN LEVER (FIN)",
                                "base_units": "No.",
                                "bom_qty": 1,
                                "avl_qty": -10,
                                "machinery_components": [
                                    {
                                        "bom_level": 4,
                                        "spare_name": "B-3000 O MAIN LEVER",
                                        "base_units": "No.",
                                        "bom_qty": 1,
                                        "avl_qty": 0,
                                    },{
                                        "bom_level": 4,
                                        "spare_name": "B-3000 O MAIN LEVER",
                                        "base_units": "No.",
                                        "bom_qty": 1,
                                        "avl_qty": 0,
                                    }]
                                }]
                }]
        }]
    }


    # def iterdict(data):
    #     print(data)




    bm = {'total': 0}
    def iterdict2(data):
        for i in range(len(data)):
            # print(data[i])
            if 'machinery_components' in data[i]:
                if type(data[i]['machinery_components']) == list:
                    # print(len(data[i]['machinery_components']) , "BOM :: " , data[i]['bom_qty'])
                    # print("+++++++++++++++++++++++++++++++++++++++++++++++")
                    # print("SECOND LOOP", data[i]['bom_qty'])
                    # main_total = data[i]['bom_qty']
                    for j in data[i]['machinery_components']:
                        # bm['total'] *= main_total
                        if 'machinery_components' in data[i]['machinery_components']:
                            if type(j['machinery_components']) == list:
                                iterdict(j['machinery_components'])
                        if j['bom_level'] == 3:
                            # print("spare_name",j["spare_name"])
                            # print("TOTAL1 ", bm['total'])
                            # print("THIRD LOOP", j['bom_qty'])
                            # print(j['bom_qty'])
                            # print("bom_level",j['bom_level'])
                            print("s")
                            bm['total'] += j['bom_qty']
                            # print("TOTAL ", bm['total'])
                        else:
                            x =[]
                            print("spare_name_else", j["spare_name"])
                            print("bom_level", j['bom_level'])
                            x.append(j['bom_level'])
                            if x[0] == 4:
                                print("sa")
                            else:
                                print("das")

                            # bm['total'] += j['bom_qty']
                            # print("TOTAL ", bm['total'])

                    iterdict2(data[i]['machinery_components'])
                    # iterdict2(data[i]['machinery_components'])
    assembly = []

    def iterdict(data):
        for i in range(len(data)):
            if 'machinery_components' in data[i]:
                if type(data[i]['machinery_components']) == list:
                    iterdict2(data[i]['machinery_components'])
                    for j in data[i]['machinery_components']:
                        try:
                            for k in j['machinery_components']:
                                if 'machinery_components' not in k:
                                    # only level 3
                                    # print("bvgvb")
                                    # new = 0
                                    # new += k['bom_qty']
                                    # print("new",new)
                                    assembly.append(
                                        {'machine_name': data[i]['machine_name'],
                                                         'spare_name':k['spare_name'],'bom_qty': k['bom_qty']})
                                else:
                                    # print("last",bm['total'])
                                    assembly.append(
                                        {'machine_name': data[i]['machine_name'],
                                                         'spare_name':k['spare_name'],'bom_qty': bm['total']})
                                    bm['total'] = 0
                                    # iterdict2(data[i]['machinery_components'])

                        except:
                            pass


        print("ASSEMBLY ..", assembly)

    iterdict(data['machinery_components'])

alogrith()


# def check_sales_data():
#         gap.drop()
#         records = []
#         parts_data = []
#         check = part_production_plan.find({}, {"_id": False}).distinct("assembly_name")
#         # print(check)
#         for x in range(0,len(check)):
#             data = part_production_plan.find({"assembly_name":check[x]}, {"_id": False})  # .limit(100)
#             for index in data:
#                 get_data = {}
#                 get_data["parts"] = index['assembly_name']
#                 get_data["live_sales"] = index['total_required']
#                 get_data["production_plan"] = 0
#                 get_data["actual_required"] = get_data["production_plan"] + get_data["live_sales"]
#                 get_data["wip_qty"] = 0
#                 get_data["finish_stock"] = 0
#                 get_data["issued_qty"] = 0
#                 get_data["supplier_list"] =[]
#                 # for supllier_data in wip_data:
#
#                 # print(get_data)
#                 arr = []
#                 wip_data = wip.find({"part_name": index['assembly_name']},
#                                     {"_id": False})  # .limit(100) index['assembly_name'] # index["assembly_name"]
#                 for list_data in wip_data:
#
#                     wip_details = str(list_data["supplier_name"]) + ':' + str(list_data['quantity'])
#                     get_data["supplier_list"].append(wip_details)
#
#                     # if list_data['supplier_name'] == "PB FINISH" or list_data['supplier_name'] == "PB ASSEMBLY":
#                     #     pass
#                     # else:
#                     wip_temp = wip.aggregate([{"$match": {"part_name": index['assembly_name']}},
#                                               {"$group": {
#                                                   "_id": index['assembly_name'],
#                                                   "sum_wip": {"$sum": {
#                                                       "$cond": [
#                                                           {
#                                                               "$in": [
#                                                                   "$supplier_name",
#                                                                   [
#                                                                       "PB FINISH",
#                                                                       "PB ASSEMBLY"
#                                                                   ]
#                                                               ]
#                                                           },
#                                                           0,
#                                                           "$quantity"
#                                                       ],
#                                                   }
#
#                                                       # {"$toInt": "$quantity"}#
#                                                   },
#                                                   "sum_finish": {"$sum": {
#                                                       "$cond": [
#                                                           {
#                                                               "$in": [
#                                                                   "$supplier_name",
#                                                                   [
#                                                                       "PB FINISH"
#                                                                   ]
#                                                               ]
#                                                           },
#                                                           "$quantity",
#                                                           0,
#                                                       ],
#                                                   }
#
#                                                       # {"$toInt": "$quantity"}#
#                                                   },
#                                                   "sum_assembly": {"$sum": {
#                                                       "$cond": [
#                                                           {
#                                                               "$in": [
#                                                                   "$supplier_name",
#                                                                   [
#                                                                       "PB ASSEMBLY"
#                                                                   ]
#                                                               ]
#                                                           },
#                                                           "$quantity",
#                                                           0,
#                                                       ],
#                                                   }
#
#                                                       # {"$toInt": "$quantity"}#
#                                                   }
#                                                   # {"$toInt": "$quantity"}#
#                                               }}
#                                               ])
#
#                     for i in wip_temp:
#                         # print(i)
#                         get_data["wip_qty"] = i["sum_wip"]
#                         get_data["finish_stock"] = i["sum_finish"]
#                         get_data["issued_qty"] = i["sum_assembly"]
#
#                 get_data["final_order"] = get_data["actual_required"] - (get_data["wip_qty"]) - (get_data[
#                     "finish_stock"]) - (get_data["issued_qty"])
#                 print(get_data)
#                 records.append(get_data)
#
#                 if index['assembly_name'] not in parts_data:
#                     # print("insetion")
#                     parts_data.append(index['assembly_name'])
#                     print(get_data)
#                     gap.insert_one(get_data)  # insert data in mobgodb
#                 else:
#                     gap.update_one({"parts": index['assembly_name']},
#                                             {"$inc": {"live_sales": get_data[
#                                                 'live_sales']}})  # update the mongodb data which are repaet
#                     gap.update_one({"parts": index['assembly_name']},
#                                             {"$inc": {
#                                                 "actual_required": get_data["production_plan"] + get_data['live_sales']}})
#
#                     update_data = gap.find({"parts": index['assembly_name']}, {"_id": 0})
#                     for change in update_data:
#                         gap.update_one({"parts": index['assembly_name']},
#                                                 {"$set": {"final_order": change["actual_required"] - change["wip_qty"] -
#                                                                          change["finish_stock"] - change["issued_qty"]}})
#
#
#
#
#         #         for i in wip_temp:
#         #             arr.append(i)
#         #             # print(i)
#         #     xyz =[dict(t) for t in {tuple(d.items()) for d in arr}]
#         #     for i in xyz:
#         #         # print(i["sum_wip"])
#         #         get_data["wip_qty"] = i["sum_wip"]
#         #         get_data["finish_stock"] = i["sum_finish"]
#         #         get_data["issued_qty"] = i["sum_assembly"]
#         #         get_data["final_order"] = get_data["actual_required"] - get_data["wip_qty"] - get_data[
#         #             "finish_stock"] - get_data["issued_qty"]
#         #     print(get_data)
#         #     records.append(get_data)
#         # gap.insert_one(records)
#             #
#             #
#             # if index['assembly_name'] not in parts_data:
#             #     # print("insetion")
#             #     parts_data.append(index['assembly_name'])
#             #     print(get_data)
#             #     gap.insert_one(get_data)  # insert data in mobgodb
#             # else:
#             #     gap.update_one({"parts": index['assembly_name']},
#             #                             {"$inc": {"live_sales": get_data[
#             #                                 'live_sales']}})  # update the mongodb data which are repaet
#             #     gap.update_one({"parts": index['assembly_name']},
#             #                             {"$inc": {
#             #                                 "actual_required": get_data["production_plan"] + get_data['live_sales']}})
#             #
#             #     update_data = gap.find({"parts": index['assembly_name']}, {"_id": 0})
#             #     for change in update_data:
#             #         gap.update_one({"parts": index['assembly_name']},
#             #                                 {"$set": {"final_order": change["actual_required"] - change["wip_qty"] -
#             #                                                          change["finish_stock"] - change["issued_qty"]}})
#
#     # try:
#     #     reset_data_gap.drop()
#     #     data_coll = gap_analysis.find({},{"_id": False}) # reset collection create
#     #     for i in data_coll:
#     #         reset_data_gap.insert(i)
#     # except:
#     #     pass
#     # record = {"timestamp": datetime.now(), "collection_name": "gap_analysis", "status": "Failed"}
#     # sync_log.insert(record)
# check_sales_data()