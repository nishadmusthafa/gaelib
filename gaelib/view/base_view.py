"""
    This Module defines the BaseView Class
    which inherits View and has logger object
"""
from flask import g, jsonify, request
from flask.views import MethodView
from werkzeug.utils import import_string, cached_property
from werkzeug.exceptions import HTTPException


from gaelib.auth.decorators import auth_required
from gaelib.cron.decorators import cron_validate
from gaelib.tasks.decorators import cron_or_task_validate


class LazyView(object):
  """
      This class is used to import the view class
      when needed and prevent upfront import.
  """

  def __init__(self, import_name, view_function):
    self.__module__, self.__name__ = import_name.rsplit('.', 1)
    self.import_name = import_name
    self.view_function = view_function

  @cached_property
  def view(self):
    return import_string(self.import_name).as_view(self.view_function)

  def __call__(self, *args, **kwargs):
    return self.view(*args, **kwargs)


class BaseHttpHandler(MethodView):
  """ BaseView Class """

  def json_response(self, response_body, status, headers=None):
    if not isinstance(response_body, dict):
      g.app.logger.error("Response body not a dict, cannot convert to JSON")
      raise TypeError(
          "'\nThe View's return type must be a dictionary,'"
          "'but it was a {response_body.__class__.__name__}.'"
          .format(response_body=response_body))

    response_body = jsonify(response_body)
    # Need to see what the best way to do this
    # is
    response_body.status_code = status

    if headers is None:
      headers = {}
    headers["Content-Type"] = "application/json"
    return response_body, status, headers

  def json_error(self, error_message, status_code, warning_message=None):
    """
        Logs error messages, defines appropriate response_dict,
        and returns the same with status code.
    """
    if warning_message is not None:
      g.app.logger.warning(warning_message)

    g.app.logger.error(error_message)
    response_dict = {}
    response_dict["success"] = 0
    response_dict["error_message"] = error_message
    return self.json_response(response_dict, status_code)

  def json_success(self, response_dict=None, status_code=200):
    """
        Updates response_dict with success=1.
        Returns the same with status code.
    """
    if not response_dict:
      response_dict = {}
    response_dict["success"] = 1
    return self.json_response(response_dict, status_code)

  def validate_request_args(self):
    request_args = request.args.to_dict()
    self.missing_args = []

    for args in self.required_request_args:
      if args not in request_args:
        self.missing_args.append(args)

    if not self.missing_args:
      return True
    return False

  def validation_error(self):
    if self.missing_args:
      return self.json_error("Missing Arguments: " + str(self.missing_args), 200)


class BaseAPIHandler(BaseHttpHandler):
  controller = None
  decorators = [auth_required]

  def validate(self, entity_id):
    if not self.controller:
      error = "No controller defined"
      response, _, _ = self.json_error(error, 500)
      raise HTTPException(error, response)

    if request.method == 'POST' and not request.content_type == 'application/json':
      error = "POST request has no json content"
      response, _, _ = self.json_error(error, 400)
      raise HTTPException(error, response)
    if entity_id and not entity_id.isnumeric():
      error = "Entity ID does not look numeric"
      response, _, _ = self.json_error(error, 400)
      raise HTTPException(error, response)

    self.controller.validate_fields()

  def get(self, entity_id=''):
    self.validate(entity_id)
    if entity_id:
      try:
        entity = self.controller.get_entities(int(entity_id))[0]
      except IndexError:
        error = f"No entity with id {entity_id}"
        response, _, _ = self.json_error(error, 400)
        raise HTTPException(error, response)
      return self.json_response(entity.to_json(), 200)
    else:
      entities = self.controller.get_entities()
      entities = [entity.to_json() for entity in entities]
      return self.json_response({'entities': entities}, 200)

  def post(self, entity_id=''):
    self.validate(entity_id)
    kwargs = request.json
    entity_id = int(entity_id) if entity_id else ''
    entity, error = self.controller.create_or_update_entity(
      entity_id, **kwargs)
    if error:
      response, _, _ = self.json_error(error, 400)
      raise HTTPException(error, response)
    return self.json_response(entity.to_json(), 200)

  def delete(self, entity_id=''):
    self.validate(entity_id)
    if not entity_id:
      error = "Cannot delete an entity without entity id"
      response, _, _ = self.json_error(error, 400)
      raise HTTPException(error, response)
    try:
      self.controller.delete_entity(int(entity_id))
    except Exception as err:
      error = f"Unexpected {err=}, {type(err)=}"
      response, _, _ = self.json_error(error, 500)
      raise HTTPException(error, response)

    return self.json_success()


class BaseCronJobHandler(BaseHttpHandler):
  decorators = [cron_validate]


class BaseTaskHandler(BaseHttpHandler):
  decorators = [cron_or_task_validate]
