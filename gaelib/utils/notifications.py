import json
import os
import jwt
import time
from firebase_admin import credentials, initialize_app, messaging
from flask import g
from hyper import HTTPConnection
from gaelib.env import get_app_or_default_prop

import constants
from gaelib.env import get_env, get_apns_notifications_credential_file_path


ALGORITHM = 'ES256'
APNS_KEY_ID = get_app_or_default_prop('APNS_KEY_ID')
APNS_TEAM_ID = get_app_or_default_prop('APNS_TEAM_ID')

if get_env() == 'staging':
  conn = HTTPConnection('api.sandbox.push.apple.com:443')
else:
  conn = HTTPConnection('api.push.apple.com:443')

IOS_BUNDLE_ID = get_app_or_default_prop(
    'IOS_BUNDLE_ID')

apns_auth_key_path = get_apns_notifications_credential_file_path()

f = open(apns_auth_key_path)
secret = f.read()


def send_apns_notification(device_tokens, failed_tokens, title, message):
  token = jwt.encode(
      {
          'iss': APNS_TEAM_ID,
          'iat': time.time()
      },
      secret,
      algorithm=ALGORITHM,
      headers={
          'alg': ALGORITHM,
          'kid': APNS_KEY_ID,
      }
  )
  request_headers = {
      'apns-expiration': '0',
      'apns-priority': '10',
      'apns-topic': IOS_BUNDLE_ID,
      'authorization': 'bearer {0}'.format(token.decode('ascii'))
  }
  payload = {
      'aps': {
          'alert': {
              'title': title,
              'body': message,
          }
      }
  }

  payload = json.dumps(payload).encode('utf-8')
  g.app.logger.info("Device Tokens are: " + str(device_tokens))
  for device_token in device_tokens:
    path = '/3/device/{0}'.format(device_token)
    g.app.logger.info("Device Token: " + device_token)
    conn.request(
        'POST',
        path,
        payload,
        headers=request_headers
    )
    resp = conn.get_response()
    g.app.logger.info("Response Status: " + str(resp.status))
    if resp.status == 200:
      failed_tokens.remove(device_token)
    g.app.logger.info(resp.read())
  g.app.logger.info('List of IOS tokens failed: {0}'.format(failed_tokens))
  return failed_tokens


def send_fcm_notification(device_tokens, failed_tokens, title, message):
  message = messaging.MulticastMessage(
      data={'title': title, 'message': message},
      tokens=device_tokens,
  )
  response = messaging.send_multicast(message)
  failure_count = response.failure_count
  if failure_count > 0:
    g.app.logger.info("Failure Count: " + str(failure_count))
    responses = response.responses
    for idx, resp in enumerate(responses):
      if resp.success:
        # The order of responses corresponds to the order of the device tokens.
        failed_tokens.remove(device_tokens[idx])
    g.app.logger.info(
        'List of Android tokens failed: {0}'.format(failed_tokens))
  else:
    g.app.logger.info("Notifications Sent to all devices successfully!")
    failed_tokens = []
  g.app.logger.info("Failed Tokens: " + str(failed_tokens))
  return failed_tokens


def send_notifications(os, device_tokens, failed_tokens, title, message):
  if os == 'android':
    return send_fcm_notification(
        device_tokens, failed_tokens, title, message)
  elif os == 'ios':
    return send_apns_notification(
        device_tokens, failed_tokens, title, message)
