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

    cloud initialization script.

    ..WARNING::
      it's not supposed to be used directly nor imported.

"""
import logging
import libcloud.security

from dispatcher.lib.cloud_factory import get_driver

LOG = logging.getLogger(__name__)

class DriverNode(object):
    """
    Single cloud driver
    """
    def _activate_connection(self):
        """ a fake connection to stimulate the propagation of real values like
        driver.host
        """
        try:
            nodes = self.driver.list_nodes()
        except Exception as e:
            pass

    def __init__(self, name, driver, data):
        self.name = name
        self.data = data
        self.type = driver.type or name
        self.driver = driver
        self._activate_connection()
        self.host = driver.connection.host

    def refresh(self):
        """ Refreshing routine to trigger new credentials or connection """
        self.__init__(self.name, self.driver)
        # self.driver = self.driver.connect()

    def __str__(self):
        return "<%s - %s Node connector>" % (self.name, self.type)


class CloudPool(object):
    """
    Handle the application cloud pool.

    ToDo:

    It is likely this is the best place to implement a route over clouds
    so this could be the best place where to implement it.

    """
    def __init__(self):
        self.pool = []

    def add_driver(self, name, driver, data):
        """
        Add a driver in the pool
        """
        self.pool.append(DriverNode(name, driver, data))

    def remove_driver(self, name):
        """
        Remove a driver from the pool
        """
        cloud_to_pop = None

        for cloud in self.pool:
            if cloud.name == name:
                cloud_to_pop = cloud

        try:
            return self.pool.pop(self.pool.index(cloud_to_pop))
        except Exception as e:
            return None
        

    def hard_refresh(self, pool):
        load_environment(pool)

    def soft_refresh(self, name):
        cloud_to_refresh = self.remove_driver(name)

        data = cloud_to_refresh.data
        engine = data.get('ENGINE', '')

        driver_class = get_driver(engine)

        # add here your custom driver
        driver = driver_class(data)
        connector = driver.connect()

        self.add_driver(name, connector, data)


    def refresh_driver(self, settings=None, name="None", soft_refresh=True):
        LOG.debug('Refresh routine')
        if soft_refresh:
            if name:
                self.soft_refresh(name)
                return True
        else:
            if settings:
                self.hard_refresh(settings)
                return True

        LOG.error('Refresh error')
        return False


    def __getitem__(self, item):
        """
        a gentle approach to get a driver
        """
        if isinstance(item, int):
            return self.pool[item]

        if isinstance(item, str) or isinstance(item, unicode):
            for cloud in self.pool:
                if cloud.name == item:
                    return cloud

        return None


def prepare_pool_dict(data):
    """
    support routine
    """
    settings_list = []
    default = data.get('default', '')
    if default:
        settings_list.append({'default': data.pop('default')})
    for other_setting in data:
        settings_list.append({other_setting: data.get(other_setting)})
    return settings_list



def load_environment(pool):
    """ Read from configuration and load """

    cloud_pool = CloudPool()
    ordered_cloud_access = prepare_pool_dict(pool.copy())

    for cloud in ordered_cloud_access:
        name, data = cloud.items()[0]
        engine = data.get('ENGINE', '')

        driver_class = get_driver(engine)

        # add here your custom driver
        driver = driver_class(data)
        connector = driver.connect()

        cloud_pool.add_driver(name, connector, data)
    return cloud_pool


def prepare_cloud_environment(pool):
    """
    Initialize and prepare cloud pool
    """

    cloud_pool = load_environment(pool)

    return cloud_pool
