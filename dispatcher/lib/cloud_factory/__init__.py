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

    Init script, here is specified a connection between user-defined drivers
and libcloud drivers

"""


from dispatcher.lib import Provider

DRIVERS = {
    Provider.DUMMY:
        ('dispatcher.lib.cloud_factory.drivers.dummy', 'DummyDriver'),

    Provider.OPENSTACK:
        ('dispatcher.lib.cloud_factory.drivers.openstack', 'OpenStackDriver'),

    Provider.EUCALYPTUS:
        ('dispatcher.lib.cloud_factory.drivers.eucalyptus', 'EucalyptusDriver'),

    Provider.EC2_US_WEST:
        ('dispatcher.lib.cloud_factory.drivers.ec2', 'EC2_US_WEST_Driver'),

    Provider.EC2_EU_WEST:
        ('dispatcher.lib.cloud_factory.drivers.ec2', 'EC2_EU_WEST_Driver'),

    Provider.EC2_US_EAST:
        ('dispatcher.lib.cloud_factory.drivers.ec2', 'EC2_US_EAST_Driver'),

    Provider.EC2_EU_EAST:
        ('dispatcher.lib.cloud_factory.drivers.ec2', 'EC2_EU_EAST_Driver'),

    Provider.RACKSPACE:
        ('dispatcher.lib.cloud_factory.drivers.rackspace', 'RackspaceDriver'),


}


def _get_provider_driver(drivers, provider):
    """
    Get a driver.
    """
    if provider in drivers:
        mod_name, driver_name = drivers[provider]
        _mod = __import__(mod_name, globals(), locals(), [driver_name])
        return getattr(_mod, driver_name)

    raise AttributeError('Provider %s does not exist' % (provider))

def get_driver(provider):
    return _get_provider_driver(DRIVERS, provider)
