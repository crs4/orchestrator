# -*- coding:utf-8 -*-

# Copyright 2015 CRS4
# All Rights Reserved.
#
#    Licensed under the GNU General Public License, version 2 (the "License");
#    you may not use this file except in compliance with the License. You may
#    obtain a copy of the License at
#
#         http://www.gnu.org/licenses/gpl-2.0.html
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


"""
    :copyright: |copy| 2015 by CRS4.
    :license: gpl-2, see License for more details.

    Various helpers, custom exceptions, login mechanism and wrappers

"""

import requests
import logging
import BaseHTTPServer  # For HTTP codes.
from werkzeug.exceptions import HTTPException

from flask import request, current_app, _request_ctx_stack, json, jsonify
from simplejson import JSONDecodeError

from flask.ext import security
from flask.ext.security import decorators
from flask.ext.principal import Identity, identity_changed
from flask.ext.login import current_user

from functools import wraps
#from dispatcher.formats import render_message
from decorator import decorator


HTTP_CODES = BaseHTTPServer.BaseHTTPRequestHandler.responses
LOG = logging.getLogger(__name__)


class MiddlewareException(HTTPException):
    """
    Cancel abortion of the current task and return with
    the given message and error code.
    """
    def __init__(self, message, format='json', state='success',
                 code=200, url=None):
        self.message = message
        LOG.error("MWException(%s %s): %s" % (state, code, message))
        #self.response = render_message(request, message,
        #         format, state=state, code=code, url=url)
        self.response = make_response(status_code=code, status=state,
                                      url=url, message=message)

    def __str__(self):
        return self.message

    def get_response(self, environ):
        return self.response


def not_implemented():
    """
    Quick function to reply with a Not implemented response
    """
    raise MiddlewareException('Not implemented',
                              state='error', code=501)


def make_response(status=None, status_code=200, other_headers=None, **kwargs):
    """
    Return a suitable HTML or JSON error message response.
    """
    short_message, long_message = HTTP_CODES.get(status_code, ('', ''))
    if status is None:
        if str(status_code).startswith('2'):
            status = 'ok'
        else:
            status = 'error'
    result = dict(
        status=status,
        status_code=status_code)
    if status == 'error':
        result['status_short_message'] = short_message
        result['status_long_message'] = long_message
    result.update(kwargs)
    if result.get('url', '') is None:
        empty_url = result.pop('url', '')
    response = jsonify(result)
    response.status_code = status_code
    if other_headers:
        response.headers.extend(other_headers)
    return response


# authentication wrapper ( embed some flask-security methods )

def _check_token():
    """
    Check token from request object, reply with a boolean to validate it.
    """
    header_key = security.core._security.token_authentication_header
    args_key = security.core._security.token_authentication_key
    header_token = request.headers.get(header_key, None)
    token = request.args.get(args_key, header_token)
    if request.json:
        token = request.json.get(args_key, token)
    serializer = security.core._security.remember_token_serializer
    try:
        data = serializer.loads(token)
    except Exception as e:
        return False
    user = security.core._security.datastore.find_user(username=data[0])
    token = data[1]
    encrypted_tokens = set([security.utils.md5(t.token) for t in user.tokens
                           if t.active])
    if token in encrypted_tokens:
        app = current_app._get_current_object()
        _request_ctx_stack.top.user = user
        identity_changed.send(app, identity=Identity(user.id))
        return True


def validate_json(validate_function, default=None):
    """Decorator to validate and marshal the incoming JSON.

    Sets request.json to the value returned from calling validate_function on
    request.json (or default() if request.json is None). If this raises
    an exception then the call stack is terminated early with a
    :func:`MiddlewareException` exception

    If request.json is None then default() is used. Note that
      1) default is a callable which must create the default value
         (to avoid accidental re-use of mutables)
      2) the result is still passed through the validate_function
         (to ensure the invariant holds)

    """
    @decorator
    def validate_with_validate_function(f, *args, **kwargs):
        try:
            data = request.data or "{}"
            input_json = json.loads(data)
        except JSONDecodeError as e:
            raise MiddlewareException("Malformed JSON stream",
                                      state='error',
                                      code=400)

        # input_json = request.json
        if input_json is None and callable(default):
            input_json = default()
        try:
            # request.json = validate_function(input_json)
            request.data = validate_function(input_json)
        except Exception as e:
            message = "Some key doesn't validate the schema - %s" % (str(e))
            raise MiddlewareException(message, state='error', code=400)
        return f(*args, **kwargs)
    return validate_with_validate_function


def auth_required(*auth_methods):
    """
    Adaptation for security.decorators.auth_required
    """
    login_mechanisms = {
        'token': lambda: _check_token(),
        'basic': lambda: decorators._check_http_auth(),
        'session': lambda: current_user.is_authenticated()
    }

    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            """ decorator farm """
            mechanisms = [login_mechanisms.get(method)
                          for method in auth_methods]
            for mechanism in mechanisms:
                if mechanism and mechanism():
                    return fn(*args, **kwargs)
            raise MiddlewareException('Forbidden',
                                      state='error', code=403)
        return decorated_view
    return wrapper


class HTTPConnection(object):
    """
    Class to make connections and deal with web services
    """

    def __init__(self, server, port, api_version, headers=None):
        self.server = server
        self.port = port
        self.api_v = api_version
        self.api_v_url = "/api/" + self.api_v
        self.server_url = 'http://%s:%s' % (server, port)
        self.headers = headers or {'content-type': 'application/json'}
        self.last_status = None
        self.last_message = None

    def get_page(self, url, method='get', payload=None):
        """
        Make a generic call with a json response

        + :attr:`url` is the relative url to contact, protocol and servername\
                is added on the fly with what has been specified on\
                initialization of the object
        + :attr:`kwargs` is an attribute of optional key/value pairs, should be:
            * :attr:`method`, the way to contact the server, default is 'get',
            * :attr:`payload`, is a dictionary structure containing additional\
            payload useful to the request

        """

        url = self.server_url + self.api_v_url + url
        try:
            r = requests.__dict__[method](url, data=json.dumps(payload),
                                          headers=self.headers)

            self.last_status = r.status_code
            res = r.json()
            try:
                self.last_message = res
            except:
                pass

        except Exception as e:
            #print str(e)
            #LOG.error("ORCHE is down")
            MiddlewareException('the host %s is down' % self.server,
                                state='error', code=503)
            res = {}
        return res


def get_a_caller(app_context):
    """
    With an app_context ( to access the settings data ) this routines will
    spawn a caller object to make HTTP calls.
    Settings are CISTERN_* data
    """
    app = app_context
    server = app.config['CISTERN_HOST']
    port = app.config['CISTERN_PORT']
    api_v = app.config['CISTERN_API']
    caller = HTTPConnection(server, port, api_v)
    return caller


# from http://flask.pocoo.org/snippets/56/



# http code reminder:
# http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html
# 201 Created
# 202 Accepted
# 301 Moved Permanently
# 400 Bad Request
# 401 Unauthorized
# 403 Forbidden
# 408 Request Timeout
# 500 Internal Server Error
# 501 Not Implemented
# 503 Service Unavailable
