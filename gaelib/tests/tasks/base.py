from mock import patch, mock_open
from gaelib.auth.models import User
from gaelib.tests.base import BaseUnitTestCase
from gaelib.utils.task import create_task


class BaseTaskUnitTestCase(BaseUnitTestCase):
  def setUp(self):
    super().setUp()
    self.perform_authentication()

  def tearDown(self):
    self.perform_cron_validation_patch.stop()
    super().tearDown()

  def mock_send_notification(self):
    self.send_notification_patch = patch(
        'gaelib.utils.notifications.send_notifications')
    self.send_notification = self.send_notification_patch.start()

  def mock_create_task(self):
    self.create_task_patch = patch(
        'gaelib.tasks.notification_task.create_task')
    self.create_task = self.create_task_patch.start()

  def mock_perform_cron_validation(self):
    self.perform_cron_validation_patch = patch(
        'gaelib.tasks.decorators.perform_cron_validation')
    self.perform_cron_validation = self.perform_cron_validation_patch.start()

  def mock_apns_file_open(self):
    self.apns_file_open_patch = patch(
        'builtins.open', new_callable=mock_open)
    self.apns_file_open = self.apns_file_open_patch.start()

  def perform_authentication(self):
    self.mock_perform_cron_validation()
    self.perform_cron_validation.return_value = True
