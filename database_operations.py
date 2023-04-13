import pymongo
import json
import pytz
import datetime
from bson.json_util import dumps, loads
from bson import ObjectId, Binary, Code, json_util
import copy
import constants

myclient1 = pymongo.MongoClient("mongodb://localhost:27017/")
# myclient1  = pymongo.MongoClient("mongodb://cyronics:cipl1234@35.184.20.184:27017/Anzen_1_0?authSource=Anzen_1_0")
mydb1 = myclient1['Anzen_1_0']
sign_up_collection = mydb1['Sign Up Questions']
import pyqrcode
# import png
from pyqrcode import QRCode
import string
import random
import uuid
import mail_api

user_collection = mydb1['Users']
visitors_collection = mydb1['Visitors']
questions_collection = mydb1['Contact Us']
settings_collection = mydb1['Settings']
all_questions_collection = mydb1['all_question']

from random import randint
import datetime
import otp_operations

import fcm_message


def get_signup_questions():
    myquery = {}
    mydoc = sign_up_collection.find(myquery, {'_id': False})
    questions = []
    for x in mydoc:
        questions.append(x)
    return questions


def signup_user_data(data):
    myquery = {"phone": data["phone"]}
    mydoc = user_collection.find(myquery, {'_id': False}).count()
    if mydoc == 0:
        data["otp"] = randint(100000, 999999)
        data["uid"] = ""
        data["epass"] = {
        }

        if "respiratory" in data:
            data["sign_up_questions"] = {
                "respiratory": data["respiratory"],
                "diabetes": data["diabetes"],
                "heart": data["heart"],
                "bp": data["bp"],
                "none": data["none"],
                "yes_age": data["yes_age"],
            }

        data["sign_up_status"] = {
            "application_status": "Rejected",
            "application_timestamp": datetime.datetime.now() + datetime.timedelta(minutes=330),
            "otp_verification_status": "False"
        }
        # data["declaration_history"]:[]
        data["attendance_history"] = []
        data["contact_trace"] = []
        user_collection.insert_one(data)
        # visitors_collection.insert_one(copy.deepcopy(data))

        otp_operations.send_otp(data["otp"], data["phone"])

        return True
    else:
        myquery = {"phone": data["phone"], "sign_up_status.otp_verification_status": "False"}
        mydoc = user_collection.find(myquery, {'_id': False}).count()
        if mydoc == 1:
            data["otp"] = randint(100000, 999999)
            myquery = {"phone": data["phone"]}
            new_data = copy.deepcopy(data)
            newvalues = {"$set": data}
            user_collection.update_one(myquery, newvalues)
            otp_operations.send_otp(data["otp"], data["phone"])
            print("-------------------------")
            print("Updated User OTP Value.")
            print("-------------------------")
            return True
        else:
            myquery = {"phone": data["phone"], "sign_up_status.otp_verification_status": "WIP"}
            mydoc = user_collection.find(myquery, {'_id': False}).count()
            if mydoc == 1:
                data["otp"] = randint(100000, 999999)
                data["uid"] = ""
                data["epass"] = {
                }

                if "respiratory" in data:
                    data["sign_up_questions"] = {
                        "respiratory": data["respiratory"],
                        "diabetes": data["diabetes"],
                        "heart": data["heart"],
                        "bp": data["bp"],
                        "none": data["none"],
                        "yes_age": data["yes_age"],
                    }

                data["sign_up_status"] = {
                    "application_status": "Rejected",
                    "application_timestamp": datetime.datetime.now() + datetime.timedelta(minutes=330),
                    "otp_verification_status": "True"
                }
                # data["declaration_history"]:[]
                data["attendance_history"] = []
                data["contact_trace"] = []
                # user_collection.insert_one(data)
                # visitors_collection.insert_one(copy.deepcopy(data))

                otp_operations.send_otp(data["otp"], data["phone"])
                newvalues = {"$set": data}
                user_collection.update_one(myquery, newvalues)
                print("-----------------")
                print(" Added Remaining Values")
                print("-----------------")

                return True
            else:
                myquery = {"phone": data["phone"], "sign_up_status.otp_verification_status": "True"}
                mydoc = user_collection.find(myquery, {'_id': False}).count()
                if mydoc == 1:
                    print("-------------------------")
                    print("Already in Data.")
                    print("-------------------------")

                return False
            # return False


def signup_user(data):
    myquery = {"phone": data["phone"]}
    mydoc = user_collection.find(myquery, {'_id': False}).count()
    if mydoc == 0:
        data["otp"] = randint(100000, 999999)
        data["uid"] = ""
        data["epass"] = {
        }

        if "respiratory" in data:
            data["sign_up_questions"] = {
                "respiratory": data["respiratory"],
                "diabetes": data["diabetes"],
                "heart": data["heart"],
                "bp": data["bp"],
                "none": data["none"],
                "yes_age": data["yes_age"],
            }

        data["sign_up_status"] = {
            "application_status": "Rejected",
            "application_timestamp": datetime.datetime.now(),
            "otp_verification_status": "False"
        }
        # data["declaration_history"]:[]
        data["attendance_history"] = []
        data["contact_trace"] = []
        user_collection.insert_one(data)
        # visitors_collection.insert_one(copy.deepcopy(data))

        otp_operations.send_otp(data["otp"], data["phone"])
        otp_operations.send_otp_via_email(data["otp"],data["email_id"])

        return True
    else:
        myquery = {"phone": data["phone"], "sign_up_status.otp_verification_status": "False"}
        mydoc = user_collection.find(myquery, {'_id': False}).count()
        if mydoc == 1:
            data["otp"] = randint(100000, 999999)
            myquery = {"phone": data["phone"]}
            new_data = copy.deepcopy(data)
            newvalues = {"$set": data}
            user_collection.update_one(myquery, newvalues)
            otp_operations.send_otp(data["otp"], data["phone"])
            otp_operations.send_otp_via_email(data["otp"], data["email_id"])
            print("-------------------------")
            print("Updated User OTP Value.")
            print("-------------------------")
            return True
        else:
            myquery = {"phone": data["phone"], "sign_up_status.otp_verification_status": "WIP"}
            mydoc = user_collection.find(myquery, {'_id': False}).count()
            if mydoc == 1:
                if mydoc == 1:
                    data["otp"] = randint(100000, 999999)
                    myquery = {"phone": data["phone"]}
                    new_data = copy.deepcopy(data)
                    newvalues = {"$set": data}
                    user_collection.update_one(myquery, newvalues)
                    otp_operations.send_otp(data["otp"], data["phone"])
                    otp_operations.send_otp_via_email(data["otp"], data["email_id"])
                    print("-------------------------")
                    print("Updated User OTP Value. User in WIP.")
                    print("-------------------------")
                    return True
            else:
                myquery = {"phone": data["phone"], "sign_up_status.otp_verification_status": "True"}
                mydoc = user_collection.find(myquery, {'_id': False}).count()
                if mydoc == 1:
                    print("-------------------------")
                    print("Already in Data.")
                    print("-------------------------")

                return False
            # return False


'''
Generation of static QR Codes with E-Pass
'''


def generate_static_epass(data):
    print("=============== ======== ===================")

    temp_dict = {}

    # correct_answers = get_daily_questions(data['o_id'])

    temp_dict["declaration_questions"] = []

    temp_dict["timestamp"] = datetime.datetime.now() + datetime.timedelta(minutes=330)

    uid = str(uuid.uuid1())

    uid = uid.replace("-", "")
    print(uid)

    valid_upto = temp_dict["timestamp"] + datetime.timedelta(days=365)
    valid_upto_string = valid_upto.strftime("%d-%m-%Y-%H-%M")
    valid_upto_string = valid_upto_string.split('-')
    # print(valid_upto_string)

    checksum = 0
    for number in valid_upto_string:
        checksum += int(number)
        # print(checksum)

    date_to_append = valid_upto.strftime("%d%m%Y%H%M")

    # print(date_to_append)
    # print(len(session["name"]))
    # print(session["name"])

    name = ""

    if len(data["name"]) > 20:
        name = data["name"][: (20 - len(data["name"]))]
    else:
        name = data["name"]
        for i in range(20 - len(data["name"])):
            name = name + "0"

    # print(name)
    # print(len(name))

    output = uid + name + data["phone"] + date_to_append + str(checksum)
    print(output)

    # uid = output
    print("=============== New QR Code ===================")

    qrcode = pyqrcode.create(output)
    qrcode.png('code/' + uid + '.png', scale=12)
    temp_dict["uid"] = uid
    temp_dict["epass_status"] = "Accepted"
    temp_dict["qrcode_link"] = "/epass/" + uid + '.png'

    myquery = {"phone": data['phone']}
    newvalues = {"$set": {"epass": temp_dict, "uid": uid}}
    user_collection.update_one(myquery, newvalues)

    myquery = {"phone": data['phone']}
    mydoc = user_collection.find(myquery, {'declaration_history': True, "_id": False})
    history = []
    for x in mydoc:
        history.append(x)
    # print(history)
    # print(history)
    if "declaration_history" in history[0]:
        history[0]['declaration_history'].append(temp_dict)
        newvalues = {"$set": {'declaration_history': history[0]['declaration_history']}}
        user_collection.update_one(myquery, newvalues)
        # print("Appending")
        # print(history)
    else:
        history = [temp_dict]
        myquery = {"phone": data['phone']}
        newvalues = {"$set": {'declaration_history': history}}
        user_collection.update_one(myquery, newvalues)
        # print("Creating_New")


