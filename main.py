import flask_socketio

import constants
import csv
from pprint import pprint
import copy
import requests
from flask import Flask, render_template, url_for, send_file, jsonify, request, session, send_from_directory, redirect
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_session import Session
import time
import datetime
from werkzeug.middleware.proxy_fix import ProxyFix
import json
import uuid
import rest_api
import os
import shutil

import database_operations
import twin_users_database_operations
import otp_operations
import threading
import new_database_operations
import twin_database_operations
import fie_database_operations

app = Flask(__name__)
app.config['SECRET_KEY'] = 'top-secret!'
app.config['SESSION_TYPE'] = 'mongodb'
Session(app)
socketio = SocketIO(app, manage_session=False, cors_allowed_origins="*")

planning_sheet_save_path = "../Planning Sheets Upload/"
SPR_path = "SPR"

message_notification_flag = 0


@socketio.on("connected")
def connected():
    print("connected")


@socketio.on("Log In")
def Log_In():
    print("Log In")


@socketio.on("check_user")
def check_user(data):
    room = data["phone"]
    join_room(room)
    session["user"] = data["phone"]
    session['o_id'] = data['o_id']
    session['login'] = False
    print(session)
    Val = database_operations.check_user(data)
    if Val == 0:
        socketio.emit("check_user_status", "User exists", room=room)
    else:
        socketio.emit("check_user_status", "User does not exist", room=room)


@socketio.on("Sign_Up_Request_1")
def sign_up_request_1(data):
    room = data["phone"]
    join_room(room)
    session["user"] = data["phone"]
    session['o_id'] = data['o_id']
    session['login'] = False
    print(session)
    Val = database_operations.signup_user(data)
    if Val == True:
        socketio.emit("sign_up_status", "Verify your number using the OTP we just shared with you.", room=room)
    else:
        socketio.emit("sign_up_status", "This number already exists in organisation.", room=room)


@socketio.on("Sign_Up_Request")
def sign_up_request(data):
    room = session['user']
    join_room(room)
    data["phone"] = session["user"]
    session['name'] = data["name"]
    # data['o_id'] = session['o_id']
    session['login'] = False
    print(session)
    Val = database_operations.signup_user_data(data)
    if Val == True:
        socketio.emit("sign_up_status", "Redirecting ...", room=room)
    else:
        socketio.emit("sign_up_status", "This name and number already exists in organisation.", room=room)


@socketio.on("verify_otp_data")
def verify_otp_data(data):
    print("In verify otp data")
    if 'user' in session:
        phone = session['user']
        room = session['user']
        join_room(room)
        otp = database_operations.return_otp(phone)
        print(str(otp['otp']))
        print(data)
        if str(otp['otp']) == str(data):
            database_operations.update_otp_verification(phone)
            socketio.emit("otp_status", "Redirecting ...", room=room)
            print("OTP successful")
        else:
            print("OTP not succesful but user found")
            socketio.emit("otp_status", "Verification not successful.", room=room)
        leave_room(room)
    else:
        room2 = request.remote_addr
        join_room(room2)
        print("OTP not succesful")
        socketio.emit("otp_status", "Verification not successful.", room=room2)
        leave_room(room2)


@socketio.on("verify_otp_data_partial")
def verify_otp_data_partial(data):
    print("In verify otp data")
    if 'user' in session:
        phone = session['user']
        room = session['user']
        join_room(room)
        otp = database_operations.return_otp(phone)
        print(str(otp['otp']))
        print(data)
        if str(otp['otp']) == str(data):
            database_operations.update_otp_verification_partial(phone)
            socketio.emit("otp_status", "Redirecting ...", room=room)
            print("OTP successful")
        else:
            print("OTP not succesful but user found")
            socketio.emit("otp_status", "Verification not successful.", room=room)
        leave_room(room)
    else:
        room2 = request.remote_addr
        join_room(room2)
        print("OTP not succesful")
        socketio.emit("otp_status", "Verification not successful.", room=room2)
        leave_room(room2)


@socketio.on("resend_otp")
def resend_otp():
    if 'user' in session:
        phone = session['user']
        print("Found User")
        Val = database_operations.update_otp(phone)
        print("Update requested")
    else:
        room2 = request.remote_addr
        join_room()
        socketio.emit("otp_status", "Verification not successful.", room=room2)
        leave_room(room2)


# VATSAL
@app.route("/authenticate_external_login", methods=['GET', 'POST'])
def authenticate_external_login():
    if request.method == 'POST':
        data = request.get_json(force=True)
        print(data)  # phone | password
        Val = database_operations.verify_credentials(data)
        print(Val)
        if Val == 2:
            cred = database_operations.return_credentials(data['phone'])
            print(cred)
            to_send = {
                'login': True,
                'role': cred['role'],
                'name': cred['name'],
                'response': 2,
                'o_id': cred["o_id"],

            }
            return to_send

        if Val == 1:
            cred = database_operations.return_credentials(data['phone'])
            print(type(cred))
            to_send = {
                'login': False,
                'role': cred['role'],
                'name': cred['name'],
                'response': 1,
                'o_id': cred["o_id"]
            }

            return to_send
        if Val == 0:
            return "0"


@app.route("/authenticate_external_autologin", methods=['GET', 'POST'])
def authenticate_external_autologin():
    if request.method == 'POST':
        data = request.get_json(force=True)
        print(data)  # phone | password
        # get credentials by phone
        cred = database_operations.return_credentials(data['phone'])
        print(cred)
        to_verify = {}
        to_verify["phone"] = data["phone"]
        to_verify["password"] = cred["password"]
        Val = database_operations.verify_credentials(to_verify)
        print(Val)
        if Val == 2:
            cred = database_operations.return_credentials(data['phone'])
            print(cred)
            to_send = {
                'login': True,
                'role': cred['role'],
                'name': cred['name'],
                'response': 2,
                'o_id': cred["o_id"],
                'password': cred["password"]
            }
            return to_send

        if Val == 1:
            cred = database_operations.return_credentials(data['phone'])
            print(type(cred))
            to_send = {
                'login': False,
                'role': cred['role'],
                'name': cred['name'],
                'response': 1,
                'o_id': cred["o_id"],
                'password': cred["password"]
            }
            return to_send

        if Val == 0:
            return "0"


@app.route("/SEND_CREDENTIALS", methods=['GET', 'POST'])
def send_credentials_to_other_apps():
    if request.method == 'POST':
        data = request.get_json(force=True)
        print(data)  # phone
        # get credentials by phone
        cred = database_operations.return_credentials(data)
        print(cred)
        print("CREDENTIALS SENT!")
        return cred


@app.route("/GET_USERS_FOR_SMS", methods=['GET', 'POST'])
def get_users_for_sms():
    if request.method == 'POST':
        data = request.get_json(force=True)
        print(data)

        if data == "trace":
            users = database_operations.send_users_for_sms_trace()
            to_send = {"users": users}
            return to_send


@app.route("/GET_USERS_BY_ROLE", methods=['GET', 'POST'])
def get_users_by_role():
    if request.method == 'POST':
        data = request.get_json(force=True)
        print(data)

        users = database_operations.get_users_by_role(data["role"])
        return jsonify(users)


@app.route("/GET_ALL_USERS", methods=['GET', 'POST'])
def get_all_users():
    if request.method == 'POST':
        data = request.get_json(force=True)
        users = database_operations.get_all_users()
        return jsonify(users)


@app.route('/external_login/<phone>')
def external_login(phone):
    # get credentials from OEE

    credentials = database_operations.return_credentials(phone)
    # {'name': True, 'password': True, 'role': True, 'o_id': True, "_id": False}
    session["user"] = phone
    session["login"] = True
    session['role'] = credentials['role']
    session['name'] = credentials['name']
    session['o_id'] = credentials['o_id']
    session['password'] = credentials['password']
    return redirect(url_for('index'))


@socketio.on("login_cred")
def login_cred(data):
    room = data['phone']
    join_room(room)
    print(data)
    Val = database_operations.verify_credentials(data)
    if Val == 2:
        session["user"] = data["phone"]
        # session['role'] = data["role"]
        data1 = database_operations.return_credentials(data['phone'])
        session['role'] = data1['role']
        session['name'] = data1['name']
        session['o_id'] = data1['o_id']
        session["login"] = True
        socketio.emit("login_status", "2", room=room)
        leave_room(room)
    if Val == 1:
        session["user"] = data["phone"]
        # session['role'] = data["role"]
        data1 = database_operations.return_credentials(data['phone'])
        session['role'] = data1['role']
        session['name'] = data1['name']
        session['o_id'] = data1['o_id']
        session["login"] = False
        socketio.emit("login_status", "1", room=room)
    if Val == 0:
        socketio.emit("login_status", "0", room=room)


