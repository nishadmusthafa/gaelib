from gaelib.tests.auth.base import BaseAuthUnitTestCase
from gaelib.auth import auth
import base64
from flask import session
from werkzeug.http import dump_cookie


class AuthTestCase(BaseAuthUnitTestCase):

  def test_user_id_and_token_for_get_user_id_and_token_when_authorization_is_present_and_session_is_present(self):
    headers = {
        'Authorization': "Basic {}".format(base64.b64encode(b"user:pass").decode("utf8"))
    }
    with self.app_for_test.test_request_context(headers=headers):
      session['gae_uid'] = 'gae_uid'
      session['gae_token'] = 'gae_token'
      self.app_for_test.preprocess_request()
      user_id, id_token = auth.get_user_id_and_token()
      self.assertEqual(user_id, 'user')
      self.assertEqual(id_token, 'pass')

  def test_user_id_and_token_for_get_user_id_and_token_when_authorization_is_present_and_session_is_not_present(self):
    headers = {
        'Authorization': "Basic {}".format(base64.b64encode(b"user:pass").decode("utf8"))
    }
    with self.app_for_test.test_request_context(headers=headers):
      self.app_for_test.preprocess_request()
      user_id, id_token = auth.get_user_id_and_token()
      self.assertEqual(user_id, 'user')
      self.assertEqual(id_token, 'pass')

  def test_user_id_and_token_for_get_user_id_and_token_when_authorization_is_not_present_and_session_is_present(self):

    with self.app_for_test.test_request_context():
      session['gae_uid'] = 'gae_uid'
      session['gae_token'] = 'gae_token'
      self.app_for_test.preprocess_request()
      user_id, id_token = auth.get_user_id_and_token()
      self.assertEqual(user_id, 'gae_uid')
      self.assertEqual(id_token, 'gae_token')

  def test_user_id_and_token_for_get_user_id_and_token_when_authorization_is_not_present_and_session_is_not_present(self):

    with self.app_for_test.test_request_context():

      self.app_for_test.preprocess_request()
      user_id, id_token = auth.get_user_id_and_token()
      self.assertIsNone(user_id)
      self.assertIsNone(id_token)

  def test_user_id_and_token_for_get_user_id_and_token_when_authorization_is_present_and_firebaseaccesstoken_is_present_and_is_dashboard_url(self):
    cookie = dump_cookie("firebaseAccessToken", 'Cookie_value')
    headers = {
        'Authorization': "Basic {}".format(base64.b64encode(b"user:pass").decode("utf8")),
        'COOKIE': cookie
    }
    url = 'admindashboard/login'
    with self.app_for_test.test_request_context(url, headers=headers):
      self.app_for_test.preprocess_request()
      user_id, id_token = auth.get_user_id_and_token()
      self.assertEqual(user_id, 'user')
      self.assertEqual(id_token, 'Cookie_value')

  def test_user_id_and_token_for_get_user_id_and_token_when_authorization_is_present_and_firebaseaccesstoken_is_present_and_is_not_dashboard_url(self):
    cookie = dump_cookie("firebaseAccessToken", 'Cookie_value')
    headers = {
        'Authorization': "Basic {}".format(base64.b64encode(b"user:pass").decode("utf8")),
        'COOKIE': cookie
    }
    with self.app_for_test.test_request_context(headers=headers):
      self.app_for_test.preprocess_request()
      user_id, id_token = auth.get_user_id_and_token()
      self.assertEqual(user_id, 'user')
      self.assertEqual(id_token, 'pass')

  def test_user_id_and_token_for_get_user_id_and_token_when_authorization_is_not_present_and_firebaseaccesstoken_is_present_and_is_dashboard_url(self):
    cookie = dump_cookie("firebaseAccessToken", 'Cookie_value')
    headers = {
        'COOKIE': cookie
    }
    url = 'admindashboard/login'
    with self.app_for_test.test_request_context(url, headers=headers):
      self.app_for_test.preprocess_request()
      user_id, id_token = auth.get_user_id_and_token()
      self.assertEqual(user_id, None)
      self.assertEqual(id_token, 'Cookie_value')

  def test_user_id_and_token_for_get_user_id_and_token_when_session_is_present_and_firebaseaccesstoken_is_present_and_is_dashboard_url(self):
    cookie = dump_cookie("firebaseAccessToken", 'Cookie_value')
    headers = {
        'COOKIE': cookie
    }
    url = 'admindashboard/login'
    with self.app_for_test.test_request_context(url, headers=headers):
      session['gae_uid'] = 'gae_uid'
      session['gae_token'] = 'gae_token'
      self.app_for_test.preprocess_request()
      user_id, id_token = auth.get_user_id_and_token()
      self.assertEqual(user_id, 'gae_uid')
      self.assertEqual(id_token, 'Cookie_value')

  def test_user_id_and_token_for_get_user_id_and_token_when_session_is_present_and_firebaseaccesstoken_is_present_and_is_not_dashboard_url(self):
    cookie = dump_cookie("firebaseAccessToken", 'Cookie_value')
    headers = {
        'COOKIE': cookie
    }
    with self.app_for_test.test_request_context(headers=headers):
      session['gae_uid'] = 'gae_uid'
      session['gae_token'] = 'gae_token'
      self.app_for_test.preprocess_request()
      user_id, id_token = auth.get_user_id_and_token()
      self.assertEqual(user_id, 'gae_uid')
      self.assertEqual(id_token, 'gae_token')

  def test_user_id_and_token_for_get_user_id_and_token_when_session_is_not_present_and_firebaseaccesstoken_is_present_and_is_dashboard_url(self):
    cookie = dump_cookie("firebaseAccessToken", 'Cookie_value')
    headers = {
        'COOKIE': cookie
    }
    url = 'admindashboard/login'
    with self.app_for_test.test_request_context(url, headers=headers):
      self.app_for_test.preprocess_request()
      user_id, id_token = auth.get_user_id_and_token()
      self.assertEqual(user_id, None)
      self.assertEqual(id_token, 'Cookie_value')

  def test_auth_type_when_auth_type_is_present_in_args(self):
    url = 'abc?auth_type=test_auth'
    with self.app_for_test.test_request_context(url):
      self.app_for_test.preprocess_request()
      auth_type = auth.get_auth_type()
      self.assertEqual(auth_type, 'test_auth')

  def test_auth_type_when_auth_type_is_present_in_json(self):
    with self.app_for_test.test_request_context(json={"auth_type": "test_auth"}):
      self.app_for_test.preprocess_request()
      auth_type = auth.get_auth_type()
      self.assertEqual(auth_type, 'test_auth')

  def test_auth_type_when_auth_type_is_present_in_form(self):
    with self.app_for_test.test_request_context(data={"auth_type": "test_auth"}):
      self.app_for_test.preprocess_request()
      auth_type = auth.get_auth_type()
      self.assertEqual(auth_type, 'test_auth')

  # def test_auth_type_for_get_user_id_and_token_when_auth_type_is_present_in_params(self):
  #   cookie = dump_cookie("auth_type", 'test_auth')
  #   headers = {
  #       'COOKIE': cookie
  #   }
  #   with self.app_for_test.test_request_context(data={"auth_type": "test_auth"}, method='POST'):
  #     self.app_for_test.preprocess_request()
  #     _, _, auth_type, _ = auth.get_user_id_and_token()
  #     self.assertEqual(auth_type, 'test_auth')

  def test_auth_type_when_auth_type_is_not_present(self):
    with self.app_for_test.test_request_context():
      self.app_for_test.preprocess_request()
      auth_type = auth.get_auth_type()
      self.assertEqual(auth_type, 'firebase')

  def test_auth0_authorize_for_no_exception(self):
    return_value = self.get_mock_response(json_data={'keys': []})
    with self.app_for_test.test_request_context():
      self.app_for_test.preprocess_request()
      self.mock_requests_get()
      self.mock_jwt_get_unverified_header()
      self.mock_jwt_decode()
      self.requests_get.return_value = return_value
      auth_obj = auth.Auth('token')
      payload = auth_obj.auth0_authorize()

  def test_authorize_login_request_when_auth_type_is_absent(self):
    return_value = {
        'sub': 'sub',
        'name': 'user',
        'email': 'email@abc'
    }
    with self.app_for_test.test_request_context():
      self.app_for_test.preprocess_request()
      self.mock_firebase_authorize()
      self.firebase_authorize.return_value = return_value
      auth_obj = auth.Auth('token')
      claims = auth_obj.authorize_login_request()
      self.assertIsNotNone(claims)
      self.assertEqual(3, len(claims))
      self.assertEqual('sub', claims['sub'])
      self.assertEqual('user', claims['name'])
      self.assertEqual('email@abc', claims['email'])

  def test_authorize_login_request_when_auth_type_is_firebase(self):
    return_value = {
        'sub': 'sub',
        'name': 'user',
        'email': 'email@abc'
    }
    with self.app_for_test.test_request_context():
      self.app_for_test.preprocess_request()
      self.mock_firebase_authorize()
      self.firebase_authorize.return_value = return_value
      auth_obj = auth.Auth('token')
      claims = auth_obj.authorize_login_request(auth_type='firebase')
      self.assertIsNotNone(claims)
      self.assertEqual(3, len(claims))
      self.assertEqual('sub', claims['sub'])
      self.assertEqual('user', claims['name'])
      self.assertEqual('email@abc', claims['email'])

  def test_authorize_login_request_when_auth_type_is_auth0(self):
    return_value = {
        'sub': 'sub',
        'name': 'user',
        'email': 'email@abc'
    }
    with self.app_for_test.test_request_context():
      self.app_for_test.preprocess_request()
      self.mock_auth0_authorize()
      self.auth0_authorize.return_value = return_value
      auth_obj = auth.Auth('token')
      claims = auth_obj.authorize_login_request(auth_type='auth0')
      self.assertIsNotNone(claims)
      self.assertEqual(3, len(claims))
      self.assertEqual('sub', claims['sub'])
      self.assertEqual('user', claims['name'])
      self.assertEqual('email@abc', claims['email'])

  def test_authorize_request_when_auth_type_is_absent_and_claimed_user_id_is_same_as_user_id(self):
    return_value = {
        'sub': 'sub',
        'name': 'user',
        'email': 'email@abc'
    }
    with self.app_for_test.test_request_context():
      self.app_for_test.preprocess_request()
      self.mock_firebase_authorize()
      self.firebase_authorize.return_value = return_value
      auth_obj = auth.Auth('token')
      auth_obj.user_id = 'sub'
      claims = auth_obj.authorize_request()
      self.assertIsNotNone(claims)
      self.assertEqual(3, len(claims))
      self.assertEqual('sub', claims['sub'])
      self.assertEqual('user', claims['name'])
      self.assertEqual('email@abc', claims['email'])

  def test_authorize_request_when_auth_type_is_absent_and_claimed_user_id_is_not_same_as_user_id(self):
    return_value = {
        'sub': 'sub',
        'name': 'user',
        'email': 'email@abc'
    }
    with self.app_for_test.test_request_context():
      self.app_for_test.preprocess_request()
      self.mock_firebase_authorize()
      self.firebase_authorize.return_value = return_value
      auth_obj = auth.Auth('token')
      auth_obj.user_id = 'sub_1'
      claims = auth_obj.authorize_request()
      self.assertEqual(len(claims), 0)

  def test_authorize_request_when_auth_type_is_firebase_and_claimed_user_id_is_same_as_user_id(self):
    return_value = {
        'sub': 'sub',
        'name': 'user',
        'email': 'email@abc'
    }
    with self.app_for_test.test_request_context():
      self.app_for_test.preprocess_request()
      self.mock_firebase_authorize()
      self.firebase_authorize.return_value = return_value
      auth_obj = auth.Auth('token')
      auth_obj.user_id = 'sub'
      claims = auth_obj.authorize_request(auth_type='firebase')
      self.assertIsNotNone(claims)
      self.assertEqual(3, len(claims))
      self.assertEqual('sub', claims['sub'])
      self.assertEqual('user', claims['name'])
      self.assertEqual('email@abc', claims['email'])

  def test_authorize_request_when_auth_type_is_firebase_and_claimed_user_id_is_not_same_as_user_id(self):
    return_value = {
        'sub': 'sub',
        'name': 'user',
        'email': 'email@abc'
    }
    with self.app_for_test.test_request_context():
      self.app_for_test.preprocess_request()
      self.mock_firebase_authorize()
      self.firebase_authorize.return_value = return_value
      auth_obj = auth.Auth('token')
      auth_obj.user_id = 'sub_1'
      claims = auth_obj.authorize_request(auth_type='firebase')
      self.assertEqual(len(claims), 0)

  def test_authorize_request_when_auth_type_is_auth0_and_claimed_user_id_is_same_as_user_id(self):
    return_value = {
        'sub': 'sub',
        'name': 'user',
        'email': 'email@abc'
    }
    with self.app_for_test.test_request_context():
      self.app_for_test.preprocess_request()
      self.mock_auth0_authorize()
      self.auth0_authorize.return_value = return_value
      auth_obj = auth.Auth('token')
      auth_obj.user_id = 'sub'
      claims = auth_obj.authorize_request(auth_type='auth0')
      self.assertIsNotNone(claims)
      self.assertEqual(3, len(claims))
      self.assertEqual('sub', claims['sub'])
      self.assertEqual('user', claims['name'])
      self.assertEqual('email@abc', claims['email'])

  def test_authorize_request_when_auth_type_is_auth0_and_claimed_user_id_is_not_same_as_user_id(self):
    return_value = {
        'sub': 'sub',
        'name': 'user',
        'email': 'email@abc'
    }    
    with self.app_for_test.test_request_context():
      self.app_for_test.preprocess_request()
      self.mock_auth0_authorize()
      self.auth0_authorize.return_value = return_value
      auth_obj = auth.Auth('token')
      auth_obj.user_id = 'sub_1'
      claims = auth_obj.authorize_request(auth_type='auth0')
      self.assertEqual(len(claims), 0)

  # TODO: auth0_authorize
  # TODO: firebase_authorize