def Sign_Up_Request_Manual(data):
    myquery = {"phone": data["phone"]}
    mydoc = user_collection.find(myquery, {'_id': False}).count()
    if mydoc == 0:
        data["otp"] = randint(100000, 999999)
        data["uid"] = ""
        data["epass"] = {
        }

        if "respiratory" in data:
            data["sign_up_questions"] = {
                "respiratory": data["respiratory"],
                "diabetes": data["diabetes"],
                "heart": data["heart"],
                "bp": data["bp"],
                "none": data["none"],
                "yes_age": data["yes_age"],
            }

        data["sign_up_status"] = {
            "application_status": "Accepted",
            "application_timestamp": datetime.datetime.now() + datetime.timedelta(minutes=330),
            "otp_verification_status": "True"
        }
        # data["declaration_history"]:[]
        data["attendance_history"] = []
        data["contact_trace"] = []
        user_collection.insert_one(data)
        # visitors_collection.insert_one(copy.deepcopy(data))

        # otp_operations.send_otp(data["otp"], data["phone"])

        generate_static_epass(data)

        return True
    else:
        myquery = {"phone": data["phone"], "sign_up_status.otp_verification_status": "True"}
        mydoc = user_collection.find(myquery, {'_id': False}).count()
        if mydoc == 1:
            print("-------------------------")
            print("Already in Data.")
            print("-------------------------")

        return False
    # return False


def get_all_non_smartphone_users(o_id):
    myquery = {"o_id": o_id, "non_smartphone": "true"}
    mydoc = user_collection.find(myquery, {'_id': False})
    non_smartphone_users = []
    for i in mydoc:
        non_smartphone_users.append(i)
    return non_smartphone_users


def return_otp(phone):
    myquery = {"phone": str(phone)}
    mydoc = user_collection.find(myquery, {'otp': True, "_id": False})
    otp = []
    for x in mydoc:
        otp.append(x)
    if len(otp) > 0:
        return otp[0]
    else:
        return 0


def update_otp_verification(phone):
    myquery = {"phone": str(phone)}
    newvalues = {"$set": {"sign_up_status.otp_verification_status": "True"}}
    user_collection.update_one(myquery, newvalues)

    mydoc = user_collection.find(myquery, {'otp': True, "_id": False})
    otp = []
    for x in mydoc:
        otp.append(x)
    if len(otp) > 0:
        return otp[0]
    else:
        return 0


def update_otp_verification_partial(phone):
    myquery = {"phone": str(phone)}
    newvalues = {"$set": {"sign_up_status.otp_verification_status": "WIP"}}
    user_collection.update_one(myquery, newvalues)

    mydoc = user_collection.find(myquery, {'otp': True, "_id": False})
    otp = []
    for x in mydoc:
        otp.append(x)
    if len(otp) > 0:
        return otp[0]
    else:
        return 0


def return_credentials(phone):
    myquery = {"phone": str(phone)}
    mydoc = user_collection.find(myquery, {'name': True, 'password': True, 'role': True, 'o_id': True, "_id": False})
    credentials = []
    for x in mydoc:
        credentials.append(x)
    if len(credentials) > 0:
        return credentials[0]
    else:
        return 0


def verify_credentials(data):
    myquery = {"phone": str(data["phone"])}
    mydoc = user_collection.find(myquery, {'password': True, 'sign_up_status': True, "_id": False})
    credentials = []
    for x in mydoc:
        credentials.append(x)
    if len(credentials) > 0:
        if data["password"] == credentials[0]["password"]:
            if credentials[0]["sign_up_status"]['application_status'] == "Accepted":
                return 2
            else:
                return 1
        else:
            return 0
    else:
        return 0


def update_otp(phone):
    myquery = {"phone": phone}
    mydoc = user_collection.find(myquery, {'_id': False}).count()

    email = user_collection.find_one({"phone": phone})["email_id"]
    if mydoc > 0:
        otp = randint(100000, 999999)
        myquery = {"phone": phone}
        newvalues = {"$set": {"otp": otp, "timestamp": datetime.datetime.now() + datetime.timedelta(minutes=330)}}
        user_collection.update_one(myquery, newvalues)
        otp_operations.send_otp_via_email(str(otp), email)
        # otp_operations.send_otp(otp)
        otp_operations.send_otp(otp, phone)
        return True
    else:
        return False


def reset_password(data):
    myquery = {"phone": data['phone']}
    mydoc = user_collection.find(myquery, {'_id': False}).count()
    if mydoc > 0:
        password = data['password']
        myquery = {"phone": data['phone']}
        newvalues = {
            "$set": {"password": password, "timestamp": datetime.datetime.now() + datetime.timedelta(minutes=330)}}
        user_collection.update_one(myquery, newvalues)
        return True
    else:
        return False


