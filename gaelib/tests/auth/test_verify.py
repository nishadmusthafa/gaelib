from gaelib.tests.auth.base import BaseAuthUnitTestCase
from gaelib.auth import verify


class VerifyTestCase(BaseAuthUnitTestCase):

  def setUp(self):
    super().setUp()
    self.mock_twilio_client()

  def test_generate_user_token(self):
    with self.app_for_test.test_request_context():
      self.app_for_test.preprocess_request()
      token = verify.generate_user_token(10)
      self.assertEqual(len(token), 10)
      self.assertTrue(token.islower())

  def test_get_user_token(self):
    url = 'admindashboard/login'
    headers = {
        'token': 'dummy_token'
    }
    with self.app_for_test.test_request_context(url, headers=headers):
      self.app_for_test.preprocess_request()
      token = verify.get_user_token()
      self.assertEqual(token, 'dummy_token')

  def test_get_user_token_when_no_token_is_sent(self):
    url = 'admindashboard/login'
    with self.app_for_test.test_request_context(url):
      self.app_for_test.preprocess_request()
      token = verify.get_user_token()
      self.assertIsNone(token)

  def test_verify_request_when_token_matches(self):
    user = self.add_user_entity(name='User', token='Token')
    with self.app_for_test.test_request_context():
      self.app_for_test.preprocess_request()
      user = verify.verify_request('Token')
      self.assertIsNotNone(user)
      self.assertEqual(user.name, 'User')

  def test_verify_request_when_token_does_not_match(self):
    user = self.add_user_entity(name='User', token='Token')
    with self.app_for_test.test_request_context():
      self.app_for_test.preprocess_request()
      user = verify.verify_request('Token_1')
      self.assertIsNone(user)
