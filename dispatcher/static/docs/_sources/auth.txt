==================
Authentication V.1
==================

Get an authentication token

GET
===

DESCRIPTION
    Retrieve authentication token to use aftermath in authenticated calls

URL STRUCTURE
    .. code-block:: guess

        https://www.example.com/api/<version>/auth

    :version: API version.
    :extension: json
    :param username: user to authenticate
    :param password: user's password

VERSIONS
    v1

ERRORS
    :200: Ok
    :403: Forbidden

EXAMPLES
    * `POST user and password with http`_
    * `POST user and password with curl`_
    * `POST wrong user and password with http`_


Examples
========

POST user and password with http
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    .. command-output:: http --pretty all -jv POST localhost:5000/api/v1/auth 'username=test' 'password=password'


POST user and password with curl
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    .. command-output:: curl -X POST -H 'Content-Type: application/json' -d '{  "username": "test", "password": "password" }' http://localhost:5000/api/v1/auth

POST wrong user and password with http
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    .. command-output:: http --pretty all -jv POST localhost:5000/api/v1/auth 'username=test' 'password=wrong_password'
        :shell:



