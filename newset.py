# import time
# from pprint import pprint
#
import time

import numpy as np
import pymongo

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

gap_calculator = mydb1["gap_calculator"]

# --------------------reset data collection------------------------------------
reset_data_gap = mydb1["reset_data_gap"]
reset_data_production_plan = mydb1["reset_data_production_plan"]
reset_data_part_prduction_plan = mydb1["reset_data_production_plan"]

# ---------------------10 documents backup data collection--------------------------------------
machinery_components_backup = mydb2['machinery_components_backup']
sales_order_backup = mydb2['sales_order_backup']
stock_backup = mydb2['stock_backup']
# parts_backup = mydb2['parts_backup']
wip_backup = mydb2['wip_backup']
vendor_details_backup = mydb2['vendor_details_backup']
machinery_components_backup1 = mydb2['machinery_components_backup1']


# data = {"machinery_components": [
# {
#             "serial_no": 25,
#             "bom_level": 1,
#             "machine_name": "BRINELL HARDNESS TESTER B-3000 PCFA [INLINE]",
#             "machine_code": "B-3000 PCFA [INLINE]",
#             "base_units": "No.",
#             "bom_qty": 0,
#             "avl_qty": 0,
#             "machinery_components": [
#                 {
#                     "bom_level": 2,
#                     "assembly_name": "B 3000 PCFA-I  STD S/C",
#                     "base_units": "No.",
#                     "bom_qty": 1,
#                     "avl_qty": 0,
#                     "machinery_components": [
#                         {
#                             "bom_level": 3,
#                             "spare_name": "BASE UTM100",
#                             "base_units": "No.",
#                             "bom_qty": 1,
#                             "avl_qty": 2,
#                             "machinery_components": [
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "BASE UTM100 [CI]",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 8
#                                 }
#                             ]
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "BASE FRAME [B-3000PCFA-I]",
#                             "base_units": "No.",
#                             "bom_qty": 1,
#                             "avl_qty": 0,
#                             "machinery_components": [
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "BASE FRAME [B-3000PCFA-I] [FAB]",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 0,
#                                     "machinery_components": [
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "MS PLATE (Kg)",
#                                             "base_units": "Kgs",
#                                             "bom_qty": 184,
#                                             "avl_qty": 4420.417
#                                         }
#                                     ]
#                                 }
#                             ]
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "IDLER BRACKET UTM",
#                             "part_code": "UTN-10-10-00-2",
#                             "base_units": "No.",
#                             "bom_qty": 2,
#                             "avl_qty": 2,
#                             "machinery_components": [
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "IDLER BRACKET UTM [M/c] 1",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 1,
#                                     "machinery_components": [
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "IDLER BRACKET UTM [Ci]",
#                                             "part_code": "UTN-10-10-00-1",
#                                             "base_units": "No.",
#                                             "bom_qty": 1,
#                                             "avl_qty": 0
#                                         }
#                                     ]
#                                 }
#                             ]
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "IDLER SPROCKET UTM",
#                             "base_units": "No.",
#                             "bom_qty": 2,
#                             "avl_qty": 0,
#                             "machinery_components": [
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "IDLER SPROCKET UTM (HOB) 2",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 0,
#                                     "machinery_components": [
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "IDLER SPROCKET UTM(M/c)1",
#                                             "base_units": "No.",
#                                             "bom_qty": 1,
#                                             "avl_qty": 0,
#                                             "machinery_components": [
#                                                 {
#                                                     "bom_level": 6,
#                                                     "spare_name": "IDLER SPROCKET UTM (CUT)",
#                                                     "base_units": "No.",
#                                                     "bom_qty": 1,
#                                                     "avl_qty": 0,
#                                                     "machinery_components": [
#                                                         {
#                                                             "bom_level": 7,
#                                                             "spare_name": "MS BLACK ROUND DIA 90",
#                                                             "base_units": "Kgs",
#                                                             "bom_qty": 1.105,
#                                                             "avl_qty": 145.8891
#                                                         }
#                                                     ]
#                                                 }
#                                             ]
#                                         }
#                                     ]
#                                 }
#                             ]
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "IDLER BRACKET PIN UTM",
#                             "base_units": "No.",
#                             "bom_qty": 2,
#                             "avl_qty": 0
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "MAIN SCREW [B-3000 PCFA-I]",
#                             "base_units": "No.",
#                             "bom_qty": 2,
#                             "avl_qty": 0
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "MAIN SCREW CAP [B3000-PCFA-I]",
#                             "base_units": "No.",
#                             "bom_qty": 2,
#                             "avl_qty": 0,
#                             "machinery_components": [
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "MAIN SCREW CAP [B3000-PCFA-I] [CUT]",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 0,
#                                     "machinery_components": [
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "En-353 Round Dia 140",
#                                             "base_units": "Kgs",
#                                             "bom_qty": 4.132,
#                                             "avl_qty": 0
#                                         }
#                                     ]
#                                 }
#                             ]
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "THRUST NUT UTM100",
#                             "base_units": "No.",
#                             "bom_qty": 2,
#                             "avl_qty": 12,
#                             "machinery_components": [
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "THRUST NUT UTM100 [CUT]",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 20,
#                                     "machinery_components": [
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "MS PROFILE ROUND DIA 170 X 110",
#                                             "base_units": "Kgs",
#                                             "bom_qty": 21.60,
#                                             "avl_qty": 819
#                                         }
#                                     ]
#                                 }
#                             ]
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "THRUST NUT CHECK NUT UTM100",
#                             "base_units": "No.",
#                             "bom_qty": 2,
#                             "avl_qty": 50,
#                             "machinery_components": [
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "THRUST NUT CHECK NUT UTM100 [CUT]",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 2,
#                                     "machinery_components": [
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "MS PROFILE RING 170 x 76 x 22",
#                                             "base_units": "Kgs",
#                                             "bom_qty": 4,
#                                             "avl_qty": 141
#                                         }
#                                     ]
#                                 }
#                             ]
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "THRUST PLATE UTM100",
#                             "base_units": "No.",
#                             "bom_qty": 2,
#                             "avl_qty": 0,
#                             "machinery_components": [
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "THRUST PLATE UTM100 [HARD] 2",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 0,
#                                     "machinery_components": [
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "THRUST PLATE UTM100 [M/C] 1",
#                                             "base_units": "No.",
#                                             "bom_qty": 1,
#                                             "avl_qty": 0,
#                                             "machinery_components": [
#                                                 {
#                                                     "bom_level": 6,
#                                                     "spare_name": "THRUST PLATE UTM100 [CUT]",
#                                                     "base_units": "No.",
#                                                     "bom_qty": 1,
#                                                     "avl_qty": 0,
#                                                     "machinery_components": [
#                                                         {
#                                                             "bom_level": 7,
#                                                             "spare_name": "En-353 Round  Dia 170",
#                                                             "base_units": "Kgs",
#                                                             "bom_qty": 4.301,
#                                                             "avl_qty": 842.7884
#                                                         }
#                                                     ]
#                                                 }
#                                             ]
#                                         }
#                                     ]
#                                 }
#                             ]
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "THRUST COLLER UTM100",
#                             "part_code": "UTN-100-12-00-2",
#                             "base_units": "No.",
#                             "bom_qty": 2,
#                             "avl_qty": 0,
#                             "machinery_components": [
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "THRUST COLLER UTM100 [Cut]",
#                                     "part_code": "UTN-100-12-00-1",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 0,
#                                     "machinery_components": [
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "MS PROFILE RING 126 X 80 X 20",
#                                             "base_units": "Kgs",
#                                             "bom_qty": 2.58,
#                                             "avl_qty": 25.80
#                                         }
#                                     ]
#                                 }
#                             ]
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "SCREW SPROCKET UTM100",
#                             "part_code": "UTN-100-13-00",
#                             "base_units": "No.",
#                             "bom_qty": 2,
#                             "avl_qty": 0,
#                             "machinery_components": [
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "SCREW SPROCKET UTM100 [R M/C] 4",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 0,
#                                     "machinery_components": [
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "SCREW SPROCKET UTM100 [HOB] 3",
#                                             "base_units": "No.",
#                                             "bom_qty": 1,
#                                             "avl_qty": 0,
#                                             "machinery_components": [
#                                                 {
#                                                     "bom_level": 6,
#                                                     "spare_name": "SCREW SPROCKET UTM100 [SHAP] 2",
#                                                     "base_units": "No.",
#                                                     "bom_qty": 1,
#                                                     "avl_qty": 0,
#                                                     "machinery_components": [
#                                                         {
#                                                             "bom_level": 7,
#                                                             "spare_name": "SCREW SPROCKET UTM100 [M/C] 1",
#                                                             "base_units": "No.",
#                                                             "bom_qty": 1,
#                                                             "avl_qty": 0,
#                                                             "machinery_components": [
#                                                                 {
#                                                                     "bom_level": 8,
#                                                                     "spare_name": "SCREW SPROCKET UTM100 [CUT]",
#                                                                     "base_units": "No.",
#                                                                     "bom_qty": 1,
#                                                                     "avl_qty": 16,
#                                                                     "machinery_components": [
#                                                                         {
#                                                                             "bom_level": 9,
#                                                                             "spare_name": "MS PROFILE RING 180 X 95 X 34",
#                                                                             "base_units": "Kgs",
#                                                                             "bom_qty": 7.50,
#                                                                             "avl_qty": 0
#                                                                         }
#                                                                     ]
#                                                                 }
#                                                             ]
#                                                         }
#                                                     ]
#                                                 }
#                                             ]
#                                         }
#                                     ]
#                                 }
#                             ]
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "KEY FOR SCREW SPOCKET UTM",
#                             "base_units": "No.",
#                             "bom_qty": 2,
#                             "avl_qty": 351
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "MOTOR SPROCKET UTM60/100",
#                             "part_code": "UTN-100-20-00",
#                             "base_units": "No.",
#                             "bom_qty": 1,
#                             "avl_qty": 0,
#                             "machinery_components": [
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "MOTOR SPROCKET UTM60/100 [R M/c] 4",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 0,
#                                     "machinery_components": [
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "MOTOR SPROCKET UTM60/100 [HOBB] 3",
#                                             "base_units": "No.",
#                                             "bom_qty": 1,
#                                             "avl_qty": 0,
#                                             "machinery_components": [
#                                                 {
#                                                     "bom_level": 6,
#                                                     "spare_name": "MOTOR SPROCKET UTM60/100 [SHAP] 2",
#                                                     "base_units": "No.",
#                                                     "bom_qty": 1,
#                                                     "avl_qty": 0,
#                                                     "machinery_components": [
#                                                         {
#                                                             "bom_level": 7,
#                                                             "spare_name": "MOTOR SPROCKET UTM60/100 [M/C] 1",
#                                                             "base_units": "No.",
#                                                             "bom_qty": 1,
#                                                             "avl_qty": 0,
#                                                             "machinery_components": [
#                                                                 {
#                                                                     "bom_level": 8,
#                                                                     "spare_name": "MOTOR SPROCKET UTM60/100 [CUT]",
#                                                                     "base_units": "No.",
#                                                                     "bom_qty": 1,
#                                                                     "avl_qty": 0,
#                                                                     "machinery_components": [
#                                                                         {
#                                                                             "bom_level": 9,
#                                                                             "spare_name": "MS PROFILE ROUND DIA 145 X 32",
#                                                                             "base_units": "Kgs",
#                                                                             "bom_qty": 4.432,
#                                                                             "avl_qty": 84.30
#                                                                         }
#                                                                     ]
#                                                                 }
#                                                             ]
#                                                         }
#                                                     ]
#                                                 }
#                                             ]
#                                         }
#                                     ]
#                                 }
#                             ]
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "KEY FOR MOTOR SPROCKET UTM STD",
#                             "base_units": "No.",
#                             "bom_qty": 1,
#                             "avl_qty": 361
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "MOVING CROSS HEAD B-3000 PCFA-I",
#                             "base_units": "No.",
#                             "bom_qty": 1,
#                             "avl_qty": 0
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "MAIN NUT UTM100",
#                             "base_units": "No.",
#                             "bom_qty": 2,
#                             "avl_qty": 17,
#                             "machinery_components": [
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "MAIN NUT UTM100 [CI]",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 32
#                                 }
#                             ]
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "MAIN NUT CHECK NUT UTM100",
#                             "base_units": "No.",
#                             "bom_qty": 2,
#                             "avl_qty": 21,
#                             "machinery_components": [
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "MAIN NUT CHECK NUT UTM100 [CUT]",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 18,
#                                     "machinery_components": [
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "MS PROFILE RING  201 x 136 x 28",
#                                             "base_units": "Kgs",
#                                             "bom_qty": 7.10,
#                                             "avl_qty": 301
#                                         }
#                                     ]
#                                 }
#                             ]
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "BACKLASH NUT UTM100",
#                             "base_units": "No.",
#                             "bom_qty": 2,
#                             "avl_qty": 18
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "BACKLASH SPRING UTM100",
#                             "base_units": "No.",
#                             "bom_qty": 8,
#                             "avl_qty": 0
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "SPRING SEAT UTM60/100",
#                             "base_units": "No.",
#                             "bom_qty": 8,
#                             "avl_qty": 0
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "CYLINDER MTG BRACKET",
#                             "base_units": "No.",
#                             "bom_qty": 1,
#                             "avl_qty": 0,
#                             "machinery_components": [
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "CYLINDER MTG BRACKET [M/C] 1",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 0,
#                                     "machinery_components": [
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "CYLINDER MTG BRACKET [FAB]",
#                                             "base_units": "No.",
#                                             "bom_qty": 1,
#                                             "avl_qty": 0
#                                         }
#                                     ]
#                                 }
#                             ]
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "LEVER CLAMP PLATE [B3000 PCFA-I]",
#                             "base_units": "No.",
#                             "bom_qty": 1,
#                             "avl_qty": 0,
#                             "machinery_components": [
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "LEVER CLAMP PLATE [B3000 PCFA-I] [MARK] 2",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 0,
#                                     "machinery_components": [
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "LEVER CLAMP PLATE [B3000 PCFA-I] [Weld] 1",
#                                             "base_units": "No.",
#                                             "bom_qty": 1,
#                                             "avl_qty": 0,
#                                             "machinery_components": [
#                                                 {
#                                                     "bom_level": 6,
#                                                     "spare_name": "LEVER CLAMP PLATE PIECE-1 [B3000 PCFA-I]",
#                                                     "base_units": "No.",
#                                                     "bom_qty": 2,
#                                                     "avl_qty": 0,
#                                                     "machinery_components": [
#                                                         {
#                                                             "bom_level": 7,
#                                                             "spare_name": "LEVER CLAMP PLATE PIECE-1 [B3000 PCFA-I] [Shap] 1",
#                                                             "base_units": "No.",
#                                                             "bom_qty": 1,
#                                                             "avl_qty": 0,
#                                                             "machinery_components": [
#                                                                 {
#                                                                     "bom_level": 8,
#                                                                     "spare_name": "LEVER CLAMP PLATE PIECE-1 [B3000 PCFA-I] [CUT]",
#                                                                     "base_units": "No.",
#                                                                     "bom_qty": 1,
#                                                                     "avl_qty": 0,
#                                                                     "machinery_components": [
#                                                                         {
#                                                                             "bom_level": 9,
#                                                                             "spare_name": "EN-8 FLAT 100 X 40",
#                                                                             "base_units": "Kgs",
#                                                                             "bom_qty": 4.118,
#                                                                             "avl_qty": 473.056
#                                                                         }
#                                                                     ]
#                                                                 }
#                                                             ]
#                                                         }
#                                                     ]
#                                                 },
#                                                 {
#                                                     "bom_level": 6,
#                                                     "spare_name": "LEVER CLAMP PLATE PIECE-2 [B3000 PCFA-I] [SR GR] 4",
#                                                     "base_units": "No.",
#                                                     "bom_qty": 1,
#                                                     "avl_qty": 0,
#                                                     "machinery_components": [
#                                                         {
#                                                             "bom_level": 7,
#                                                             "spare_name": "LEVER CLAMP PLATE PIECE-2 [B3000 PCFA-I] [Mill] 3",
#                                                             "base_units": "No.",
#                                                             "bom_qty": 1,
#                                                             "avl_qty": 0,
#                                                             "machinery_components": [
#                                                                 {
#                                                                     "bom_level": 8,
#                                                                     "spare_name": "LEVER CLAMP PLATE PIECE-2 [B3000 PCFA-I] [M/C] 2",
#                                                                     "base_units": "No.",
#                                                                     "bom_qty": 1,
#                                                                     "avl_qty": 0,
#                                                                     "machinery_components": [
#                                                                         {
#                                                                             "bom_level": 9,
#                                                                             "spare_name": "LEVER CLAMP PLATE PIECE-2 [B3000 PCFA-I] [SHAP] 1",
#                                                                             "base_units": "No.",
#                                                                             "bom_qty": 1,
#                                                                             "avl_qty": 0,
#                                                                             "machinery_components": [
#                                                                                 {
#                                                                                     "bom_level": 10,
#                                                                                     "spare_name": "LEVER CLAMP PLATE PIECE-2 [B3000 PCFA-I] [CUT]",
#                                                                                     "base_units": "No.",
#                                                                                     "bom_qty": 1,
#                                                                                     "avl_qty": 0,
#                                                                                     "machinery_components": [
#                                                                                         {
#                                                                                             "bom_level": 11,
#                                                                                             "spare_name": "MS PROFILE FLAT 80 X 60 X 240",
#                                                                                             "base_units": "Kgs",
#                                                                                             "bom_qty": 9.80,
#                                                                                             "avl_qty": 0
#                                                                                         }
#                                                                                     ]
#                                                                                 }
#                                                                             ]
#                                                                         }
#                                                                     ]
#                                                                 }
#                                                             ]
#                                                         }
#                                                     ]
#                                                 },
#                                                 {
#                                                     "bom_level": 6,
#                                                     "spare_name": "LEVER CLAMP PLATE PIECE-3 [B3000 PCFA-I] [Sr Grind]",
#                                                     "base_units": "No.",
#                                                     "bom_qty": 1,
#                                                     "avl_qty": 0,
#                                                     "machinery_components": [
#                                                         {
#                                                             "bom_level": 7,
#                                                             "spare_name": "LEVER CLAMP PLATE PIECE-3 [B3000 PCFA-I] [M/C] 2",
#                                                             "base_units": "No.",
#                                                             "bom_qty": 1,
#                                                             "avl_qty": 0,
#                                                             "machinery_components": [
#                                                                 {
#                                                                     "bom_level": 8,
#                                                                     "spare_name": "LEVER CLAMP PLATE PIECE-3 [B3000 PCFA-I] [SHAP] 1",
#                                                                     "base_units": "No.",
#                                                                     "bom_qty": 1,
#                                                                     "avl_qty": 0,
#                                                                     "machinery_components": [
#                                                                         {
#                                                                             "bom_level": 9,
#                                                                             "spare_name": "LEVER CLAMP PLATE PIECE-3 [B3000 PCFA-I] [CUT]",
#                                                                             "base_units": "No.",
#                                                                             "bom_qty": 1,
#                                                                             "avl_qty": 0,
#                                                                             "machinery_components": [
#                                                                                 {
#                                                                                     "bom_level": 10,
#                                                                                     "spare_name": "MS PROFILE FLAT 240 X 205 X 20",
#                                                                                     "base_units": "Kgs",
#                                                                                     "bom_qty": 8,
#                                                                                     "avl_qty": 0
#                                                                                 }
#                                                                             ]
#                                                                         }
#                                                                     ]
#                                                                 }
#                                                             ]
#                                                         }
#                                                     ]
#                                                 }
#                                             ]
#                                         }
#                                     ]
#                                 }
#                             ]
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "CYLINDER MOUNTING L BRACKET",
#                             "base_units": "No.",
#                             "bom_qty": 1,
#                             "avl_qty": 0,
#                             "machinery_components": [
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "CYLINDER MOUNTING L BRACKET [BOR] 1",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 0,
#                                     "machinery_components": [
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "CYLINDER MOUNTING L BRACKET [FAB]",
#                                             "base_units": "No.",
#                                             "bom_qty": 1,
#                                             "avl_qty": 0
#                                         }
#                                     ]
#                                 }
#                             ]
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "PUSH ROD [B3000-PCFA-I]",
#                             "base_units": "No.",
#                             "bom_qty": 1,
#                             "avl_qty": 0,
#                             "machinery_components": [
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "PUSH ROD [B3000-PCFA-I] [CUT]",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 0,
#                                     "machinery_components": [
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "MS BRIGHT HEXAGON A/F 22",
#                                             "base_units": "Kgs",
#                                             "bom_qty": 0.337,
#                                             "avl_qty": 140.511
#                                         }
#                                     ]
#                                 }
#                             ]
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "CLAMPING CONE [B3000-PCFA-I]",
#                             "base_units": "No.",
#                             "bom_qty": 1,
#                             "avl_qty": 0,
#                             "machinery_components": [
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "CLAMPING CONE [B3000-PCFA-I] [MILL] 2",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 0,
#                                     "machinery_components": [
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "CLAMPING CONE [B3000-PCFA-I] [M/C] 1",
#                                             "base_units": "No.",
#                                             "bom_qty": 1,
#                                             "avl_qty": 0,
#                                             "machinery_components": [
#                                                 {
#                                                     "bom_level": 6,
#                                                     "spare_name": "CLAMPING CONE [B3000-PCFA-I] [CUT]",
#                                                     "base_units": "No.",
#                                                     "bom_qty": 1,
#                                                     "avl_qty": 0,
#                                                     "machinery_components": [
#                                                         {
#                                                             "bom_level": 7,
#                                                             "spare_name": "MS PROFILE ROUND DIA 165 X45",
#                                                             "base_units": "Kgs",
#                                                             "bom_qty": 7.90,
#                                                             "avl_qty": 0
#                                                         }
#                                                     ]
#                                                 }
#                                             ]
#                                         }
#                                     ]
#                                 }
#                             ]
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "RESTING PAD B 3000 PCFA-I",
#                             "base_units": "No.",
#                             "bom_qty": 1,
#                             "avl_qty": 0
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "MAIN LEVER ASSEMBLY B 3000 PCFA-I",
#                             "base_units": "No.",
#                             "bom_qty": 1,
#                             "avl_qty": 0
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "PIVOT BLOCK B 3000 PCFA-I",
#                             "base_units": "No.",
#                             "bom_qty": 1,
#                             "avl_qty": 5
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "U BRACKET B 3000 PCFA-I",
#                             "base_units": "No.",
#                             "bom_qty": 1,
#                             "avl_qty": 0
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "SWIVELLING ATTACHMENT B 3000 PCFA-I",
#                             "base_units": "No.",
#                             "bom_qty": 1,
#                             "avl_qty": 0
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "ADAPTOR PLATE ASSEMBLY B 3000 PCFA-I",
#                             "base_units": "No.",
#                             "bom_qty": 1,
#                             "avl_qty": 0
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "HANGER BODY ASSEMBLY B 3000 PCFA-I",
#                             "base_units": "No.",
#                             "bom_qty": 1,
#                             "avl_qty": 5
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "BOTTOM WEIGHT B 3000 PCFA-I",
#                             "base_units": "No.",
#                             "bom_qty": 1,
#                             "avl_qty": 0
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "WEIGHT SHAFT B 3000 PCFA-I",
#                             "base_units": "No.",
#                             "bom_qty": 1,
#                             "avl_qty": 0
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "250 KG WEIGHT B 3000 PCFA-I",
#                             "base_units": "No.",
#                             "bom_qty": 11,
#                             "avl_qty": 0
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "HYDRAULIC POWER PACK B 3000 PCFA-I",
#                             "base_units": "No.",
#                             "bom_qty": 1,
#                             "avl_qty": 0
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "BALL INDENTOR 5MM [Std]",
#                             "base_units": "No.",
#                             "bom_qty": 1,
#                             "avl_qty": 23
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "BALL INDENTOR 10MM (B 3000 O )",
#                             "base_units": "No.",
#                             "bom_qty": 1,
#                             "avl_qty": 0
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "DRIVE PANNEL B-3000 (PCFA-I)",
#                             "base_units": "No.",
#                             "bom_qty": 1,
#                             "avl_qty": 0,
#                             "machinery_components": [
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "CRC SHEET 16swg",
#                                     "base_units": "Kgs",
#                                     "bom_qty": 47.30,
#                                     "avl_qty": 59.11
#                                 }
#                             ]
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "STARTER PLATE DRIVE PANNEL B-3000 PCFA-I",
#                             "base_units": "No.",
#                             "bom_qty": 1,
#                             "avl_qty": 0,
#                             "machinery_components": [
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "CRC SHEET 16swg",
#                                     "base_units": "Kgs",
#                                     "bom_qty": 3.50,
#                                     "avl_qty": 59.11
#                                 }
#                             ]
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "TOP PLATE [B 3000-PCFA-I]",
#                             "base_units": "No.",
#                             "bom_qty": 1,
#                             "avl_qty": 0,
#                             "machinery_components": [
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "TOP PLATE [B 3000-PCFA-I] [CUT]",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 0,
#                                     "machinery_components": [
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "MS PROFILE FLAT 705 X 1005 X 50",
#                                             "base_units": "Kgs",
#                                             "bom_qty": 280.10,
#                                             "avl_qty": 0
#                                         }
#                                     ]
#                                 }
#                             ]
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "MIDDLE BUSH [B3000-PCFA-I]",
#                             "base_units": "No.",
#                             "bom_qty": 4,
#                             "avl_qty": 0,
#                             "machinery_components": [
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "MIDDLE BUSH [B3000-PCFA-I] [CUT]",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 0,
#                                     "machinery_components": [
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "MS BLACK ROUND DIA 45",
#                                             "base_units": "Kgs",
#                                             "bom_qty": 0.779,
#                                             "avl_qty": 8.6257
#                                         }
#                                     ]
#                                 }
#                             ]
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "BOTTOM PLATE [B3000-PCFA-I]",
#                             "base_units": "No.",
#                             "bom_qty": 1,
#                             "avl_qty": 0,
#                             "machinery_components": [
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "BOTTOM PLATE [B3000-PCFA-I] [CUT]",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 0,
#                                     "machinery_components": [
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "MS PROFILE ROUND DIA 505 X 50",
#                                             "base_units": "Kgs",
#                                             "bom_qty": 79,
#                                             "avl_qty": 0
#                                         }
#                                     ]
#                                 }
#                             ]
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "PLUNGER ASSEMBLY B 3000 PCFA-I",
#                             "base_units": "No.",
#                             "bom_qty": 1,
#                             "avl_qty": 5
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "B3000PC-OTB ASSEMBLY",
#                             "base_units": "No.",
#                             "bom_qty": 1,
#                             "avl_qty": -5,
#                             "machinery_components": [
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "CAMERA HOLDER OTB",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 20,
#                                     "machinery_components": [
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "CAMERA HOLDER OTB [M/c]1",
#                                             "base_units": "No.",
#                                             "bom_qty": 1,
#                                             "avl_qty": 2,
#                                             "machinery_components": [
#                                                 {
#                                                     "bom_level": 6,
#                                                     "spare_name": "CAMERA HOLDER OTB [Cut]",
#                                                     "base_units": "No.",
#                                                     "bom_qty": 1,
#                                                     "avl_qty": 10,
#                                                     "machinery_components": [
#                                                         {
#                                                             "bom_level": 7,
#                                                             "spare_name": "AL ROUND DIA 32",
#                                                             "base_units": "Kgs",
#                                                             "bom_qty": 0.086,
#                                                             "avl_qty": 8.008
#                                                         }
#                                                     ]
#                                                 }
#                                             ]
#                                         }
#                                     ]
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "CONNECTOR COVER OTB(DRIL)2",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 10,
#                                     "machinery_components": [
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "CONNECTOR COVER OTB(M/c)1",
#                                             "Primary_Item": "CONNECTOR COVER OTB(DRIL)2",
#                                             "base_units": "No.",
#                                             "bom_qty": 1,
#                                             "avl_qty": 0,
#                                             "machinery_components": [
#                                                 {
#                                                     "bom_level": 6,
#                                                     "spare_name": "Connector Cover Otb[Cut]",
#                                                     "Primary_Item": "CONNECTOR COVER OTB(DRIL)2",
#                                                     "base_units": "No.",
#                                                     "bom_qty": 1,
#                                                     "avl_qty": 25,
#                                                     "machinery_components": [
#                                                         {
#                                                             "bom_level": 7,
#                                                             "spare_name": "AL ROUND DIA 40",
#                                                             "base_units": "Kgs",
#                                                             "bom_qty": 0.027,
#                                                             "avl_qty": 0
#                                                         }
#                                                     ]
#                                                 }
#                                             ]
#                                         }
#                                     ]
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "END CAP OTB(DRL)2",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 10,
#                                     "machinery_components": [
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "END CAP OTB(M/c)1",
#                                             "base_units": "No.",
#                                             "bom_qty": 1,
#                                             "avl_qty": 0,
#                                             "machinery_components": [
#                                                 {
#                                                     "bom_level": 6,
#                                                     "spare_name": "END CAP OTB [Cut]",
#                                                     "base_units": "No.",
#                                                     "bom_qty": 1,
#                                                     "avl_qty": 25,
#                                                     "machinery_components": [
#                                                         {
#                                                             "bom_level": 7,
#                                                             "spare_name": "AL ROUND DIA 50",
#                                                             "base_units": "Kgs",
#                                                             "bom_qty": 0.095,
#                                                             "avl_qty": 94.50
#                                                         }
#                                                     ]
#                                                 }
#                                             ]
#                                         }
#                                     ]
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "FRONT TUBE OTB(DRIL)2",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 12,
#                                     "machinery_components": [
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "FRONT TUBE OTB(M/c)1",
#                                             "base_units": "No.",
#                                             "bom_qty": 1,
#                                             "avl_qty": 15,
#                                             "machinery_components": [
#                                                 {
#                                                     "bom_level": 6,
#                                                     "spare_name": "FRONT TUBE OTB [CUT]",
#                                                     "base_units": "No.",
#                                                     "bom_qty": 1,
#                                                     "avl_qty": 15,
#                                                     "machinery_components": [
#                                                         {
#                                                             "bom_level": 7,
#                                                             "spare_name": "AL ROUND DIA 45",
#                                                             "base_units": "Kgs",
#                                                             "bom_qty": 0.383,
#                                                             "avl_qty": 0
#                                                         }
#                                                     ]
#                                                 }
#                                             ]
#                                         }
#                                     ]
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "ILLUMINATION RING OTB",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 27,
#                                     "machinery_components": [
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "ILLUMINATION RING OTB [MIL]2",
#                                             "base_units": "No.",
#                                             "bom_qty": 1,
#                                             "avl_qty": 0,
#                                             "machinery_components": [
#                                                 {
#                                                     "bom_level": 6,
#                                                     "spare_name": "ILLUMINATION RING OTB [M/C]1",
#                                                     "base_units": "No.",
#                                                     "bom_qty": 1,
#                                                     "avl_qty": 0,
#                                                     "machinery_components": [
#                                                         {
#                                                             "bom_level": 7,
#                                                             "spare_name": "ILLUMINATION RING OTB [CUT]",
#                                                             "base_units": "No.",
#                                                             "bom_qty": 1,
#                                                             "avl_qty": 16,
#                                                             "machinery_components": [
#                                                                 {
#                                                                     "bom_level": 8,
#                                                                     "spare_name": "AL ROUND DIA 32",
#                                                                     "base_units": "Kgs",
#                                                                     "bom_qty": 0.054,
#                                                                     "avl_qty": 8.008
#                                                                 }
#                                                             ]
#                                                         }
#                                                     ]
#                                                 }
#                                             ]
#                                         }
#                                     ]
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "NUT OTB",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 0,
#                                     "machinery_components": [
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "NUT OTB [M/C]1",
#                                             "base_units": "No.",
#                                             "bom_qty": 1,
#                                             "avl_qty": 13,
#                                             "machinery_components": [
#                                                 {
#                                                     "bom_level": 6,
#                                                     "spare_name": "NUT OTB [Cut]",
#                                                     "base_units": "No.",
#                                                     "bom_qty": 1,
#                                                     "avl_qty": 15,
#                                                     "machinery_components": [
#                                                         {
#                                                             "bom_level": 7,
#                                                             "spare_name": "AL ROUND DIA 40",
#                                                             "base_units": "Kgs",
#                                                             "bom_qty": 0.05,
#                                                             "avl_qty": 0
#                                                         }
#                                                     ]
#                                                 }
#                                             ]
#                                         }
#                                     ]
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "OBJECTIVE HOLDER OTB",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 11,
#                                     "machinery_components": [
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "OBJECTIVE HOLDER OTB [MILL]2",
#                                             "base_units": "No.",
#                                             "bom_qty": 1,
#                                             "avl_qty": 10,
#                                             "machinery_components": [
#                                                 {
#                                                     "bom_level": 6,
#                                                     "spare_name": "OBJECTIVE HOLDER OTB [M/C]1",
#                                                     "base_units": "No.",
#                                                     "bom_qty": 1,
#                                                     "avl_qty": 5,
#                                                     "machinery_components": [
#                                                         {
#                                                             "bom_level": 7,
#                                                             "spare_name": "OBJECTIVE HOLDER OTB [CUT]",
#                                                             "base_units": "No.",
#                                                             "bom_qty": 1,
#                                                             "avl_qty": 20,
#                                                             "machinery_components": [
#                                                                 {
#                                                                     "bom_level": 8,
#                                                                     "spare_name": "AL ROUND DIA 32",
#                                                                     "base_units": "Kgs",
#                                                                     "bom_qty": 0.065,
#                                                                     "avl_qty": 8.008
#                                                                 }
#                                                             ]
#                                                         }
#                                                     ]
#                                                 }
#                                             ]
#                                         }
#                                     ]
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "OBJECTIVE HOLD. PIN  OTB [BLK]",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 0,
#                                     "machinery_components": [
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "OBJECTIVE HOLD. PIN  OTB[M/C]1",
#                                             "base_units": "No.",
#                                             "bom_qty": 1,
#                                             "avl_qty": 51,
#                                             "machinery_components": [
#                                                 {
#                                                     "bom_level": 6,
#                                                     "spare_name": "OBJECTIVE HOLD. PIN  OTB[CUT]",
#                                                     "base_units": "No.",
#                                                     "bom_qty": 1,
#                                                     "avl_qty": 20,
#                                                     "machinery_components": [
#                                                         {
#                                                             "bom_level": 7,
#                                                             "spare_name": "MS BRIGHT ROUND DIA 10",
#                                                             "base_units": "Kgs",
#                                                             "bom_qty": 0.015,
#                                                             "avl_qty": 1.882
#                                                         }
#                                                     ]
#                                                 }
#                                             ]
#                                         }
#                                     ]
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "REAR TUBE OTB B3000",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 9,
#                                     "machinery_components": [
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "REAR TUBE OTB B3000 [DRILL]2",
#                                             "base_units": "No.",
#                                             "bom_qty": 1,
#                                             "avl_qty": 1,
#                                             "machinery_components": [
#                                                 {
#                                                     "bom_level": 6,
#                                                     "spare_name": "REAR TUBE OTB B3000 [M/C]1",
#                                                     "base_units": "No.",
#                                                     "bom_qty": 1,
#                                                     "avl_qty": 0,
#                                                     "machinery_components": [
#                                                         {
#                                                             "bom_level": 7,
#                                                             "spare_name": "REAR TUBE OTB B3000 [CUT]",
#                                                             "base_units": "No.",
#                                                             "bom_qty": 1,
#                                                             "avl_qty": 25,
#                                                             "machinery_components": [
#                                                                 {
#                                                                     "bom_level": 8,
#                                                                     "spare_name": "AL ROUND DIA 55",
#                                                                     "base_units": "Kgs",
#                                                                     "bom_qty": 1.175,
#                                                                     "avl_qty": 0
#                                                                 }
#                                                             ]
#                                                         }
#                                                     ]
#                                                 }
#                                             ]
#                                         }
#                                     ]
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "Washer for 5/10 Dia Ball Ind",
#                                     "base_units": "No.",
#                                     "bom_qty": 2,
#                                     "avl_qty": 11,
#                                     "machinery_components": [
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "Washer for 5/10 Dia Ball Ind [Cut]",
#                                             "base_units": "No.",
#                                             "bom_qty": 1,
#                                             "avl_qty": 28,
#                                             "machinery_components": [
#                                                 {
#                                                     "bom_level": 6,
#                                                     "spare_name": "STAINLESS STEEL ROUND DIA 16",
#                                                     "base_units": "Kgs",
#                                                     "bom_qty": 0.024,
#                                                     "avl_qty": 3.2078
#                                                 }
#                                             ]
#                                         }
#                                     ]
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "Washer for OTB B3000 PCFA",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 16,
#                                     "machinery_components": [
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "Washer for OTB B3000 PCFA [CUT]",
#                                             "base_units": "No.",
#                                             "bom_qty": 1,
#                                             "avl_qty": 4,
#                                             "machinery_components": [
#                                                 {
#                                                     "bom_level": 6,
#                                                     "spare_name": "BRASS ROUND DIA 55",
#                                                     "base_units": "Kgs",
#                                                     "bom_qty": 0.405,
#                                                     "avl_qty": 34.8374
#                                                 }
#                                             ]
#                                         }
#                                     ]
#                                 }
#                             ]
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "CLAMP ROD UTE",
#                             "base_units": "No.",
#                             "bom_qty": 1,
#                             "avl_qty": 0
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "LIMIT SWITCH BRACKET B-3000 PCFA I",
#                             "base_units": "No.",
#                             "bom_qty": 1,
#                             "avl_qty": 0,
#                             "machinery_components": [
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "CRC SHEET 16swg",
#                                     "base_units": "Kgs",
#                                     "bom_qty": 0.30,
#                                     "avl_qty": 59.11
#                                 }
#                             ]
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "U COVER UTM100",
#                             "base_units": "No.",
#                             "bom_qty": 1,
#                             "avl_qty": 0,
#                             "machinery_components": [
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "CRC SHEET 16swg",
#                                     "base_units": "Kgs",
#                                     "bom_qty": 53,
#                                     "avl_qty": 59.11
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "MS BLACK FLAT 25 X 3",
#                                     "base_units": "Kgs",
#                                     "bom_qty": 0.942,
#                                     "avl_qty": 520.66
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "HEX BOLT 6 X 12",
#                                     "base_units": "No.",
#                                     "bom_qty": 15,
#                                     "avl_qty": 1547
#                                 }
#                             ]
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "CLAMPING CONE B-3000 PCFA-I [SAROJ]",
#                             "base_units": "No.",
#                             "bom_qty": 1,
#                             "avl_qty": 0
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "ANGLE PLATE B 3000 PCFA I",
#                             "base_units": "No.",
#                             "bom_qty": 2,
#                             "avl_qty": 0,
#                             "machinery_components": [
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "ANGLE PLATE B 3000 PCFA I [MILL] 1",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 0,
#                                     "machinery_components": [
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "ANGLE PLATE B 3000 PCFA I [FAB] 1",
#                                             "base_units": "No.",
#                                             "bom_qty": 1,
#                                             "avl_qty": 0
#                                         }
#                                     ]
#                                 }
#                             ]
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "LIMIT SWITCH CAP FOR B 3000 PCFA I",
#                             "base_units": "No.",
#                             "bom_qty": 1,
#                             "avl_qty": 0,
#                             "machinery_components": [
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "CRC SHEET 16swg",
#                                     "base_units": "Kgs",
#                                     "bom_qty": 0.25,
#                                     "avl_qty": 59.11
#                                 }
#                             ]
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "MAIN LEVER TOP COVER B 3000 PCFA I",
#                             "base_units": "No.",
#                             "bom_qty": 1,
#                             "avl_qty": 0,
#                             "machinery_components": [
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "CRC SHEET 16swg",
#                                     "base_units": "Kgs",
#                                     "bom_qty": 3.10,
#                                     "avl_qty": 59.11
#                                 }
#                             ]
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "WIRING BRACKET B 3000 PCFA I",
#                             "base_units": "No.",
#                             "bom_qty": 1,
#                             "avl_qty": 0,
#                             "machinery_components": [
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "CRC SHEET 16swg",
#                                     "base_units": "Kgs",
#                                     "bom_qty": 0.15,
#                                     "avl_qty": 59.11
#                                 }
#                             ]
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "FOUNDATION PLATE B 3000 PCFA-I",
#                             "base_units": "No.",
#                             "bom_qty": 2,
#                             "avl_qty": 0,
#                             "machinery_components": [
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "FOUNDATION PLATE B 3000 PCFA-I [CUT]",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 0,
#                                     "machinery_components": [
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "MS BRIGHT FLAT 25 X 10",
#                                             "base_units": "Kgs",
#                                             "bom_qty": 0.817,
#                                             "avl_qty": 0
#                                         }
#                                     ]
#                                 }
#                             ]
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "B3000 GUIDE BLOCK",
#                             "base_units": "No.",
#                             "bom_qty": 1,
#                             "avl_qty": 0,
#                             "machinery_components": [
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "B3000 GUIDE BLOCK[MILL]1",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 0,
#                                     "machinery_components": [
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "B3000 GUIDE BLOCK[Cut]",
#                                             "base_units": "No.",
#                                             "bom_qty": 1,
#                                             "avl_qty": 0,
#                                             "machinery_components": [
#                                                 {
#                                                     "bom_level": 6,
#                                                     "spare_name": "MS BRIGHT FLAT 32 X 32",
#                                                     "base_units": "Kgs",
#                                                     "bom_qty": 0.603,
#                                                     "avl_qty": 60.6512
#                                                 }
#                                             ]
#                                         }
#                                     ]
#                                 }
#                             ]
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "LIMIT SWITCH BKT FOR PISTON B3000 PCFA(Drill]2",
#                             "base_units": "No.",
#                             "bom_qty": 1,
#                             "avl_qty": 6
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "L/S ANGLE PLATE B-3000 PCFA",
#                             "base_units": "No.",
#                             "bom_qty": 1,
#                             "avl_qty": 0
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "L S PLATE B3000PCFA",
#                             "base_units": "No.",
#                             "bom_qty": 1,
#                             "avl_qty": 2
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "MANIFOLD B3000 PCFA",
#                             "base_units": "No.",
#                             "bom_qty": 1,
#                             "avl_qty": 0,
#                             "machinery_components": [
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "MANIFOLD B3000 PCFA [DRIL]2",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 0,
#                                     "machinery_components": [
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "MANIFOLD B3000 PCFA [MIL]1",
#                                             "base_units": "No.",
#                                             "bom_qty": 1,
#                                             "avl_qty": 0,
#                                             "machinery_components": [
#                                                 {
#                                                     "bom_level": 6,
#                                                     "spare_name": "MANIFOLD B3000 PCFA [Cut]",
#                                                     "base_units": "No.",
#                                                     "bom_qty": 1,
#                                                     "avl_qty": 0,
#                                                     "machinery_components": [
#                                                         {
#                                                             "bom_level": 7,
#                                                             "spare_name": "MS PROFILE FLAT 90 X 100 X 80",
#                                                             "base_units": "Kgs",
#                                                             "bom_qty": 6.712,
#                                                             "avl_qty": 37.10
#                                                         }
#                                                     ]
#                                                 }
#                                             ]
#                                         }
#                                     ]
#                                 }
#                             ]
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "MANIFOLD PLATE B3000 PCFA",
#                             "base_units": "No.",
#                             "bom_qty": 1,
#                             "avl_qty": 0,
#                             "machinery_components": [
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "MANIFOLD PLATE B3000 PCFA[Drill]2",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 0,
#                                     "machinery_components": [
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "MANIFOLD PLATE B3000 PCFA[Mill]1",
#                                             "base_units": "No.",
#                                             "bom_qty": 1,
#                                             "avl_qty": 0,
#                                             "machinery_components": [
#                                                 {
#                                                     "bom_level": 6,
#                                                     "spare_name": "MANIFOLD PLATE B3000 PCFA[Cut]",
#                                                     "base_units": "No.",
#                                                     "bom_qty": 1,
#                                                     "avl_qty": 0,
#                                                     "machinery_components": [
#                                                         {
#                                                             "bom_level": 7,
#                                                             "spare_name": "MS PROFILE FLAT 250 X 265 X 20",
#                                                             "base_units": "Kgs",
#                                                             "bom_qty": 10.80,
#                                                             "avl_qty": 121.60
#                                                         }
#                                                     ]
#                                                 }
#                                             ]
#                                         }
#                                     ]
#                                 }
#                             ]
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "CONNECTION B3000 PCFA",
#                             "base_units": "No.",
#                             "bom_qty": 4,
#                             "avl_qty": 0,
#                             "machinery_components": [
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "CONNECTION B3000 PCFA(MAC)1",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 0,
#                                     "machinery_components": [
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "CONNECTION B3000 PCFA(Cut]",
#                                             "base_units": "No.",
#                                             "bom_qty": 1,
#                                             "avl_qty": 10,
#                                             "machinery_components": [
#                                                 {
#                                                     "bom_level": 6,
#                                                     "spare_name": "MS BRIGHT HEXAGON A/F 19",
#                                                     "base_units": "Kgs",
#                                                     "bom_qty": 0.162,
#                                                     "avl_qty": 0
#                                                 }
#                                             ]
#                                         }
#                                     ]
#                                 }
#                             ]
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "BACKLITE RING B3000 PCFA",
#                             "base_units": "No.",
#                             "bom_qty": 1,
#                             "avl_qty": 0,
#                             "machinery_components": [
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "BACKLITE RING B3000 PCFA(M/C)1",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 8,
#                                     "machinery_components": [
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "BACKLITE RING B3000 PCFA(CUT]",
#                                             "base_units": "No.",
#                                             "bom_qty": 1,
#                                             "avl_qty": 0,
#                                             "machinery_components": [
#                                                 {
#                                                     "bom_level": 6,
#                                                     "spare_name": "Nylon Plate  170 x 170 x 10 mm",
#                                                     "base_units": "No.",
#                                                     "bom_qty": 1,
#                                                     "avl_qty": 0
#                                                 }
#                                             ]
#                                         }
#                                     ]
#                                 }
#                             ]
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "CYLINDER B 3000 PCFA-I",
#                             "base_units": "No.",
#                             "bom_qty": 1,
#                             "avl_qty": 0,
#                             "machinery_components": [
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "CI CASTING ( Bearing Cap - Celeros )",
#                                     "base_units": "Kgs",
#                                     "bom_qty": 14,
#                                     "avl_qty": 239
#                                 }
#                             ]
#                         }
#                     ]
#                 },
#                 {
#                     "bom_level": 2,
#                     "assembly_name": "B 3000 Pc Inline B/o",
#                     "base_units": "No.",
#                     "bom_qty": 1,
#                     "avl_qty": 1,
#                     "machinery_components": [
#                         {
#                             "bom_level": 3,
#                             "spare_name": "B 3000 Pc Inline B/o Loading Unit",
#                             "base_units": "No.",
#                             "bom_qty": 1,
#                             "avl_qty": 0,
#                             "machinery_components": [
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "SHCS 12 X 60",
#                                     "base_units": "No.",
#                                     "bom_qty": 6,
#                                     "avl_qty": 370
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "SHCS 12 X 35",
#                                     "base_units": "No.",
#                                     "bom_qty": 6,
#                                     "avl_qty": 251
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "SHCS 10 X 30",
#                                     "base_units": "No.",
#                                     "bom_qty": 4,
#                                     "avl_qty": 532
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "SHCS 5 X 16",
#                                     "base_units": "No.",
#                                     "bom_qty": 5,
#                                     "avl_qty": 683
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "HEX BOLT 16 X 80",
#                                     "base_units": "No.",
#                                     "bom_qty": 4,
#                                     "avl_qty": 124
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "HEX BOLT 12 X 30",
#                                     "base_units": "No.",
#                                     "bom_qty": 2,
#                                     "avl_qty": 416
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "HEX BOLT 10 X 75",
#                                     "base_units": "No.",
#                                     "bom_qty": 8,
#                                     "avl_qty": 271
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "GRUB SCREW 12 X 16",
#                                     "base_units": "No.",
#                                     "bom_qty": 2,
#                                     "avl_qty": 329
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "GRUB SCREW 12 X 12",
#                                     "base_units": "No.",
#                                     "bom_qty": 6,
#                                     "avl_qty": 379
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "GRUB SCREW 10 X 12",
#                                     "base_units": "No.",
#                                     "bom_qty": 2,
#                                     "avl_qty": 435
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "GRUB SCREW 6 X10",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 423
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "GRUB SCREW 5 X 12",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 214
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "GRUB SCREW 5 X 6",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 461
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "HEX NUT M5",
#                                     "base_units": "No.",
#                                     "bom_qty": 2,
#                                     "avl_qty": 1290
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "HEX NUT M24",
#                                     "base_units": "No.",
#                                     "bom_qty": 3,
#                                     "avl_qty": 143
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "Spring Washer 12 Mm",
#                                     "base_units": "No.",
#                                     "bom_qty": 6,
#                                     "avl_qty": 628
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "MS WASHER M12",
#                                     "base_units": "No.",
#                                     "bom_qty": 2,
#                                     "avl_qty": 1663
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "MS WASHER M5",
#                                     "base_units": "No.",
#                                     "bom_qty": 2,
#                                     "avl_qty": 1604
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "ROUND HEAD M/C SCREW 5 X 8",
#                                     "base_units": "No.",
#                                     "bom_qty": 8,
#                                     "avl_qty": 940
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "ROUND HEAD M/C SCREW 3 X 6",
#                                     "base_units": "No.",
#                                     "bom_qty": 4,
#                                     "avl_qty": 1242
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "BEARING 6218 ZZ",
#                                     "base_units": "No.",
#                                     "bom_qty": 2,
#                                     "avl_qty": 17
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "BEARING 51218 BMT",
#                                     "base_units": "No.",
#                                     "bom_qty": 2,
#                                     "avl_qty": 16
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "SOFT DOWEL PIN 8 X 35",
#                                     "base_units": "No.",
#                                     "bom_qty": 2,
#                                     "avl_qty": 196
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "CHAIN 10.1 UTN",
#                                     "base_units": "Fts",
#                                     "bom_qty": 7,
#                                     "avl_qty": 138.50
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "ELE.MOTOR 0.5HP,3 PH,1390RPM(GEAR MOTOR)",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 2
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "SHCS 10 X 30",
#                                     "base_units": "No.",
#                                     "bom_qty": 2,
#                                     "avl_qty": 532
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "Shcs 10 x 90",
#                                     "base_units": "No.",
#                                     "bom_qty": 2,
#                                     "avl_qty": 27
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "SHCS 5 X 40",
#                                     "base_units": "No.",
#                                     "bom_qty": 4,
#                                     "avl_qty": 152
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "SHCS 4 X 20",
#                                     "base_units": "No.",
#                                     "bom_qty": 4,
#                                     "avl_qty": 404
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "CHEES HEAD SCREW M3 X 25",
#                                     "base_units": "No.",
#                                     "bom_qty": 4,
#                                     "avl_qty": 2278
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "CHEES HEAD SCREW M6 X 110",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": -116
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "HEX NUT M6",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 138
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "CSK M/C SCREW 3 X 16",
#                                     "base_units": "No.",
#                                     "bom_qty": 6,
#                                     "avl_qty": 574
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "SHCS 5 X 10",
#                                     "base_units": "No.",
#                                     "bom_qty": 6,
#                                     "avl_qty": 254
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "Shcs 16 x 110",
#                                     "base_units": "No.",
#                                     "bom_qty": 4,
#                                     "avl_qty": 12
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "SHCS 16 X 35",
#                                     "base_units": "No.",
#                                     "bom_qty": 2,
#                                     "avl_qty": 117
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "SHCS 12 X 40",
#                                     "base_units": "No.",
#                                     "bom_qty": 4,
#                                     "avl_qty": 277
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "SHCS 6 X 35",
#                                     "base_units": "No.",
#                                     "bom_qty": 8,
#                                     "avl_qty": 726
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "SHCS 6 X 75",
#                                     "base_units": "No.",
#                                     "bom_qty": 2,
#                                     "avl_qty": -39
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "SHCS 6 X 20",
#                                     "base_units": "No.",
#                                     "bom_qty": 5,
#                                     "avl_qty": 151
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "SHCS 6 X 16",
#                                     "base_units": "No.",
#                                     "bom_qty": 3,
#                                     "avl_qty": 328
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "SHCS 8 X 30",
#                                     "base_units": "No.",
#                                     "bom_qty": 4,
#                                     "avl_qty": 727
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "SHCS 5 X 55",
#                                     "base_units": "No.",
#                                     "bom_qty": 4,
#                                     "avl_qty": 182
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "SHCS 6 X 25",
#                                     "base_units": "No.",
#                                     "bom_qty": 4,
#                                     "avl_qty": 58
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "HEX BOLT 12 X 35",
#                                     "base_units": "No.",
#                                     "bom_qty": 4,
#                                     "avl_qty": 206
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "HEX BOLT 10 X 25",
#                                     "base_units": "No.",
#                                     "bom_qty": 2,
#                                     "avl_qty": -691
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "HEX BOLT 10 X 30",
#                                     "base_units": "No.",
#                                     "bom_qty": 2,
#                                     "avl_qty": 187
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "STRAINER CUM BREATHER ( FSB -05)",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 5
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "YUKEN FLOW CONTROL VALVE FCG-01-4-11",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 4
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "HYDRAULIC VALVE CIT-06-5-2080",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": -1
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "Hy Hose Connection 3/4\" Bsp x 1/4\" Bsp",
#                                     "base_units": "No.",
#                                     "bom_qty": 5,
#                                     "avl_qty": 0
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "Hy Hose Connection 1/4\" Bsp x 1/4\" Bsp",
#                                     "base_units": "No.",
#                                     "bom_qty": 10,
#                                     "avl_qty": 24
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "Hy Hose Connection 1/4\" Bsp x 20 x 1.5",
#                                     "base_units": "No.",
#                                     "bom_qty": 10,
#                                     "avl_qty": 0
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "Hy Hose Connection 3/4\" Bsp x M 20 x 1.5",
#                                     "base_units": "No.",
#                                     "bom_qty": 5,
#                                     "avl_qty": -5
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "Hydraulic Hose 250 Bar Pressure ¼\" Straight At One End-1/4\"BSP Straight at Other End Female Connection. 2500 mm",
#                                     "base_units": "No.",
#                                     "bom_qty": 2,
#                                     "avl_qty": 0
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "ALL.NAME PLATE B-3000 PC",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 84
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "EYE BOLT 12MM",
#                                     "base_units": "No.",
#                                     "bom_qty": 2,
#                                     "avl_qty": 51
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "ALL.NAME PLATE OIL LEVEL",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 48
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "ALL.NAME PLATE ELECTRIC ARROW",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 81
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "ALL.NAME PLATE ELE.EARTH",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": -5
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "ALL.NAME PLATE ELE.STRAGHT ARROW",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 14
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "HOSE PIPE M16 x 1.5 Mtr",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 4
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "GRUB SCREW 6 X 25",
#                                     "base_units": "No.",
#                                     "bom_qty": 3,
#                                     "avl_qty": 71
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "HEX NUT M6",
#                                     "base_units": "No.",
#                                     "bom_qty": 3,
#                                     "avl_qty": 138
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "SHCS 4 X 16",
#                                     "base_units": "No.",
#                                     "bom_qty": 3,
#                                     "avl_qty": 558
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "Hydraulic Hose 250 Bar Pressure ¼” BSP Elbow at One End  & ¼” BSP Straight at Other End Female 2500 mm Length",
#                                     "base_units": "No.",
#                                     "bom_qty": 2,
#                                     "avl_qty": 0
#                                 }
#                             ]
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "Elecetrical & Electronic Assembly B 3000 Inline",
#                             "base_units": "No.",
#                             "bom_qty": 1,
#                             "avl_qty": 0,
#                             "machinery_components": [
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "M S CHANNEL 13\"",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": -47
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "CONNECTOR CST 6",
#                                     "base_units": "No.",
#                                     "bom_qty": 37,
#                                     "avl_qty": 1
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "RELAY 2C/0 12D PLA (Fie)",
#                                     "base_units": "No.",
#                                     "bom_qty": 2,
#                                     "avl_qty": 11
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "CAPACITOR 220/25V (Fie)",
#                                     "base_units": "No.",
#                                     "bom_qty": 2,
#                                     "avl_qty": 14
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "16 AMP FUSE",
#                                     "base_units": "No.",
#                                     "bom_qty": 3,
#                                     "avl_qty": 26
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "FUSE HOLDER 20 H CNS C&S MAKE",
#                                     "base_units": "No.",
#                                     "bom_qty": 3,
#                                     "avl_qty": 1
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "CONTACTOR TC 10 AMP ( LC1- D099)",
#                                     "base_units": "No.",
#                                     "bom_qty": 3,
#                                     "avl_qty": 6
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "ROTARY S/W ON-OFF ACP1034",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": -2
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "RELAY 1 TO 1.6 TC  ( LR1- D09306)",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 0
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "RELAY 0.63 TO 1 TC  ( TR2- D09305)",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 22
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "MICRO SWITCH KAYCEE KIA5431-04",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 0
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "MICRO SWITCH KAYCEE K1B-20",
#                                     "base_units": "No.",
#                                     "bom_qty": 2,
#                                     "avl_qty": 17
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "MICRO SWITCH ZIPPY",
#                                     "base_units": "No.",
#                                     "bom_qty": 2,
#                                     "avl_qty": 127
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "EMERGENCY SWITCH RED (STEY PUT )",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 2
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "AUTO CABLE 1 Mmsq GRAY WIRE",
#                                     "base_units": "Mtr.",
#                                     "bom_qty": 30,
#                                     "avl_qty": -52
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "Polycab WIRE FOUR CORE 1.5 Sq mm",
#                                     "base_units": "Fts",
#                                     "bom_qty": 65,
#                                     "avl_qty": -199
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "Polycab WIRE FOUR CORE 0.75 Sq mm",
#                                     "base_units": "Fts",
#                                     "bom_qty": 27,
#                                     "avl_qty": 551
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "Polycab WIRE TWO CORE 0.75 Sq mm",
#                                     "base_units": "Fts",
#                                     "bom_qty": 40,
#                                     "avl_qty": 218.50
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "AUTO CABLE 1 Mmsq BLACK WIRE",
#                                     "base_units": "Mtr.",
#                                     "bom_qty": 5,
#                                     "avl_qty": 91
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "AUTO CABLE 1 Mmsq BLUE WIRE",
#                                     "base_units": "Mtr.",
#                                     "bom_qty": 5,
#                                     "avl_qty": 414
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "AUTO CABLE 1 Mmsq GREEN WIRE",
#                                     "base_units": "Mtr.",
#                                     "bom_qty": 5,
#                                     "avl_qty": 63.80
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "AUTO CABLE 1 Mmsq RED WIRE",
#                                     "base_units": "Mtr.",
#                                     "bom_qty": 5,
#                                     "avl_qty": 405
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "AUTO CABLE 1 Mmsq WHITE WIRE",
#                                     "base_units": "Mtr.",
#                                     "bom_qty": 5,
#                                     "avl_qty": 497
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "AUTO CABLE 1 Mmsq YELLOW WIRE",
#                                     "base_units": "Mtr.",
#                                     "bom_qty": 5,
#                                     "avl_qty": 397
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "AUTO CABLE 1.5 Sqmm YELLOW",
#                                     "base_units": "Mtr.",
#                                     "bom_qty": 6,
#                                     "avl_qty": 16
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "AUTO CABLE 1.5 Sqmm BLUE",
#                                     "base_units": "Mtr.",
#                                     "bom_qty": 6,
#                                     "avl_qty": 166
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "AUTO CABLE 1.5 Sqmm RED",
#                                     "base_units": "Mtr.",
#                                     "bom_qty": 6,
#                                     "avl_qty": 16
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "SOCKET PG 13.5 15MM",
#                                     "base_units": "No.",
#                                     "bom_qty": 3,
#                                     "avl_qty": -123
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "PVC HOSE PIPE 15 MM",
#                                     "base_units": "Fts",
#                                     "bom_qty": 8,
#                                     "avl_qty": -154
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "NEXGENIE-1000 PLC and Load Cell Interface Module.",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 0
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "Timer Selec Make 220v Ac Model 800XA",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": -1
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "Relay Modual 8way  24vdc 1 C/O with Socket",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": -1
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "BOHAMAN LIMIT SWITCH LSR",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 5
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "SMPS 10A 24VDC (EOE12010005)",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": -1
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "Meanwell Smps Net 35 B",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": -4
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "TRANSFORMER UTE 0-440V, 230V, 0.5 AMP",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 15
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "Isolation Transformer 2kva,Pri 415volt Sec 200v",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 0
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "2 A SPDT GILLARD SWITCH",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 109
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "PUSH BOTTON ELCOM MPS1 4A 250V",
#                                     "base_units": "No.",
#                                     "bom_qty": 3,
#                                     "avl_qty": 0
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "CCD CAMERA WATEC 660D P-3.7",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 3
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "VIDEO CAPTURE CARD",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 3
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "OBJECTIVE 4X",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 20
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "LED HOLDER 5MM",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 205
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "LED 5MM",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 1250
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "5 PIN AUDIO FEMALE CONNECTOR",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": -23
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "5 PIN AUDIO  MALE CONNECTOR",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": -7
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "9 PIN D TYPE WIRE SOL FEMALE CONN",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 235
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "9 PIN DUST COVER",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 598
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "HEAT SHRINK SLEEVE",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 999
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "TOGGLE SWITCH 713-21B DPST 4.5 A BLACK",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": -37
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "ELEMENT S2",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 4
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "SOCKET PG-29",
#                                     "base_units": "No.",
#                                     "bom_qty": 3,
#                                     "avl_qty": 47
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "SOCKET PG 13.5 15MM",
#                                     "base_units": "No.",
#                                     "bom_qty": 2,
#                                     "avl_qty": -123
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "METAL CLUOD PLUG 20 AMP 3 POLE  BP 20",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 5
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "Expansion 8 I/p, 8 O/p 24 VDC ( NE16DX)",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": -1
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "CHEES HEAD SCREW M4 X 6",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 6123
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "SOFT DOWEL PIN 8 X 25",
#                                     "base_units": "No.",
#                                     "bom_qty": 2,
#                                     "avl_qty": 218
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "SHCS 10 X 50",
#                                     "base_units": "No.",
#                                     "bom_qty": 5,
#                                     "avl_qty": 195
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "CHEES HEAD SCREW M5 X 16",
#                                     "base_units": "No.",
#                                     "bom_qty": 4,
#                                     "avl_qty": 834
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "CHEES HEAD SCREW M5 X 12",
#                                     "base_units": "No.",
#                                     "bom_qty": 6,
#                                     "avl_qty": 1297
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "CHEES HEAD SCREW M4 X 16",
#                                     "base_units": "No.",
#                                     "bom_qty": 8,
#                                     "avl_qty": 1227
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "CHEES HEAD SCREW M4 X 12",
#                                     "base_units": "No.",
#                                     "bom_qty": 12,
#                                     "avl_qty": 2037
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "CHEES HEAD SCREW M4 X 8",
#                                     "base_units": "No.",
#                                     "bom_qty": 40,
#                                     "avl_qty": 396
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "CHEES HEAD SCREW M3 X 25",
#                                     "base_units": "No.",
#                                     "bom_qty": 20,
#                                     "avl_qty": 2278
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "CHEES HEAD SCREW M3 X 16",
#                                     "base_units": "No.",
#                                     "bom_qty": 8,
#                                     "avl_qty": -4
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "CHEES HEAD SCREW M3 X 10",
#                                     "base_units": "No.",
#                                     "bom_qty": 4,
#                                     "avl_qty": 3091
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "BHCS 4 X 12",
#                                     "base_units": "No.",
#                                     "bom_qty": 6,
#                                     "avl_qty": 438
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "BHCS 3 X 10",
#                                     "base_units": "No.",
#                                     "bom_qty": 4,
#                                     "avl_qty": -27
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "ROUND HEAD M/C SCREW 3 X 30",
#                                     "base_units": "No.",
#                                     "bom_qty": 2,
#                                     "avl_qty": 562
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "HEX NUT M12",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 1064
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "HEX NUT M4",
#                                     "base_units": "No.",
#                                     "bom_qty": 4,
#                                     "avl_qty": 3053
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "HEX NUT M3",
#                                     "base_units": "No.",
#                                     "bom_qty": 20,
#                                     "avl_qty": 4852
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "SPRING WASHER 5MM",
#                                     "base_units": "No.",
#                                     "bom_qty": 10,
#                                     "avl_qty": 3396
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "SPRING WASHER 4 MM",
#                                     "base_units": "No.",
#                                     "bom_qty": 20,
#                                     "avl_qty": 286
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "SPRING WASHER 3MM",
#                                     "base_units": "No.",
#                                     "bom_qty": 32,
#                                     "avl_qty": 6972
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "MS WASHER M12",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 1663
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "MS WASHER M5",
#                                     "base_units": "No.",
#                                     "bom_qty": 4,
#                                     "avl_qty": 1604
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "MS WASHER M4 (BIG)",
#                                     "base_units": "No.",
#                                     "bom_qty": 20,
#                                     "avl_qty": 1567
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "MS WASHER M3",
#                                     "base_units": "No.",
#                                     "bom_qty": 32,
#                                     "avl_qty": 3548
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "BRASS NUT M6",
#                                     "base_units": "No.",
#                                     "bom_qty": 4,
#                                     "avl_qty": 1153
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "BRASS WASHER M6",
#                                     "base_units": "No.",
#                                     "bom_qty": 8,
#                                     "avl_qty": 957
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "CHEES HEAD SCREW M6 X 65(BRASS)",
#                                     "base_units": "No.",
#                                     "bom_qty": 4,
#                                     "avl_qty": 98
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "NYLON BUSH 3MM",
#                                     "base_units": "No.",
#                                     "bom_qty": 20,
#                                     "avl_qty": 8169
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "RUBBER GOAT DIA. 16MM",
#                                     "base_units": "No.",
#                                     "bom_qty": 7,
#                                     "avl_qty": -69
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "All Name Plate Fie B 3000 Inline ( Spl)",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 1
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "BHCS 5 X 20",
#                                     "base_units": "No.",
#                                     "bom_qty": 30,
#                                     "avl_qty": 140
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "BHCS 5 X 8",
#                                     "base_units": "No.",
#                                     "bom_qty": 14,
#                                     "avl_qty": 479
#                                 }
#                             ]
#                         },
#                         {
#                             "bom_level": 3,
#                             "spare_name": "Packing Assembly B 3000 Inline",
#                             "base_units": "No.",
#                             "bom_qty": 1,
#                             "avl_qty": -2,
#                             "machinery_components": [
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "Tool Assembly UTE 100",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 1,
#                                     "machinery_components": [
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "ALLEN KEY 14MM",
#                                             "base_units": "No.",
#                                             "bom_qty": 1,
#                                             "avl_qty": 9
#                                         },
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "ALLEN KEY 2MM",
#                                             "base_units": "No.",
#                                             "bom_qty": 1,
#                                             "avl_qty": 98
#                                         },
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "ALLEN KEY 3MM",
#                                             "base_units": "No.",
#                                             "bom_qty": 1,
#                                             "avl_qty": 228
#                                         },
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "ALLEN KEY 4MM(PB)",
#                                             "base_units": "No.",
#                                             "bom_qty": 1,
#                                             "avl_qty": -111
#                                         },
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "ALLEN KEY 5MM",
#                                             "base_units": "No.",
#                                             "bom_qty": 1,
#                                             "avl_qty": 170
#                                         },
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "ALLEN KEY 6MM",
#                                             "base_units": "No.",
#                                             "bom_qty": 1,
#                                             "avl_qty": 99
#                                         },
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "ALLEN KEY 8MM",
#                                             "base_units": "No.",
#                                             "bom_qty": 1,
#                                             "avl_qty": 69
#                                         },
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "D/E SPANNER 12 X 13",
#                                             "base_units": "No.",
#                                             "bom_qty": 1,
#                                             "avl_qty": 27
#                                         },
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "D/E SPANNER 17 X 19",
#                                             "base_units": "No.",
#                                             "bom_qty": 1,
#                                             "avl_qty": -1
#                                         },
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "D/E SPANNER 22 X 24",
#                                             "base_units": "No.",
#                                             "bom_qty": 1,
#                                             "avl_qty": 34
#                                         },
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "D/E SPANNER 30 X 32",
#                                             "base_units": "No.",
#                                             "bom_qty": 1,
#                                             "avl_qty": 26
#                                         },
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "D/E SPANNER 6 X 7",
#                                             "base_units": "No.",
#                                             "bom_qty": 1,
#                                             "avl_qty": 120
#                                         },
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "D/E SPANNER 8 X 10",
#                                             "base_units": "No.",
#                                             "bom_qty": 1,
#                                             "avl_qty": 86
#                                         },
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "SCREW DRIVER 6\"/606 FL",
#                                             "base_units": "No.",
#                                             "bom_qty": 1,
#                                             "avl_qty": 78
#                                         },
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "O RING SET ASSEMBLY",
#                                             "base_units": "No.",
#                                             "bom_qty": 1,
#                                             "avl_qty": 35,
#                                             "machinery_components": [
#                                                 {
#                                                     "bom_level": 6,
#                                                     "spare_name": "O RING 10 X 16 X  3",
#                                                     "base_units": "No.",
#                                                     "bom_qty": 1,
#                                                     "avl_qty": 112
#                                                 },
#                                                 {
#                                                     "bom_level": 6,
#                                                     "spare_name": "O RING 24 X 28 X 2",
#                                                     "base_units": "No.",
#                                                     "bom_qty": 1,
#                                                     "avl_qty": 140
#                                                 },
#                                                 {
#                                                     "bom_level": 6,
#                                                     "spare_name": "O RING 30 X 35 X 2.5",
#                                                     "base_units": "No.",
#                                                     "bom_qty": 1,
#                                                     "avl_qty": 143
#                                                 },
#                                                 {
#                                                     "bom_level": 6,
#                                                     "spare_name": "O RING 7 X 11 X 2",
#                                                     "base_units": "No.",
#                                                     "bom_qty": 2,
#                                                     "avl_qty": 197
#                                                 }
#                                             ]
#                                         },
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "ALLEN KEY 10MM",
#                                             "base_units": "No.",
#                                             "bom_qty": 1,
#                                             "avl_qty": 32
#                                         },
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "ALLEN KEY 17 MM",
#                                             "base_units": "No.",
#                                             "bom_qty": 1,
#                                             "avl_qty": 42
#                                         },
#                                         {
#                                             "bom_level": 5,
#                                             "spare_name": "ALLEN KEY 2.5MM",
#                                             "base_units": "No.",
#                                             "bom_qty": 1,
#                                             "avl_qty": 253
#                                         }
#                                     ]
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "POLY COVER 2\" X 2\" X 4\"",
#                                     "base_units": "Kgs",
#                                     "bom_qty": 0.80,
#                                     "avl_qty": 2.065
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "POLY COVER 3 1/2\" X 3 1/2\" X 7\"",
#                                     "base_units": "Kgs",
#                                     "bom_qty": 2,
#                                     "avl_qty": -1.44
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "POLY COVER 3 1/4\" X 3 1/4\" X 4 1/4\"",
#                                     "base_units": "Kgs",
#                                     "bom_qty": 1.20,
#                                     "avl_qty": -27.60
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "PLASTIC BAG 10 X 12",
#                                     "base_units": "Kgs",
#                                     "bom_qty": 1,
#                                     "avl_qty": 49.01
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "PLASTIC PAPER LOOS",
#                                     "base_units": "Kgs",
#                                     "bom_qty": 2,
#                                     "avl_qty": -25.525
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "NYLON BAG",
#                                     "base_units": "No.",
#                                     "bom_qty": 12,
#                                     "avl_qty": 0
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "SILICA GEL",
#                                     "base_units": "Kgs",
#                                     "bom_qty": 1.50,
#                                     "avl_qty": -1.10
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "MANUAL B-3000 PC",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 2
#                                 },
#                                 {
#                                     "bom_level": 4,
#                                     "spare_name": "B 3000 Pc Inline Packing (Base Only)",
#                                     "base_units": "No.",
#                                     "bom_qty": 1,
#                                     "avl_qty": 0
#                                 }
#                             ]
#                         }
#                     ]
#                 }
#             ]
#         },
#     ]}
#
# # def alogrith():
#     # bm = {'total': 0}
#     #
#     # def iterdict2(data):
#     #     for i in range(len(data)):
#     #         # print(data[i])
#     #         if 'machinery_components' in data[i]:
#     #             if type(data[i]['machinery_components']) == list:
#     #                 # print(len(data[i]['machinery_components']) , "BOM :: " , data[i]['bom_qty'])
#     #                 # print("+++++++++++++++++++++++++++++++++++++++++++++++")
#     #                 # print("SECOND LOOP", data[i]['bom_qty'])
#     #                 # main_total = data[i]['bom_qty']
#     #                 for j in data[i]['machinery_components']:
#     #                     # bm['total'] *= main_total
#     #                     if 'machinery_components' in data[i]['machinery_components']:
#     #                         if type(j['machinery_components']) == list:
#     #                             iterdict(j['machinery_components'])
#     #                     if j['bom_level'] == 3:
#     #                         # print("spare_name",j["spare_name"])
#     #                         bm['total'] += j['bom_qty']
#     #                         # print("TOTAL ", bm['total'])
#     #                     else:
#     #                         # bm['total'] += j['bom_qty']
#     #                         print(bm['total'])
#     #
#     #                         # bm['total'] += j['bom_qty']
#     #                         # print("TOTAL ", bm['total'])
#     #
#     #                 iterdict2(data[i]['machinery_components'])
#     #                 # iterdict2(data[i]['machinery_components'])
#     #
#     # assembly = []
#     #
#     # def iterdict(data):
#     #     for i in range(len(data)):
#     #         if 'machinery_components' in data[i]:
#     #             if type(data[i]['machinery_components']) == list:
#     #                 iterdict2(data[i]['machinery_components'])
#     #                 for j in data[i]['machinery_components']:
#     #                     try:
#     #                         for k in j['machinery_components']:
#     #                             if 'machinery_components' not in k:
#     #                                 # only level 3
#     #                                 # print("bvgvb")
#     #                                 # new = 0
#     #                                 # new += k['bom_qty']
#     #                                 # print("new",new)
#     #                                 assembly.append(
#     #                                     {'machine_name': data[i]['machine_name'],
#     #                                      'spare_name': k['spare_name'], 'bom_qty': k['bom_qty']})
#     #                             else:
#     #                                 # print("last",bm['total'])
#     #                                 assembly.append(
#     #                                     {'machine_name': data[i]['machine_name'],
#     #                                      'spare_name': k['spare_name'], 'bom_qty': bm['total']})
#     #                                 bm['total'] = 0
#     #                                 # iterdict2(data[i]['machinery_components'])
#     #
#     #                     except:
#     #                         pass
#     #
#     #     print("ASSEMBLY ..", assembly)
#     #
#     # iterdict(data['machinery_components'])
# b = 0
# def sum_nested_level(val, bom_val):
#     global b
#     b += bom_val
#     for key, value in val.items():
#         if key == 'machinery_components':
#             for i in range(len(value)):
#                 time.sleep(0.05)
#                 sum_nested_level(value[i], value[i]['bom_qty'])
#
# mc  = []
# prim =[]
#
# def check_compo(key, value):
#     global b
#     global mc_name
#     primary_items = ''
#     if key == 'machinery_components':
#         for i in range(len(value)):
#             if 'machine_name' in  value[i]:
#                 mc_name = value[i]['machine_name']
#                 # print('mc_name',mc_name)
#             if 'Primary_Item' in value[i]:
#                 primary_items = value[i]['Primary_Item']
#                 spare_item = value[i]['spare_name']
#                 # print(primary_items)
#                 prim.append({"primary_items":primary_items,'spare_item':value[i]['spare_name']})
#
#
#             if value[i]['bom_level'] == 3:
#                 # print("<", i, ">", value[i])
#                 sum_nested_level(value[i], value[i]['bom_qty'])
#                 value[i]['total_bom_qty'] = b
#                 mc.append({'total_bom_qty' : b ,"primary_items":primary_items, 'spare_name' :value[i]['spare_name'] ,'machine_name': mc_name })
#                 # print("B :: ", b)
#                 b = 0
#             time.sleep(0.05)
#             for key1, value2 in value[i].items():
#                 check_compo(key1, value2)
#
# for key, value in data.items():
#     check_compo(key, value)
# # for name , number in value:
# #     print("Parent Key " + key + " Child name " + name + " Child number " + number)
#
# # print("Changed Data is : ",data)
# print(prim)
# # pprint(mc)
#
def find_primary_key():
    data = {}
    meta = []
    doc = machinery_components.find({}, {"_id": 0})
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
                    prime_item.append({"primary_items": primary_items})

                for key1, value2 in value[i].items():
                    check_compo(key1, value2)

    for key, value in data.items():
        check_compo(key, value)
    # print(prime_item)
    return prime_item


