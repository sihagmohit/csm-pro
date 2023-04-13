import json

import pymongo


myclient1 = pymongo.MongoClient("mongodb://localhost:27017/")
# myclient1  = pymongo.MongoClient("mongodb://cyronics:cipl1234@35.184.20.184:27017/Anzen_1_0?authSource=Anzen_1_0")
mydb1 = myclient1['fie_data']
part_production_plan = mydb1["part_production_plan"]
wip = mydb1['wip']
machinery_components = mydb1['machinery_components']
mydb2 = myclient1['test1']
gap = mydb2['gap']

gap.drop()


def algo():
    data1 = [{'Machine': 'BRINELL HARDNESS TESTER B-3000 E', 'quantity': '7'}]
    data = {}
    for i in range(0, len(data1)):
        # print()
        uniqe_data = machinery_components.find({'machine_name': data1[i]["Machine"]}, {'_id': 0})
        bm = {'total': 0}
        for doc in uniqe_data:
            data["machinery_components"] = [doc]
    print(data)

    def iterdict2(data):
        for i in range(len(data)):
            # print(data[i])
            if 'machinery_components' in data[i]:
                if type(data[i]['machinery_components']) == list:
                    # print(len(data[i]['machinery_components']) , "BOM :: " , data[i]['bom_qty'])
                    # print("+++++++++++++++++++++++++++++++++++++++++++++++")
                    print("SECOND LOOP", data[i]['bom_qty'])
                    main_total = data[i]['bom_qty']
                    for j in data[i]['machinery_components']:
                        bm['total'] *= main_total
                        if 'machinery_components' in data[i]['machinery_components']:
                            if type(j['machinery_components']) == list:
                                iterdict(j['machinery_components'])
                        print("THIRD LOOP", j['bom_qty'])
                        print(j['bom_qty'])
                        if not 'spare_name':
                            bm['total'] = 0
                        else:
                            bm['total'] += j['bom_qty']
                        # print("TOTAL 2 ", bm['total'])
                    iterdict2(data[i]['machinery_components'])

    assembly = []

    def iterdict(data):
        for i in range(len(data)):

            if 'machinery_components' in data[i]:
                if type(data[i]['machinery_components']) == list:
                    # print(len(data[i]['machinery_components']) , "BOM :: " , data[i]['bom_qty'])
                    # print("+++++++++++++++++++++++++++++++++++++++++++++++")
                    print("Initial Val :: ", data[i]['bom_qty'])
                    main_total = data[i]['bom_qty']
                    iterdict2(data[i]['machinery_components'])
                    # print("TOTAL 1 ", bm['total'])
                    for j in data[i]['machinery_components']:
                        bm['total'] += main_total
                        #     print(j)
                        #     print(j['bom_qty'])
                        bm['total'] *= j['bom_qty']
                        # print("TOTAL 1" ,bm['total'] )
                        try:
                            assembly.append({'machine_name': data[i]['machine_name'],
                                             'assembly_name': j['assembly_name'],
                                             'spare_name': j['machinery_components'][0]['spare_name'],
                                             'bom_qty': bm['total']})
                            bm['total'] = 1
                        except:
                            pass
                    #

        print("ASSEMBLY ..", assembly)

    iterdict(data['machinery_components'])
algo()

sum_sales_order = gap_calculator.aggregate([{"$match": {"primary_item": "ECCENTRIC PIN"}},
                                            {"$group": {
                                                "_id": "",
                                                "machine": "",
                                                "parts": value,
                                                "live_sales": "$live_sales",
                                                "production": "$production",
                                                "$actual_required": {"$sum": {"$toInt": "$actual_required"}},
                                                "wip_qty": {"$sum": {"$toInt": "$wip_qty"}},
                                                "finish_stock": {"$sum": {"$toInt": "$finish_stock"}},
                                                "issued_qty": {"$sum": {"$toInt": "$issued_qty"}},
                                                "final_order": {"$sum": {"$toInt": "$final_order"}},
                                                # "supplier_list": {"$sum": {"$toInt": "$supplier_list"}},
                                                "Cumulative_data": {"$sum": {"$toInt": "$Cumulative_data"}},
                                                "primary_item": "",

                                            }}, {"$project": {"_id": 0,
                                                              "machine": "",
                                                              "parts": "$parts",
                                                              "live_sales": "$live_sales",
                                                              "production": "$production",
                                                              "actual_required": "$actual_required",
                                                              "wip_qty": "$wip_qty",
                                                              "finish_stock": "$finish_stock",
                                                              "issued_qty": "$issued_qty",
                                                              "final_order": "$final_order",
                                                              "supplier_list": "$supplier_list",
                                                              "Cumulative_data": "$Cumulative_data",
                                                              "primary_item": "",

                                                              }}
                                            ])