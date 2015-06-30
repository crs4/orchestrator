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
    :license: gpl-2, see License for more details


"""



class GenericDriver(object):
    def __init__(self, creds):
        self.creds = creds
        self.user = self.creds.get('USER', '')
        self.password = self.creds.get('PASSWORD', '')
        self.extra = self.creds.get('EXTRA_PARAMS', {})

    def connect(self, **kwargs):
        """
        Method Prototype, should be overriden.
        """
        pass