# find_primary_item()

def volume1():
    prime = gap_calculator.find({}, {"_id": 0}).distinct("primary_item")
    prime.pop(0)
    # print(prime)
    for i in range(0, len(prime)):
        # print(prime[i])
        sum_sales_order = gap_calculator.aggregate([{"$match": {"primary_item": prime[i]}},
                                                    {"$group": {
                                                        "_id": "$live_sales",
                                                        "actual_required": {"$first": {"$toInt": "$actual_required"}},
                                                        "wip_qty": {"$sum": {"$toInt": "$wip_qty"}},
                                                        "finish_stock": {"$sum": {"$toInt": "$finish_stock"}},
                                                        "issued_qty": {"$sum": {"$toInt": "$issued_qty"}},
                                                        # "final_order": {"$sum": {"$toInt": "$final_order"}},
                                                        "supplier_list": {"$push": "$supplier_list"},
                                                        "Cumulative_data": {"$first": {"$toInt": "$Cumulative_data"}},
                                                    }}, {"$project": {"_id": 0,
                                                                      "machine": "",
                                                                      "parts": prime[i],
                                                                      "live_sales": "$_id",
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
                                                                      "Cumulative_data": "$Cumulative_data",
                                                                      "primary_item": "",

                                                                      }}
                                                    ])

        for j in sum_sales_order:
            print(j)
            # gap_calculator.insert_one(j)
        # print(prime[i])
    # for k in range(0, len(prime)):
    #     print(prime[k])
    # gap_calculator.remove({"primary_item":prime[k]})
    # for value in set(v for d in primary_item for v in d.values()):
    #     # print(value)
    #     gap_calculator.remove([{"$match":{"primary_item": value}}])

    # x = list(set(val for dic in primary_item for val in dic.values()))
    # # print(x[0])
    #
    # for j in range(len(x)):
    #     print(x[j])
    #     gap_data = gap_calculator.find_one({"primary_item": "ECCENTRIC PIN"}, {"_id": 0})
    #     print(gap_data)
    #     if gap_data is None:
    #         pass
    #     else:
    #         actual_required = gap_data['actual_required']
    #         wip_data += gap_data["wip_qty"]
    #         finish_data +=  gap_data["finish_stock"]
    #         issued_qty += gap_data["issued_qty"]
    #         final_order = actual_required - (wip_data) -(finish_data) -(issued_qty)
    #         supplier_list.extend(gap_data['supplier_list'])
    #         Cumulative_data += gap_data["Cumulative_data"]

    # if gap_data["primary_item"] == value:
    #     print(value)

    # gap_new_dict = {"machine": "",
    #             "parts": value,
    #             "live_sales": gap_data['total_required'],
    #             "production": 0,
    #             "actual_required": gap_data['total_required'] + 0,
    #             "wip_qty": wip_data,
    #             "finish_stock": finish_data,
    #             "issued_qty": issued_qty,
    #             "final_order": final_order,
    #             "supplier_list": supplier_list,
    #             "Cumulative_data": Cumulative_data,
    #             "primary_item": ''
    #             }
    #
    #
    # #
    # # print(actual_required)
    #   print(wip_data)
    # # print(finish_data)
    # # print(issued_qty)
    # # print(final_order)

    # for i in primary_item:
    #     # print("*****************************************")
    #     gap_calculator.update_one({"parts": i['primary_items']},
    #                                                         {"$set": {"actual_required": actual_required,'wip_qty':
    #                                                             wip_data,'finish_stock':finish_data,"issued_qty":issued_qty,"final_order":final_order,'Cumulative_data':Cumulative_data,"supplier_list":supplier_list}})
    #
    #     gap_data = gap_calculator.find_one({'parts': i['spare_item']}, {"_id": 0})
    #     if gap_data is None:
    #         pass
    #     else:
    #         # print(gap_data)
    #         uni.append(gap_data['parts'])
    #     # gap_calculator.delete_one(gap_data['parts'])
    # print(uni)
    # check = np.array(uni)
    # spare_name = np.unique(check)
    # for i in range(len(spare_name)):
    #     print("spare",spare_name[i])
    #     gap_calculator.remove({"parts":spare_name[i]})