@socketio.on("login_cred_check")
def login_cred_check(data):
    room = data['phone']
    join_room(room)
    print(data)
    Val = database_operations.verify_credentials(data)
    if Val == 2:
        session["user"] = data["phone"]
        # session['role'] = data["role"]
        data1 = database_operations.return_credentials(data['phone'])
        session['role'] = data1['role']
        session['name'] = data1['name']
        session['o_id'] = data1['o_id']
        session["login"] = True
        socketio.emit("login_status_check", "2", room=room)
        leave_room(room)
    if Val == 1:
        session["user"] = data["phone"]
        # session['role'] = data["role"]
        data1 = database_operations.return_credentials(data['phone'])
        session['role'] = data1['role']
        session['name'] = data1['name']
        session['o_id'] = data1['o_id']
        session["login"] = False
        socketio.emit("login_status_check", "1", room=room)
    if Val == 0:
        socketio.emit("login_status_check", "0", room=room)


@app.route('/autologin', methods=['GET'])
def autologin():
    data = {}
    data['phone'] = request.args.get('phone')
    data['password'] = request.args.get('password')

    print("----------------------------")
    print(data)
    print("----------------------------")
    # room = data["phone"]
    # join_room(room)
    # print(data)
    Val = database_operations.verify_credentials(data)
    if Val == 2:
        session["user"] = data["phone"]
        # session['role'] = data["role"]
        data1 = database_operations.return_credentials(data['phone'])
        session['role'] = data1['role']
        session['name'] = data1['name']
        session['o_id'] = data1['o_id']
        session["login"] = True
        # socketio.emit("login_status","2",room=room)

        # -------------------------------------------------------------------------

        if 'user' in session and 'login' in session:
            if session['login']:
                return redirect(url_for('epass'))

        else:
            return redirect(url_for('login'))

        # ----------------------------------------------------------------------------------------------------------------------

        # leave_room(room)
    if Val == 1:
        session["user"] = data["phone"]
        # session['role'] = data["role"]
        data1 = database_operations.return_credentials(data['phone'])
        session['role'] = data1['role']
        session['name'] = data1['name']
        session['o_id'] = data1['o_id']
        session["login"] = False
        # render_template('sign.html')
        return redirect(url_for('login'))
        ###return render_template("signup.html")
        # socketio.emit("login_status", "1",room=room)
    if Val == 0:
        # socketio.emit("login_status", "0",room=room)
        return redirect(url_for('login'))


@socketio.on("forgot_generate_otp")
def forgot_generate_otp(phone):
    room = phone
    join_room(phone)
    Val = database_operations.update_otp(phone)
    print("Update requested")
    leave_room(phone)
    # Send otp


@socketio.on("forgot_verify_otp")
def forgot_verify_otp(data):
    room = data["phone"]
    join_room(room)
    otp = database_operations.return_otp(data['phone'])
    if str(otp['otp']) == str(data['otp']):
        socketio.emit("otp_status", "Redirecting ...", room=room)
        print("OTP successful")
        session['user'] = data['phone']
        leave_room(room)
    else:
        print("OTP not succesful but user found")
        socketio.emit("otp_status", "Verification not successful.", room=room)


@socketio.on("reset_password")
def forgot_verify_otp(password):
    if 'user' in session:
        room = session['user']
        join_room(room)
        data = {}
        data['phone'] = session['user']
        data['password'] = password
        print("Found User")
        Val = database_operations.reset_password(data)
        if Val == True:
            socketio.emit("update_pass_status", "True", room=room)
            leave_room(room)
        else:
            socketio.emit("update_pass_status", "False", room=room)


@socketio.on("logout")
def logout():
    if 'user' in session:
        session.pop('user')
        session.pop("role")
        session.pop("name")
        session.pop('o_id')
        session.pop('login')
        print("Logged Out")
    else:
        print("User not found !")


@socketio.on("declaration_data")
def declaration(data):
    print(data)
    if 'user' in session:
        phone = session['user']
        room = phone
        join_room(room)
        Val = database_operations.update_declaration(phone, data, session)
        time.sleep(1)
        socketio.emit("declaration_submitted", room=room)
        # leave_room(room)


@app.route('/')
@app.route('/login')
def login():
    '''if 'user' in session:
        phone = session['user']
        credentials = database_operations.return_credentials(phone)
        return render_template("signin.html", phone=phone, password=credentials['password'],
                               role=credentials['role'])
    else:'''
    return render_template("signin.html")


@app.route('/createaccount')
def createaccount():
    return render_template("createaccount.html")


@app.route('/signup')
def signup():
    questions = database_operations.get_signup_questions()
    return render_template("signup.html")


@app.route('/signup1')
def signup1():
    return render_template("signup1.html")


@app.route('/signup2')
def signup2():
    return render_template("signup2.html")


@app.route('/verifyotp')
def verifyotp():
    if 'user' in session:
        print(session['user'])
        return render_template("verifyotp.html", user=session["user"])
    else:
        return render_template("signup.html")


@app.route('/forgotpassword')
def forgotpassword():
    return render_template("forgotpassword.html")


@app.route('/newpassword')
def newpassword():
    if 'user' in session:
        return render_template("newpassword.html")
    else:
        return render_template("signup.html")


@app.route('/applications')
def application():
    if 'user' in session and 'login' in session:
        if session['login']:
            return render_template("application.html",
                                   active_page='applications',
                                   role=session['role'],
                                   name=session['name'],
                                   phone=session["user"]
                                   )
    else:
        return redirect(url_for('login'))


@socketio.on("application_data")
def application_data():
    if 'user' in session:
        room = session['user']
        join_room(room)
        print(session['o_id'])
        data = database_operations.application_data(session['o_id'])

        socketio.emit("application", data, room=room)


@socketio.on("change_status")
def change_status(arr):
    if 'user' in session:
        room = session["user"]
        join_room(room)
        data = database_operations.change_status(arr, session['o_id'])
        # socketio.emit("application",data,room=room)


@socketio.on("modal_application")
def modal_application(x):
    if 'user' in session:
        room = session["user"]
        join_room(room)
        data = database_operations.modal_application(x, session['o_id'])
        socketio.emit("modal_data_application", data, room=room)


@socketio.on("updated_role")
def updated_role(arr):
    if 'user' in session:
        room = session["user"]
        data = database_operations.update_role(arr, session['o_id'])
        return "ok"


@socketio.on("updated_employee_status")
def updated_employee_status(arr):
    print(arr)
    if 'user' in session:
        room = session["user"]
        data = database_operations.update_employee_type(arr, session['o_id'])
        return "ok"


'''====================================================================='''
'''====================================================================='''
'''===================      TWIN ORDER TRACKING    ====================='''
'''====================================================================='''
'''====================================================================='''


@app.route('/file_upload', methods=['GET', 'POST'])
def file_upload():
    print("file loading")
    f = 0
    if request.method == 'POST':
        print("file received")
        f = request.files['file']

        f.save((planning_sheet_save_path + f.filename))
        print("file=", f.filename)
        return jsonify({'file_upload_successful': f.filename})

    return render_template("twin_home.html",
                           active_page='production_plan',
                           role=session['role'],
                           name=session['name'],
                           file_status="Uploaded Successfully!",
                           filename=f.filename
                           )


@app.route('/all_apps')
def all_apps():
    if 'user' in session and 'login' in session:
        if session['login']:
            return render_template("all_apps.html",
                                   active_page='all_apps',
                                   role=session['role'],
                                   name=session['name'],
                                   phone=session['user']
                                   )
    else:
        return redirect(url_for('login'))


@app.route('/download/<path>')
def download_file1(path):
    print(path)
    path = path.replace("^", "/")
    print(path)
    return send_file(path, as_attachment=True)


@app.route('/twin_file_upload/<rpo>', methods=['GET', 'POST'])
def twin_file_upload(rpo):
    print("----------------------------------------------------------")
    print("report loading")
    print(rpo)
    f = 0
    path = ""
    if request.method == 'POST':
        # print("file received................")
        f = request.files['file']
        os.makedirs(os.path.join('twin_reports', rpo), exist_ok=True)
        # when saving the file

        path = os.path.join('twin_reports', rpo, f.filename)
        f.save(path)

        print("================================")
        print(path)
        return jsonify({'file_upload_successful': f.filename, 'file_path': path})

    print("i am here")
    return render_template('twin_reports_upload.html',
                           rpo=rpo,
                           role=session['role'],
                           name=session['name'],
                           file_status="Uploaded Successfully!",
                           fname=f.filename,
                           path=path

                           )


