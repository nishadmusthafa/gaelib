from gaelib.tests.tasks.base import BaseTaskUnitTestCase
from gaelib.utils.task import create_task
from flask import app
import requests
import json


class NotificationTaskTestCase(BaseTaskUnitTestCase):

  def setUp(self):
    super().setUp()
    self.mock_apns_file_open()
    self.mock_create_task()
    self.mock_send_notification()

  def tearDown(self):
    self.create_task_patch.stop()
    self.send_notification_patch.stop()
    super().tearDown()

  def test_task_creation_if_sequence_number_is_not_in_the_payload(self):
    response = self.client.post(
        '/notification_task_handler/', data=json.dumps({}))
    data = json.loads(response.get_data(as_text=True))
    self.assertEqual(400, response.status_code)
    self.assertEqual("Sequence Number is mandatory", data['error_message'])

  def test_task_creation_if_sequence_number_is_greater_than_max_retries(self):
    response = self.client.post(
        '/notification_task_handler/', data=json.dumps({"seq": 30}))
    data = json.loads(response.get_data(as_text=True))
    self.assertEqual(400, response.status_code)
    self.assertEqual("Max number of retries reached", data['error_message'])

  def test_create_task_called_when_the_failed_tokens_list_is_empty(self):
    response = self.client.post(
        '/notification_task_handler/', data=json.dumps({"seq": 1, "device_tokens": [], "os": "ios"}))
    data = json.loads(response.get_data(as_text=True))
    self.assertEqual(200, response.status_code)
    self.assertFalse(self.create_task.called)

  def test_create_task_called_when_the_failed_tokens_list_is_not_empty(self):
    response = self.client.post(
        '/notification_task_handler/', data=json.dumps({"seq": 1, "device_tokens": ['t1', 't2'], "os": "ios"}))
    data = json.loads(response.get_data(as_text=True))
    self.assertEqual(200, response.status_code)
    self.create_task.assert_called()
    self.create_task.assert_called_with(
        data='{"device_tokens": ["t1", "t2"], "message": "", "title": "", "seq": 2, "os": "ios"}')

  def test_create_task_called_when_send_notifications_throw_an_exception(self):
    self.send_notification.side_effect = Exception()
    response = self.client.post(
        '/notification_task_handler/', data=json.dumps({"seq": 1, "device_tokens": ['t1', 't2'], "os": "ios"}))
    data = json.loads(response.get_data(as_text=True))
    self.assertEqual(200, response.status_code)
    self.create_task.assert_called()
    self.create_task.assert_called_with(
        data='{"device_tokens": ["t1", "t2"], "message": "", "title": "", "seq": 2, "os": "ios"}')
