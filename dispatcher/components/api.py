# -*- coding:utf-8 -*-

# Copyright 2014 CRS4
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

    :copyright: |copy| 2014 by CRS4.
    :license: gpl-2, see License for more details.

    Description
    ~~~~~~~~~~~

    Base file where parent routines are defined and from where
    these will be inherited.

"""

from flask.views import MethodView

from dispatcher.lib.helpers import not_implemented  # ,MiddlewareException


class VMManageAPI(MethodView):
    """
    Abstract response class, used to have global implementation for
    unused methods.
    """
    def get(self, *args, **kwargs):
        return "Dev"

    def post(self, *args, **kwargs):
        not_implemented()

    def put(self, *args, **kwargs):
        not_implemented()

    def patch(self, *args, **kwargs):
        not_implemented()

    def delete(self, *args, **kwargs):
        not_implemented()

    def options(self, *args, **kwargs):
        not_implemented()
