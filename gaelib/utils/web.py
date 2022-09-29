import os
import logging


from flask import g, Flask, json, request
from google.cloud.logging_v2.client import Client
from google.cloud.logging_v2.handlers import CloudLoggingHandler
from gaelib.env import (
    get_app_or_default_prop,
    get_auth_config,
    get_dashboard_url_prefix,
    get_env,
    get_sidebar_template,
    get_twilio_account_sid,
    get_twilio_auth_token,
    get_twilio_verification_sid,
    is_dev)
from gaelib import filters
from gaelib.urls import (auth_urls,
                         verification_urls,
                         dashboard_lib_urls,
                         dashboard_lib_template_dir,
                         client_logger_urls,
                         task_urls)
from firebase_admin import credentials, initialize_app
from werkzeug.exceptions import HTTPException


PARAMETER_LOGGING = get_app_or_default_prop('PARAMETER_LOGGING')

app_template_dir = os.path.abspath('./templates/')

app = Flask(__name__, template_folder=app_template_dir)

# Uncomment to debug template loading issues
app.config['EXPLAIN_TEMPLATE_LOADING'] = True

app.jinja_loader.searchpath.append(dashboard_lib_template_dir)


@app.errorhandler(HTTPException)
def handle_exception(e):
  """Return JSON instead of HTML for HTTP errors."""
  # start with the correct headers and status code from the error
  response = e.get_response()
  # replace the body with JSON
  response.data = json.dumps({
      "code": e.code,
      "name": e.name,
      "description": e.description,
  })
  response.content_type = "application/json"
  return response


@app.before_request
def log_request_info():
  """
      Logs request params before dispatching request
  """
  g.app = app

  if not PARAMETER_LOGGING:
    return

  request_data = None
  request_args = request.args.to_dict()
  request_form = request.form.to_dict()

  if request_args:
    g.app.logger.info('Request args: ' + str(request_args))
  if request_form:
    g.app.logger.info('Request form: ' + str(request_form))
  if request.content_type == 'application/json' and request.json:
    g.app.logger.info('Request json: ' + str(request.json))


@app.context_processor
def inject_global_template_vars():
  return dict(app_name=get_app_or_default_prop('APP_NAME'),
              auth_config=get_auth_config(),
              dashboard_notification_admin=get_app_or_default_prop(
      'DASHBOARD_NOTIFICATION_ADMIN'),
      dashboard_prefix=get_dashboard_url_prefix(), env=get_env(),
      sidebar_template=get_sidebar_template(),
  )


def startup(auth=True, blueprint_scope='', parameter_logging=False, client_logging=False, dashboard=True, verification=True):
  """The startup script to create flask app and check if
      the application is running on local server or production.
  """

  if is_dev():
    # Dumb hack we need to run the app locally
    # The private key that's in this file is not associated with
    #  a real account
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getcwd() + \
        '/fake_creds.json'
    app.logger.setLevel(logging.DEBUG)
  else:
    gcp_client = Client()
    gcph = CloudLoggingHandler(gcp_client)
    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(gcph)

  # For Notifications
  app.register_blueprint(task_urls, name=f"{blueprint_scope}_tasks")

  if auth:
    app.register_blueprint(auth_urls, name=f"{blueprint_scope}_auth")

  if dashboard:
    app.register_blueprint(dashboard_lib_urls, name=f"{blueprint_scope}_dashboard")

  app.register_blueprint(filters.blueprint, name=f"{blueprint_scope}_filters")

  app.secret_key = get_app_or_default_prop(
      'SESSION_SECRET')   # Used for session management

  if verification:
    app.register_blueprint(verification_urls, name=f"{blueprint_scope}_verification")
    # Used for Twilio
    app.config['VERIFICATION_SID'] = get_twilio_verification_sid()
    app.config['ACCOUNT_SID'] = get_twilio_account_sid()
    app.config['AUTH_TOKEN'] = get_twilio_auth_token()

  if client_logging:
    app.register_blueprint(client_logger_urls, name=f"{blueprint_scope}_clientlogger")

  return app
