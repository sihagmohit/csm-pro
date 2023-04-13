'''SOFTWARE GENERAL'''

timezone_offset = 0
time_format = "%d/%m/%Y, %H:%M:%S"

spr_time_format = "%H:%M:%S"
only_date = "%d/%m/%Y"



cron_job_time = 10
kpi_cron_job_time = 10

'''PRODUCTION PLAN'''
production_plan_limit = 50

A_shift_start_time = "06:00:00"
A_shift_end_time = "14:00:00"

B_shift_start_time = "14:00:00"
B_shift_end_time = "22:00:00"

C_shift_start_time = "22:00:00"
C_shift_end_time = "06:00:00"

PQCR_timings = ["00:00:00", "04:00:00", "08:00:00", "12:00:00", "16:00:00", "20:00:00"]
PQCR_threshold = 30

shift_data = {
    "INJECTION PRESSURE": ["1_IP", "2_IP", "3_IP", "4_IP", "5_IP", "6_IP"],
    "INJECTION SPEED": ["1_IS", "2_IS", "3_IS", "4_IS", "5_IS", "6_IS"],
    "INJECTION POSITION": ["1_IV", "2_IV", "3_IV", "4_IV", "5_IV", "6_IV"],
    "HOLDING PRESSURE": ["1_HP", "2_HP", "3_HP", "4_HP", "5_HP", "6_HP"],
    "HOLDING TIME": ["1_HT", "2_HT", "3_HT", "4_HT", "5_HT", "6_HT"],
    "BARREL TEMP": ["1_BT", "2_BT", "3_BT", "4_BT", "", "", "", "", "", "", "", ""],
    "REFILLING PRESSURE": ["1_RF", "2_RF", "3_RF"],
    "FILL TIME": ["1_FT"],
    "CUSHION": ["1_C"],
    "MATERIAL PRE HEATING TEMP": ["1_M"],
    "COOLING TIME": ["1_C"],
    "SHOT SIZE/ MATERIAL FEED": ["1_SS"],
    "REFILLING TIME": ["1_RT"],
    "HOT RUNNER TEMP": ["1_HR", "2_HR", "3_HR", "", "", "", "", "", "", "", "",
                        "", "", "", "", "", "", "", "", "", "", "",
                        "", "", "", "", "", "", "", "", "", ""],
    "N2 GAS PRESSURE": ["1_N2", "2_N2", "3_N2"]
}

PQCR_start = "00:00:00"
PQCR_duration = 24