@app.route('/upload_image/<rpo>', methods=['GET', 'POST'])
def upload_image(rpo):
    print("----------------------------------------------------------")
    print("image loading")
    print(rpo)
    f = 0
    path = ""
    if request.method == 'POST':
        # print("file received................")
        f = request.files['file']
        os.makedirs(os.path.join('rpo_images', rpo), exist_ok=True)
        # when saving the file

        path = os.path.join('rpo_images', rpo, f.filename)
        f.save(path)

        print("================================")
        print(path)
        return jsonify({'file_upload_successful': f.filename, 'file_path': path})

    return render_template('new_client.html',
                           rpo=rpo,
                           role=session['role'],
                           name=session['name'],
                           file_status="Uploaded Successfully!",
                           fname=f.filename,
                           path=path

                           )


@app.route('/display_image/<fname>')
def display_image(fname):
    fname = fname.replace("&&", "/")
    print(fname)
    filename = "rpo_images/" + fname
    # return redirect(url_for('rpo_images', filename=fname), code=301)
    return send_file(filename, mimetype='image/gif')


@app.route('/twin_reports_upload/<rpo>')
def twin_reports_upload(rpo):
    if 'user' in session and 'login' in session:
        if session['login']:
            return render_template("twin_reports_upload.html",
                                   active_page='twin_home',
                                   role=session['role'],
                                   name=session['name'],
                                   phone=session["user"],
                                   rpo=rpo
                                   )
    else:
        return redirect(url_for('login'))


@app.route('/twin_profile')
def twin_profile():
    if 'user' in session and 'login' in session:
        if session['login']:
            return render_template("twin_profile.html",
                                   active_page='twin_profile',
                                   role=session['role'],
                                   name=session['name'],
                                   phone=session["user"]
                                   )
    else:
        return redirect(url_for('login'))


@app.route('/additional_notes_display/<rpo>')
def additional_notes_display(rpo):
    if 'user' in session and 'login' in session:
        if session['login']:
            return render_template("additional_notes_display.html",
                                   active_page='rrr',
                                   role=session['role'],
                                   name=session['name'],
                                   phone=session["user"],
                                   rpo=rpo
                                   )
    else:
        return redirect(url_for('login'))


@app.route('/additional_notes_input/<rpo>')
def additional_notes_input(rpo):
    if 'user' in session and 'login' in session:
        if session['login']:
            return render_template("additional_notes_input.html",
                                   active_page='twin_home',
                                   role=session['role'],
                                   name=session['name'],
                                   phone=session["user"],
                                   rpo=rpo
                                   )
    else:
        return redirect(url_for('login'))


@app.route('/dispatch_details_display/<rpo>')
def dispatch_details_display(rpo):
    if 'user' in session and 'login' in session:
        if session['login']:
            return render_template("dispatch_details_display.html",
                                   active_page='twin_home',
                                   role=session['role'],
                                   name=session['name'],
                                   phone=session["user"],
                                   rpo=rpo
                                   )
    else:
        return redirect(url_for('login'))


@app.route('/dispatch_details_input/<rpo>')
def dispatch_details_input(rpo):
    if 'user' in session and 'login' in session:
        if session['login']:
            return render_template("dispatch_details_input.html",
                                   active_page='twin_home',
                                   role=session['role'],
                                   name=session['name'],
                                   phone=session["user"],
                                   rpo=rpo
                                   )
    else:
        return redirect(url_for('login'))


@app.route('/rpo_status')
def rpo_status():
    if 'user' in session and 'login' in session:
        if session['login']:
            return render_template("rpo_status.html",
                                   active_page='rpo_status',
                                   role=session['role'],
                                   name=session['name'],
                                   phone=session["user"]
                                   )
    else:
        return redirect(url_for('login'))


@app.route('/new_client/<client_id>')
def new_client(client_id):
    if 'user' in session and 'login' in session:
        if session['login']:
            return render_template("new_client.html",
                                   active_page='new_client',
                                   role=session['role'],
                                   name=session['name'],
                                   phone=session["user"],
                                   client_id=client_id
                                   )
    else:
        return redirect(url_for('login'))


@app.route('/edit_rpo/<rpo_id>')
def edit_rpo(rpo_id):
    if 'user' in session and 'login' in session:
        if session['login']:
            print(rpo_id)
            return render_template("edit_rpo.html",
                                   active_page='twin_home',
                                   role=session['role'],
                                   name=session['name'],
                                   phone=session["user"],
                                   rpo_id=rpo_id
                                   )
    else:
        return redirect(url_for('login'))


@app.route('/twin_home')
def index():
    if 'user' in session and 'login' in session:
        if session['login']:
            return render_template("twin_home.html",
                                   active_page='twin_home',
                                   role=session['role'],
                                   name=session['name'],
                                   phone=session["user"]
                                   )

    else:
        return redirect(url_for('login'))


@app.route('/updates/<rpo>')
def updates(rpo):
    if 'user' in session and 'login' in session:
        if session['login']:
            return render_template("updates.html",
                                   active_page='twin_home',
                                   role=session['role'],
                                   name=session['name'],
                                   phone=session["user"],
                                   rpo=rpo
                                   )
    else:
        return redirect(url_for('login'))


@app.route('/activity_presets')
def activity_presets():
    if 'user' in session and 'login' in session:
        if session['login']:
            return render_template("activity_presets.html",
                                   active_page='activity_presets',
                                   role=session['role'],
                                   name=session['name'],
                                   phone=session["user"],

                                   )
    else:
        return redirect(url_for('login'))


@app.route('/approval')
def approval():
    if 'user' in session and 'login' in session:
        if session['login']:
            return render_template("approvals.html",
                                   active_page='approvals',
                                   role=session['role'],
                                   name=session['name'],
                                   phone=session["user"],

                                   )
    else:
        return redirect(url_for('login'))


# =============================== UPDATES ===================================


@app.route('/updates_design/<rpo>')
def updates_design(rpo):
    if 'user' in session and 'login' in session:
        if session['login']:
            return render_template("updates_design.html",
                                   active_page='twin_home',
                                   role=session['role'],
                                   name=session['name'],
                                   phone=session["user"],
                                   rpo=rpo
                                   )
    else:
        return redirect(url_for('login'))


@app.route('/updates_production/<rpo>')
def updates_production(rpo):
    if 'user' in session and 'login' in session:
        if session['login']:
            return render_template("updates_production.html",
                                   active_page='twin_home',
                                   role=session['role'],
                                   name=session['name'],
                                   phone=session["user"],
                                   rpo=rpo
                                   )
    else:
        return redirect(url_for('login'))


@app.route('/updates_purchase/<rpo>')
def updates_purchase(rpo):
    if 'user' in session and 'login' in session:
        if session['login']:
            return render_template("updates_purchase.html",
                                   active_page='twin_home',
                                   role=session['role'],
                                   name=session['name'],
                                   phone=session["user"],
                                   rpo=rpo
                                   )
    else:
        return redirect(url_for('login'))


@app.route('/updates_testing/<rpo>')
def updates_testing(rpo):
    if 'user' in session and 'login' in session:
        if session['login']:
            return render_template("updates_testing.html",
                                   active_page='twin_home',
                                   role=session['role'],
                                   name=session['name'],
                                   phone=session["user"],
                                   rpo=rpo
                                   )
    else:
        return redirect(url_for('login'))


@app.route('/updates_dispatch/<rpo>')
def updates_dispatch(rpo):
    if 'user' in session and 'login' in session:
        if session['login']:
            return render_template("updates_dispatch.html",
                                   active_page='twin_home',
                                   role=session['role'],
                                   name=session['name'],
                                   phone=session["user"],
                                   rpo=rpo
                                   )
    else:
        return redirect(url_for('login'))


# =============================== CUSTOMER PAGES ===============================


@app.route('/new_status/<rpo>')
def new_status(rpo):
    return render_template("new_status.html",
                           active_page='twin_home',
                           rpo=rpo
                           )


@app.route('/customer_home')
def customer_home():
    return render_template("customer_search.html",
                           active_page='twin_home',
                           )


# =============================== RPO =========================================

