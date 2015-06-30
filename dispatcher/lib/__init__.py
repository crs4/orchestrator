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


class Provider(object):
    """
        Defines for each of the supported providers
    """
    DUMMY = 'dummy'
    OPENSTACK = 'openstack'
    EUCALYPTUS = 'eucalyptus'

    # public amazon
    EC2_US_WEST = 'ec2_us_west'
    EC2_EU_WEST = 'ec2_eu_west'
    EC2_US_EAST = 'ec2_us_east'
    EC2_EU_EAST = 'ec2_eu_east'

    # rackspace
    RACKSPACE = 'rackspace'

