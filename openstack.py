# ESEMPIOOOOOOOOOOOOOOOOOOOOOOOOOOO


from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from libcloud.compute.types import NodeState


import libcloud.security

libcloud.security.VERIFY_SSL_CERT = False

OpenStack = get_driver(Provider.OPENSTACK)

driver = OpenStack('demo', 'keypass',
                   ex_force_auth_url='http://nova.crs4.it:5000/v2.0',
                   ex_force_auth_version='2.0_password',
                   ex_tenant_name='invisible_to_admin'
                   )
                   

nodes = driver.list_nodes()


#from libcloud.compute.drivers.dummy import DummyNodeDriver
#driver = DummyNodeDriver(0)
#node = driver.create_node()
#node.get_uuid()
#driver.list_nodes()
#driver.list_locations()
#driver.list_sizes()  ## flavors!