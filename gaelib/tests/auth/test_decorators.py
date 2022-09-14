from gaelib.tests.auth.base import BaseAuthUnitTestCase
from gaelib.auth.decorators import auth_required, verification_required, get_login_user, access_control
from gaelib.auth.models import User, UserRole
from mock import Mock
import json


class DecoratorsTestCase(BaseAuthUnitTestCase):

  def setUp(self):
    super().setUp()
    self.mock_get_user_id_and_token()
    self.mock_firebase_authorize()
    self.mock_get_user_token()
    self.mock_get_auth_type()

  def tearDown(self):
    self.get_user_id_and_token_patch.stop()
    self.firebase_authorize_patch.stop()
    self.get_user_token_patch.stop()
    self.get_auth_type_patch.stop()
    super().tearDown()

  def test_auth_required_when_user_id_is_not_present_and_id_token_is_not_present_and_is_dashboard_url(self):
    self.get_user_id_and_token.return_value = (
        None, None)
    with self.app_for_test.test_request_context('/admindashboard/login'):
      self.app_for_test.preprocess_request()
      decorated_func = auth_required(Mock(return_value="OK"))
      response = decorated_func()
      self.assertEqual(302, response.status_code)
      self.assertEqual('/admindashboard/login', response.location)

  def test_auth_required_when_user_id_is_not_present_and_id_token_is_present_and_is_dashboard_url(self):
    self.get_user_id_and_token.return_value = (
        None, 'test_token')
    with self.app_for_test.test_request_context('/admindashboard/login'):
      self.app_for_test.preprocess_request()
      decorated_func = auth_required(Mock(return_value="OK"))
      response = decorated_func()
      self.assertEqual(302, response.status_code)
      self.assertEqual('/admindashboard/login', response.location)

  def test_auth_required_when_user_id_is_present_and_id_token_is_not_present_and_is_dashboard_url(self):
    self.get_user_id_and_token.return_value = (
        'test_user', None)
    with self.app_for_test.test_request_context('/admindashboard/login'):
      self.app_for_test.preprocess_request()
      decorated_func = auth_required(Mock(return_value="OK"))
      response = decorated_func()
      self.assertEqual(302, response.status_code)
      self.assertEqual('/admindashboard/login', response.location)

  def test_auth_required_when_user_id_is_present_and_id_token_is_present_and_is_dashboard_url(self):
    return_value = {
        'sub': 'sub',
        'name': 'user',
        'email': 'email@abc'
    }
    self.firebase_authorize.return_value = return_value
    self.get_user_id_and_token.return_value = (
        'sub', 'test_token')
    self.get_auth_type.return_value = 'firebase'
    with self.app_for_test.test_request_context('/admindashboard/login'):
      self.app_for_test.preprocess_request()
      user = self.add_user_entity(uid='sub', name='user')
      decorated_func = auth_required(Mock(return_value="OK"))
      response = decorated_func()
      self.assertEqual("OK", response)

  def test_auth_required_when_user_id_is_not_present_and_id_token_is_not_present_and_not_is_dashboard_url(self):
    self.get_user_id_and_token.return_value = (
        None, None)
    with self.app_for_test.test_request_context():
      decorated_func = auth_required(Mock(return_value="OK"))
      response = decorated_func()
      data = json.loads(response[0].get_data(as_text=True))
      self.assertEqual('UNAUTHORIZED USER', data['error_message'])

  def test_auth_required_when_user_id_is_not_present_and_id_token_is_present_and_is_not_dashboard_url(self):
    self.get_user_id_and_token.return_value = (
        None, 'test_token')
    with self.app_for_test.test_request_context():
      decorated_func = auth_required(Mock(return_value="OK"))
      response = decorated_func()
      data = json.loads(response[0].get_data(as_text=True))
      self.assertEqual('UNAUTHORIZED USER', data['error_message'])

  def test_auth_required_when_user_id_is_present_and_id_token_is_not_present_and_is_not_dashboard_url(self):
    self.get_user_id_and_token.return_value = (
        'test_user', None)
    with self.app_for_test.test_request_context():
      self.app_for_test.preprocess_request()
      decorated_func = auth_required(Mock(return_value="OK"))
      response = decorated_func()
      data = json.loads(response[0].get_data(as_text=True))
      self.assertEqual('UNAUTHORIZED TOKEN', data['error_message'])

  def test_auth_required_when_user_id_is_present_and_id_token_is_present_and_is_not_dashboard_url(self):
    return_value = {
        'sub': 'sub',
        'name': 'user',
        'email': 'email@abc'
    }
    self.firebase_authorize.return_value = return_value
    with self.app_for_test.test_request_context():
      self.app_for_test.preprocess_request()
      self.get_user_id_and_token.return_value = (
          'test_user', 'test_token')
      decorated_func = auth_required(Mock(return_value="OK"))
      response = decorated_func()

  def test_verification_required_when_token_is_absent_and_is_dashboard_url(self):
    self.get_user_token.return_value = (None)
    with self.app_for_test.test_request_context('/admindashboard/login'):
      self.app_for_test.preprocess_request()
      decorated_func = verification_required(Mock(return_value="OK"))
      response = decorated_func()
      self.assertEqual(302, response.status_code)
      self.assertEqual('/admindashboard/login', response.location)

  def test_verification_required_when_token_is_present_and_is_not_dashboard_url(self):
    self.get_user_token.return_value = ('test_token')
    decorated_func = verification_required(Mock(return_value="OK"))
    with self.app_for_test.test_request_context():
      self.app_for_test.preprocess_request()
      response = decorated_func()
      data = json.loads(response[0].get_data(as_text=True))
      self.assertEqual('Unauthorised login for web request found',
                       data['error_message'])

  def test_verification_required_when_token_is_absent_and_is_not_dashboard_url(self):
    self.get_user_token.return_value = (None)
    decorated_func = verification_required(Mock(return_value="OK"))
    with self.app_for_test.test_request_context():
      self.app_for_test.preprocess_request()
      response = decorated_func()
      data = json.loads(response[0].get_data(as_text=True))
      self.assertEqual('USER TOKEN NOT FOUND IN HEADERS',
                       data['error_message'])

  def test_verification_required_when_token_is_present_and_is_dashboard_url_and_user_with_token_is_present(self):
    self.get_user_token.return_value = ('test_token')
    decorated_func = verification_required(Mock(return_value="OK"))
    with self.app_for_test.test_request_context('/admindashboard/login'):
      self.app_for_test.preprocess_request()
      user = self.add_user_entity(token='test_token')
      response = decorated_func()
      self.assertEqual("OK", response)

  def test_verification_required_when_token_is_present_and_is_not_dashboard_url_and_user_with_token_is_present(self):
    self.get_user_token.return_value = ('test_token')
    decorated_func = verification_required(Mock(return_value="OK"))
    with self.app_for_test.test_request_context('/admindashboard/login'):
      self.app_for_test.preprocess_request()
      user = self.add_user_entity(token='test_token')
      response = decorated_func()
      self.assertEqual("OK", response)

  def test_verification_required_when_token_is_present_and_is_dashboard_url_and_user_with_token_is_absent(self):
    self.get_user_token.return_value = ('test_token')
    decorated_func = verification_required(Mock(return_value="OK"))
    with self.app_for_test.test_request_context('/admindashboard/login'):
      self.app_for_test.preprocess_request()
      response = decorated_func()
      self.assertEqual(302, response.status_code)
    self.assertEqual('/admindashboard/login', response.location)

  def test_login_user_when_auth_type_is_firebase(self):
    self.get_auth_type.return_value = 'firebase'
    self.get_user_token.return_value = ('token_1')
    self.get_user_id_and_token.return_value = ('id_2', None)
    with self.app_for_test.test_request_context():
      user1 = User(uid='id_1', token='token_1')
      user2 = User(uid='id_2', token='token_2')
      user1.put()
      user2.put()
      self.app_for_test.preprocess_request()
      response = get_login_user()
      self.assertEqual(user2.key().id, response.key().id)

  def test_login_user_when_auth_type_is_auth0(self):
    self.get_auth_type.return_value = 'auth0'
    self.get_user_token.return_value = ('token_1')
    self.get_user_id_and_token.return_value = ('id_2', None)
    with self.app_for_test.test_request_context():
      user1 = User(uid='id_1', token='token_1')
      user2 = User(uid='id_2', token='token_2')
      user1.put()
      user2.put()
      self.app_for_test.preprocess_request()
      response = get_login_user()
      self.assertEqual(user2.key().id, response.key().id)

  def test_login_user_when_auth_type_is_verify(self):
    self.get_auth_type.return_value = 'verify'
    self.get_user_token.return_value = ('token_1')
    self.get_user_id_and_token.return_value = ('id_2', None)
    with self.app_for_test.test_request_context():
      user1 = User(uid='id_1', token='token_1')
      user2 = User(uid='id_2', token='token_2')
      user1.put()
      user2.put()
      self.app_for_test.preprocess_request()
      response = get_login_user()
      self.assertEqual(user1.key().id, response.key().id)

  def test_access_control_when_user_is_staff_member_and_auth_type_is_firebase(self):
    self.get_auth_type.return_value = 'firebase'
    self.get_user_id_and_token.return_value = ('id_1', None)
    decorated_func = access_control(role=UserRole.STAFF)
    with self.app_for_test.test_request_context():
      self.app_for_test.preprocess_request()
      user = self.add_user_entity(role=1, uid='id_1')
      decorated_func_1 = decorated_func(Mock(return_value="OK"))
      response = decorated_func_1()
      self.assertEqual("OK", response)  

  def test_access_control_when_user_is_staff_member_and_auth_type_is_auth0(self):
    self.get_auth_type.return_value = 'auth0'
    self.get_user_id_and_token.return_value = ('id_1', None)
    decorated_func = access_control(role=UserRole.STAFF)
    with self.app_for_test.test_request_context():
      self.app_for_test.preprocess_request()
      user = self.add_user_entity(role=1, uid='id_1')
      decorated_func_1 = decorated_func(Mock(return_value="OK"))
      response = decorated_func_1()
      self.assertEqual("OK", response)

  def test_access_control_when_user_is_staff_member_and_auth_type_is_verify(self):
    self.get_auth_type.return_value = 'verify'
    self.get_user_token.return_value = ('token_1')
    decorated_func = access_control(role=UserRole.STAFF)
    with self.app_for_test.test_request_context():
      self.app_for_test.preprocess_request()
      user = self.add_user_entity(role=1, token='token_1')
      decorated_func_1 = decorated_func(Mock(return_value="OK"))
      response = decorated_func_1()
      self.assertEqual("OK", response)

  def test_access_control_when_user_is_non_staff_member_and_auth_type_is_firebase(self):
    self.get_auth_type.return_value = 'firebase'
    self.get_user_id_and_token.return_value = ('id_1', None)
    decorated_func = access_control(role=UserRole.STAFF)
    with self.app_for_test.test_request_context():
      self.app_for_test.preprocess_request()
      user = self.add_user_entity(role=0, uid='id_1')
      decorated_func_1 = decorated_func(Mock(return_value="OK"))
      response = decorated_func_1()
      data = json.loads(response[0].get_data(as_text=True))
      self.assertEqual('UNAUTHORIZED ACCESS',
                        data['error_message'])

  def test_access_control_when_user_is_non_staff_member_and_auth_type_is_auth0(self):
    self.get_auth_type.return_value = 'auth0'
    self.get_user_id_and_token.return_value = ('id_1', None)
    decorated_func = access_control(role=UserRole.STAFF)
    with self.app_for_test.test_request_context():
      self.app_for_test.preprocess_request()
      user = self.add_user_entity(role=0, uid='id_1')
      decorated_func_1 = decorated_func(Mock(return_value="OK"))
      response = decorated_func_1()
      data = json.loads(response[0].get_data(as_text=True))
      self.assertEqual('UNAUTHORIZED ACCESS',
                        data['error_message'])

  def test_access_control_when_user_is_non_staff_member_and_auth_type_is_verify(self):
    self.get_auth_type.return_value = 'verify'
    self.get_user_token.return_value = ('token_1')
    decorated_func = access_control(role=UserRole.STAFF)
    with self.app_for_test.test_request_context():
      self.app_for_test.preprocess_request()
      user = self.add_user_entity(role=0, token='token_1')
      decorated_func_1 = decorated_func(Mock(return_value="OK"))
      response = decorated_func_1()
      data = json.loads(response[0].get_data(as_text=True))
      self.assertEqual('UNAUTHORIZED ACCESS',
                        data['error_message'])

  def test_access_control_when_user_does_not_exist_and_auth_type_is_firebase(self):
    self.get_auth_type.return_value = 'firebase'
    self.get_user_id_and_token.return_value = ('id_1', None)
    decorated_func = access_control(role=UserRole.STAFF)
    with self.app_for_test.test_request_context():
      self.app_for_test.preprocess_request()
      decorated_func_1 = decorated_func(Mock(return_value="OK"))
      response = decorated_func_1()
      data = json.loads(response[0].get_data(as_text=True))
      self.assertEqual('UNAUTHORIZED ACCESS',
                        data['error_message'])

  def test_access_control_when_user_does_not_exist_and_auth_type_is_auth0(self):
    self.get_auth_type.return_value = 'auth0'
    self.get_user_id_and_token.return_value = ('id_1', None)
    decorated_func = access_control(role=UserRole.STAFF)
    with self.app_for_test.test_request_context():
      self.app_for_test.preprocess_request()
      decorated_func_1 = decorated_func(Mock(return_value="OK"))
      response = decorated_func_1()
      data = json.loads(response[0].get_data(as_text=True))
      self.assertEqual('UNAUTHORIZED ACCESS',
                        data['error_message'])

  def test_access_control_when_user_does_not_exist_and_auth_type_is_verify(self):
    self.get_auth_type.return_value = 'verify'
    self.get_user_token.return_value = ('token_1')
    decorated_func = access_control(role=UserRole.STAFF)
    with self.app_for_test.test_request_context():
      self.app_for_test.preprocess_request()
      decorated_func_1 = decorated_func(Mock(return_value="OK"))
      response = decorated_func_1()
      data = json.loads(response[0].get_data(as_text=True))
      self.assertEqual('UNAUTHORIZED ACCESS',
                        data['error_message'])