@app.before_first_request
def activate_job():
    def run_job():
        global message_notification_flag

        while True:
            # VATSAL
            print("8pm messages cronjob active.")
            ct = datetime.datetime.now()
            today8pm = ct.replace(hour=20, minute=10, second=0, microsecond=0)  # try sending msg
            today8pm1min = ct.replace(hour=20, minute=19, second=0, microsecond=0)  # stop trying reset flag after this

            if ct > today8pm1min:
                message_notification_flag = 0

            if (today8pm < ct < today8pm1min) and message_notification_flag == 0:
                twin_database_operations.send_eod()
                message_notification_flag = 1

            time.sleep(300)

    thread = threading.Thread(target=run_job)
    thread.start()


@socketio.on("save_client_details")
def save_client_details(data):
    if 'user' in session:
        room = request.sid
        join_room(room)

        print("######################### NEW CLIENT DETAILS RECEIVED ##############################")

        response = twin_database_operations.insert_order(data)
        socketio.emit("save_client_details_response", response, room=room)


@socketio.on("edit_rpo_details")
def edit_rpo_details(data):
    if 'user' in session:
        room = request.sid
        join_room(room)
        twin_database_operations.edit_rpo_details(data)


@socketio.on("active_projects_page")
def get_page(data):
    if 'user' in session:
        room = request.sid
        join_room(room)
        active_projects = twin_database_operations.query_active_projects()
        socketio.emit("sent_active_projects", active_projects, room=room)


@socketio.on("get_client_info")
def get_client_info(data):
    if 'user' in session:
        room = request.sid
        join_room(room)
        rpo = data
        client_info = twin_database_operations.get_client_details(rpo)
        print(client_info)

        if client_info is not None:
            socketio.emit("sent_client_info", client_info, room=room)
        else:
            socketio.emit("sent_client_info", {}, room=room)


@socketio.on("get_specific_rpo")
def get_specific_rpo(data):
    if 'user' in session:
        room = request.sid
        join_room(room)
        print(data)
        rpo = twin_database_operations.get_specific_rpo(data)

        socketio.emit("sent_specific_rpo", rpo, room=room)


@socketio.on("delete_rpo")
def delete_rpo(data):
    if 'user' in session:
        room = request.sid
        join_room(room)
        print("RPO DELETE REQUEST RECIEVED")
        print(data)
        rpo = twin_database_operations.delete_rpo(data)
        print("-------------------------- RPO DELETED -------------------------------------------")
        socketio.emit("delete_rpo_response", 0, room=room)


@socketio.on("get_rpos_ready_to_dispatch")
def get_rpos_ready_to_dispatch():
    if 'user' in session:
        room = request.sid
        join_room(room)

        resp = twin_database_operations.get_rpos_ready_to_dispatch()
        socketio.emit("sent_rpos_ready_to_dispatch", resp, room=room)


@socketio.on("get_closed_rpos")
def get_closed_rpos():
    if 'user' in session:
        room = request.sid
        join_room(room)

        resp = twin_database_operations.get_closed_rpos()
        for rec in resp:
            rec["closed_on"] = rec["closed_on"].strftime(constants.time_format)

        socketio.emit("sent_closed_rpos", resp, room=room)


@socketio.on("approve1_rpo")
def approve1_rpo(data):
    if 'user' in session:
        room = request.sid
        join_room(room)

        client_info = twin_database_operations.approve1_rpo(data)


@socketio.on("approve2_rpo")
def approve2_rpo(data):
    if 'user' in session:
        room = request.sid
        join_room(room)

        client_info = twin_database_operations.approve2_rpo(data)


@socketio.on("approve3_rpo")
def approve3_rpo(data):
    if 'user' in session:
        room = request.sid
        join_room(room)

        client_info = twin_database_operations.approve3_rpo(data)


@socketio.on("close_rpo")
def close_rpo(data):
    if 'user' in session:
        room = request.sid
        join_room(room)

        client_info = twin_database_operations.close_rpo(data)


@socketio.on("send_to_dsm")
def send_to_dsm(data):
    if 'user' in session:
        room = request.sid
        join_room(room)

        resp = twin_database_operations.send_rpo_to_dsm(data)
        socketio.emit("sent_to_dsm", resp, room=room)


# ======================================== Design Activity =================================================


@socketio.on("add_new_design_activity")
def add_new_design_activity(data):
    if 'user' in session:
        room = request.sid
        join_room(room)
        response = twin_database_operations.insert_design_activity(data)
        socketio.emit("add_new_design_activity_response", response, room=room)


@socketio.on("get_design_activity_data")
def get_design_activity_data(rpo):
    if 'user' in session:
        room = request.sid
        join_room(room)
        design_activity_info = twin_database_operations.query_design_activity_info(rpo)
        socketio.emit("sent_design_activity_info", design_activity_info, room=room)


@socketio.on("get_specific_design_activity_data")
def get_specific_design_activity_data(activity_no, rpo):
    if 'user' in session:
        room = request.sid
        join_room(room)
        activity_data = twin_database_operations.get_specific_design_activity_data(activity_no, rpo)
        socketio.emit("sent_specific_design_activity_data", activity_data, room=room)


@socketio.on("update_specific_design_activity_data")
def update_specific_design_activity_data(data):
    if 'user' in session:
        room = request.sid
        join_room(room)
        twin_database_operations.update_specific_design_activity_data(data)


@socketio.on("delete_specific_design_activity_data")
def delete_specific_design_activity_data(rpo, activity_no):
    if 'user' in session:
        room = request.sid
        join_room(room)
        twin_database_operations.delete_specific_design_activity_data(rpo, activity_no)


'''===================================Production Activity===================================='''


@socketio.on("add_new_production_activity")
def add_new_production_activity(data):
    if 'user' in session:
        room = request.sid
        join_room(room)
        response = twin_database_operations.insert_production_activity(data)
        socketio.emit("add_new_production_activity_response", response, room=room)


@socketio.on("get_production_activity_data")
def get_production_activity_data(rpo):
    if 'user' in session:
        room = request.sid
        join_room(room)
        production_activity_info = twin_database_operations.query_production_activity_info(rpo)
        socketio.emit("sent_production_activity_info", production_activity_info, room=room)


@socketio.on("get_specific_production_activity_data")
def get_specific_production_activity_data(activity_no, rpo):
    if 'user' in session:
        room = request.sid
        join_room(room)
        print(activity_no)
        print(rpo)
        activity_data = twin_database_operations.get_specific_production_activity_data(activity_no, rpo)
        socketio.emit("sent_specific_production_activity_data", activity_data, room=room)


@socketio.on("update_specific_production_activity_data")
def update_specific_production_activity_data(data):
    if 'user' in session:
        room = request.sid
        join_room(room)
        twin_database_operations.update_specific_production_activity_data(data)


@socketio.on("delete_specific_production_activity_data")
def delete_specific_production_activity_data(rpo, activity_no):
    if 'user' in session:
        room = request.sid
        join_room(room)
        twin_database_operations.delete_specific_production_activity_data(rpo, activity_no)


'''===================================Purchase Activity===================================='''


@socketio.on("add_new_purchase_activity")
def add_new_purchase_activity(data):
    if 'user' in session:
        room = request.sid
        join_room(room)
        res = twin_database_operations.insert_purchase_activity(data)
        socketio.emit("add_new_purchase_activity_response", res, room=room)


@socketio.on("get_purchase_activity_data")
def get_purchase_activity_data(rpo):
    if 'user' in session:
        room = request.sid
        join_room(room)
        purchase_activity_info = twin_database_operations.query_purchase_activity_info(rpo)
        socketio.emit("sent_purchase_activity_info", purchase_activity_info, room=room)


@socketio.on("get_specific_purchase_activity_data")
def get_specific_purchase_activity_data(activity_no, rpo):
    if 'user' in session:
        room = request.sid
        join_room(room)
        activity_data = twin_database_operations.get_specific_purchase_activity_data(activity_no, rpo)
        socketio.emit("sent_specific_purchase_activity_data", activity_data, room=room)


@socketio.on("update_specific_purchase_activity_data")
def update_specific_purchase_activity_data(data):
    if 'user' in session:
        room = request.sid
        join_room(room)
        twin_database_operations.update_specific_purchase_activity_data(data)


@socketio.on("delete_specific_purchase_activity_data")
def delete_specific_purchase_activity_data(rpo, activity_no):
    if 'user' in session:
        room = request.sid
        join_room(room)
        twin_database_operations.delete_specific_purchase_activity_data(rpo, activity_no)


'''===================================Dispatch Activity===================================='''


