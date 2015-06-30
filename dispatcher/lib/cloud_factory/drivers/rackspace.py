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

class RackspaceDriver(GenericDriver):
    """
        Rackspace base node driver
    """

    def __init__(self, creds):
        """
        @param  creds: Credentials

        """
        
        super(RackspaceDriver, self).__init__(creds)
        self.driver = get_driver(Provider.RACKSPACE)

    def connect(self, **kwargs):
        driver = self.driver(self.user, self.password, **self.extra)
        return driver
