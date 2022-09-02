"""
    This module contains all defaults available for when
    the application importing the lib doesnt set values
"""
DASHBOARD_URL_PREFIX = 'admindashboard'
DASHBOARD_NOTIFICATION_ADMIN = False
ADMIN_DASHBOARD_POST_LOGIN_PAGE = ''
SIDEBAR_TEMPLATE = 'dashboard/sidebar'
PARAMETER_LOGGING = 'true'
SESSION_SECRET = 'lib_key'
# TODO: Move this to a more generic bucket name
DEFAULT_PROFILE_IMAGE = 'default_image.jpg'

# Twilio Auth Settings
VERIFICATION_SID = ''
ACCOUNT_SID = ''
AUTH_TOKEN = ''
TOKEN_LENGTH = 12

# Firebase Notifications Settings
AUTH0_JKWS_DOMAIN = ''
APNS_KEY_ID = ''
APNS_TEAM_ID = ''
APNS_AUTH_KEY_PATH = ''
IOS_BUNDLE_ID = ''

# Task Queues
TASK_QUEUE_STAGING = {
    'queue_name': 'TBD',
    'location': 'TBD'}
TASK_QUEUE_PROD = {
    'queue_name': 'TBD',
    'location': 'TBD'}

# Notification Task Constants
MAX_NOTIFICATION_TASK_RETRIES = 5