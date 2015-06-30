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

    API level v2 blueprint

    This module is a mere template for future developments.

"""

from dispatcher.components.api import VMManageAPI
from dispatcher.components.api_v1 import SystemStatus

from flask import Blueprint  # , request


apiv2 = Blueprint(__name__, __name__, url_prefix='/api/v2')


class VMManageAPIV2(VMManageAPI):
    pass


# vm status
apiv2.add_url_rule('/<action>',
                   view_func=SystemStatus.as_view(
                   'apiv1_system_status'))

apiv2.add_url_rule('/<action>/<cloud>',
                   view_func=SystemStatus.as_view(
                   'apiv1_system_status_cloud'))


apiv2.add_url_rule('/', view_func=VMManageAPIV2.as_view('apiv2'))
