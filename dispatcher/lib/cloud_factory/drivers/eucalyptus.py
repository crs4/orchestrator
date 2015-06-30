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

from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

from . import GenericDriver

class EucalyptusDriver(GenericDriver):
    """
        Eucalyptus base node driver
    """

    def __init__(self, creds):
        """
        @param  creds: Credentials

        """

        self.creds = creds
        self.user = self.creds.get('USER', '')
        self.password = self.creds.get('PASSWORD', '')
        self.extra = self.creds.get('EXTRA_PARAMS', {})
        self.extra['secret'] = self.password

        self.driver = get_driver(Provider.EUCALYPTUS)

    def connect(self, **kwargs):
        driver = self.driver(self.user, **self.extra)
        return driver