PQCR_chart_refresh_time = 30
PQCR_readings_list = 20
PQCR_chart_last_known_threshold = 24 * 60 * 60
PQCR_mapping = {
    "INJECTION PRESSURE": "Inj  Press [MPa]",
    "INJECTION POSITION": "Inj start Pos [mm]",
    "HOLDING PRESSURE": "H P Trans Prs [MPa]",
    "BARREL TEMP 1": "NH Temp [°C]",
    "BARREL TEMP 2": "H1 Temp [°C]",
    "BARREL TEMP 3": "H2 Temp [°C]",
    "BARREL TEMP 4": "H3 Temp [°C]",
    "BARREL TEMP 5": "H4 Temp [°C]",
    "REFILLING PRESSURE": "Back Press [MPa]",
    "FILL TIME": 'Inj  Time [s]',
    "CUSHION": "Cushion [mm]",
    "REFILLING TIME": "Recovery T [s]",
}
PQCR_unknown_mapping = {
    "INJECTION SPEED": "NA",
    "HOLDING TIME": "NA",
    "HOT RUNNER TEMP": "NA",
    "MATERIAL PRE HEATING TEMP": "NA",
    "N2 GAS PRESSURE": "",
}
PQCR_JSON = [
    {"parameter": "INJECTION PRESSURE", "current_value": "NA", "trend": [0] * PQCR_readings_list,
     "source": "Software", "color": "#e8f2fc", "border": "#0358a0", "unit": "[MPa]", "Last_Update": "NA"},
    {"parameter": "INJECTION SPEED", "current_value": "NA",
     "trend": [0] * PQCR_readings_list, "source": "Software", "color": "#e0f9d1",
     "border": "#27ad66", "unit": "NA", "Last_Update": "NA"},
    {"parameter": "INJECTION POSITION", "current_value": "NA", "trend": [0] * PQCR_readings_list,
     "source": "Software", "color": "#e8f2fc", "border": "#0358a0", "unit": "[mm]", "Last_Update": "NA"},
    {"parameter": "HOLDING PRESSURE", "current_value": "NA", "trend": [0] * PQCR_readings_list,
     "source": "Software", "color": "#e0f9d1", "border": "#27ad66", "unit": "[MPa]", "Last_Update": "NA"},
    {"parameter": "HOLDING TIME", "current_value": "NA", "trend": [0] * PQCR_readings_list,
     "source": "Software", "color": "#F2D8C7", "border": "#AA907A", "unit": "NA", "Last_Update": "NA"},
    {"parameter": "BARREL TEMP 1", "current_value": "NA", "trend": [0] * PQCR_readings_list,
     "source": "Software", "color": "#e8f2fc", "border": "#0358a0", "unit": "[°C]", "Last_Update": "NA"},
    {"parameter": "BARREL TEMP 2", "current_value": "NA", "trend": [0] * PQCR_readings_list,
     "source": "Software", "color": "#e8f2fc", "border": "#0358a0", "unit": "[°C]", "Last_Update": "NA"},
    {"parameter": "BARREL TEMP 3", "current_value": "NA", "trend": [0] * PQCR_readings_list,
     "source": "Software", "color": "#e0f9d1", "border": "#27ad66", "unit": "[°C]", "Last_Update": "NA"},
    {"parameter": "BARREL TEMP 4", "current_value": "NA", "trend": [0] * PQCR_readings_list,
     "source": "Software", "color": "#e8f2fc", "border": "#0358a0", "unit": "[°C]", "Last_Update": "NA"},
    {"parameter": "BARREL TEMP 5", "current_value": "NA",
     "trend": [0] * PQCR_readings_list, "source": "Software", "color": "#e0f9d1",
     "border": "#27ad66", "unit": "[°C]", "Last_Update": "NA"},
    {"parameter": "HOT RUNNER TEMP", "current_value": "NA", "trend": [0] * PQCR_readings_list,
     "source": "Software", "color": "#F2D8C7", "border": "#AA907A", "unit": "[°C]", "Last_Update": "NA"},
    {"parameter": "REFILLING PRESSURE", "current_value": "NA", "trend": [0] * PQCR_readings_list,
     "source": "Software", "color": "#e8f2fc", "border": "#0358a0", "unit": "[°C]", "Last_Update": "NA"},
    {"parameter": "FILL TIME", "current_value": "NA",
     "trend": [0] * PQCR_readings_list, "source": "Software", "color": "#e0f9d1",
     "border": "#27ad66", "unit": "[s]", "Last_Update": "NA"},
    {"parameter": "CUSHION", "current_value": "NA", "trend": [0] * PQCR_readings_list,
     "source": "Software", "color": "#e8f2fc", "border": "#0358a0", "unit": "[mm]", "Last_Update": "NA"},
    {"parameter": "MATERIAL PRE HEATING TEMP", "current_value": "NA", "trend": [0] * PQCR_readings_list,
     "source": "Software", "color": "#e0f9d1", "border": "#27ad66", "unit": "[°C]", "Last_Update": "NA"},
    {"parameter": "REFILLING TIME", "current_value": "NA", "trend": [0] * PQCR_readings_list,
     "source": "Software", "color": "#F2D8C7", "border": "#AA907A", "unit": "[s]", "Last_Update": "NA"},
    {"parameter": "N2 GAS PRESSURE", "current_value": "NA", "trend": [0] * PQCR_readings_list,
     "source": "Software", "color": "#F2D8C7", "border": "#AA907A", "unit": "[MPa]", "Last_Update": "NA"}]

'''Minutes'''
shift_duration = 480
empty_production_orders = []

'''Downtimes'''