@socketio.on("add_new_dispatch_activity")
def add_new_dispatch_activity(data):
    if 'user' in session:
        room = request.sid
        join_room(room)
        res = twin_database_operations.insert_dispatch_activity(data)
        socketio.emit("add_new_dispatch_activity_response", res, room=room)


@socketio.on("get_dispatch_activity_data")
def get_dispatch_activity_data(rpo):
    if 'user' in session:
        room = request.sid
        join_room(room)
        dispatch_activity_info = twin_database_operations.query_dispatch_activity_info(rpo)
        socketio.emit("sent_dispatch_activity_info", dispatch_activity_info, room=room)


@socketio.on("get_specific_dispatch_activity_data")
def get_specific_dispatch_activity_data(activity_no, rpo):
    if 'user' in session:
        room = request.sid
        join_room(room)
        activity_data = twin_database_operations.get_specific_dispatch_activity_data(activity_no, rpo)
        socketio.emit("sent_specific_dispatch_activity_data", activity_data, room=room)


@socketio.on("update_specific_dispatch_activity_data")
def update_specific_dispatch_activity_data(data):
    if 'user' in session:
        room = request.sid
        join_room(room)
        twin_database_operations.update_specific_dispatch_activity_data(data)


@socketio.on("delete_specific_dispatch_activity_data")
def delete_specific_dispatch_activity_data(rpo, activity_no):
    if 'user' in session:
        room = request.sid
        join_room(room)
        twin_database_operations.delete_specific_dispatch_activity_data(rpo, activity_no)


'''===================================Testing Activity===================================='''


@socketio.on("add_new_testing_activity")
def add_new_testing_activity(data):
    if 'user' in session:
        room = request.sid
        join_room(room)
        res = twin_database_operations.insert_testing_activity(data)
        socketio.emit("add_new_testing_activity_response", res, room=room)


@socketio.on("get_testing_activity_data")
def get_testing_activity_data(rpo):
    if 'user' in session:
        room = request.sid
        join_room(room)
        testing_activity_info = twin_database_operations.query_testing_activity_info(rpo)
        socketio.emit("sent_testing_activity_info", testing_activity_info, room=room)


@socketio.on("get_specific_testing_activity_data")
def get_specific_testing_activity_data(activity_no, rpo):
    if 'user' in session:
        room = request.sid
        join_room(room)
        activity_data = twin_database_operations.get_specific_testing_activity_data(activity_no, rpo)
        socketio.emit("sent_specific_testing_activity_data", activity_data, room=room)


@socketio.on("update_specific_testing_activity_data")
def update_specific_testing_activity_data(data):
    if 'user' in session:
        room = request.sid
        join_room(room)
        twin_database_operations.update_specific_testing_activity_data(data)


@socketio.on("delete_specific_testing_activity_data")
def delete_specific_testing_activity_data(rpo, activity_no):
    if 'user' in session:
        room = request.sid
        join_room(room)
        twin_database_operations.delete_specific_testing_activity_data(rpo, activity_no)


'''===================================Weightage per RPO=================================='''


@socketio.on("get_rpo_weightage")
def get_rpo_weightage(rpo):
    if 'user' in session:
        room = request.sid
        join_room(room)

        flag = twin_database_operations.validate_rpo(rpo)

        if flag == 1:
            socketio.emit("rpo_not_found", "Please enter valid RPO !", room=room)
        elif flag == 2:

            total_rpo_status = twin_database_operations.get_rpo_status(rpo)
            socketio.emit("sent_total_status", total_rpo_status, room=room)

            design_total = twin_database_operations.get_design_status_for_rpo(rpo)
            socketio.emit("sent_design_status", design_total, room=room)

            production_total = twin_database_operations.get_production_status_for_rpo(rpo)
            socketio.emit("sent_production_status", production_total, room=room)

            purchase_total = twin_database_operations.get_purchase_status_for_rpo(rpo)
            socketio.emit("sent_purchase_status", purchase_total, room=room)


'''===================================Dispatch Details=================================='''


@socketio.on("save_dispatch_details")
def save_dispatch_details(data):
    if 'user' in session:
        room = request.sid
        join_room(room)
        twin_database_operations.insert_dispatch_details(data)


@socketio.on("validate_rpo_for_dispatch_details")
def validate_rpo_for_dispatch_details(rpo):
    if 'user' in session:
        room = request.sid
        join_room(room)
        count = twin_database_operations.validate_rpo(rpo)
        if count == 1:
            socketio.emit("dispatch_rpo_not_found", "Please enter valid RPO !", room=room)
        if count == 2:
            socketio.emit("dispatch_rpo_found", "Found", room=room)


@socketio.on("get_dispatch_details")
def get_dispatch_details(rpo):
    if 'user' in session:
        room = request.sid
        join_room(room)
        dispatch_details = twin_database_operations.get_dispatch_details(rpo)
        socketio.emit("sent_dispatch_details", dispatch_details, room=room)


'''===================================Additional Notes=================================='''


@socketio.on("save_additional_notes")
def save_additional_notes(data):
    if 'user' in session:
        room = request.sid
        join_room(room)
        twin_database_operations.insert_additional_notes(data)


@socketio.on("validate_rpo_for_additional_notes")
def validate_rpo_for_additional_notes(rpo):
    if 'user' in session:
        room = request.sid
        join_room(room)
        count = twin_database_operations.validate_rpo(rpo)
        if count == 1:
            socketio.emit("add_notes_rpo_not_found", "Please enter valid RPO !", room=room)
        if count == 2:
            socketio.emit("add_notes_rpo_found", "Found", room=room)


@socketio.on("get_additional_notes")
def get_additional_notes(rpo):
    if 'user' in session:
        room = request.sid
        join_room(room)
        additional_notes = twin_database_operations.get_additional_notes(rpo)
        socketio.emit("sent_additional_notes", additional_notes, room=room)


'''===================================Profile=================================='''


@socketio.on("save_profile_details")
def save_profile_details(data):
    if 'user' in session:
        room = request.sid
        join_room(room)
        twin_database_operations.insert_profile(data)


'''===================================Reports=================================='''


@socketio.on("save_report_details")
def save_report_details(data):
    if 'user' in session:
        room = request.sid
        join_room(room)
        rpo = data["RPO"]
        f = data["Filename"]
        print(data)
        twin_database_operations.insert_report_details(data)


@socketio.on("delete_report")
def delete_report(data):
    if 'user' in session:
        room = request.sid
        join_room(room)

        response = twin_database_operations.delete_report(data)
        if response == 1:
            print("Report deleted")


@socketio.on("get_report_data_for_display")
def get_report_data_for_display(data):
    if 'user' in session:
        room = request.sid
        join_room(room)
        rpo = data
        report_data_for_display = twin_database_operations.get_report_data_for_display(rpo)
        socketio.emit("sent_report_data_for_display", report_data_for_display, room=room)


@socketio.on("validate_rpo_for_reports")
def validate_rpo_for_reports(rpo):
    if 'user' in session:
        room = request.sid
        join_room(room)
        count = twin_database_operations.validate_rpo(rpo)
        if count == 1:
            socketio.emit("reports_rpo_not_found", "Please enter valid RPO !", room=room)
        if count == 2:
            socketio.emit("reports_rpo_found", "Found", room=room)


# ------------------------------------presets--------------------------------------------
@socketio.on("add_new_preset")
def add_new_preset(data):
    if 'user' in session:
        room = request.sid
        join_room(room)

        response = twin_database_operations.add_new_preset(data)
        socketio.emit("add_new_preset_response", response, room=room)


@socketio.on("delete_preset")
def delete_preset(data):
    if 'user' in session:
        room = request.sid
        join_room(room)
        response = twin_database_operations.delete_preset(data)


@socketio.on("get_activity_presets")
def get_activity_presets():
    if 'user' in session:
        room = request.sid
        join_room(room)
        print("activity presets requested")
        all_presets = twin_database_operations.get_activity_presets()
        socketio.emit("sent_activity_presets", all_presets, room=room)


@socketio.on("get_machine_types_from_activity_preset")
def get_machine_types_from_activity_preset():
    if 'user' in session:
        room = request.sid
        join_room(room)
        print("machine types requested")
        machine_types = twin_database_operations.get_machine_types_from_activity_preset()
        socketio.emit("sent_machine_types_from_activity_preset", machine_types, room=room)


@socketio.on("get_activity_types_for_new_activity_preset")
def get_activity_types_for_new_activity_preset():
    if 'user' in session:
        room = request.sid
        join_room(room)

        activity_types = twin_database_operations.get_activity_types_for_new_activity_preset()
        socketio.emit("sent_activity_types_for_new_activity_preset", activity_types, room=room)