volume1()

# def find_cumulative():
#     # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#     # print("________________________________",machine_name)
#     data = {}
#     for i in range(0, 1):
#         uniqe_data = machinery_components.find({'machine_name': "ROCKWELL HARDNESS TESTER(RASN)"}, {'_id': 0})
#         for doc in uniqe_data:
#             data["machinery_components"] = [doc]
#     # print(data)
#     global b
#     b = 0
#     def sum_nested_level(val, bom_val):
#         global b
#         b += bom_val
#         for key, value in val.items():
#             if key == 'machinery_components':
#                 for i in range(len(value)):
#                     time.sleep(0.05)
#                     if 'Primary_Item' in value[i]:
#                         sum_nested_level(value[i], value[i]['bom_qty'])
#
#     mc = []
#
#     def check_compo(key, value):
#         global b
#         global mc_name
#         if key == 'machinery_components':
#             for i in range(len(value)):
#                 if 'machine_name' in value[i]:
#                     mc_name = value[i]['machine_name']
#                     # print('mc_name', mc_name)
#                 if value[i]['bom_level'] == 3:
#                     if 'Primary_Item' in value[i]:
#                         sum_nested_level(value[i], value[i]['bom_qty'])
#                         value[i]['total_bom_qty'] = b
#                         mc.append({"primary_items" : value[i]['Primary_Item'],'total_bom_qty': b, 'spare_name': value[i]['spare_name'], 'machine_name': mc_name})
#                     # print("B :: ", b)
#                         b = 0
#                 time.sleep(0.05)
#                 for key1, value2 in value[i].items():
#                     check_compo(key1, value2)
#
#     for key, value in data.items():
#         check_compo(key, value)
#     # for name , number in value:
#     #     print("Parent Key " + key + " Child name " + name + " Child number " + number)
#
#     # print("Changed Data is : ", data)
#     print(mc)
#
#
#     # return mc
#
#
# find_cumulative()
