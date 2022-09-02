from flask import g, render_template, request, session
from gaelib.auth.decorators import auth_required, access_control
from gaelib.auth.models import User, UserRole
from gaelib.env import (get_admin_dashboard_post_login_page,
                        get_dev_user_emails)
from gaelib.view.base_view import BaseHttpHandler
from gaelib.utils.web import app
from gaelib.utils.task import create_task
import json


class DashboardView(BaseHttpHandler):
  decorators = [access_control(role=UserRole.STAFF), auth_required]
  methods = ['GET', 'POST']


class DashboardLogin(BaseHttpHandler):
  """
      The view to get handle dashboard login
  """
  methods = ['GET']

  def dispatch_request(self):
    return render_template("login.html",
                           post_login_page=get_admin_dashboard_post_login_page()
                           )


class DashboardLogout(BaseHttpHandler):
  """
      The view to get handle dashboard logout
  """
  methods = ['GET']

  def dispatch_request(self):
    try:
      session.pop("gae_uid")
    except KeyError:
      pass
    return render_template("logout.html")


class Notifications(DashboardView):
  """
      The view to get handle notification admin. It's optional and
      a link is only displayed if constants.DASHBOARD_NOTIFICATION_ADMIN
      is set to True
  """
  methods = ['GET', 'POST']

  def dispatch_request(self):
    if request.method == 'GET':
      return render_template("notifications.html")
    elif request.method == 'POST':
      data = request.form.to_dict()
      title = data.get('title', '')
      message = data.get('message', '')
      group = data.get('group', [])
      android_device_tokens = []
      ios_device_tokens = []
      if not title or not message or not group:
        g.app.logger.info('Empty args for notify method. Returning')
        return render_template("notifications.html", message="Empty Arguments")

      g.app.logger.info(
          '%s notification with title: %s message: %s', group, title, message)

      users = []
      if group == 'internal':
        # Get Dev Users
        dev_user_emails = get_dev_user_emails()
        g.app.logger.info("Dev User E-mails are: " + str(dev_user_emails))
        dev_users = []
        for email in dev_user_emails:
          email_filter = ('email', '=', email)
          users_retrieved = User.retrieve(filters=[email_filter])
          if users_retrieved:
            users.append(users_retrieved[0])
      else:
        users = User.retrieve()

      android_device_tokens, ios_device_tokens = self.get_device_tokens(users)

      # Create the payload for the task
      payload = {}
      payload['message'] = message
      payload['title'] = title
      payload['seq'] = 1
      self.create_notification_task(payload, android_device_tokens, 'android')
      self.create_notification_task(payload, ios_device_tokens, 'ios')
      return render_template("notifications.html")

  def get_device_tokens(self, users):
    android_device_tokens = []
    ios_device_tokens = []
    for user in users:
      if user.os and user.device_notification_token:
        if user.os == 'android':
          android_device_tokens.append(user.device_notification_token)
        else:
          ios_device_tokens.append(user.device_notification_token)
    return android_device_tokens, ios_device_tokens

  def create_notification_task(self, payload, device_tokens, os):
    for i in range(0, len(device_tokens), 500):
      payload['device_tokens'] = device_tokens[i:i+500]
      payload['os'] = os
      response = create_task(data=json.dumps(payload))