@socketio.on("get_subtypes_for_machine_type")
def get_subtypes_for_machine_type(data):
    if 'user' in session:
        room = request.sid
        join_room(room)
        print("machine sub types requested")
        machine_types = twin_database_operations.get_subtypes_for_machine_type(data)
        socketio.emit("sent_subtypes_for_machine_type", machine_types, room=room)


@socketio.on("get_customer_page_data")
def get_customer_page_data(data):
    if 'user' in session:
        room = request.sid
        join_room(room)
        print("here")
        response = twin_database_operations.get_customer_page_data2(data)
        print(response)
        print("all_activites")
        socketio.emit("sent_customer_page_data", response, room=room)


'''===================================TWIN Login & Sign up (TEMPORARY) =================================='''


@socketio.on("twin_login_cred")
def twin_login_cred(data):
    room = data['phone']
    join_room(room)
    print(data)
    Val = twin_users_database_operations.verify_credentials(data)
    if Val == 2:
        session["user"] = data["phone"]
        # session['role'] = data["role"]
        data1 = twin_users_database_operations.return_credentials(data['phone'])
        session['role'] = data1['role']
        session['name'] = data1['name']
        session["login"] = True
        socketio.emit("twin_login_status", "2", room=room)
        leave_room(room)
    if Val == 1:
        session["user"] = data["phone"]
        # session['role'] = data["role"]
        data1 = twin_users_database_operations.return_credentials(data['phone'])
        session['role'] = data1['role']
        session['name'] = data1['name']
        session["login"] = False
        socketio.emit("twin_login_status", "1", room=room)
    if Val == 0:
        socketio.emit("twin_login_status", "0", room=room)


@socketio.on("twin_login_cred_check")
def twin_login_cred_check(data):
    room = data['phone']
    join_room(room)
    print(data)
    Val = twin_users_database_operations.verify_credentials(data)
    if Val == 2:
        session["user"] = data["phone"]
        # session['role'] = data["role"]
        data1 = twin_users_database_operations.return_credentials(data['phone'])
        session['role'] = data1['role']
        session['name'] = data1['name']
        session["login"] = True
        socketio.emit("twin_login_status_check", "2", room=room)
        leave_room(room)
    if Val == 1:
        session["user"] = data["phone"]
        # session['role'] = data["role"]
        data1 = twin_users_database_operations.return_credentials(data['phone'])
        session['role'] = data1['role']
        session['name'] = data1['name']
        session["login"] = False
        socketio.emit("twin_login_status_check", "1", room=room)
    if Val == 0:
        socketio.emit("twin_login_status_check", "0", room=room)


@app.route('/report_uploader', methods=['GET', 'POST'])
def report_uploader():
    if 'user' in session and 'login' in session:
        if session['login']:
            if request.method == 'POST':
                print("TEST")
                f = request.files['fileToUpload']
                report_name = request.form['modal1_report_name']
                order_number = request.form['modal1_rpo_name']
                note = request.form['modal1_report_note']
                report_file_path = "twin_reports/" + order_number
                path = report_file_path + "/" + f.filename
                twin_database_operations.add_new_twin_report(order_number, report_name, note, path)
                try:
                    os.makedirs(report_file_path)
                except FileExistsError:
                    # directory already exists
                    pass
                f.save(report_file_path + "/" + f.filename)

                return 'file uploaded successfully'
    else:
        return redirect(url_for('login'))


@app.route('/customer_database')
def customer_database():
    if 'user' in session and 'login' in session:
        if session['login']:
            return render_template("customer_database.html",
                                   active_page='customer_database',
                                   role=session['role'],
                                   name=session['name'],
                                   phone=session["user"],
                                   )
    else:
        return redirect(url_for('login'))


@app.route('/get_customers_table', methods=['POST', 'GET'])
def get_customers_table():
    if 'user' in session and 'login' in session:
        if session['login']:
            if request.method == 'POST':
                customers_data = twin_database_operations.get_customers_table()
        return jsonify(customers_data)
    else:
        return redirect(url_for('login'))


@app.route('/create_new_customer', methods=['POST', 'GET'])
def create_new_customer():
    if 'user' in session and 'login' in session:
        if session['login']:
            if request.method == 'POST':
                data = request.get_json()
                twin_database_operations.create_new_customer(data)
                return "Customer added successfully"
    else:
        return redirect(url_for('login'))


@app.route('/get_specific_customer', methods=['POST', 'GET'])
def get_specific_customer():
    if 'user' in session and 'login' in session:
        if session['login']:
            if request.method == 'POST':
                data = request.get_json()
                specific_customer_data = twin_database_operations.get_specific_customer(data)
                return jsonify(specific_customer_data)
    else:
        return redirect(url_for('login'))


@app.route('/update_specific_customer', methods=['POST', 'GET'])
def update_specific_customer():
    if 'user' in session and 'login' in session:
        if session['login']:
            if request.method == 'POST':
                data = request.get_json()
                twin_database_operations.update_specific_customer(data)
                return jsonify("Customer updated successfully")
    else:
        return redirect(url_for('login'))


@app.route('/complaints')
def complaints():
    if 'user' in session and 'login' in session:
        if session['login']:
            return render_template("complaints.html",
                                   active_page='complaints',
                                   role=session['role'],
                                   name=session['name'],
                                   phone=session['user']
                                   )
    else:
        return redirect(url_for('login'))


@app.route('/check_customer_id_database', methods=['POST', 'GET'])
def check_customer_id_database():
    if 'user' in session and 'login' in session:
        if session['login']:
            if request.method == 'POST':
                data = request.get_json()
                customer_data = twin_database_operations.check_customer_id_database(data)
                return jsonify(customer_data)
    else:
        return redirect(url_for('login'))


@app.route('/check_rpo_database', methods=['POST', 'GET'])
def check_rpo_database():
    if 'user' in session and 'login' in session:
        if session['login']:
            if request.method == 'POST':
                data = request.get_json()
                rpo_status = twin_database_operations.check_rpo_database(data)
                return jsonify(rpo_status)
    else:
        return redirect(url_for('login'))


@app.route('/customer_details/<client_id>')
def customer_details(client_id):
    if 'user' in session and 'login' in session:
        if session['login']:
            return render_template("customer_details.html",
                                   active_page='customer_database',
                                   role=session['role'],
                                   name=session['name'],
                                   phone=session['user'],
                                   client_id=client_id
                                   )
    else:
        return redirect(url_for('login'))


@app.route('/get_customer_details_table', methods=['POST', 'GET'])
def get_customer_details_table():
    if 'user' in session and 'login' in session:
        if session['login']:
            if request.method == 'POST':
                data = request.get_json()
                table_data = twin_database_operations.get_customer_details_table(data)
                return jsonify(table_data)
    else:
        return redirect(url_for('login'))


@app.route('/get_specific_customer_details_data', methods=['POST', 'GET'])
def get_specific_customer_details_data():
    if 'user' in session and 'login' in session:
        if session['login']:
            if request.method == 'POST':
                data = request.get_json()
                customer_details_data = twin_database_operations.get_specific_customer_details_data(data)
                return jsonify(customer_details_data)
    else:
        return redirect(url_for('login'))


@app.route('/update_specific_customer_detail', methods=['POST', 'GET'])
def update_specific_customer_detail():
    if 'user' in session and 'login' in session:
        if session['login']:
            if request.method == 'POST':
                data = request.get_json()
                twin_database_operations.update_specific_customer_detail(data)
                return jsonify("Data updated successfully")
    else:
        return redirect(url_for('login'))


@app.route('/get_specific_customer_details_for_rpo/<client_id>', methods=['POST', 'GET'])
def get_specific_customer_data_for_rpo(client_id):
    if request.method == 'GET':
        get_customer_data = twin_database_operations.get_specific_customer_data_for_rpo(client_id)
    return jsonify(get_customer_data)


# ------------------------------amol---------------------------------------------------


@app.route('/production_plan')
def production_plan():
    if 'user' in session and 'login' in session:
        if session['login']:
            return render_template("plan_order_new.html",
                                   active_page='plan_order_new',
                                   role=session['role'],
                                   name=session['name'],
                                   phone=session["user"],
                                   )
    else:
        return redirect(url_for('login'))

    # planned_qty=0
    # reqd_qty_as_per_bom=0
    # last_month_pending_qty=0
    # last_month_pending_qty=0
    # finish_store_stock=0
    # wip_qty=0
    #
    #
    # actual_required_quantity=((planned_qty * reqd_qty_as_per_bom) + last_month_pending_qty - finish_store_stock - wip_qty)


