# Import necessary classes and modules
from pyapns_client import AsyncAPNSClient, TokenBasedAuth, IOSPayload, IOSNotification, IOSPayloadAlert
from pyapns_client import UnregisteredException, APNSDeviceException, APNSServerException, APNSProgrammingException

from os import getenv
from dotenv import load_dotenv

# from common import config as cfg
# from api.chat.ChatThreadHandler import ChatThreadHandler

load_dotenv()
APNS_AUTH_KEY_ID = getenv('APNS_AUTH_KEY_ID')
APNS_TEAM_ID = getenv('APNS_TEAM_ID')
IOS_BUNDLE_ID = getenv('IOS_BUNDLE_ID')


async def pushiOSMessage(push_token: str, alert_title: str, alert_body: str, thread: str = 'some_thread'):
    async with AsyncAPNSClient(
        mode=AsyncAPNSClient.MODE_DEV,
        authentificator=TokenBasedAuth(
            auth_key_path=f'./AuthKey_{APNS_AUTH_KEY_ID}.p8',
            auth_key_id=APNS_AUTH_KEY_ID,
            team_id=APNS_TEAM_ID,
        )
    ) as client:
        try:
            # Create the payload for the notification
            alert = IOSPayloadAlert(
                title=alert_title, body=alert_body)
            payload = IOSPayload(alert=alert, sound='bleat.wav',
                                 thread_id=thread, mutable_content=False)

            # Create the notification object with the payload and other optional parameters
            # the 'topic' value is the iOS Bundle ID
            notification = IOSNotification(
                payload=payload, priority=10, topic=IOS_BUNDLE_ID)

            # Send the notification asynchronously to one or more device tokens
            await client.push(notification=notification, device_token=push_token)
        except UnregisteredException as e:
            print(
                f'device is unregistered, compare timestamp {e.timestamp_datetime} and remove from db')
        except APNSDeviceException:
            print(
                'flag the device as potentially invalid and remove from db after a few tries')
        except APNSServerException:
            print('try again later')
        except APNSProgrammingException:
            print('check your code and try again later')
        else:
            # Handle successful push
            print('Push notification sent successfully!')
