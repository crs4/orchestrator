Resources
=========

.. include:: isonum.txt

:Author: `Carlo Impagliazzo`
:Organization: `CRS4`_
:Version: |release|
:Date: 08/08/2013
:License: `GPL2 License`_

.. _CRS4: http://www.crs4.it
.. _GPL2 License: http://www.gnu.org/licenses/gpl-2.0.html

Contents
--------

.. toctree::
   :maxdepth: 2
   :titlesonly:
   :glob:

   api_v1
   dispatcher
   auth
   howto
   manutenzione

.. currentmodule:: dispatcher




General notes
=============

This is the REST API for orchestrator project, briefly called only `the orchestrator` for the latter use.
The orchestrator deals with several cloud providers using a LibCloud layer, it is able to respond in RESTful
with Flask.
The orchestrator is intended to be used in conjunction with Cistern project, `the brain`, where all decisions
are taken and where recipes are cooked.



URL template
------------

The URLs all follow pattern::

    /api/<version>/<resource>/<optional cloud_name>

Optional arguments are passed using a data json stream in the request.


Authentication
--------------

Authentication by token is implemented but actually not used

More information about how to use it here:
	.. toctree::
	   :maxdepth: 2
	   :titlesonly:
	   :glob:
	
	   auth


Data formatting
---------------

Only `JSON`_ is supported. The is reflected by an HTTP header of ``Content-Type:
application/json``. As per `rfc4627`_, JSON is always encoded Unicode with a
default encoding of UTF-8. So it is fine to include non-ASCII in the messages.

For maximum compatibility, normalize to http://unicode.org/reports/tr15 (Unicode
Normalization Form C) (NFC) before UTF-8 encoding.

Error handling
--------------

Errors are indicated using standard `HTTP error codes`_. Additional information
is usually included in the returned JSON. Specific meanings for the error codes
are given below.

Tools used
----------
This documentation use 2 tools to test and report codes:

- http ( httpie, from pip repository  )
- curl

Testing
-------
There is a test coverage to verify a proper behaviour of the middleware

To run tests:

    .. code-block:: guess
       
        cd tests
        python test_rest.py


TODO: list them

.. _HTTP error codes: http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html
.. _JSON: http://json.org
.. _rfc4627: http://www.ietf.org/rfc/rfc4627.txt


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

