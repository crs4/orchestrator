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

    Various constants definition

"""


class Const(object):
    """
    Abstract class used in a confort
    """
    not_implemented = 'Not implemented'
    cloud_not_valid = 'Cloud not valid'
    cloud_or_invalid_path = 'Cloud not valid or wrong path'
    action_not_valid = 'Unrecognized action found'


    list_images = 'list_images'
    list_sizes = 'list_sizes'
    list_nodes = 'list_nodes'

    destroy_node = 'destroy_node'
    create_node = 'create_node'

    OK = 'ok'
    ERROR = 'error'
    MAX_ITERATIONS = 3
