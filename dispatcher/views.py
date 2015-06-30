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

    View file, used to register blueprints/api versions 
"""

from dispatcher import app
from dispatcher.components import api_v1
from dispatcher.components import api_v2

from flask import jsonify

@app.route('/')
def index():
    return 'Hello World!'


app.register_blueprint(api_v1.apiv1)
app.register_blueprint(api_v2.apiv2)


@app.errorhandler(404)
def page_not_found(e):
    message ={"status": "error",
            "message": "Page not found"}
    return jsonify(message), 404