@app.route('/gap_analysis')
def gap_analysis():
    if 'user' in session and 'login' in session:
        if session['login']:
            return render_template("gap_analysis.html",
                                   active_page='gap_analysis',
                                   role=session['role'],
                                   name=session['name'],
                                   phone=session["user"]
                                   )
    else:
        return redirect(url_for('login'))


#     ---------------------------------------------- code by Amit --------------------------------------------------------------

# @app.route('/machine_stocks', methods = ['POST','GET'])
# def Machine_Stocks():
#     if request.method == 'POST':
#         data = request.get_json(force=True)
#         print(data)
#         fie_database_operations.Machine_Stocks_data(data)
#     return jsonify('Sucessfull created1')

# @app.route('/fie_dump_data', methods=['POST', 'GET'])
# def Machine_Stocks():
#     if request.method == 'POST':
#         data = request.get_json(force=True)
#         print(data)
#         fie_database_operations.Machine_Stocks_data(data)
#         return jsonify('Sucessfull created1')
#
#
# @app.route('/fie_dump_database', methods=['POST', 'GET'])
# def MachineryComponents():
#     if request.method == 'POST':
#         data = request.get_json(force=True)
#         fie_database_operations.MachineryComponents_data(data)
#         return jsonify('Sucessfull created2')


# @app.route('/machinerycomponents', methods = ['POST','GET'])
# def MachineryComponents():
#     if request.method == 'POST':
#         data = request.get_json(force=True)
#         fie_database_operations.MachineryComponents_data(data)
#     return jsonify('Sucessfull created2')


@socketio.on('send_machine_sales_data')
def send_machine_sales_data():
    get_machine_sales = fie_database_operations.send_machine_sales_data()
    print('I am in stock ')
    # print(get_machine_stock)
    socketio.emit('get_machine_sales_data', get_machine_sales)


@app.route('/sales_order')
def sales_order():
    if 'user' in session and 'login' in session:
        if session['login']:
            return render_template("sales_order.html",
                                   active_page='sales_order',
                                   role=session['role'],
                                   name=session['name'],
                                   phone=session["user"]
                                   )
    else:
        return redirect(url_for('login'))


@app.route('/stock')
def stock_data():
    if 'user' in session and 'login' in session:
        if session['login']:
            return render_template("stock.html",
                                   active_page='stock_data',
                                   role=session['role'],
                                   name=session['name'],
                                   phone=session["user"],
                                   )
    else:
        return redirect(url_for('login'))


@app.route('/parts')
def parts():
    if 'user' in session and 'login' in session:
        if session['login']:
            return render_template("parts.html",
                                   active_page='parts_data',
                                   role=session['role'],
                                   name=session['name'],
                                   phone=session["user"],
                                   )
    else:
        return redirect(url_for('login'))


@app.route('/machinery_components')
def machinery_components():
    if 'user' in session and 'login' in session:
        if session['login']:
            return render_template("machinery_components.html",
                                   active_page='machinery_components_data',
                                   role=session['role'],
                                   name=session['name'],
                                   phone=session["user"],
                                   )
    else:
        return redirect(url_for('login'))


@app.route('/wip_stocks')
def wip_stocks():
    if 'user' in session and 'login' in session:
        if session['login']:
            return render_template("wip_stocks.html",
                                   active_page='wip_stocks_data',
                                   role=session['role'],
                                   name=session['name'],
                                   phone=session["user"],
                                   )
    else:
        return redirect(url_for('login'))


@app.route('/vendor_details')
def vendor_details():
    if 'user' in session and 'login' in session:
        if session['login']:
            return render_template("vendor_details.html",
                                   active_page='vendor_details_data',
                                   role=session['role'],
                                   name=session['name'],
                                   phone=session["user"],
                                   )
    else:
        return redirect(url_for('login'))


@socketio.on('get_vendor_data')
def get_vendor_data():
    if 'user' in session:
        room = request.sid
        vendor_data = fie_database_operations.get_vendor_data()
        socketio.emit('send_vendor_data', vendor_data, room=room)


@socketio.on('get_sales_order_data')
def get_sales_order_data():
    if 'user' in session:
        room = request.sid
        sales_order_data = fie_database_operations.get_sales_order_data()
        socketio.emit('send_sales_order_data', sales_order_data, room=room)


@socketio.on('get_wip_stocks_data')
def get_wip_stocks_data():
    if 'user' in session:
        room = request.sid
        wip_stocks_data = fie_database_operations.get_wip_stocks_data()
        socketio.emit('send_wip_stocks_data', wip_stocks_data, room=room)


@socketio.on('get_machinery_components_data')
def get_machinery_components_data():
    if 'user' in session:
        room = request.sid
        machinery_components_data = fie_database_operations.get_machinery_components_data()
        socketio.emit('send_machinery_components_data', machinery_components_data, room=room)


@socketio.on('get_stock_data')
def get_stock_data():
    if 'user' in session:
        room = request.sid
        stock_data = fie_database_operations.get_stock_data()
        socketio.emit('send_stock_data', stock_data, room=room)


@socketio.on('get_parts_data')
def get_parts_data():
    if 'user' in session:
        room = request.sid
        parts_data = fie_database_operations.get_parts_data()
        socketio.emit('send_parts_data', parts_data, room=room)


@socketio.on('get_month_year')
def get_month_year():
    if 'user' in session:
        room = request.sid
        month_year = fie_database_operations.get_month_year()
        socketio.emit('send_month_year', month_year, room=room)


@app.route('/sales_order_data', methods=['POST', 'GET'])
def sales_order_data():
    if request.method == 'POST':
        data = request.get_json(force=True)
        fie_database_operations.write_to_json(data, "sales_order")
        fie_database_operations.sales_order_data(data)
        fie_database_operations.backup_data_sales_order(data)
        result = fie_database_operations.create_part_plan_data()
        if result == 0:
            response = "ERROR : Please first add machinery_component json in Database "
        else:
            response = "SALES ORDERS SYNCED SUCCESSFULLY"
        return jsonify({"Response": response })


@app.route('/stocks_data', methods=['POST', 'GET'])
def stocks_data():
    if request.method == 'POST':
        data = request.get_json(force=True)
        fie_database_operations.write_to_json(data, "stocks")
        fie_database_operations.stocks_data(data)
        fie_database_operations.backup_data_stock(data)

        return jsonify({"Response": "STOCK DATA SYNCED SUCCESSFULLY"})

@app.route('/machinery_components_data', methods=['POST', 'GET'])
def machinery_components_data():
    if request.method == 'POST':
        data = request.get_json(force=True)
        fie_database_operations.write_to_json(data, "machinery_component")
        fie_database_operations.machinery_components_data(data)
        fie_database_operations.new_collection(data)
        fie_database_operations.backup_data_machinery_components(data)
        return jsonify({"Response": "MACHINERY COMPONENTS DATA SYNCED SUCCESSFULLY"})


@app.route('/wip_stocks_data', methods=['POST', 'GET'])
def wip_stocks_data():
    if request.method == 'POST':
        data = request.get_json(force=True)
        fie_database_operations.write_to_json(data, "wip")
        fie_database_operations.wip_stocks_data(data)
        fie_database_operations.backup_data_wip_stocks(data)
        result = fie_database_operations.check_sales_data()
        if result == 0:
           response = "Error: Please first add Sales Order json in Database"
        else:
            response = "WIP DATA SYNCED SUCCESSFULLY"
        return jsonify({"Response": response})
        # return jsonify({"Response": "WIP DETAILS SYNCED SUCCESSFULLY"})

@app.route('/vendor_details_data', methods=['POST', 'GET'])
def vendor_details_data():
    if request.method == 'POST':
        data = request.get_json(force=True)
        fie_database_operations.write_to_json(data, "vendors")
        fie_database_operations.vendor_details_data(data)
        fie_database_operations.backup_data_vendor_details(data)
        return jsonify({"Response": "VENDOR DETAILS SYNCED SUCCESSFULLY"})



@app.route('/render_machinery_component/<record>')
def render_machinery_component(record):
    if 'user' in session and 'login' in session:
        if session['login']:
            return render_template("view_machinery_component.html",
                                   active_page='machinery_components_data',
                                   role=session['role'],
                                   name=session['name'],
                                   phone=session["user"],
                                   data = record
                                   )
    else:
        return redirect(url_for('login'))