def id_generator(size=12, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def update_declaration(phone, declaration, session):
    temp_dict = {}
    temp_dict["declaration_questions"] = {
        "fever": declaration["fever"],
        "cough": declaration["cough"],
        "breathing": declaration["breathing"],
        "redzone": declaration["redzone"],
    }
    temp_dict["timestamp"] = datetime.datetime.now() + datetime.timedelta(minutes=330)

    # uid = str(uuid.uuid1())

    print("=============== ======== ===================")
    uid = str(uuid.uuid1())

    uid = uid.replace("-", "")
    print(uid)

    valid_upto = temp_dict["timestamp"] + datetime.timedelta(days=1)
    valid_upto_string = valid_upto.strftime("%d-%m-%Y-%H-%M")
    valid_upto_string = valid_upto_string.split('-')
    # print(valid_upto_string)

    checksum = 0
    for number in valid_upto_string:
        checksum += int(number)
        # print(checksum)

    date_to_append = valid_upto.strftime("%d%m%Y%H%M")

    # print(date_to_append)
    # print(len(session["name"]))
    # print(session["name"])

    name = ""

    if len(session["name"]) > 20:
        name = session["name"][: (20 - len(session["name"]))]
    else:
        name = session["name"]
        for i in range(20 - len(session["name"])):
            name = name + "0"

    # print(name)
    # print(len(name))

    output = uid + name + session["user"] + date_to_append + str(checksum)
    print(output)

    # uid = output
    print("=============== New QR Code ===================")

    if declaration["fever"] == "no" and declaration["cough"] == "no" and declaration["breathing"] == "no" and \
            declaration["redzone"] == "no":

        qrcode = pyqrcode.create(output)
        qrcode.png('code/' + uid + '.png', scale=12)
        temp_dict["uid"] = uid
        temp_dict["epass_status"] = "Accepted"
        temp_dict["qrcode_link"] = "/epass/" + uid + '.png'
    else:
        temp_dict["uid"] = uid
        temp_dict["epass_status"] = "Rejected"
        temp_dict["qrcode_link"] = "/epass/reject.svg"

    myquery = {"phone": phone}
    newvalues = {"$set": {"epass": temp_dict, "uid": uid}}
    user_collection.update_one(myquery, newvalues)

    myquery = {"phone": phone}
    mydoc = user_collection.find(myquery, {'declaration_history': True, "_id": False})
    history = []
    for x in mydoc:
        history.append(x)
    # print(history)
    # print(history)
    if "declaration_history" in history[0]:
        history[0]['declaration_history'].append(temp_dict)
        newvalues = {"$set": {'declaration_history': history[0]['declaration_history']}}
        user_collection.update_one(myquery, newvalues)
        # print("Appending")
        # print(history)
    else:
        history = [temp_dict]
        myquery = {"phone": phone}
        newvalues = {"$set": {'declaration_history': history}}
        user_collection.update_one(myquery, newvalues)
        # print("Creating_New")


def update_declaration_new(phone, declaration, session):
    temp_dict = {}
    '''temp_dict["declaration_questions"] = {
        "fever": declaration["fever"],
        "cough": declaration["cough"],
        "breathing": declaration["breathing"],
        "redzone": declaration["redzone"],
    }'''
    temp_dict["declaration_questions"] = declaration

    temp_dict["timestamp"] = datetime.datetime.now() + datetime.timedelta(minutes=330)

    # uid = str(uuid.uuid1())

    print("=============== ======== ===================")
    uid = str(uuid.uuid1())

    uid = uid.replace("-", "")
    print(uid)

    valid_upto = temp_dict["timestamp"] + datetime.timedelta(days=1)
    valid_upto_string = valid_upto.strftime("%d-%m-%Y-%H-%M")
    valid_upto_string = valid_upto_string.split('-')
    # print(valid_upto_string)

    checksum = 0
    for number in valid_upto_string:
        checksum += int(number)
        # print(checksum)

    date_to_append = valid_upto.strftime("%d%m%Y%H%M")

    # print(date_to_append)
    # print(len(session["name"]))
    # print(session["name"])

    name = ""

    if len(session["name"]) > 20:
        name = session["name"][: (20 - len(session["name"]))]
    else:
        name = session["name"]
        for i in range(20 - len(session["name"])):
            name = name + "0"

    # print(name)
    # print(len(name))

    output = uid + name + session["user"] + date_to_append + str(checksum)
    print(output)

    # uid = output
    print("=============== New QR Code ===================")

    correct_answers = get_daily_questions(session['o_id'])

    # print(correct_answers)
    # print(declaration)

    flag = 1
    for i in range(0, len(correct_answers)):
        if correct_answers[i]["question"]["correct/better_option"] != "" or correct_answers[i]["question"][
            "correct/better_option"] != []:
            for j in range(0, len(declaration)):
                if correct_answers[i]["question"]['q_id'] == declaration[j]["question"]['q_id']:
                    if correct_answers[i]["question"]["type"] == "Options":
                        if correct_answers[i]["question"]["correct/better_option"] != declaration[j]["question"][
                            "correct/better_option"]:
                            flag = 0

                    if correct_answers[i]["question"]["type"] == "Multiple_Options":
                        for k in range(0, len(declaration[j]["question"]["correct/better_option"])):
                            if declaration[j]["question"]["correct/better_option"][k] not in \
                                    correct_answers[i]["question"]["correct/better_option"]:
                                flag = 0

    '''if declaration["fever"] == "no" and declaration["cough"] == "no" and declaration["breathing"] == "no" and \
            declaration["redzone"] == "no":'''
    if flag == 1:
        qrcode = pyqrcode.create(output)
        qrcode.png('code/' + uid + '.png', scale=12)
        temp_dict["uid"] = uid
        temp_dict["epass_status"] = "Accepted"
        temp_dict["qrcode_link"] = "/epass/" + uid + '.png'
    else:
        temp_dict["uid"] = uid
        temp_dict["epass_status"] = "Rejected"
        temp_dict["qrcode_link"] = "/epass/reject.svg"

    # Setting Epass/UID Variable
    myquery = {"phone": phone}
    newvalues = {"$set": {"epass": temp_dict, "uid": uid}}
    user_collection.update_one(myquery, newvalues)

    myquery = {"phone": phone}
    mydoc = user_collection.find(myquery, {'declaration_history': True, "_id": False})
    history = []
    for x in mydoc:
        history.append(x)

    # print(history)
    # print(history)
    if "declaration_history" in history[0]:
        print("IN APPEND LOOP")
        history[0]['declaration_history'].append(temp_dict)
        newvalues = {"$set": {'declaration_history': history[0]['declaration_history']}}
        user_collection.update_one(myquery, newvalues)
        # print("Appending")
        # print(history)
    else:
        history = [temp_dict]
        myquery = {"phone": phone}
        newvalues = {"$set": {'declaration_history': history}}
        user_collection.update_one(myquery, newvalues)
        # print("Creating_New")


def get_epass(phone):
    myquery = {"phone": phone}
    mydoc = user_collection.find(myquery, {'epass': True, "_id": False})

    epass = []
    for x in mydoc:
        epass.append(x)
    print("------PRINTING EPASS------------")
    print(epass[0])
    return epass[0]['epass']


def get_latest_temmperature(phone):
    myquery = {"phone": phone}
    mydoc = user_collection.find(myquery, {'attendance_history': True, "_id": False}).sort("attendance_history",
                                                                                           pymongo.ASCENDING)
    attendance = []
    for x in mydoc:
        attendance.append(x)

    print(attendance)
    print("------ GETTING LATEST TEMPERATURE ------------")
    if len(attendance) > 0 and len(attendance[0]["attendance_history"]) != 0:
        print(attendance[0]["attendance_history"][len(attendance[0]["attendance_history"]) - 1])
        return 1, attendance[0]["attendance_history"][len(attendance[0]["attendance_history"]) - 1]
    else:
        return 0, 0


def get_oid_settings(o_id):
    myquery = {"o_id": o_id}
    mydoc = settings_collection.find(myquery, {'scan_settings': True, "_id": False})
    scan_settings = []
    for x in mydoc:
        scan_settings.append(x)
    if len(scan_settings) != 0:
        if len(scan_settings[0]["scan_settings"]) > 0:
            return 1, scan_settings[0]["scan_settings"]
        else:
            return 0, 0
    else:
        return 0, 0


def date_formatter(date_in):
    temp = date_in.split("-")
    # print("Temp..........",temp)
    return datetime.date(int(temp[0]), int(temp[1]), int(temp[2]))


def date_formatter2(date_in):
    date_in = date_in.date().strftime("%Y-%m-%d")
    temp = str(date_in).split("-")
    # print("Temp..........",temp)
    return datetime.date(int(temp[0]), int(temp[1]), int(temp[2]))


def attendance_data(o_id, date_in):
    current_time = datetime.datetime.now() + datetime.timedelta(minutes=330)
    date = current_time.strftime("%d/%m/%Y")
    data_to_return = []
    myquery = {"o_id": o_id}
    data = user_collection.find(myquery, {'_id': False, "name": True,
                                          "role": True,
                                          "employee_type": True,
                                          "employee_id": True,
                                          "account_freeze": True,
                                          "phone": True, "attendance_history": True,
                                          "declaration_history": True, "epass": True})

    # default_declarations
    all_data = []
    for temp_data in data:
        all_data.append(temp_data)

    # print(all_data[0]["epass"])
    from_date = date_formatter(date_in["from_date"])
    to_date = date_formatter(date_in["to_date"])
    for user_data in all_data:
        # print(user_data["attendance_history"])
        if "declaration_history" in user_data and user_data["declaration_history"] != []:
            for declaration_hist in user_data["declaration_history"]:
                if 'scan_details' not in declaration_hist:
                    xx = date_formatter2(declaration_hist["timestamp"])
                    if from_date <= xx <= to_date:
                        temp_arr = []
                        name = user_data["name"]
                        phone = user_data["phone"]
                        date_attendance = declaration_hist["timestamp"].strftime("%d/%m/%Y")
                        time = "-"
                        employee_type = user_data["employee_type"]
                        if "employee_id" in user_data:
                            employee_id = user_data["employee_id"]
                        else:
                            employee_id = "NA"
                        epass_status = declaration_hist["epass_status"]
                        temp = "-"
                        attendance_status = "No"
                        temp_arr.append(name)
                        temp_arr.append(phone)
                        temp_arr.append(date_attendance)
                        temp_arr.append(time)
                        temp_arr.append(employee_type)
                        temp_arr.append(employee_id)
                        temp_arr.append(epass_status)
                        temp_arr.append(temp)
                        temp_arr.append(attendance_status)
                        temp_arr.append(
                            "<button class='btn btn-sm btn-primary' data-toggle='modal' data-target='#myModal' value=" + phone + "  onclick = 'modal_fun(this)'>View</button>")
                        temp = "<button class='btn btn-sm btn-primary' value=" + phone + "  onclick = 'freeze(this)'> FREEZE </button>"
                        if "account_freeze" in user_data:
                            if user_data["account_freeze"] == "frozen":
                                # print("00000000000000000000000000000000000000000000000000000000")
                                temp = "<button class='btn btn-sm btn-danger' value=" + phone + "  onclick = 'unfreeze(this)'> UNFREEZE </button>"
                        temp_arr.append(temp)

                        data_to_return.append(temp_arr)

                        # data_to_return.append(temp_arr)
                else:
                    xx = date_formatter2(declaration_hist['scan_details']["timestamp"])
                    if from_date <= xx <= to_date:
                        temp_arr = []
                        name = user_data["name"]
                        phone = user_data["phone"]
                        date_attendance = declaration_hist['scan_details']["timestamp"].strftime("%d/%m/%Y")
                        time = (declaration_hist['scan_details']["timestamp"] + datetime.timedelta(
                            minutes=0)).strftime("%H:%M:%S")
                        employee_type = user_data["employee_type"]
                        if "employee_id" in user_data:
                            employee_id = user_data["employee_id"]
                        else:
                            employee_id = "NA"
                        epass_status = "Accepted"
                        temp = declaration_hist['scan_details']["temperature"]
                        attendance_status = "Yes"
                        temp_arr.append(name)
                        temp_arr.append(phone)
                        temp_arr.append(date_attendance)
                        temp_arr.append(time)
                        temp_arr.append(employee_type)
                        temp_arr.append(employee_id)
                        temp_arr.append(epass_status)
                        temp_arr.append(temp)
                        temp_arr.append(attendance_status)
                        temp_arr.append(
                            "<button class='btn btn-sm btn-primary' data-toggle='modal' data-target='#myModal' value=" + phone + "  onclick = 'modal_fun(this)'>View</button>")
                        temp = "<button class='btn btn-sm btn-primary' value=" + phone + "  onclick = 'freeze(this)'> FREEZE </button>"
                        if "account_freeze" in user_data:
                            if user_data["account_freeze"] == "frozen":
                                # print("00000000000000000000000000000000000000000000000000000000")
                                temp = "<button class='btn btn-sm btn-danger' value=" + phone + "  onclick = 'unfreeze(this)'> UNFREEZE </button>"
                        temp_arr.append(temp)

                        data_to_return.append(temp_arr)

    return data_to_return


def attendance_modal(data, o_id):
    '''
    date = data["date"]

    myquery = {"o_id": o_id, "phone": str(data["number"])}
    data = user_collection.find(myquery, {'_id': False, "name": True, "phone": True,
                                          "declaration_history": True})

    # default_declarations
    all_data = []
    for temp_data in data:
        all_data.append(temp_data)

    data = {'breathing': "",
            'cough': "",
            'fever': "",
            'redzone': ""}

    # print(all_data)
    for user_data in all_data:

        if "declaration_history" in user_data:

            for declaration in user_data["declaration_history"]:
                if "declaration_questions" in declaration:
                    if declaration["timestamp"].strftime("%d/%m/%Y") == date:
                        data = declaration["declaration_questions"]

    '''
    myquery = {"o_id": o_id, "phone": str(data["number"])}
    data = user_collection.find_one(myquery, {"epass.declaration_questions": True, '_id': False})
    return (data['epass']['declaration_questions'])


def date_wise_attendance(date, o_id):
    # current_time = datetime.datetime.now() + datetime.timedelta(minutes=330)
    # date_str = '29/12/2017' # The date - 29 Dec 2017

    settings = []
    myquery = {"o_id": o_id}
    mydoc = settings_collection.find(myquery, {'_id': False, "scan_settings": True})
    # print(mydoc)

    for i in mydoc:
        settings.append(i)
    scan_time = settings[0]["scan_settings"]["scan_time"]

    print(scan_time)

    end_time_string = date + "::" + scan_time
    print(end_time_string)

    format_str = '%d/%m/%Y::%H:%M'  # The format

    end_time = datetime.datetime.strptime(end_time_string, format_str)
    print(end_time.date())

    start_time = end_time - datetime.timedelta(hours=24)
    print(start_time.date())

    data_to_return = []
    myquery = {"o_id": o_id}
    data = user_collection.find(myquery, {'_id': False, "name": True, "phone": True, "attendance_history": True,
                                          "declaration_history": True, "employee_type": True})

    # default_declarations
    all_data = []
    for temp_data in data:
        all_data.append(temp_data)

    # print(all_data)
    for user_data in all_data:
        temp_arr = []
        name = user_data["name"]
        phone = user_data["phone"]
        employee_type = user_data["employee_type"]
        if "declaration_history" in user_data:
            epass_status = "No"
            for declaration in user_data["declaration_history"]:
                if "timestamp" in declaration:
                    if (start_time < declaration["timestamp"] and end_time > declaration["timestamp"]):
                        epass_status = "Yes"

            attendance_status = "No"
            temp = " - "
            for attendance_data in user_data["attendance_history"]:
                if attendance_data["timestamp"].strftime("%d/%m/%Y") == end_time.strftime("%d/%m/%Y"):
                    attendance_status = "Yes"
                    epass_status = "Yes"
                    temp = str(attendance_data["temperature"])
            temp_arr.append(name)
            temp_arr.append(phone)
            temp_arr.append(employee_type)
            temp_arr.append(epass_status)
            temp_arr.append(
                "<button class='btn btn-sm btn-primary' data-toggle='modal' data-target='#myModal' value=" + phone + "  onclick = 'modal_fun(this)'>GO</button>")
            temp_arr.append(temp)
            temp_arr.append(attendance_status)
            data_to_return.append(temp_arr)
        else:
            pass

    return data_to_return


# --------------------------------------------------end-Attendance------------------------------------


# --------------------------------------------------Visitors-------------------------------------------
def visitor_data(o_id):
    current_time = datetime.datetime.now() + datetime.timedelta(minutes=330)
    date = current_time.strftime("%d/%m/%Y")
    data_to_return = []
    myquery = {"o_id": o_id}
    data = visitors_collection.find(myquery, {'_id': False, "name": True,
                                              "parent_organisation": True,
                                              "phone": True, "attendance_history": True,
                                              "declaration_history": True})

    # default_declarations
    all_data = []
    for temp_data in data:
        all_data.append(temp_data)

    # print(all_data)
    for user_data in all_data:
        temp_arr = []
        name = user_data["name"]
        parent_organisation = user_data["parent_organisation"]
        phone = user_data["phone"]
        if "declaration_history" in user_data:
            epass_status = "No"
            for declaration in user_data["declaration_history"]:
                if "timestamp" in declaration:
                    if declaration["timestamp"].strftime("%d/%m/%Y") == date:
                        epass_status = "Yes"
            attendance_status = "No"
            temp = " - "
            for attendance_data in user_data["attendance_history"]:
                if attendance_data["timestamp"].strftime("%d/%m/%Y") == date:
                    attendance_status = "Yes"
                    temp = str(attendance_data["temperature"])
            temp_arr.append(name)
            temp_arr.append(parent_organisation)
            temp_arr.append(epass_status)
            temp_arr.append(
                "<button class='btn btn-sm btn-primary' data-toggle='modal' data-target='#myModal' value=" + phone + "  onclick = 'modal_fun(this)'>GO</button>")
            temp_arr.append(temp)
            temp_arr.append(attendance_status)
            data_to_return.append(temp_arr)
        else:
            pass
    return data_to_return


def visitor_modal(data, o_id):
    date = data["date"]
    myquery = {"o_id": o_id, "phone": str(data["number"])}
    data = visitors_collection.find(myquery, {'_id': False, "name": True, "phone": True,
                                              "declaration_history": True})

    # default_declarations
    all_data = []
    for temp_data in data:
        all_data.append(temp_data)

    data = {'breathing': "",
            'cough': "",
            'fever': "",
            'redzone': ""}

    # print(all_data)
    for user_data in all_data:

        if "declaration_history" in user_data:

            for declaration in user_data["declaration_history"]:
                if "declaration_questions" in declaration:
                    if declaration["timestamp"].strftime("%d/%m/%Y") == date:
                        data = declaration["declaration_questions"]
    return data


def date_wise_visitor(date, o_id):
    # current_time = datetime.datetime.now() + datetime.timedelta(minutes=330)
    # date = current_time.strftime("%d/%m/%Y")
    data_to_return = []
    myquery = {"o_id": o_id}
    data = user_collection.find(myquery, {'_id': False, "name": True, "phone": True, "attendance_history": True,
                                          "declaration_history": True})

    # default_declarations
    all_data = []
    for temp_data in data:
        all_data.append(temp_data)

    # print(all_data)
    for user_data in all_data:
        temp_arr = []
        name = user_data["name"]
        phone = user_data["phone"]
        if "declaration_history" in user_data:
            epass_status = "No"
            for declaration in user_data["declaration_history"]:
                if "timestamp" in declaration:
                    if declaration["timestamp"].strftime("%d/%m/%Y") == date:
                        epass_status = "Yes"
            attendance_status = "No"
            temp = " - "
            for attendance_data in user_data["attendance_history"]:
                if attendance_data["timestamp"].strftime("%d/%m/%Y") == date:
                    attendance_status = "Yes"
                    temp = str(attendance_data["temperature"])
            temp_arr.append(name)
            temp_arr.append(epass_status)
            temp_arr.append(
                "<button class='btn btn-sm btn-primary' data-toggle='modal' data-target='#myModal' value=" + phone + "  onclick = 'modal_fun(this)'>GO</button>")
            temp_arr.append(temp)
            temp_arr.append(attendance_status)
            data_to_return.append(temp_arr)
        else:
            pass

    return data_to_return


# --------------------------------------------------end-Visitors------------------------------------


# --------------------------------------------------Application---------------------------------------
def application_data(o_id):
    temp = user_collection.find({"o_id": o_id, "sign_up_status.otp_verification_status": "True"})
    data_to_return = []
    for i in temp:
        temp_arr = []
        temp_arr.append(i["name"])
        try:
            temp_arr.append(i["email_id"])
        except:
            temp_arr.append(" - ")

        temp_arr.append(i["phone"])
        temp_arr.append(i["sign_up_status"]["application_timestamp"].strftime("%d/%m/%Y"))
        temp_arr.append(
            (i["sign_up_status"]["application_timestamp"] + datetime.timedelta(minutes=0)).strftime("%H:%M:%S"))
        temp_arr.append('<select class="form-control form-control-sm wd-150" data-phone="' + i["phone"] + '" onchange="employee_type_change(this)" id="contract">\
        			   <option value="' + i["employee_type"] + '" selected disabled> ' + i["employee_type"] + ' </option>\
        				<option value="Full Time">Full Time</option>\
        				  <option value="Contract">Contract</option>\
        		</select>')
        if 'contract_organisation' in i:
            if i["contract_organisation"] == "":
                temp_arr.append(" - ")
            else:
                temp_arr.append(i["contract_organisation"])
        else:
            temp_arr.append("NA")
        temp_arr.append('<select class="form-control form-control-sm wd-150" data-phone="' + i["phone"] + '" onchange="role_change(this)" id="role">\
			   <option value="' + i["role"] + '" selected disabled> ' + i["role"] + ' </option>\
                <option value="Super-Admin" >Super-Admin</option>\
                <option value="Admin" >Admin</option>\
                <option value="customer" >Customer</option>\
                <option value="DSM-SE" >DSM-SE</option>\
                <option value="DSM-Super-Admin" >DSM-Super-Admin</option>\
                <option value="DSM-CS" >DSM-CS</option>\
                <option value="DSM-Office" >DSM-Office</option>\
                <option value="SF-Admin" >SF-Admin</option>\
                <option value="SF-Operator" >SF-Operator</option>\
                        </select>')
        attribute_data = i["phone"]
        temp_arr.append(
            "<button class='btn btn-sm btn-primary Rectangle_without_color' data-toggle='modal' data-target='#myModal' value=" + attribute_data + "  onclick = 'modal_fun(this)' disabled>View</button>")
        if i["sign_up_status"]["application_status"] == "Accepted":
            temp_arr.append(
                '<button class="btn btn-sm btn-success Rectangle_without_color" onclick="acc_rej(this)" value =' + attribute_data + '>' +
                i["sign_up_status"]["application_status"] + '</button>')
        else:
            temp_arr.append(
                '<button class="btn btn-sm btn-danger Rectangle_without_color" onclick="acc_rej(this)" value =' + attribute_data + '>' +
                i["sign_up_status"]["application_status"] + '</button>')
        data_to_return.append(temp_arr)
    return data_to_return



def change_status(arr, o_id):
    user_collection.update({"o_id": o_id, "phone": str(arr[0])},
                           {'$set': {"sign_up_status.application_status": arr[1]}})
    otp_operations.send_signup_accept(arr[1], arr[0])
    return application_data(o_id)


def modal_application(no, o_id):
    i = user_collection.find_one({"o_id": o_id, "phone": str(no)})
    # New type of Sign Up Questions
    if "General_Questions" in i:
        data = i["General_Questions"]
    # Old Type of Sign Up Questions
    else:
        data = {'respiratory': i["respiratory"], 'diabetes': i["diabetes"], 'heart': i["heart"], 'bp': i["bp"],
                'yes_age': i["yes_age"], "none": i["none"]}
    return data


def update_role(arr, o_id):
    user_collection.update({"o_id": o_id, "phone": str(arr[0])}, {'$set': {"role": arr[1]}})
    # otp_operations.send_signup_role(arr[1],arr[0])
    return "ok"


def update_employee_type(arr, o_id):
    user_collection.update({"o_id": o_id, "phone": str(arr[0])}, {'$set': {"employee_type": arr[1]}})
    # otp_operations.send_signup_role(arr[1],arr[0])
    return "ok"


# --------------------------------------------------Trace-------------------------------------------

def trace_data(input, o_id):
    count = 0
    data = None
    if input["searchby"] == "name":
        myquery = {"o_id": o_id, "name": input["search"]}
        data = user_collection.find_one(myquery, {"contact_trace": True})
    if input["searchby"] == "number":
        myquery = {"o_id": o_id, "phone": input["search"]}
        data = user_collection.find_one(myquery, {"contact_trace": True})
    if data == None:
        return False, 0
    else:
        data_to_return = []
        if "contact_trace" in data:
            for i in data["contact_trace"]:
                temp_dict = {}
                temp_dict["name"] = i["name"]
                temp_dict["number"] = i["number"]
                dt = i["timestamp"]
                temp_dict["timestamp"] = dt.strftime("%d/%m/%Y")
                print(temp_dict)
                data_to_return.append(temp_dict)
            return True, data_to_return


# ==========================================
# add visitor code

def visitor_request(data):
    myquery = {"phone": data["phone"]}
    mydoc = visitors_collection.find(myquery, {'_id': False}).count()
    if mydoc == 0:

        data["otp"] = randint(100000, 999999)
        data["uid"] = ""
        data["epass"] = {

        }
        data["sign_up_questions"] = {
            "respiratory": data["respiratory"],
            "diabetes": data["diabetes"],
            "heart": data["heart"],
            "bp": data["bp"],
            "none": data["none"],
            "yes_age": data["yes_age"],
        }
        data["sign_up_status"] = {
            "application_status": "Rejected",
            "application_timestamp": datetime.datetime.now() + datetime.timedelta(minutes=330),
            "otp_verification_status": "True"
        }
        # data["declaration_history"]:[]
        data["attendance_history"] = []
        data["contact_trace"] = []
        visitors_collection.insert_one(data)
        print("inserted")
    else:
        newvalues = {"$set": data}
        visitors_collection.update_one(myquery, newvalues)
        print("Updated")
    # visitors_collection
    # ------------------------------
    # Now E-Pass turn
    # ------------------------------
    declaration = copy.deepcopy(data)
    # print(declaration)
    temp_dict = {}
    temp_dict["declaration_questions"] = {
        "fever": declaration["fever"],
        "cough": declaration["cough"],
        "breathing": declaration["breathing"],
        "redzone": declaration["redzone"],
    }
    temp_dict["timestamp"] = datetime.datetime.now() + datetime.timedelta(minutes=330)
    uid = str(uuid.uuid1())
    if declaration["fever"] == "no" and declaration["cough"] == "no" and declaration["breathing"] == "no" and \
            declaration["redzone"] == "no":

        qrcode = pyqrcode.create(uid)
        qrcode.png('code/' + uid + '.png', scale=12)

        temp_dict["uid"] = uid
        temp_dict["epass_status"] = "Accepted"
        temp_dict["qrcode_link"] = "/epass/" + uid + '.png'

        otp_operations.send_qrcode("https://anzenhealth.app" + temp_dict["qrcode_link"], data["phone"])
    else:
        temp_dict["uid"] = uid
        temp_dict["epass_status"] = "Rejected"
        temp_dict["qrcode_link"] = "/epass/reject.svg"

    myquery = {"phone": data["phone"]}
    newvalues = {"$set": {"epass": temp_dict, "uid": uid}}
    visitors_collection.update_one(myquery, newvalues)

    myquery = {"phone": data["phone"]}
    mydoc = visitors_collection.find(myquery, {'declaration_history': True, "_id": False})
    history = []
    for x in mydoc:
        history.append(x)
    print(history)
    print("---------------------------------")
    # print(history)
    if "declaration_history" in history[0]:
        history[0]['declaration_history'].append(temp_dict)
        newvalues = {"$set": {'declaration_history': history[0]['declaration_history']}}
        visitors_collection.update_one(myquery, newvalues)
        # print("Appending")
        # print(history)
    else:
        history = [temp_dict]
        myquery = {"phone": data["phone"]}
        newvalues = {"$set": {'declaration_history': history}}
        visitors_collection.update_one(myquery, newvalues)
        # print("Creating_New")
    print(temp_dict["epass_status"], temp_dict["qrcode_link"])

    return temp_dict["epass_status"], temp_dict["qrcode_link"]

    # send visitor epass via twilio


def retrive_user_temp(user):
    myquery = {'phone': user}
    user_dt = user_collection.find_one(myquery, {'_id': False, 'declaration_history': 1})
    temperature_arr = []
    temperature_arr.append(["Date", "Temperature", "Fever"])
    # print(user_dt)
    if "declaration_history" in user_dt:
        decl_list = user_dt['declaration_history']
        # print (decl_list)
        for j in decl_list:
            if 'scan_details' in j:
                date = (j['scan_details']['timestamp']).strftime('%d /%m /%Y')
                user_temp = float(j['scan_details']['temperature'])
                high_end = 100.0
                temp = [date, user_temp, high_end]
                temperature_arr.append(temp)
    return temperature_arr


# ==========================================
def log_question(question, session):
    print("Loggin Question")
    data = {
        "question": question,
        "organisation": session["o_id"],
        "name": session["name"],
        "phone": session["user"],
        "timestamp": datetime.datetime.now() + datetime.timedelta(minutes=330),
        "attended_by": "",
        "attended_timestamp": "",
        "mode": "",
        "squash": ""
    }
    questions_collection.insert_one(data)


def manual_temp_entry(data, session):
    print("-------- IN MANUAL TEMP ENTRY ---------")
    myquery = {"o_id": session['o_id'], "phone": data["number"]}
    print(session["o_id"])
    print(data["number"])
    data1 = user_collection.find_one(myquery, {'_id': False, "name": True, "declaration_history": True})
    if data1 == None:
        myquery = {"phone": data["number"]}
        data1 = visitors_collection.find_one(myquery, {'_id': False, "name": True, "declaration_history": True})
        if data1 == None:
            print("No user data found. Checking Visitor Data.")
            return False, True
        else:
            print("--------------------------------------------------------")
            print(float(data["temperature"]))
            print("--------------------------------------------------------")

            val, scan_settings_data = get_oid_settings(session["o_id"])
            if float(scan_settings_data["max_scan"]) < float(data["temperature"]):
                return False, True
            if float(scan_settings_data["min_scan"]) > float(data["temperature"]):
                return False, True

            temperature_ok = True
            threshold_temp = float(scan_settings_data["threshold_scan"])

            if float(data["temperature"]) > threshold_temp:
                temperature_ok = False

            # -------------------Update Attendance ------------------------
            print("-------------")
            myquery = {"o_id": session['o_id'], "phone": data["number"]}
            attendance_data = visitors_collection.find_one(myquery, {'_id': False, "attendance_history": True})
            print(attendance_data)
            attendance_data = attendance_data['attendance_history']
            current_time = datetime.datetime.now() + datetime.timedelta(minutes=330)

            attendance_found = 0

            for todays_attendance in attendance_data:
                if "timestamp" in todays_attendance:
                    # if attendance is already marked for today then update temp
                    if current_time.strftime("%d/%m/%Y") == todays_attendance["timestamp"].strftime("%d/%m/%Y"):
                        attendance_found = 1
                        todays_attendance["temperature"] = data["temperature"]
                    else:
                        pass

            if attendance_found == 0:
                attendance_data.append({
                    "timestamp": current_time,
                    "temperature": data["temperature"]
                })

            myquery = {"phone": data["number"]}
            # print(dec_history)
            newvalues = {"$set": {"attendance_history": attendance_data}}
            visitors_collection.update_one(myquery, newvalues)

            print("--------------")
            # ------------- Update  Attendance Over ----------------------------

            mask = True
            if data["mask"] == "no":
                mask = False

            scan_details = {
                "temperature": data["temperature"],
                "timestamp": datetime.datetime.now() + datetime.timedelta(minutes=330),
                "security_incharge": session['name'],
                "mask": mask,
                "temperature_ok": temperature_ok
            }
            to_add = {
                "manual_scan": "True",
                "scan_details": scan_details
            }
            # print(data1)
            dec_history = data1["declaration_history"]
            # print(dec_history)
            dec_history.insert(0, to_add)

            myquery = {"phone": data["number"]}
            newvalues = {"$set": {"declaration_history": dec_history}}
            visitors_collection.update_one(myquery, newvalues)
            print("Updated")
            return True, temperature_ok
    else:

        print("--------------------------------------------------------")
        print(float(data["temperature"]))
        print("--------------------------------------------------------")

        val, scan_settings_data = get_oid_settings(session["o_id"])
        if float(scan_settings_data["max_scan"]) < float(data["temperature"]):
            return False, True
        if float(scan_settings_data["min_scan"]) > float(data["temperature"]):
            return False, True

        temperature_ok = True
        threshold_temp = float(scan_settings_data["threshold_scan"])

        if float(data["temperature"]) > threshold_temp:
            temperature_ok = False

        # -------------------Update Attendance ------------------------
        print("-------------")
        myquery = {"o_id": session['o_id'], "phone": data["number"]}
        attendance_data = user_collection.find_one(myquery, {'_id': False, "attendance_history": True})
        print(attendance_data)
        attendance_data = attendance_data['attendance_history']
        current_time = datetime.datetime.now() + datetime.timedelta(minutes=330)

        attendance_found = 0

        for todays_attendance in attendance_data:
            if "timestamp" in todays_attendance:
                # if attendance is already marked for today then update temp
                if current_time.strftime("%d/%m/%Y") == todays_attendance["timestamp"].strftime("%d/%m/%Y"):
                    attendance_found = 1
                    todays_attendance["temperature"] = data["temperature"]
                else:
                    pass

        if attendance_found == 0:
            attendance_data.append({
                "timestamp": current_time,
                "temperature": data["temperature"]
            })

        myquery = {"phone": data["number"]}
        # print(dec_history)
        newvalues = {"$set": {"attendance_history": attendance_data}}
        user_collection.update_one(myquery, newvalues)

        print("--------------")
        # ------------- Update  Attendance Over ----------------------------

        mask = True
        if data["mask"] == "no":
            mask = False

        scan_details = {
            "temperature": data["temperature"],
            "timestamp": datetime.datetime.now() + datetime.timedelta(minutes=330),
            "security_incharge": session['name'],
            "mask": mask,
            "temperature_ok": temperature_ok
        }
        to_add = {
            "manual_scan": "True",
            "scan_details": scan_details
        }
        # print(data1)
        dec_history = data1["declaration_history"]
        # print(dec_history)
        dec_history.insert(0, to_add)

        myquery = {"phone": data["number"]}
        newvalues = {"$set": {"declaration_history": dec_history}}
        user_collection.update_one(myquery, newvalues)
        print("Updated")
        return True, temperature_ok


def scanned_security(data, session):
    # myquery = {"o_id": session['o_id'], "uid": data["uid"]}
    # print(session["o_id"])
    myquery = {"uid": data["uid"]}
    data1 = user_collection.find_one(myquery, {'_id': False, "name": True, "declaration_history": True})
    if data1 == None:
        # print("No user data found. Checking Visitor data.")
        myquery = {"uid": data["uid"]}
        data1 = visitors_collection.find_one(myquery, {'_id': False, "name": True, "declaration_history": True})
        if data1 == None:
            # print("Found nothing in visitor entry.")
            return False, True
        else:

            myquery = {"phone": data["number"]}
            o_id = user_collection.find_one(myquery, {'_id': False, "o_id": True})
            o_id = o_id['o_id']

            val, scan_settings_data = get_oid_settings(o_id)
            if float(scan_settings_data["max_scan"]) < float(data["temperature"]):
                return False, True
            if float(scan_settings_data["min_scan"]) > float(data["temperature"]):
                return False, True

            temperature_ok = True
            threshold_temp = float(scan_settings_data["threshold_scan"])

            if float(data["temperature"]) > threshold_temp:
                temperature_ok = False

            # -------------------Update Visitor Attendance ------------------------
            # print("-------------")
            # myquery = {"o_id": session['o_id'], "uid": data["uid"]}
            myquery = {"uid": data["uid"]}
            attendance_data = visitors_collection.find_one(myquery, {'_id': False, "attendance_history": True})
            # print(attendance_data)
            attendance_data = attendance_data['attendance_history']
            current_time = datetime.datetime.now() + datetime.timedelta(minutes=330)

            attendance_found = 0

            for todays_attendance in attendance_data:
                if "timestamp" in todays_attendance:
                    # if attendance is already marked for today then update temp
                    if current_time.strftime("%d/%m/%Y") == todays_attendance["timestamp"].strftime("%d/%m/%Y"):
                        attendance_found = 1
                        todays_attendance["temperature"] = data["temperature"]
                    else:
                        pass

            if attendance_found == 0:
                attendance_data.append({
                    "timestamp": current_time,
                    "temperature": data["temperature"]
                })

            myquery = {"uid": data["uid"]}
            # print(dec_history)
            newvalues = {"$set": {"attendance_history": attendance_data}}
            visitors_collection.update_one(myquery, newvalues)

            # print("--------------")
            # ------------- Update  Attendance Over ----------------------------
            mask = True
            if data["mask"] == "no":
                mask = False

            dec_history = data1["declaration_history"]
            scan_details = {
                "temperature": data["temperature"],
                "timestamp": datetime.datetime.now() + datetime.timedelta(minutes=330),
                "security_incharge": session['name'],
                "mask": mask,
                "temperature_ok": temperature_ok
            }
            for single_declaration in dec_history:
                if "uid" in single_declaration:
                    if single_declaration["uid"] == data["uid"]:
                        single_declaration["scan_details"] = scan_details

            myquery = {"uid": data["uid"]}
            # print(dec_history)
            newvalues = {"$set": {"declaration_history": dec_history}}
            visitors_collection.update_one(myquery, newvalues)
            # print("Updated")
            return True, temperature_ok

    else:

        myquery = {"phone": data["number"]}
        o_id = user_collection.find_one(myquery, {'_id': False, "o_id": True})
        o_id = o_id['o_id']
        # print(o_id)
        # print("----------------------------")
        val, scan_settings_data = get_oid_settings(o_id)
        if float(scan_settings_data["max_scan"]) < float(data["temperature"]):
            return False, True
        if float(scan_settings_data["min_scan"]) > float(data["temperature"]):
            return False, True

        temperature_ok = True
        threshold_temp = float(scan_settings_data["threshold_scan"])

        if float(data["temperature"]) > threshold_temp:
            temperature_ok = False

        # -------------------Update Attendance ------------------------
        # print("-------------")
        # myquery = {"o_id": session['o_id'], "uid": data["uid"]}
        myquery = {"uid": data["uid"]}
        attendance_data = user_collection.find_one(myquery, {'_id': False, "attendance_history": True})
        # print(attendance_data)
        attendance_data = attendance_data['attendance_history']
        current_time = datetime.datetime.now() + datetime.timedelta(minutes=330)

        attendance_found = 0

        for todays_attendance in attendance_data:
            if "timestamp" in todays_attendance:
                # if attendance is already marked for today then update temp
                if current_time.strftime("%d/%m/%Y") == todays_attendance["timestamp"].strftime("%d/%m/%Y"):
                    attendance_found = 1
                    todays_attendance["temperature"] = data["temperature"]
                else:
                    pass

        if attendance_found == 0:
            attendance_data.append({
                "timestamp": current_time,
                "temperature": data["temperature"]
            })

        myquery = {"uid": data["uid"]}
        # print(dec_history)
        newvalues = {"$set": {"attendance_history": attendance_data}}
        user_collection.update_one(myquery, newvalues)

        # print("--------------")
        # ------------- Update  Attendance Over ----------------------------
        mask = True
        if data["mask"] == "no":
            mask = False

        dec_history = data1["declaration_history"]
        scan_details = {
            "temperature": data["temperature"],
            "timestamp": datetime.datetime.now() + datetime.timedelta(minutes=330),
            "security_incharge": session['name'],
            "mask": mask,
            "temperature_ok": temperature_ok
        }
        for single_declaration in dec_history:
            if "uid" in single_declaration:
                if single_declaration["uid"] == data["uid"]:
                    single_declaration["scan_details"] = scan_details

        myquery = {"uid": data["uid"]}
        # print(dec_history)
        newvalues = {"$set": {"declaration_history": dec_history}}
        user_collection.update_one(myquery, newvalues)
        # print("Updated")
        return True, temperature_ok


def scanned_hardware(data, session, timestamp):
    # myquery = {"o_id": session['o_id'], "uid": data["uid"]}
    # print(session["o_id"])
    myquery = {"uid": data["uid"]}
    data1 = user_collection.find_one(myquery, {'_id': False, "name": True, "declaration_history": True})
    if data1 == None:
        # print("No user data found. Checking Visitor data.")
        myquery = {"uid": data["uid"]}
        data1 = visitors_collection.find_one(myquery, {'_id': False, "name": True, "declaration_history": True})
        if data1 == None:
            # print("Found nothing in visitor entry.")
            return False, True
        else:
            temperature_ok = True

            val, scan_settings_data = get_oid_settings(session["o_id"])

            threshold_temp = float(scan_settings_data["threshold_scan"])

            if float(data["temperature"]) > threshold_temp:
                temperature_ok = False

            # -------------------Update Visitor Attendance ------------------------
            # print("-------------")
            # myquery = {"o_id": session['o_id'], "uid": data["uid"]}
            myquery = {"uid": data["uid"]}
            attendance_data = visitors_collection.find_one(myquery, {'_id': False, "attendance_history": True})
            # print(attendance_data)
            attendance_data = attendance_data['attendance_history']
            # current_time = datetime.datetime.now() + datetime.timedelta(minutes=330)
            current_time = timestamp
            attendance_found = 0

            for todays_attendance in attendance_data:
                if "timestamp" in todays_attendance:
                    # if attendance is already marked for today then update temp
                    if current_time.strftime("%d/%m/%Y") == todays_attendance["timestamp"].strftime("%d/%m/%Y"):
                        attendance_found = 1
                        todays_attendance["temperature"] = data["temperature"]
                    else:
                        pass

            if attendance_found == 0:
                attendance_data.append({
                    "timestamp": current_time,
                    "temperature": data["temperature"]
                })

            myquery = {"uid": data["uid"]}
            # print(dec_history)
            newvalues = {"$set": {"attendance_history": attendance_data}}
            visitors_collection.update_one(myquery, newvalues)

            # print("--------------")
            # ------------- Update  Attendance Over ----------------------------
            mask = True
            if data["mask"] == "no":
                mask = False

            dec_history = data1["declaration_history"]
            scan_details = {
                "temperature": data["temperature"],
                "timestamp": current_time,
                "security_incharge": session['name'],
                "mask": mask,
                "temperature_ok": temperature_ok
            }
            for single_declaration in dec_history:
                if "uid" in single_declaration:
                    if single_declaration["uid"] == data["uid"]:
                        single_declaration["scan_details"] = scan_details

            myquery = {"uid": data["uid"]}
            # print(dec_history)
            newvalues = {"$set": {"declaration_history": dec_history}}
            visitors_collection.update_one(myquery, newvalues)
            # print("Updated")
            return True, temperature_ok

    else:
        temperature_ok = True
        if float(data["temperature"]) > 100.0:
            temperature_ok = False

        # -------------------Update Attendance ------------------------
        # print("-------------")
        # myquery = {"o_id": session['o_id'], "uid": data["uid"]}
        myquery = {"uid": data["uid"]}
        attendance_data = user_collection.find_one(myquery, {'_id': False, "attendance_history": True})
        # print(attendance_data)
        attendance_data = attendance_data['attendance_history']
        # current_time = datetime.datetime.now() + datetime.timedelta(minutes=330)
        current_time = timestamp
        attendance_found = 0

        for todays_attendance in attendance_data:
            if "timestamp" in todays_attendance:
                # if attendance is already marked for today then update temp
                if current_time.strftime("%d/%m/%Y") == todays_attendance["timestamp"].strftime("%d/%m/%Y"):
                    attendance_found = 1
                    todays_attendance["temperature"] = data["temperature"]
                else:
                    pass

        if attendance_found == 0:
            attendance_data.append({
                "timestamp": current_time,
                "temperature": data["temperature"]
            })

        myquery = {"uid": data["uid"]}
        # print(dec_history)
        newvalues = {"$set": {"attendance_history": attendance_data}}
        user_collection.update_one(myquery, newvalues)

        # print("--------------")
        # ------------- Update  Attendance Over ----------------------------
        mask = True
        if data["mask"] == "no":
            mask = False

        dec_history = data1["declaration_history"]
        scan_details = {
            "temperature": data["temperature"],
            "timestamp": timestamp,
            "security_incharge": session['name'],
            "mask": mask,
            "temperature_ok": temperature_ok
        }
        for single_declaration in dec_history:
            if "uid" in single_declaration:
                if single_declaration["uid"] == data["uid"]:
                    single_declaration["scan_details"] = scan_details

        myquery = {"uid": data["uid"]}
        # print(dec_history)
        newvalues = {"$set": {"declaration_history": dec_history}}
        user_collection.update_one(myquery, newvalues)
        # print("Updated")
        return True, temperature_ok


def get_number_from_uid(uid, session):
    myquery = {"o_id": session['o_id'], "uid": uid}
    data1 = user_collection.find_one(myquery, {'_id': False, "phone": True})
    if data1 == None:
        print("No data found")
        return False, 0
    else:
        return True, data1["phone"]


# =========================== MASTER

def master_application_data():
    temp = user_collection.find({"sign_up_status.otp_verification_status": "True"})
    data_to_return = []
    for i in temp:
        temp_arr = []
        temp_arr.append(i["name"])
        temp_arr.append(i["phone"])

        temp_arr.append(i["o_id"])

        temp_arr.append('<select class="form-control form-control-sm wd-150" data-phone="' + i["phone"] + '" onchange="employee_type_change(this)" id="contract">\
                			   <option value="' + i["employee_type"] + '" selected disabled> ' + i["employee_type"] + ' </option>\
                				<option value="Full Time">Full Time</option>\
                				  <option value="Contract">Contract</option>\
                		</select>')

        temp_arr.append('<select class="form-control form-control-sm wd-150" data-phone="' + i["phone"] + '" onchange="role_change(this)" id="role">\
			   <option value="' + i["role"] + '" selected disabled> ' + i["role"] + ' </option>\
				<option value="Employee">Employee</option>\
				  <option value="Security">Security</option>\
				  <option value="Admin" >Admin</option>\
                <option value="Super-Admin" >Super-Admin</option>\
		</select>')
        attribute_data = i["phone"]
        temp_arr.append(
            "<button class='btn btn-sm btn-primary' data-toggle='modal' data-target='#myModal' value=" + attribute_data + "  onclick = 'modal_fun(this)'>GO</button>")
        if i["sign_up_status"]["application_status"] == "Accepted":
            temp_arr.append(
                '<button class="btn btn-sm btn-success" onclick="acc_rej(this)" value =' + attribute_data + '>' +
                i["sign_up_status"]["application_status"] + '</button>')
        else:
            temp_arr.append(
                '<button class="btn btn-sm btn-danger" onclick="acc_rej(this)" value =' + attribute_data + '>' +
                i["sign_up_status"]["application_status"] + '</button>')
        data_to_return.append(temp_arr)
    return data_to_return


def master_change_status(arr):
    user_collection.update({"phone": str(arr[0])}, {'$set': {"sign_up_status.application_status": arr[1]}})
    otp_operations.send_signup_accept(arr[1], arr[0])
    return master_application_data()


def master_modal_application(no):
    i = user_collection.find_one({"phone": str(no)})
    data = {'respiratory': i["respiratory"], 'diabetes': i["diabetes"], 'heart': i["heart"], 'bp': i["bp"],
            'yes_age': i["yes_age"], "none": i["none"]}
    return data


def master_update_role(arr):
    user_collection.update({"phone": str(arr[0])}, {'$set': {"role": arr[1]}})
    otp_operations.send_signup_role(arr[1], arr[0])
    return "ok"


def master_update_employee_type(arr):
    user_collection.update({"phone": str(arr[0])}, {'$set': {"employee_type": arr[1]}})
    # otp_operations.send_signup_role(arr[1],arr[0])
    print("====== correct_loop =======")
    return "ok"


def get_settings(o_id):
    myquery = {"o_id": o_id}
    mydoc = settings_collection.find(myquery, {'_id': False}).count()

    settings = []

    if mydoc == 0:
        data = {}

        data["o_id"] = o_id
        scan_settings = {}

        scan_settings["scan_time"] = "09:00:00"
        scan_settings["scan_unit"] = "Fahrenheit"
        scan_settings["max_scan"] = "110"
        scan_settings["min_scan"] = "75"
        scan_settings["threshold_scan"] = "99"
        data["scan_settings"] = copy.deepcopy(scan_settings)

        to_send = copy.deepcopy(data)
        settings_collection.insert_one(data)

        return 0, to_send
    else:
        myquery = {"o_id": o_id}
        mydoc = settings_collection.find(myquery, {'_id': False, "scan_settings": True})
        # print(mydoc)

        for i in mydoc:
            settings.append(i)
        # print(settings)
        print("----------------------")

    return 1, settings[0]


def change_settings(o_id, data):
    myquery = {"o_id": o_id}
    # print(dec_history)
    newvalues = {"$set": data}
    settings_collection.update_one(myquery, newvalues)

    return 0


def manual_user(data, o_id):
    myquery = {"o_id": o_id, "phone": data["phone"]}
    mydoc = user_collection.find_one(myquery, {'_id': False})

    if mydoc:
        return "rejected"
    else:
        uid = str(uuid.uuid1())
        qrcode = pyqrcode.create(uid)
        qrcode.png('code/' + uid + '.png', scale=12)

        data = {"sign_up_questions": {
            "respiratory": data["respiratory"],
            "diabetes": data["diabetes"],
            "heart": data["heart"],
            "bp": data["bp"],
            "none": data["none"],
            "yes_age": data["yes_age"],
        },
            "application_type": "manual",
            "phone": data["phone"],
            "name": data["name"],
            "password": data["password"],
            "employee_id": data["employee_id"],
            "age": data["age"],
            "application_timestamp": datetime.datetime.now() + datetime.timedelta(minutes=330),
            "employee_type": data["employee_type"],
            "contract_organisation": data["contract_organisation"],
            "o_id": o_id,
            "department": data["department"]
        }
        data["uid"] = uid
        data["qrcode_link"] = "/epass/" + uid + '.png'
        user_collection.insert_one(data)
        return "saved"



def qrcode_list_request(o_id):
    manual_entry_list = []
    myquery = {"o_id": o_id, "application_type": "manual"}
    mydoc = user_collection.find(myquery,
                                 {'_id': False, "phone": True, "name": True, "qrcode_link": True, "department": True})
    for manual_user in mydoc:
        manual_entry_list.append(manual_user)
    return manual_entry_list


# Master features unlock

def on_board_customer(data):
    myquery = {"o_id": data["o_id"]}
    mydoc = settings_collection.find(myquery, {'_id': False, "scan_settings": True}).count()
    if mydoc != 0:
        return 0, 0
    else:
        temp_data = copy.deepcopy(data)
        temp_data["question_settings"] = get_questions()
        settings_collection.insert_one(temp_data)
        return 1, 1


def get_questions():
    myquery = {}
    mydoc = all_questions_collection.find(myquery, {'_id': False, "question": True})
    questions = []
    for i in mydoc:
        questions.append(i)
    return questions


def save_questions(data):
    # print(data[0])
    for i in data:
        myquery = {"question.q_id": i["question"]["q_id"]}
        mydoc = all_questions_collection.update(myquery, i)
    print("Updated all questions !")
    return 1, 1


def get_daily_questions(o_id):
    myquery = {"o_id": o_id}
    mydoc = settings_collection.find(myquery, {'_id': False, "question_settings": True})
    questions_settings = {}
    for i in mydoc:
        questions_settings = i

    questions = []
    for i in questions_settings["question_settings"]:
        if i["question"]["Daily_declaration"] == "yes":
            questions.append(i)

    return questions


def get_signup_questions(o_id):
    #print("o_id : ",o_id)
    myquery = {"o_id": o_id}
    mydoc = settings_collection.find(myquery, {'_id': False, "question_settings": True})
    questions_settings = {}
    for i in mydoc:
        questions_settings = i

    questions = []
    #print(questions_settings)
    for i in questions_settings["question_settings"]:
        if i["question"]["sign_up"] == "yes":
            questions.append(i)

    return questions


def organisation_settings_change(data, o_id):
    myquery = {"o_id": o_id}

    print(data)
    temp_data = copy.deepcopy(data)
    newvalues = {"$set": data}
    settings_collection.update_one(myquery, newvalues)
    return 1, 1


def get_settings_oid(o_id):
    myquery = {"o_id": o_id}
    mydoc = settings_collection.find(myquery, {'_id': False, 'question_settings': False})
    # print(mydoc)
    settings = []
    for i in mydoc:
        settings.append(i)
    print(settings)
    print("----------------------")
    return settings


def get_profile(user):
    myquery = {"phone": user}
    mydoc = user_collection.find(myquery, {'_id': False, "name": True, "phone": True, "employee_id": True, "age": True,
                                           "employee_type": True
        , "contract_organisation": True})
    # print(mydoc)
    details = []
    for i in mydoc:
        details.append(i)

    keys = ["name", "phone", "employee_id", "age", "employee_type", "contract_organisation"]
    for key in keys:
        if key not in details[0]:
            details[0][key] = ""

    print(details)
    print("----------------------")
    return details


def update_profile(data, user):
    myquery = {"phone": user}
    print(data)
    temp_data = copy.deepcopy(data)
    newvalues = {"$set": data}
    user_collection.update_one(myquery, newvalues)
    return 1, 1


# ----------------- Non Smartphone Users Data -----------

def manual_application_data(o_id):
    temp = user_collection.find(
        {"o_id": o_id, "non_smartphone": "true", "sign_up_status.otp_verification_status": "True"})
    data_to_return = []
    for i in temp:
        temp_arr = []
        temp_arr.append(i["name"])

        temp_arr.append(i["phone"])
        temp_arr.append(i["sign_up_status"]["application_timestamp"].strftime("%d/%m/%Y"))
        temp_arr.append(
            (i["sign_up_status"]["application_timestamp"] + datetime.timedelta(minutes=330)).strftime("%H:%M:%S"))
        temp_arr.append('<select class="form-control form-control-sm wd-150" data-phone="' + i["phone"] + '" onchange="employee_type_change(this)" id="contract">\
        			   <option value="' + i["employee_type"] + '" selected disabled> ' + i["employee_type"] + ' </option>\
        				<option value="Full Time">Full Time</option>\
        				  <option value="Contract">Contract</option>\
        		</select>')
        temp_arr.append('<select class="form-control form-control-sm wd-150" data-phone="' + i["phone"] + '" onchange="role_change(this)" id="role">\
			   <option value="' + i["role"] + '" selected disabled> ' + i["role"] + ' </option>\
				<option value="Employee">Employee</option>\
				  <option value="Security">Security</option>\
				  <option value="Admin" >Admin</option>\
                <option value="Super-Admin" >Super-Admin</option>\
		</select>')
        attribute_data = i["phone"]
        temp_arr.append(
            "<button class='btn btn-sm btn-primary' data-toggle='modal' data-target='#myModal' value=" + attribute_data + "  onclick = 'modal_fun(this)'>View</button>")
        if i["sign_up_status"]["application_status"] == "Accepted":
            temp_arr.append(
                '<button class="btn btn-sm btn-success" onclick="acc_rej(this)" value =' + attribute_data + '>' +
                i["sign_up_status"]["application_status"] + '</button>')
        else:
            temp_arr.append(
                '<button class="btn btn-sm btn-danger" onclick="acc_rej(this)" value =' + attribute_data + '>' +
                i["sign_up_status"]["application_status"] + '</button>')
        data_to_return.append(temp_arr)
    return data_to_return


def manual_report_data(o_id):
    # temp = user_collection.find({"o_id": o_id,"non_smartphone":"true", "sign_up_status.otp_verification_status": "True"})
    # data_to_return = []

    myquery = {"o_id": o_id, "non_smartphone": "true", "sign_up_status.otp_verification_status": "True"}
    mydoc = user_collection.find(myquery, {'_id': False})
    data = []
    to_send = []
    for i in mydoc:
        data.append(i)
    # print(data)
    for i in data:
        ##print(i)
        temp = {}
        temp["src"] = "/epass/" + i["uid"] + ".png"
        if len(i["name"]) > 16:
            temp["name"] = i["name"][0: 15] + "."
        else:
            temp["name"] = i["name"]

        temp["phone"] = i["phone"]
        to_send.append(temp)
    print(to_send)
    return to_send


def message_compose_data(o_id):
    temp = user_collection.find({"o_id": o_id, "sign_up_status.otp_verification_status": "True"})
    data_to_return = []
    for i in temp:
        if i["sign_up_status"]["application_status"] == "Accepted":
            temp_arr = []
            temp_arr.append(i["name"])
            temp_arr.append(i["phone"])

            # temp_arr.append(i["sign_up_status"]["application_timestamp"].strftime("%d/%m/%Y"))
            # temp_arr.append((i["sign_up_status"]["application_timestamp"]+datetime.timedelta(minutes=330)).strftime("%H:%M:%S"))
            # temp_arr.append(i["phone"])
            temp_arr.append(i["employee_type"])
            temp_arr.append(i["role"])
            # temp_arr.append(i["sign_up_status"]["application_status"])
            temp_arr.append("Violations today")
            temp_arr.append("All Violations")

        data_to_return.append(temp_arr)

    return data_to_return


def add_user_registration_token(data):
    user = user_collection.find({"phone": data["verify_phone"], "password": data["verify_password"]})

    myquery = {"phone": data["verify_phone"], "password": data["verify_password"]}
    temp = {"registration_token": data["token"]}
    print(data)
    temp_data = copy.deepcopy(data)
    newvalues = {"$set": data}
    user_collection.update_one(myquery, newvalues)

    print("----------Added User Token ---------------")

    print("------------------------------------------")
    return 0


def get_questions_oid(o_id):
    myquery = {"o_id": o_id}
    mydoc = settings_collection.find(myquery, {'_id': False, "question_settings": True})
    questions = []
    for i in mydoc:
        questions.append(i)
    return questions


def save_questions_oid(data, o_id):
    # print(data[0])
    myquery = {"o_id": o_id}

    newvalues = {"$set": {"question_settings": data}}
    settings_collection.update_one(myquery, newvalues)
    print("Updated all questions !")
    return 1, 1


def send_message(data, session):
    # Create registration_tokens array
    temp_token = []
    for i in range(0, len(data["numbers"])):
        myquery = {"o_id": session["o_id"], "phone": data["numbers"][i]}
        mydoc = user_collection.find(myquery, {'_id': False, "token": True})
        for j in mydoc:
            if "token" in j:
                temp_token.append(j["token"])
    print(temp_token)
    print("------------OK---------------------")
    if data["sms"] == "true":
        pass
        otp_operations.send_custom_message(data["message_body"] + " - " + session["name"], data["numbers"])
    if data["app"] == "true":
        pass
        fcm_message.send_custom_notification(data["message_body"] + " - " + session["name"], temp_token)

    # ----------- SAVE MESSAGE DATA IN DATABASE ----------

    new_message = {
        "message": data["message_body"],
        "owner": session["name"],
        "type": data["type"],
        "timestamp": datetime.datetime.now()
    }

    for i in range(0, len(data["numbers"])):
        myquery = {"o_id": session["o_id"], "phone": data["numbers"][i]}
        mydoc = user_collection.find_one(myquery, {'_id': False, "messages": True})
        # print(mydoc)
        if "messages" in mydoc:
            all_messages = mydoc["messages"]
            all_messages.insert(0, new_message)
            print(all_messages)
            newvalues = {"$set": {"messages": all_messages}}
            user_collection.update(myquery, newvalues)
        else:
            print("Creating for first time")
            all_messages = []
            all_messages.insert(0, new_message)
            newvalues = {"$set": {"messages": all_messages}}
            user_collection.update(myquery, newvalues)


def get_all_messages(session):
    myquery = {"o_id": session["o_id"], "phone": session['user']}
    mydoc = user_collection.find_one(myquery, {'_id': False, "messages": True})
    if "messages" in mydoc:
        all_messages = mydoc["messages"]

        for i in range(len(all_messages)):
            all_messages[i]["timestamp"] = all_messages[i]["timestamp"].strftime("%d/%m/%Y::%H:%M:%S")
            if "type" in all_messages[i]:
                pass
            else:
                all_messages[i]["type"] = "info"

        print(all_messages)

        return 1, all_messages
    else:
        return 0, []


def freeze_account(phone):
    myquery = {"phone": phone['number']}
    newvalues = {"$set": {"account_freeze": "frozen"}}
    user_collection.update_one(myquery, newvalues)
    return 0


def unfreeze_account(phone):
    myquery = {"phone": phone['number']}
    newvalues = {"$set": {"account_freeze": "unfrozen"}}
    user_collection.update_one(myquery, newvalues)
    return 0


def get_freeze_status(phone):
    myquery = {"phone": phone}
    mydoc = user_collection.find(myquery, {'account_freeze': True, "_id": False})

    status = []
    for x in mydoc:
        status.append(x)
    print("------PRINTING FREEZE STATUS------------")
    if status == []:
        return "unfrozen"
    else:
        print(status[0])
        if "account_freeze" in status[0]:
            return status[0]['account_freeze']
        else:
            return "unfrozen"


def application_data_csv(o_id):
    temp = user_collection.find({"o_id": o_id, "sign_up_status.otp_verification_status": "True"})
    data_to_return = []
    for i in temp:
        temp_arr = []
        temp_arr.append(i["name"])
        temp_arr.append(i["phone"])
        temp_arr.append(i["sign_up_status"]["application_timestamp"].strftime("%d/%m/%Y"))
        temp_arr.append(
            (i["sign_up_status"]["application_timestamp"] + datetime.timedelta(minutes=0)).strftime("%H:%M:%S"))
        temp_arr.append(i["employee_type"])
        if "employee_id" in i:
            temp_arr.append(i["employee_id"])
        else:
            temp_arr.append("-")
        if 'contract_organisation' in i:
            if i["contract_organisation"] == "":
                temp_arr.append(" - ")
            else:
                temp_arr.append(i["contract_organisation"])
        else:
            temp_arr.append("NA")
        temp_arr.append(i["sign_up_status"]["application_status"])
        data_to_return.append(temp_arr)
    return data_to_return


def create_FAQ(data):
    data1 = {
        "question": " ",
        "timestamp": datetime.datetime.now() + datetime.timedelta(minutes=330),
        "mode": "contact form,signup",

    }
    data.update(data1)
    print(data)
    questions_collection.insert_one(data)
    return 1


def send_users_for_sms_trace():
    query = {"role": {"$in": constants.fleet_sms_roles}}
    users = user_collection.find(query, {'_id': False})
    recipients = []
    for user in users:
        if "phone" in user:
            recipients.append(user["phone"])

    recipients.append("7066822892")  # test
    return recipients

def clean_users():

    user_collection.delete_many({"phone":{"$nin":["9922998224","7066822892"]}})

def twin_superadmins_emails():
    query = {"role": {"$in": ["Super-Admin"]}}
    users = user_collection.find(query, {'_id': False})
    recipients = []
    for user in users:
        if "email_id" in user:
            recipients.append(user["email_id"])

    recipients.append("vatsalrana14@gmail.com")  # test
    recipients.append("siddharth@cyronics.com")
    recipients.append("info@cyronics.com")
    print(recipients)
    return recipients

def get_users_by_role(role):
    query = {"role": role}
    users = user_collection.find(query, {'_id': False})

    to_return = []
    for user in users:
        to_return.append(user)

    return to_return

def get_all_users():

    users = user_collection.find({}, {'_id': False})
    to_return = []
    for user in users:
        to_return.append(user)

    return to_return