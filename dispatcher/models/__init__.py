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

    dispatcher initialization script
    This script provides the structure to the authentication layer

"""

import uuid


from datetime import datetime
from dispatcher import app

from flask.ext.sqlalchemy import SQLAlchemy
#from flask.ext.security import UserMixin, RoleMixin
from flask.ext import security

from itsdangerous import URLSafeTimedSerializer

db = SQLAlchemy(app)
login_serializer = URLSafeTimedSerializer(app.secret_key)

# Define models
roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


#token_users = db.Table('token_users',
#        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
#        db.Column('token_id', db.Integer(), db.ForeignKey('token.id')))

class Role(db.Model, security.RoleMixin):
    """
    User Role
    """
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

#http://blog.thecircuitnerd.com/flask-login-tokens/



class User(db.Model, security.UserMixin):
    """
    User class inherited and overridden, in addition there is a username field,
    a new get_auth_token and a few other attributes
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    #tokens = db.relationship('Token', secondary=token_users,
    #                        backref=db.backref('tokens', lazy='dynamic'))

    #def __init__(self, userid, password):
    #    self.id = userid
    #    self.password = password

    #def get_auth_token(self):
    #    """
    #    Encode a secure token for cookie
    #    """
    #    data = [str(self.username), self.password]
    #    return login_serializer.dumps(data)
    
    def get_auth_token(self):
        """Returns the user's authentication token."""
        #data = [str(self.username), security.utils.md5(self.password)]
        clear_token = str(uuid.uuid1())

        db.session.add(Token(token=clear_token, user=self))
        db.session.commit()
        data = [str(self.username), security.utils.md5(clear_token) ]
        http_token = security.core._security.remember_token_serializer.dumps(data)

        return http_token

    @staticmethod
    def get(userid):
        """
        Static method to search the database and see if userid exists.  If it 
        does exist then return a User Object.  If not then return None as 
        required by Flask-Login. 
        """
        try:
            return User.query.get(userid)
        except:
            return None



class Token(db.Model):
    id = db.Column(db.Integer, db.Sequence('user_id_seq'), primary_key=True)
    token = db.Column(db.String(255), unique=True)
    active = db.Column(db.Boolean(),default=True)
    creation_date = db.Column(db.DateTime(), default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User',
                            backref=db.backref('tokens', 
#                                        lazy='dynamic'
                                )
                            )
