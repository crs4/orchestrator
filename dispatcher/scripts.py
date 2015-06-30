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

    Scripts file, used within flask-script routines to initialize the Orchestrator
    environment

"""

from flask.ext.script import Command, Option
from dispatcher.models.populate import populate_data
from dispatcher.models import db
import datetime


class ResetDB(Command):
        """Drops all tables and recreates them"""
        def run(self, **kwargs):
            """ Run reset routine """
            db.drop_all()
            db.create_all()

class PopulateDB(Command):
        """Fills in predefined data into DB"""
        def run(self, **kwargs):
            """ Run populate routine """
            populate_data()
