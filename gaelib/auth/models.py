from enum import Enum
from gaelib.db import model, properties
from flask import g, request
import json


class UserRole(Enum):
  """
      Enum for User.role
  """
  DEFAULT = 0
  STAFF = 1
  ADMIN = 2


USER_ROLE_CHOICES = [user_role.value for user_role in UserRole]


class User(model.Model):
  """
      The database model for User kind.
  """
  email = properties.StringProperty()
  uid = properties.StringProperty()
  name = properties.StringProperty()
  picture = properties.StringProperty()
  role = properties.IntegerProperty(choices=USER_ROLE_CHOICES)
  os = properties.StringProperty()
  device_notification_token = properties.StringProperty()
  token = properties.StringProperty()
  phone = properties.StringProperty()

  def update_device_token_data(self):
    device_token_data = {}
    try:
      device_token_data = request.json.get('device_token')
    except (AttributeError, KeyError):
      device_token_data = {}

    if not device_token_data:
      try:
        device_token_data = request.form.get('device_token')
      except (AttributeError, KeyError):
        device_token_data = {}

    if not device_token_data:
      try:
        device_token_data = request.args.get('device_token')
      except (AttributeError, KeyError):
        device_token_data = {}

    if not device_token_data:
      try:
        device_token_data = request.params.get('device_token')
      except (AttributeError, KeyError):
        device_token_data = {}

    if device_token_data:
      device_token_data = json.loads(device_token_data)
      self.os = device_token_data.get('os')
      self.device_notification_token = device_token_data.get('token')
    else:
      g.app.logger.error('Device Token data not found in the request')
