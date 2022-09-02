from flask import request, abort
from gaelib.cron import constants
from flask.json import jsonify


def cron_validate(handler):
  def check_if_cron(*args, **kwargs):
    cron_validation_response = perform_cron_validation()
    if cron_validation_response == True:
      return handler(*args, **kwargs)
    return cron_validation_response
  return check_if_cron


def perform_cron_validation():
  if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
    client_ip = request.environ['REMOTE_ADDR']
  else:
    client_ip = request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0]

  if (request.headers.get('X-AppEngine-Cron') is None) and (client_ip not in constants.VALID_CRON_JOB_IP_ADDRS):
    response_dict = {}
    response_dict["error_message"] = "Cron Validation Failed!"
    return jsonify(response_dict), 400
  return True
