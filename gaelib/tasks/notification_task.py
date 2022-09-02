from gaelib.view.base_view import BaseTaskHandler
from flask import request, render_template, g
from gaelib.utils.task import create_task
from gaelib.env import get_dev_user_emails, get_app_or_default_prop
from gaelib.auth.models import User
from gaelib.utils.notifications import send_notifications
import json


class NotificationTask(BaseTaskHandler):
  methods = ['POST']

  def dispatch_request(self):
    if request.method == 'GET':
      # Write code for Cron Job here.
      pass

    elif request.method == 'POST':
      data = json.loads(request.get_data(as_text=True))
      max_notification_task_retries = get_app_or_default_prop(
          'MAX_NOTIFICATION_TASK_RETRIES')
      seq = data.get('seq')
      if seq is None:
        return self.json_error("Sequence Number is mandatory", 400)
      if seq > max_notification_task_retries:
        # This is to ensure that tasks are not spawned infinitely in case of some permanent failures
        return self.json_error("Max number of retries reached", 400)
      title = data.get('title', '')
      message = data.get('message', '')
      device_tokens = data.get('device_tokens', [])
      os = data.get('os', [])
      # The success tokens are removed from the list. The failed tokens are remaining in the list up till exception
      failed_device_tokens = device_tokens.copy()
      if device_tokens:
        try:
          failed_device_tokens = send_notifications(
              os, device_tokens, failed_device_tokens, title, message)
        except:
          g.app.logger.error(
              "An exception occured while sending notifications")
          # 1. Create Payload of the child task
          payload = {}
          payload['device_tokens'] = failed_device_tokens
          payload['message'] = message
          payload['title'] = title
          payload['seq'] = seq + 1
          payload['os'] = os

          # 2. Create Task
          response = create_task(data=json.dumps(payload))

      if failed_device_tokens:
        # 1. Create Payload of the child task
        g.app.logger.info("Failed Tokens: " + str(failed_device_tokens))
        payload = {}
        payload['device_tokens'] = failed_device_tokens
        payload['message'] = message
        payload['title'] = title
        payload['seq'] = seq + 1
        payload['os'] = os

        # 2. Create Task
        response = create_task(data=json.dumps(payload))
      return self.json_success({}, 200)
