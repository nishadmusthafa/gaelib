import unittest
from requests.auth import _basic_auth_str

from gaelib.auth.models import User
from gaelib.db import helpers
from gaelib.utils import web
from google.cloud import datastore
from mock import patch


class BaseUnitTestCase(unittest.TestCase):
  app_for_test = web.startup(parameter_logging=True,
                             client_logging=True,
                             blueprint_scope='gaelib')

  def setUp(self):
    self.client = self.app_for_test.test_client()
    self.clear_database()

  def tearDown(self):
    self.clear_database()



  def clear_database(self):
    # Nosetests use a different database and it also does not use namespace from app.yaml,
    # so for now, we need to use the default namespace,
    # we will change this stuff later after further research.
    client = datastore.Client(namespace=helpers.get_datastore_namespace())
    query = client.query(kind='__kind__')
    query.keys_only()
    kinds = [entity.key.id_or_name for entity in query.fetch()]

    for kind in kinds:
      query = client.query(kind=kind)
      query.keys_only()
      keys = [entity.key for entity in query.fetch()]
      for i in range(0, len(keys), 499):
        client.delete_multi(keys[i:i + 499])

  def get_entity_count(self, kind):
    client = datastore.Client(namespace=helpers.get_datastore_namespace())
    query = client.query(kind=kind)
    query.keys_only()
    keys = [entity.key for entity in query.fetch()]
    return len(keys)

  def mock_storage_client(self):
    self.storage_client_patch = patch(
        'google.cloud.storage.Client')
    self.storage_client = self.storage_client_patch.start()

  def mock_bucket(self):
    self.bucket_patch = patch(
        'google.cloud.storage.Bucket')
    self.bucket = self.bucket_patch.start()

  def mock_blob(self):
    self.blob_patch = patch(
        'google.cloud.storage.Blob')
    self.blob = self.blob_patch.start()

  def mock_flask_request(self):
    self.request_patch = patch('flask.request')
    self.request = self.request_patch.start()


class BaseAuthenticatedUnitTestCase(BaseUnitTestCase):
  def return_authorize_request(self, auth_type='firebase'):
    return {'email': self.user.email,
            'picture': self.user.picture,
            'name': self.user.name,
            }

  def auth_headers(self):
    return {
        'Authorization': _basic_auth_str(self.user.uid, 'password'),
    }

  def setUp(self):
    super().setUp()
    self.authorize_request_patch = patch(
        'gaelib.auth.auth.Auth.authorize_request')
    self.authorize_request = self.authorize_request_patch.start()
    self.authorize_request.side_effect = self.return_authorize_request

  def add_user_entity(self, name='', email='', uid='', picture='http://dp.com', client_user=False):
    user = User()
    user.update(
        name=name,
        email=email,
        picture=picture,
        uid=uid,
    )
    user.put()
    if client_user:
      self.user = user
    return user

  def tearDown(self):
    self.authorize_request_patch.stop()
    super().tearDown()
