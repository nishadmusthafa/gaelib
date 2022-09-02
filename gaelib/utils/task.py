from google.cloud import tasks_v2
from gaelib.view.base_view import BaseHttpHandler
from gaelib.auth.auth import get_user_id_and_token
import datetime
import base64
import os
from gaelib.env import get_task_queue
from flask import g


def create_task(data=None):
  project = os.getenv('GOOGLE_CLOUD_PROJECT')
  queue = get_task_queue()
  client = tasks_v2.CloudTasksClient()
  parent = client.queue_path(project, queue['location'], queue['queue_name'])
  user_id, token = get_user_id_and_token()
  authorization_string = user_id + ":" + token
  g.app.logger.info("Creating Task with project={} queue={} parent={} user_id={} token={}".format(
      project, queue, parent, user_id, token))
  authorization_string_bytes = authorization_string.encode("ascii")
  authorization_string_base64_bytes = base64.b64encode(
      authorization_string_bytes)

  # Construct the request body.
  task = {
      'app_engine_http_request': {
          'app_engine_routing': {
              'version': 'manmeet'
          },
          'http_method': tasks_v2.HttpMethod.POST,
          'headers': {
              'Authorization': "Basic " + authorization_string_base64_bytes.decode("ascii")
          },
          'relative_uri': '/notification_task_handler/',
          'body': data
      }
  }
  if data is not None:
    # The API expects a payload of type bytes.
    converted_payload = str(data).encode()

    # Add the payload to the request.
    task['app_engine_http_request']['body'] = converted_payload

  # Use the client to build and send the task.
  response = client.create_task(parent=parent, task=task)

  g.app.logger.info('Created task {}'.format(response.name))
  return response
