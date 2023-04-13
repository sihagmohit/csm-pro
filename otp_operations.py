'''import requests
import json

URL = 'https://www.sms4india.com/api/v1/sendCampaign'

# get request
def sendPostRequest(reqUrl, apiKey, secretKey, useType, phoneNo, senderId, textMessage):
  req_params = {
  'apikey':apiKey,
  'secret':secretKey,
  'usetype':useType,
  'phone': phoneNo,
  'message':textMessage,
  'senderid':senderId
  }
  return requests.post(reqUrl, req_params)

# get response
#response = sendPostRequest(URL, 'provided-api-key', 'provided-secret', 'prod/stage', 'valid-to-mobile', 'active-sender-id', 'message-text' )
#response = sendPostRequest(URL, '8QZZ067CDEVC8TRVLKUQ4X8S1LC2J9SE','BW745NL8IIOE4GHM','stage','8275906923','SMSIMD',"Your Anzen OTP is xxxxxx.")
#response = sendPostRequest(URL, 'BREK9U8IPBMD2A07BRZJEVVW07G29NGK','U3CCT3PW359WHSSJ','prod','9922998224','CYRNCS',"Your Anzen OTP is xxxxxx.")

"""
  Note:-
    you must provide apikey, secretkey, usetype, mobile, senderid and message values
    and then requst to api
"""
# print response if you want
#print (response.text)'''

from twilio.rest import Client
import mail_api

account_sid = 'ACd7cc871fc723b1c200f64dbaacba8f92'
auth_token = 'd9930f9c4000fb5c2c976df9470b1423'

phone_number = '+16502939447'


def send_otp(code,number):
    # Your Account Sid and Auth Token from twilio.com/console
    # DANGER! This is insecure. See http://twil.io/secure
    #account_sid = 'AC62c074cad2d81786eca5f45908af7450'
    #auth_token = '74f1ea7cdeabd5f91b3cc8268733a220'
    client = Client(account_sid, auth_token)
    try :
        message = client.messages \
            .create(
            body="Your OTP for Cyronics IOT Software - " + str(code) + " .",
            from_=str(phone_number),
            to='+91'+str(number)
        )
        print("In new code")
        print(message.error_code)
        print(message.error_message)
        print(message.sid)
    except :
        print("MESSAGE SENDING FAILED")
def send_signup_accept(status,number):
    # Your Account Sid and Auth Token from twilio.com/console
    # DANGER! This is insecure. See http://twil.io/secure
    client = Client(account_sid, auth_token)
    try :
        message = client.messages \
            .create(
            body="Your application for Cyronics IOT Software is " + status +  ".",
            #from_='+14172753291',
            from_=str(phone_number),
            to='+91'+str(number)
        )
        print(message.sid)
    except:
        print("MESSAGE SENDING FAILED")

def send_signup_role(role,number):
    # Your Account Sid and Auth Token from twilio.com/console
    # DANGER! This is insecure. See http://twil.io/secure

    client = Client(account_sid, auth_token)
    try :
        message = client.messages \
            .create(
            body="Your role for Cyronics IOT Software has been updated to " + role +  ".",
            #from_='+14172753291',
            from_=str(phone_number),
            to='+91'+str(number)
        )
        print(message.sid)
    except :
        print("MESSAGE SENDING FAILED")
def send_otp_via_email(otp,email_id):

    mail_header = """ \
                        <html>
                    <head>
                    <title></title>
                    </head>
                    <style>
                    h1 {
                      font-family: 'Trebuchet MS', sans-serif;
                      font-size:50px;
                      font-weight:bold;
                      color:#69051e;
                    }
                    h3 {
                      font-family: 'Trebuchet MS', sans-serif;
                      font-size:30px;
                      
                    }
                    
                    </style>
                    <body>
                    <center>
                    <div style="padding-top:50px">
                        <div>
                        <img src="http://cyrocal.xyz/cyronics_iot_logo.png" style="height:50px">
                        </div>
                        
                        <div style="padding-top:20px">
                        <hr>
                                                
                        <h3>Your OTP for Cyronics Software is </H3>
                        <h1>
                    """
    mail_footer = """\
                        </h1>
                        <hr>
	                    
                        </div>
                    </div></center>
                    </body>
                    """
    final_html = mail_header + str(otp) + mail_footer
    recipient = []
    recipient.append(email_id)
    try:
        mail_api.send_mail(recipient, "OTP - Cyronics Software", final_html)
    except :
        print("MESSAGE SENT FAILED")

def send_custom_message(message,numbers):

    client = Client(account_sid, auth_token)
    try :
        for number in numbers :
            message = client.messages \
                .create(
                body="Cyronics IOT Software Notification : " + message,
                #from_='+14172753291',
                from_=str(phone_number),
                to='+91'+str(number)
            )
            print(message.sid)
    except :
        print("MESSAGE SEND FAILED")

if __name__ == "__main__":
    #print("hello there")
    #send_otp_via_email(12345,"vatsalrana14@gmail.com")
    send_otp(123456,"9922998224")