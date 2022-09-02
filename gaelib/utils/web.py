import os
import logging


from flask import g, Flask, request
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

from gaelib.env import (get_app_or_default_prop)

PARAMETER_LOGGING = get_app_or_default_prop('PARAMETER_LOGGING')

app_template_dir = os.path.abspath('./templates/')

app = Flask(__name__, template_folder=app_template_dir)

# Uncomment to debug template loading issues
app.config['EXPLAIN_TEMPLATE_LOADING'] = True

app.jinja_loader.searchpath.append(dashboard_lib_template_dir)


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
              dashboard_notification_admin=get_app_or_default_prop('DASHBOARD_NOTIFICATION_ADMIN'),
              dashboard_prefix=get_dashboard_url_prefix(), env=get_env(),
              sidebar_template=get_sidebar_template(),
              )


def startup(auth=True, parameter_logging=False, client_logging=False, dashboard=True, verification=True):
  """The startup script to create flask app and check if
      the application is running on local server or production.
  """

  if is_dev():
    # os.environ['DATASTORE_EMULATOR_HOST'] = '172.17.0.2:8888'
    # if get_app_or_default_prop('DATASTORE_PROJECT_ID'):
    #   os.environ['DATASTORE_PROJECT_ID'] = get_app_or_default_prop('DATASTORE_PROJECT_ID')
    # if get_app_or_default_prop('GOOGLE_CLOUD_PROJECT'):
    #   os.environ['GOOGLE_CLOUD_PROJECT'] = get_app_or_default_prop('GOOGLE_CLOUD_PROJECT')

    # Dumb hack we need to run locally
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
  app.register_blueprint(task_urls)

  if auth:
    app.register_blueprint(auth_urls)

  if dashboard:
    app.register_blueprint(dashboard_lib_urls)

  app.register_blueprint(filters.blueprint)

  app.secret_key = get_app_or_default_prop(
      'SESSION_SECRET')   # Used for session management

  if verification:
    app.register_blueprint(verification_urls)
    # Used for Twilio
    app.config['VERIFICATION_SID'] = get_twilio_verification_sid()
    app.config['ACCOUNT_SID'] = get_twilio_account_sid()
    app.config['AUTH_TOKEN'] = get_twilio_auth_token()

  if client_logging:
    app.register_blueprint(client_logger_urls)

  return app
