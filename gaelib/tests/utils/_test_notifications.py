from gaelib.tests.tasks.base import BaseUnitTestCase
from gaelib.utils.task import create_task
from gaelib.utils.notifications import send_apns_notification, send_fcm_notification
import requests
import json
from mock.mock import patch
import hyper
from firebase_admin import messaging
from mock import Mock


class NotificationsTestCase(BaseUnitTestCase):

  def setUp(self):
    super().setUp()
    self.mock_http_conn()
    self.mock_messaging()
    self.mock_send_multicast_response()
    self.request = requests.Request()
    self.response = requests.Response()
    self.http_conn.return_value.request.return_value = self.request
    self.http_conn.return_value.get_response.return_value = self.response
    self.messaging.send_multicast.return_value = self.send_multicast_response

  def tearDown(self):
    self.http_conn_patch.stop()
    self.messaging_patch.stop()
    self.send_multicast_response_patch.stop()
    super().tearDown()

  def test_send_apns_notification_when_all_the_tokens_are_successful(self):
    with self.app_for_test.test_request_context():
      self.app_for_test.preprocess_request()
      device_tokens = ['token_1', 'token_2']
      failed_device_tokens = device_tokens.copy()
      success_response = Mock(hyper.HTTP11Response)
      success_response.status = 200
      success_response.read.return_value = ''
      self.http_conn.get_response.return_value = success_response
      failed_tokens_response = send_apns_notification(
          device_tokens, failed_device_tokens, '', '')
      self.assertEqual([], failed_tokens_response)

  def test_send_apns_notification_when_all_the_tokens_are_unsuccessful(self):
    with self.app_for_test.test_request_context():
      self.app_for_test.preprocess_request()
      device_tokens = ['token_1', 'token_2']
      failed_device_tokens = device_tokens.copy()
      success_response = Mock(hyper.HTTP11Response)
      success_response.status = 400
      success_response.read.return_value = ''
      self.http_conn.get_response.return_value = success_response
      failed_tokens_response = send_apns_notification(
          device_tokens, failed_device_tokens, '', '')
      self.assertEqual(failed_device_tokens, failed_tokens_response)

  def test_send_fcm_notification_when_all_the_tokens_are_successful(self):
    self.send_multicast_response.failure_count = 0
    with self.app_for_test.test_request_context():
      self.app_for_test.preprocess_request()
      device_tokens = ['token_1', 'token_2']
      failed_device_tokens = device_tokens.copy()
      failed_tokens_response = send_fcm_notification(
          device_tokens, failed_device_tokens, '', '')
      self.assertEqual([], failed_tokens_response)

  def test_send_fcm_notification_when_all_the_tokens_are_unsuccessful(self):
    self.send_multicast_response.failure_count = 2
    response_1 = requests.Response()
    response_1.success = False
    response_2 = requests.Response()
    response_2.success = False
    self.send_multicast_response.responses = [response_1, response_2]
    with self.app_for_test.test_request_context():
      self.app_for_test.preprocess_request()
      device_tokens = ['token_1', 'token_2']
      failed_device_tokens = device_tokens.copy()
      failed_tokens_response = send_fcm_notification(
          device_tokens, failed_device_tokens, '', '')
      self.assertEqual(failed_device_tokens, failed_tokens_response)

  def test_send_fcm_notification_when_some_tokens_are_unsuccessful(self):
    self.send_multicast_response.failure_count = 1
    response_1 = requests.Response()
    response_1.success = True
    response_2 = requests.Response()
    response_2.success = False
    self.send_multicast_response.responses = [response_1, response_2]
    with self.app_for_test.test_request_context():
      self.app_for_test.preprocess_request()
      device_tokens = ['token_1', 'token_2']
      failed_device_tokens = device_tokens.copy()
      failed_tokens_response = send_fcm_notification(
          device_tokens, failed_device_tokens, '', '')
      self.assertEqual(['token_2'], failed_tokens_response)
