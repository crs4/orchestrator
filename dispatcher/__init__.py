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
    .. include:: isonum.txt
    :copyright: |copy| 2015 by CRS4.
    :license: gpl-2, see License for more details.

    Dispatcher initialization script.
    
    Dispatcher is the core of the Orchestrator, it provides a RESTful API web service with
    a JSON dialect.


    The initialization script is not supposed to be used directly or imported.

    In addiction to switch between development or production config file set proporly the variable:
    
        >>> DEV = True  # Debug on
        >>> DEV = False # Debug off

"""

import os
import logging
from logging.handlers import RotatingFileHandler
from logging import Formatter

from flask import Flask

from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required


from dispatcher import settings
from dispatcher.lib import cloud_init
# from restapiblueprint.lib import use_pretty_default_error_handlers


##################################
# DEVELOPMENT MODE 
##################################
DEV = True


def configure_app(app):
    """
    setup the flask application using setting directives.

    there are 3 ways to properly configure the flask app:

    * changing ``settings.py`` content
    * using the environmental variable ``MIDDLEWARE_SETTINGS``
    * using a custom python file ``settings_local.cfg``

    """
    if DEV:
        setup = settings.DevelopmentConfig
    else:
        setup = settings.ProductionConfig

    app.config.from_object(setup)
    app.config.from_envvar('MIDDLEWARE_SETTINGS', silent=True)
    # cloud configuration
    app.config.from_object(settings.CloudConfig)
    app.config['POOL'] = cloud_init.prepare_cloud_environment(
                                                    app.config['CLOUD_FARM'])
    # parent directory
    here = os.path.dirname(os.path.abspath( __file__ ))
    config_path = os.path.join(os.path.dirname(here), 'settings_local.cfg')
    if os.path.exists(config_path):
        app.config.from_pyfile(config_path)



def setup_logging(app):
    """
    setup logging facilities on setting directives
    """
    log_file_path = app.config.get('LOG_FILE')
    log_level = app.config.get('LOG_LEVEL', logging.WARN)
    if log_file_path:
        file_handler = RotatingFileHandler(log_file_path)
        file_handler.setFormatter(Formatter(
            '%(name)s:%(levelname)s:[%(asctime)s] %(message)s '
            '[in %(pathname)s:%(lineno)d]'
            ))
        file_handler.setLevel(log_level)
        app.logger.addHandler(file_handler)
        logger = logging.getLogger('dispatcher')
        logger.setLevel(log_level)
        logger.addHandler(file_handler)



def create_app():
    """
    Used to create a configured flask application
    """
    app = Flask(__name__)
    configure_app(app)
#    setup_error_email(app)
    setup_logging(app)
    return app

# (Keep pyflakes quiet)
#restapiblueprint.views


app = create_app()

import dispatcher.views
from dispatcher.database import *





from dispatcher.models import db, User, Role

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)









