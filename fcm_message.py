import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging

cred = credentials.Certificate("anzen-1-0-firebase-adminsdk-mn430-b091432f56.json")
firebase_admin.initialize_app(cred)



#This registration token comes from the client FCM SDKs.
#registration_token = 'dHXlp24kQI25jc9qgz9zny:APA91bEPgh4W5SPDdQ7tNQKF9dzTNnqBZSSiYVwBlX4TNpA82RzJegFMigBI-sKVd-Zf09Z97_QsEJhRC8v6P5wd92JVe68scMzN-RxJIBdaoDgLav1KFNsWvDdookwxr_JAgoNEMDgD'
#registration_token = 'feRrnoOFT2m_pomwtXBiiv:APA91bHnvMGh_D2PjcxJrlrkN1pI-ZpNvSi5idLUDc886n5hYkdzv6sQBqKBMOcwAVnop88mfOsug_oPt8Qi-99N-GZVbRlm4DhvgqnWOlkYEjqrvGcAj-7j9KXE43J-E76ljijhJAdP'
#registration_token = ["feRrnoOFT2m_pomwtXBiiv:APA91bHnvMGh_D2PjcxJrlrkN1pI-ZpNvSi5idLUDc886n5hYkdzv6sQBqKBMOcwAVnop88mfOsug_oPt8Qi-99N-GZVbRlm4DhvgqnWOlkYEjqrvGcAj-7j9KXE43J-E76ljijhJAdP"]
def send_custom_notification(message_body,tokens):


    for token in tokens :
        # See documentation on defining a message payload.
        message = messaging.Message(
            notification=messaging.Notification(
                title= "Anzen",
                body=message_body,
            ),
            token=token,
        )

        # Send a message to the device corresponding to the provided
        # registration token.
        response = messaging.send(message)
        # Response is a message ID string.
        print('Successfully sent message:', response)


#send_custom_notification("Hello",registration_token)