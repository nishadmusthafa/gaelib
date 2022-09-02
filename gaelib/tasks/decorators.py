from flask import request, abort
from gaelib.cron.decorators import perform_cron_validation
from gaelib.auth.decorators import perform_authentication
from flask.json import jsonify


def task_validate(handler):
  def check_if_task(*args, **kwargs):
    task_validation_response = perform_task_validation()
    if task_validation_response == True:
      return handler(*args, **kwargs)
    return task_validation_response
  return check_if_task


def perform_task_validation():
  if (request.headers.get('X-AppEngine-QueueName') is None):
    response_dict = {}
    response_dict["error_message"] = "Task Validation Failed!"
    return jsonify(response_dict), 400
  return True


def cron_or_task_validate(handler):
  def check_if_cron_or_task(*args, **kwargs):
    task_validation_response = perform_task_validation()
    cron_validation_response = perform_cron_validation()
    authentication_response = perform_authentication()

    if (task_validation_response == True and authentication_response == True) or cron_validation_response == True:
      return handler(*args, **kwargs)
    return abort(400)
  return check_if_cron_or_task
