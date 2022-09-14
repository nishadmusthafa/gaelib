from flask import Blueprint, json

from gaelib.db import model, properties
from gaelib.tests.base import BaseAuthenticatedUnitTestCase
from gaelib.utils import web
from gaelib.view.base_view import BaseAPIHandler
from gaelib.view.base_view import LazyView


class SampleAPINoController(BaseAPIHandler):
  controller = None


class SampleModel(model.Model):
  """
      The database model for a Sample Entity
  """
  string_field = properties.StringProperty()
  date_field = properties.DateTimeProperty()
  float_field = properties.FloatProperty()

  def to_json(self):
    return {'string_field': self.string_field,
            'date_field': self.date_field,
            'float_field': self.float_field}


class SampleController():
  """
      The controller for the Sample Model
  """
  @staticmethod
  def get_entities(entity_id=None):
    kwargs = {}
    if entity_id:
      kwargs = {'key_strs': [entity_id]}
    return SampleModel.retrieve(**kwargs)

  @staticmethod
  def validate_fields(**kwargs):
    # perform validation here
    return True, None

  @staticmethod
  def create_or_update_entity(sample_entity_id='', **kwargs):
    if sample_entity_id:
      sample_entity = SampleModel(key_str=sample_entity_id)
    else:
      sample_entity = SampleModel()

    validated, errors = SampleController.validate_fields(**kwargs)
    if validated:
      sample_entity.update(string_field=kwargs.get('string_field'),
                           date_field=kwargs.get('date_field'),
                           #  needs validation
                           float_field=kwargs.get('float_field'),
                           )
      sample_entity.put()
    return sample_entity, errors

  def delete_entity(self, sample_entity_id):
    sample_entity = SampleModel(key_str=sample_entity_id)
    sample_entity.delete()


class SampleAPI(BaseAPIHandler):
  controller = SampleController


class SampleAPI2(BaseAPIHandler):
  controller = SampleController


class SampleAPI3(BaseAPIHandler):
  controller = SampleController


class SampleAPI4(BaseAPIHandler):
  controller = SampleController


api_test_urls = Blueprint('test_api', __name__)
api_test_urls.add_url_rule(
    '/sampleapiwithnocontroller/',
    view_func=LazyView(
      'gaelib.tests.views.test_base_view.SampleAPINoController', 'sample_api_with_no_controller'),
    methods=['GET', 'POST'])

api_test_urls.add_url_rule(
    '/sampleapigetentities/',
    view_func=LazyView(
      'gaelib.tests.views.test_base_view.SampleAPI', 'sample_api_get_entities'),
    methods=['GET'])

api_test_urls.add_url_rule(
    '/sampleapicreateentity/',
    view_func=LazyView(
      'gaelib.tests.views.test_base_view.SampleAPI2', 'sample_api_create_entity'),
    methods=['POST'])

api_test_urls.add_url_rule(
    '/sampleapigetentity/<entity_id>',
    view_func=LazyView(
      'gaelib.tests.views.test_base_view.SampleAPI3', 'sample_api_get_entity'),
    methods=['GET'])

api_test_urls.add_url_rule(
    '/sampleapiupdateentity/<entity_id>',
    view_func=LazyView(
      'gaelib.tests.views.test_base_view.SampleAPI4', 'sample_api_update_entity'),
    methods=['POST'])

api_test_app = web.startup(parameter_logging=True,
                           client_logging=True)
api_test_app.register_blueprint(api_test_urls, name=f"gaelib_test_api")