@socketio.on('array_machinery_components')
def array_machinery_components(record):
    if 'user' in session:
        room = request.sid
        send_array_machinery_components = fie_database_operations.get_array_machinery_components(record)
        socketio.emit('send_array_machinery_components', send_array_machinery_components, room=room)


@socketio.on('machinery_components_parts')
def machinery_components_parts(id_data,bomvalue):
    if 'user' in session:
        room = request.sid
        send_array_machinery_components = fie_database_operations.get_machinery_components_parts(id_data,bomvalue)
        socketio.emit('send_machinery_components_parts', send_array_machinery_components, room=room)

@app.route('/template_machinery_component/<record>/<bomlevel>')
def template_machinery_component(record,bomlevel):
    if 'user' in session and 'login' in session:
        if session['login']:
            return render_template("view_machinery_component.html",
                                   active_page='machinery_components_data',
                                   role=session['role'],
                                   name=session['name'],
                                   phone=session["user"],
                                   data = record,
                                   bomvalue = bomlevel
                                   )
    else:
        return redirect(url_for('login'))



# @socketio.on('part_plan_data')
# def part_plan_data():
#     if 'user' in session:
#         room = request.sid
#         plan_data = fie_database_operations.get_part_plan_data()
#         # print(plan_data)
#         socketio.emit('send_part_plan_data', plan_data, room=room)

@app.route('/part_plan_data', methods=['POST', 'GET'])
def part_plan_data():
    if 'user' in session:
        if request.method == 'POST':
            data = request.get_json(force=True)
            result = fie_database_operations.get_part_plan_data()
            return jsonify(result)




@socketio.on('gap_analysis_data')
def gap_analysis_data():
    if 'user' in session:
        room = request.sid
        gap_analysis = fie_database_operations.gap_analysis_data()
        # print(plan_data)
        socketio.emit('send_gap_analysis_data', gap_analysis, room=room)

@app.route('/history')
def history_data():
    if 'user' in session and 'login' in session:
        if session['login']:
            return render_template("history.html",
                                   active_page='history_fie',
                                   role=session['role'],
                                   name=session['name'],
                                   phone=session["user"]
                                   )
    else:
        return redirect(url_for('login'))


@app.route('/history_page1/<database>')
def history_page1(database):
    if 'user' in session and 'login' in session:
        if session['login']:
            return render_template("history_page1.html",
                                   active_page='history_fie',
                                   role=session['role'],
                                   name=session['name'],
                                   phone=session["user"],
                                   record = database
                                   )
    else:
        return redirect(url_for('login'))

@app.route('/view_history_data', methods=['POST', 'GET'])
def view_history_data():
    if request.method == 'POST':
        data = request.get_json(force=True)
        history_record = fie_database_operations.view_history_data(data)
        return jsonify(history_record)

@app.route('/vendor_backup_page/<data>')
def vendor_backup_page(data):
    if 'user' in session and 'login' in session:
        if session['login']:
            return render_template("vendor_backup_page.html",
                                   active_page='history_fie',
                                   role=session['role'],
                                   name=session['name'],
                                   phone=session["user"],
                                   docs=data
                                   )
    else:
        return redirect(url_for('login'))

@app.route('/view_vender_page', methods=['POST', 'GET'])
def view_vender_page():
    if request.method == 'POST':
        data = request.get_json(force=True)
        history_record = fie_database_operations.view_vender_page(data)
        return jsonify(history_record)



@app.route('/backup_sales_order/<data>')
def sales_order_backup_page(data):
    if 'user' in session and 'login' in session:
        if session['login']:
            return render_template("backup_sales_order.html",
                                   active_page='history_fie',
                                   role=session['role'],
                                   name=session['name'],
                                   phone=session["user"],
                                   docs=data
                                   )
    else:
        return redirect(url_for('login'))


@app.route('/view_sales_order_page', methods=['POST', 'GET'])
def view_sales_order_page():
    if 'user' in session and 'login' in session:
        if request.method == 'POST':
            data = request.get_json(force=True)
            history_record = fie_database_operations.view_sales_order_page(data)
            return jsonify(history_record)
    else:
        return redirect(url_for('login'))


@app.route('/wip_backup_page/<data>')
def wip_backup_page(data):
    if 'user' in session and 'login' in session:
        if session['login']:
            return render_template("wip_backup_page.html",
                                   active_page='history_fie',
                                   role=session['role'],
                                   name=session['name'],
                                   phone=session["user"],
                                   docs=data
                                   )
    else:
        return redirect(url_for('login'))

@app.route('/view_wip_page', methods=['POST', 'GET'])
def view_wip_page():
    if 'user' in session and 'login' in session:
        if request.method == 'POST':
            data = request.get_json(force=True)
            history_record = fie_database_operations.view_wip_page(data)
            return jsonify(history_record)

    else:
        return redirect(url_for('login'))

@app.route('/machinery_components_backup_page/<data>')
def machinery_components_backup_page(data):
    if 'user' in session and 'login' in session:
        if session['login']:
            return render_template("machinery_components_backup_page.html",
                                   active_page='history_fie',
                                   role=session['role'],
                                   name=session['name'],
                                   phone=session["user"],
                                   docs=data
                                   )
    else:
        return redirect(url_for('login'))



@app.route('/view_machinery_components_page', methods=['POST', 'GET'])
def view_machinery_components_page():
    if 'user' in session:
        if request.method == 'POST':
            data = request.get_json(force=True)
            history_record = fie_database_operations.view_machinery_components_page(data)
            return jsonify(history_record)
    else:
        return redirect(url_for('login'))

@app.route('/stock_backup_page/<data>')
def stock_backup_page(data):
    if 'user' in session and 'login' in session:
        if session['login']:
            return render_template("stock_backup_page.html",
                                   active_page='history_fie',
                                   role=session['role'],
                                   name=session['name'],
                                   phone=session["user"],
                                   docs=data
                                   )
    else:
        return redirect(url_for('login'))



@app.route('/view_stock_page', methods=['POST', 'GET'])
def view_stock_page():
    if 'user' in session:
        if request.method == 'POST':
            data = request.get_json(force=True)
            history_record = fie_database_operations.view_stock_page(data)
            return jsonify(history_record)
    else:
        return redirect(url_for('login'))



@socketio.on('get_drop_down_machinelist')
def get_drop_down_machinelist():
    if 'user' in session:
        room = request.sid
        drop_down_machinelist = fie_database_operations.get_drop_down_machinelist()
        # print(plan_data)
        socketio.emit('send_drop_down_machinelist', drop_down_machinelist, room=room)

@socketio.on('change_in_machine_plan')
def change_in_machine_plan(data):
    if 'user' in session:
        room = request.sid
        fie_database_operations.change_in_machine_plan(data)
        # fie_database_operations.edit_gap_analysis()
        # print(plan_data)
        # socketio.emit('send_drop_down_machinelist', get_change_in_machine_plan, room=room)


@app.route('/reset_machine_data', methods=['POST', 'GET'])
def reset_machine_data():
    if 'user' in session:
        if request.method == 'POST':
            data = request.get_json(force=True)
            result = fie_database_operations.reset_machine_data(data)
            return jsonify(result)
    else:
        return redirect(url_for('login'))

@app.route('/edit_particular_data', methods=['POST', 'GET'])
def edit_particular_data():
    # if 'user' in session:
    if request.method == 'POST':
        data = request.get_json(force=True)
        result = fie_database_operations.edit_particular_data(data)
        return jsonify("Response")
    else:
        return redirect(url_for('login'))

@app.route('/gap_calculator')
def gap_calculator():
    if 'user' in session and 'login' in session:
        if session['login']:
            return render_template("gap_calculator.html",
                                   active_page='gap_calculator',
                                   role=session['role'],
                                   name=session['name'],
                                   phone=session['user']
                                   )
    else:
        return redirect(url_for('login'))


@app.route('/getting_data_gap_analysis', methods=['POST', 'GET'])
def getting_data_gap_analysis():
    if 'user' in session:
        if request.method == 'POST':
            data = request.get_json(force=True)
            result = fie_database_operations.getting_data_gap_analysis(data)
            return jsonify(result)
    else:
        return redirect(url_for('login'))


@app.route('/getting_gap_calculator', methods=['POST', 'GET'])
def getting_gap_calculator():
    if 'user' in session:
        if request.method == 'POST':
            data = request.get_json(force=True)
            result = fie_database_operations.getting_gap_calculator(data)
            return jsonify(result)
    else:
        return redirect(url_for('login'))



if __name__ == "__main__":
    # socketio.run(app, host="0.0.0.0", port=80, debug=True)
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
