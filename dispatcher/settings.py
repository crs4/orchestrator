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

    Description
    ~~~~~~~~~~~

    Settings file, used to configure the main Flask app.

    This configuration provides three classes:

    + :class:`Config` defines attributes for a global behaviour
    + :class:`ProductionConfig` defines and set attributes to use only in a\
            stable environment ( like a loggin level not pushed to extreme )
    + :class:`DevelopmentConfig` defines and set attrs only for a dev environment

    There is also another class, :class:`CloudConfig` contains credentials and\
    url of the favorite cloud providers

"""

from dispatcher.lib import Provider

LOGGIN_LEVEL = {'DEBUG': 10,
                'WARN': 30,
                'INFO': 20
                }


class Config(object):
    """
    Main configuration class, is intended to be used as a base class to
    inheritate
    """
    # WHERE THE WEB SERVICE SHOULD LISTEN
    HOST = '0.0.0.0'
    PORT = 5070

    SECRET_KEY = 'dev key pass foobar 1 2 3'

    #  ### DB CONNECTION
    SQLALCHEMY_DATABASE_URI = 'sqlite:////home/achmed/test/log_and_db/auth.db'

    LOG_FILE = "/home/achmed/test/log_and_db/middleware.log"
    LOG_LEVEL = LOGGIN_LEVEL['DEBUG']

    # security
    SECURITY_REGISTERABLE = False
    SECURITY_URL_PREFIX = "/api/v1/auth"
    SECURITY_TOKEN_AUTHENTICATION_HEADER = "X-Auth-Token"
                                         #Defaults: Authentication-Token
    SECURITY_TOKEN_AUTHENTICATION_KEY = 'auth_token'
    # SECURITY_TRACKABLE = True

    #  ### CISTERN CONNECTION SETTINGS
    CISTERN_HOST = '127.0.0.1'
    CISTERN_PORT = 5071
    CISTERN_API = 'v1'


class ProductionConfig(Config):
    """ Production settings """
    DEBUG = False
    TESTING = False
    LOG_LEVEL = LOGGIN_LEVEL['INFO']


class DevelopmentConfig(Config):
    """ Development settings """
    DEBUG = True
    TESTING = True
    LOG_FILE = "/home/achmed/test/log_and_db/middleware_dev.log"
    LOG_LEVEL = LOGGIN_LEVEL['DEBUG']


class CloudConfig(object):
    CLOUD_FARM = {'default':

                   {'ENGINE': Provider.OPENSTACK,
                    'USER': 'user',
                    'PASSWORD': 'password',
                    'EXTRA_PARAMS': {'ex_force_auth_url':
                                         'http://openstack.crs4.it:5000/v2.0',
                                     'ex_force_auth_version': '2.0_password',
                                     'ex_tenant_name': 'demo',
                                     # if used in a multi region is mandatory a line with
                                     # an explainatory region.
                                     # ex_force_service_region' : 'regionOne'
                                     }
                    },

                   'fake_driver': { 'ENGINE': Provider.DUMMY
                                   # this driver emulates a cloud
                                   },

                    #'eucalyptus': { 'ENGINE' : Provider.EUCALYPTUS,
                    #                'USER' : 'USER_KEY',
                    #                    # EC2_ACCESS_KEY
                    #                'PASSWORD' : 'PWD',
                    #                'EXTRA_PARAMS': {
                    #                        'host': "eucalyptus.ecc.eucalyptus.com", 
                    #                        'secure' : False,
                    #                        'port' : 8773,
                    #                        'path' : "/services/Eucalyptus"
                    #                                }
                    #            }

                  }