class BaseAPIHandlerTestCase(BaseAuthenticatedUnitTestCase):
  app_for_test = api_test_app

  def setUp(self):
    super().setUp()

  def tearDown(self):
    super().tearDown()

  def test_when_no_controller_is_specified_get_request(self):
    """
        Testing when no controller is specified for Base API
    """
    self.add_user_entity(
        name='user1', email='a@b.com', uid='user1', client_user=True)
    response = self.client.get(
        '/sampleapiwithnocontroller/', headers=self.auth_headers())

    self.assertEqual(response.status_code, 500)
    self.assertEqual(response.json['error_message'], 'No controller defined')

  def test_when_no_controller_is_specified_post_request(self):
    """
        Testing when no controller is specified for Base API
    """
    self.add_user_entity(
        name='user1', email='a@b.com', uid='user1', client_user=True)
    response = self.client.post(
        f"/sampleapiwithnocontroller/",
        data=json.dumps(dict(string_field='s1')),
        headers=self.auth_headers(),
        content_type='application/json')
    self.assertEqual(response.status_code, 500)
    self.assertEqual(response.json['error_message'], 'No controller defined')

  def test_get_entities(self):
    """
        Testing a fetch of multiple entities
    """
    self.add_user_entity(
        name='user1', email='a@b.com', uid='user1', client_user=True)

    s1 = SampleModel(string_field='s1')
    s1.put()
    s2 = SampleModel(string_field='s2')
    s2.put()
    response = self.client.get(
        '/sampleapigetentities/', headers=self.auth_headers())

    self.assertEqual(response.status_code, 200)
    self.assertTrue(response.is_json)
    self.assertIn(response.json['entities'][0]['string_field'], ['s1', 's2'])
    self.assertIn(response.json['entities'][1]['string_field'], ['s1', 's2'])

  def test_get_entity(self):
    """
        Testing a fetch of single entity with id
    """
    self.add_user_entity(
        name='user1', email='a@b.com', uid='user1', client_user=True)

    s1 = SampleModel(string_field='s1')
    s1.put()
    s2 = SampleModel(string_field='s2')
    s2.put()

    response = self.client.get(
        f"/sampleapigetentity/{s1.key().id}", headers=self.auth_headers())
    self.assertEqual(response.status_code, 200)
    self.assertTrue(response.is_json)
    self.assertIn(response.json['string_field'], 's1')

    response = self.client.get(
        f"/sampleapigetentity/{s2.key().id}", headers=self.auth_headers())
    self.assertEqual(response.status_code, 200)
    self.assertTrue(response.is_json)
    self.assertEqual(response.json['string_field'], 's2')

  def test_get_entity_with_invalid_id(self):
    """
        Testing a fetch of single entity with id
    """
    self.add_user_entity(
        name='user1', email='a@b.com', uid='user1', client_user=True)

    response = self.client.get(
        f"/sampleapigetentity/1234abc", headers=self.auth_headers())
    self.assertEqual(response.status_code, 400)
    self.assertTrue(response.is_json)
    self.assertEqual(response.json['error_message'],
                     'Entity ID does not look numeric')

  def test_get_entity_with_nonexistent_entity_id(self):
    """
        Testing a fetch of single entity with id
    """
    self.add_user_entity(
        name='user1', email='a@b.com', uid='user1', client_user=True)

    response = self.client.get(
        f"/sampleapigetentity/12341234", headers=self.auth_headers())
    self.assertEqual(response.status_code, 400)
    self.assertTrue(response.is_json)
    self.assertEqual(response.json['error_message'],
                     'No entity with id 12341234')

  def test_create_entity_malformed_request(self):
    """
        Testing a fetch of single entity with id
    """
    self.add_user_entity(
        name='user1', email='a@b.com', uid='user1', client_user=True)

    response = self.client.post(
        f"/sampleapicreateentity/",
        data=dict(string_field='s1'),
        headers=self.auth_headers())
    self.assertEqual(response.status_code, 400)
    self.assertEqual(response.json['error_message'],
                     'POST request has no json content')

  def test_create_entity(self):
    """
        Testing a fetch of single entity with id
    """
    self.add_user_entity(
        name='user1', email='a@b.com', uid='user1', client_user=True)

    response = self.client.post(
        f"/sampleapicreateentity/",
        data=json.dumps(dict(string_field='s1')),
        headers=self.auth_headers(),
        content_type='application/json')
    self.assertEqual(response.status_code, 200)
    self.assertTrue(response.is_json)
    self.assertEqual(response.json['string_field'], 's1')

    response = self.client.get(
        '/sampleapigetentities/', headers=self.auth_headers())
    self.assertEqual(response.status_code, 200)
    self.assertTrue(response.is_json)
    self.assertIn(response.json['entities'][0]['string_field'], 's1')

  def test_update_entity(self):
    """
        Testing a fetch of single entity with id
    """
    self.add_user_entity(
        name='user1', email='a@b.com', uid='user1', client_user=True)
    s1 = SampleModel(string_field='s1')
    s1.put()
    response = self.client.get(
        f"/sampleapigetentity/{s1.key().id}", headers=self.auth_headers())
    self.assertEqual(response.status_code, 200)
    self.assertTrue(response.is_json)
    self.assertEqual(response.json['string_field'], 's1')

    response = self.client.post(
        f"/sampleapiupdateentity/{s1.key().id}",
        data=json.dumps(dict(string_field='s2')),
        headers=self.auth_headers(),
        content_type='application/json')
    self.assertEqual(response.status_code, 200)
    self.assertTrue(response.is_json)
    self.assertEqual(response.json['string_field'], 's2')

    response = self.client.get(
        f"/sampleapigetentity/{s1.key().id}", headers=self.auth_headers())
    self.assertEqual(response.status_code, 200)
    self.assertTrue(response.is_json)
    self.assertEqual(response.json['string_field'], 's2')
