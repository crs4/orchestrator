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

    Provides routines to pre-populate the database
    
"""

from dispatcher import user_datastore
from dispatcher.models import db

def create_roles():
    """ Create roles """
    for role in ('admin', 'agent'):
        user_datastore.create_role(name=role, description=role)
    db.session.commit()


def create_users():
    """ Create users """
    for u in  (('user1','user1@xxxx.it','password',['pwd1'],True),
               ('user2','user2@yyyy.it','password',['pwd2'],True),
               ('user3','user3@wwww.it','password',['pwd3'],True)):
        user_datastore.create_user(username=u[0], email=u[1], password=u[2],
                                   roles=u[3], active=u[4])
        db.session.commit()

def populate_data():
    """ Sequence of creation routines """
    create_roles()
    create_users()