downtime_type = ["Startup Time", "Mould Change", "Power Cut", "Holiday Startup", "Breakdown", "Trial",
                 "No Plan", "Software"]

downtime_time = [0, 0, 0, 0, 0, 0, 0, 0]

'''Rejection '''
rejection_type = ["AIR BUBBLE", "GAS MARK", "BLACK DOT", "PATCH MARK", "PIN MARK", "SCRATCH", "MOISTURE",
                  "BLACK FLOW", "BLACK MARK", "WILD LINE", "POWER CUT REJECTION", "SHORT MOLDING", "SILVER",
                  "SINK MARK", "BURN MARK", "OIL MARK", "FLOW MARK"]
rejection_qty = [0, 0, 0, 0, 0, 0, 0,
                 0, 0, 0, 0, 0, 0,
                 0, 0, 0, 0]

""" SPR STRUCTURE """
SPR = {
    "DATE": "",
    "SHIFT": "",
    "MACHINE": "",
    "TEAM LEADER": "",
    "TEAM MEMBERS": "",
    "PLANT": "PLANT III",
    "DEPARTMENT HEAD": "",

    "SECTION 1": {

        "ORDER_NUMBER_RIGHT": "",
        "PLAN QTY_RIGHT": "",  # NEW QTY
        "ACTUAL OK QTY_RIGHT": "",  # ACTUAL QTY - len(REJECTIONS)
        "GAP_RIGHT": "",  # NEW QTY - ACTUAL OK QTY
        "STARTUP_REJECTION_KG (RIGHT)": "",  # STARTUP REJECTION LEFT

        "ORDER_NUMBER_LEFT": "",
        "PLAN QTY_LEFT": "",  # NEW QTY
        "ACTUAL OK QTY_LEFT": "",  # ACTUAL QTY - len(REJECTIONS)
        "GAP_LEFT": "",  # NEW QTY - ACTUAL OK QTY
        "STARTUP_REJECTION_KG (LEFT)": "",  # STARTUP REJECTION LEFT

        "STARTUP_SCRAP_KG": "",  # SUM OF LEFT + RIGHT
        "TOTAL_STARTUP_REJECTION_KG": "",  # TOTAL STARTUP REJECTION

        "TOTAL_LINE_REJECTION_QTY": "",  # TOTAL_LINE_REJECTION_QTY
        "TOTAL_LINE_REJECTION_WEIGHT": "",  # SUM OF ALL LINE REJECTIONS KG
        "PROCESS SCRAP": "",  # PROCESS_SCRAP

    }

}

# adding limits for datatables in constants  # done by SNB  # please note
limit_orders = 100

# RELATIVE ENDPOINTS TO OTHER SOFTWARES
cbm_api_endpoint = "http://15.207.74.145"
trace_api_endpoint = "http://65.0.111.81"
fleet_api_endpoint = "http://15.206.242.16"
oee_api_endpoint = "http://65.0.90.213"

# ideal parameters

OEE = 90
A = 90
P = 90
Q = 90

spr_roles = ["Super-Admin"]

pqcr_roles = ["Super-Admin"]

temporary_mail_list = ["vardan@ppapco.com",
                       "siddharth@cyronics.com",
                       "vatsalrana14@gmail.com",
                       "kumarkamal@ppapco.com",
                       "acgupta@ppapco.com"]

test_mail_list = ["vatsalrana14@gmail.com"]
mail_auto_send = True

fleet_sms_roles = ["Super-Admin"]

twin_mail_temp = ["vatsalrana14@gmail.com",
                  "aditya.90941@gmail.com",
                  "info_iot@cyronics",
                  "atharva@twinengineers.com",
                  "omkar.kachare@c4i4.org",
                  "sanchita@twinengineers.com"]

SEND_MAIL = False
dsm_new_rpo_endpoint = "http://192.168.1.131:82/dsm_rpo_endpoint"

'''
E-SCHEDULING 

Weekly meet
track department progress
intergrated production plan


month begining
plan machines 
for a month.
inventory check in 70 percent


Configurator
get machine specs,  from customer 
propose a model based on specs








'''