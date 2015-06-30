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

    API level v1 blueprint

    This blueprint provides V.1 API dialect to specific functions:

    + :class:`RunAndStopVM` provides start and stop VMs facilities
    + :class:`AssignReleaseVM` provides facilities to reserve and release VMs for users and applications
    + :class:`SystemStatus` to have always the system under control

    In `api_call_examples` file there are several examples about how to use and
    deal with the middleware.


"""

import time
import logging

from flask import current_app
from flask import Blueprint, request, json, jsonify
from flask.ext.security import login_user  # , login_required

from dispatcher.components.api import VMManageAPI

from dispatcher.lib.helpers import auth_required, make_response, validate_json
from dispatcher.lib.helpers import MiddlewareException, not_implemented
from dispatcher.lib.helpers import get_a_caller
from dispatcher.models import User  # , Role

from dispatcher.lib.constants import Const as const

from schema import Schema, Optional, And  # , Use

LOG = logging.getLogger(__name__)

apiv1 = Blueprint(__name__, __name__, url_prefix='/api/v1')

#
# validating schema

STARTING_PARAMS = Schema({'name': And(unicode, len),
                          'image': And(unicode, len),
                          'size': And(unicode, len),
                          # 'size': And(Use(int), lambda n: 1 <= n),
                          Optional('keyname'): And(unicode, len),
                          # ToDo, maybe a metadata validation is needed...
                          Optional('metadata'): dict,
                          
                          })


STOPPING_PARAMS = Schema({Optional('node'): And(unicode, len),
                          Optional('hostname'): And(unicode, len),
                          })


ASSIGN_VM_PARAMS = Schema({
    Optional('node'): And(unicode, len),
    Optional('hostname'): And(unicode, len),
    'user': And(unicode, len),
    'vm_type': And(unicode, len),
    Optional('emulate'): bool,
})

RELEASE_VM_PARAMS = Schema({
    Optional('node'): And(unicode, len),
    Optional('hostname'): And(unicode, len),
    Optional('emulate'): bool,
})


class CloudConnection(object):

    """
    Service Class, used to serve queries on demand routed over clouds.

    This Class is designed to provide an uniformed layer to get

    + :meth:`get_node`
    + :meth:`get_images`
    + :meth:`get_size`

    """

    @staticmethod
    def make_query(cloud, method, **kwargs):

        """
        Abstraction to make cloud queries only here.
        method is something like 'list_nodes'.

        This could be a good place to implement a different routine to choose
        which cloud to work with.

        """

        max_iterations = current_app.config.get('MAX_ITERATIONS', 
                                                const.MAX_ITERATIONS)
        for iteration in xrange(min( max_iterations, const.MAX_ITERATIONS)):

            query = getattr(current_app.config['POOL'][cloud].driver, method)
            try:

                response = query(**kwargs)
                return response

            except AttributeError as e:
                LOG.error("Attribute error: %s" % str(e))
                raise MiddlewareException(const.cloud_not_valid, 'json',
                                          state=const.ERROR,
                                          code=400)

            except Exception as e:
                if "401" in e.message:
                    LOG.warn('Refreshing connection: %s' % cloud)
                    
                    current_app.config['POOL'].refresh_driver(name=cloud)
                    continue

            LOG.error("Something went wrong with your connection: %s" % str(e))
            raise MiddlewareException(const.cloud_or_invalid_path, 'json',
                                      state=const.ERROR,
                                      code=500)

    @staticmethod
    def fetch_object_by_field(cloud, method, id_obj, field):
        """
        General fetching routine filtered by field
        """
        response = CloudConnection.make_query(cloud, method)
        for obj in response:
            if id_obj == getattr(obj, field):
                return obj
        return None

    @staticmethod
    def fetch_object_by_id(cloud, method, id_obj):
        """
        General fetch routine by some ids
        """

        field = "id"
        return CloudConnection.fetch_object_by_field(cloud, method,
                                                     id_obj, field)

    @staticmethod
    def get_image(cloud, id_obj):
        """
        get a particular image by id from your favorite cloud
        """
        # is it possible libcloud is unable to get a single specific image ?!
        response = CloudConnection.fetch_object_by_id(cloud,
                                                      const.list_images,
                                                      id_obj)
        if not response:
            raise MiddlewareException('no useful image id here',
                                      state=const.ERROR, code=400)

        return response

    @staticmethod
    def get_size(cloud, id_obj):
        """
        get a particular flavor by id from your favorite cloud
        """
        # is it possible libcloud is unable to get a single specific image ?!
        response = CloudConnection.fetch_object_by_id(cloud,
                                                      const.list_sizes, id_obj)

        if not response:
            raise MiddlewareException('no useful size id here',
                                      state=const.ERROR, code=400)
        return response

    @staticmethod
    def get_node(cloud, **kwargs):
        """
        get a particular node by id from your favorite cloud

        :attr:`kwargs` should contain `data`, a dictionary structured as

        .. code-block:: guess

            {
                "node" : 42,
                "hostname" : "this is an hostname"
            }

        node and hostname are complementary, is strictly necessary only one of
        these.

        """
        # is it possible libcloud is unable to get a single specific image ?!
        data = kwargs.get('data', {})
        id_node = data.get("node", None)
        hostname = data.get("hostname", None)

        if not id_node and not hostname:
            raise MiddlewareException('no valid node id nor hostname here',
                                      state=const.ERROR, code=400)

        response = CloudConnection.make_query(cloud, const.list_nodes)
        filtered = None

        for node in response:
            if (id_node == node.id) or (hostname == node.name):
                filtered = node
                break

        response = filtered
        if not response:
            raise MiddlewareException('no useful node id here',
                                      state=const.ERROR, code=400)
        return response


class CisternConnection(object):

    """
    Service Class to route queries over CISTERN API
    """

    def __init__(self, cloud):
        """ Warm up engines """
        app = current_app
        self.caller = get_a_caller(app)
        self.cloud = cloud

    def get_all_nodes(self, with_faulty_nodes=True):
        """ Get all nodes from cistern """
        data = {"with_faulty_nodes": with_faulty_nodes}
        url = "/nodes/%s" % self.cloud
        res = self.caller.get_page(url, method="get", payload=data)
        return res.get('nodes', [])

    def get_all_active_nodes(self):
        """
        Get all nodes an then filter by activity.
        No extra params needed.

        """
        return self.get_all_nodes(with_faulty_nodes=False)

    def get_node_by_field(self, field, value):
        """
        Get all nodes an then filter by a field.
        """
        nodes = self.get_all_nodes()
        for node in nodes:
            if node.get(field) == value:
                return node

        self.caller.last_message = { "message" : "Node not found" }
        self.caller.last_status = 400
        return None

    def get_page(self, url, **kwargs):
        """
        Make a request to cistern.

        + :attr:`url` is the url to contact, protocol and servername\
                is added on the fly with what has been specified on\
                initialization of the object
        + :attr:`kwargs` is an attribute of optional key/value pairs, should be:
            * :attr:`method`, the way to contact the server, default is 'get',
            * :attr:`payload`, is a dictionary structure containing additional\
            payload useful to the request

        """
        return self.caller.get_page(url, **kwargs)


class AuthAPI(VMManageAPI):

    """
        Authentication endpoint class, used to get auth token
    """

    def post(self):
        """

        """
        data = request.get_json()

        #data = json.loads(request.data)
        username = data.get('username', '')
        password = data.get('password', '')
        match = User.query.filter_by(username=username,
                                     password=password).all()
        if len(match) and match[0].active:
            login_user(match[0])
            return make_response(token=match[0].get_auth_token())

        raise MiddlewareException('Forbidden',
                                  state=const.ERROR, code=403)


class RunAndStopVM(VMManageAPI):

    """
    Provides start and stop routines to launch VMs in the cloud
    """

    def _check_start_params(self, data):
        if not len(data):
            raise MiddlewareException('no useful parameters here', 'json',
                                      state=const.ERROR,
                                      code=400)

    @validate_json(STARTING_PARAMS.validate)
    def post(self, cloud='default'):
        """
        Used to launch a new VM

        `request.data` is the payload in JSON and should contain :

        + `image` : the image identifier, a string like\
                    "3c725bdb-b575-4e0f-b21b-67b0d089867d"
        + `size` : the size/flavor identifier, same thing as images
        + `metadata` : custom Key/Value metadata dictionary t0o associate\
                        with a node
        + `keyname` : A string containing the name of existing public key to\
                     inject into instance

        Depending cloud provider needs this class could be enhanced and\
        extended, each cloud takes his own attributes

        """
        try:
            data = request.get_json()

            image = CloudConnection.get_image(cloud, data.get('image'))
            size = CloudConnection.get_size(cloud, data.get('size'))

            data['image'] = image
            data['size'] = size
            data['ex_metadata'] = data.get('metadata', {})
            data['ex_keyname'] = data.get('keyname', "")

            node = CloudConnection.make_query(cloud, const.create_node, **data)

            node_response = {'name': node.name,
                             'uuid': node.get_uuid(),
                             'id': node.id,
                             'provider': node.driver.type,
                             'public_ips': node.public_ips,
                             'private_ips': node.private_ips,
                             'cloud_type': node.driver.name,
                             'state': node.state,
                             'extra': node.extra
                             }
            response = {'status': const.OK, 'nodes': node_response}
            return jsonify(**response)
        except Exception as e:
            raise MiddlewareException('Something went wrong %s' % str(e),
                                    'json', state=const.ERROR, code=500)

    @validate_json(STOPPING_PARAMS.validate)
    def put(self, cloud='default'):
        """
        Used to stop a VM, this is the shutdown process
        """
        data = request.get_json()

        node = data.get('node', None)
        hostname = data.get('hostname', None)

        node = CloudConnection.get_node(cloud, data=data)
        node_id = node.id
        data['node'] = node

        hostname = data.pop('hostname', '')  # just to clean the struct
        result = CloudConnection.make_query(cloud, const.destroy_node, **data)
        response = {'status': const.OK,
                    'result': 'Node %s deleted' % node_id}
        return jsonify(**response)


class VMSystemMonitor(VMManageAPI):

    """
    List instances or get a single instance status
    """

    def get(self, action):
        if action == 'list':
            pass
        elif action == 'status':
            pass
        else:
            not_implemented()


class AssignmentStatusVM(VMManageAPI):

    """
    Assignment status for remote clouds
    """

    def get(self, cloud="default"):
        """
        Support remote resources
        """

        cis_conn = CisternConnection(cloud)
        active_nodes = cis_conn.get_all_active_nodes()
        nodes = active_nodes[:]
        if nodes:
            response = {"status": const.OK, "nodes": nodes}
            return jsonify(**response)
        else:
            response = {"status": const.OK, "nodes": {}}
            return jsonify(**response)
            # NOTE(carlo): ToDo, verify if is possible to replace the code below
            # with a plain response = {"status": const.OK, "nodes": {}}
            #raise MiddlewareException('Something went wrong', 'json',
            #                          state=const.ERROR, code=400)


class AssignReleaseVM(VMManageAPI):

    """
        Assign / Release VM to user
    """


    def _assign_doc_purpose(self, cloud, **kwargs):
        """
        The documentation part needs something to emulate a Cistern behaviour
        but keeping Cistern down.
        This method is intended to be used only with the purpose of
        auto-documentation.
        """
        return {"status": const.OK,
                "id_vm": '-fake_id-',
                "id": 42,
                "result": "Node -fake_id- assigned"
                }

    def _release_doc_purpose(self, cloud, **kwargs):
        """
        The documentation part needs something to emulate a Cistern behaviour
        but keeping Cistern down.
        This method is intended to be used only with the purpose of
        auto-documentation.
        """
        return {"status": const.OK,
                "id_vm": '-fake_id-',
                "id": 42,
                "result": "Node -fake_id- assigned"
                }

    @validate_json(ASSIGN_VM_PARAMS.validate)
    def _assign(self, cloud, **kwargs):
        """
        Support routine to assignation dues
        """
        #app = current_app
        data = request.get_json()

        #data = json.loads(request.data)
        node = data.get('node', None)
        hostname = data.get('hostname', None)

        if not hostname:
            cis_conn = CisternConnection(cloud)
            cis_node = cis_conn.get_node_by_field('id_vm', node)

            if cis_conn.caller.last_status != 200:
                raise MiddlewareException(cis_conn.caller.last_message.get(
                                          'message', 'unknown'),
                                          'json',
                                          state=const.ERROR,
                                          code=400)

            hostname = cis_node.get('hostname')

        user = data['user']
        vm_type = data['vm_type']

        data = {"hostname": hostname,
                "user": user,
                "vm_type": vm_type
                }

        url = '/vm/assign/%s' % cloud

        # caller = get_a_caller(app)
        # res = caller.get_page(url, method="post", payload=data)
        cis_conn = CisternConnection(cloud)
        res = cis_conn.get_page(url, method="post", payload=data)

        status = res.get('status', const.ERROR)

        if status == const.OK:
            id_vm = res.get('id_vm')
            id = res.get('id')
            result = res.get("result")
            return {"status": const.OK,
                    "id_vm": id_vm,
                    "id": id,
                    "result": result
                    }
        else:
            raise MiddlewareException(res.get('message', 'unknown'), 'json',
                                      state=const.ERROR,
                                      code=400)

    @validate_json(RELEASE_VM_PARAMS.validate)
    def _release(self, cloud, **kwargs):
        """
        Support routine to release dues
        """
        data = request.get_json()

        cis_conn = CisternConnection(cloud)

        node = data.get('node', None)
        hostname = data.get('hostname', None)
        if not hostname:
            cis_node = cis_conn.get_node_by_field('id_vm', node)
            hostname = cis_node.get('hostname')

        if not node:
            cis_node = cis_conn.get_node_by_field('hostname', hostname)
            node = cis_node.get('id_vm')

        data = {"hostname": hostname}
        url = '/vm/release/%s' % cloud

        # RELEASE
        res = cis_conn.get_page(url, method="put", payload=data)
        status = res.get('status', const.ERROR)

        # DROP
        if status!=const.ERROR:
            data = {'node': node}
            node = CloudConnection.get_node(cloud, data=data)
            node_id = node.id
            data['node'] = node
           
            # asap remove this kludge used to sync something ...
            time.sleep(25)
            result = CloudConnection.make_query(cloud, const.destroy_node, **data)

            if status == const.OK:
                id_vm = res.get('id_vm')
                id = res.get('id')
                result = res.get("result") + " and deleted"

                return {"status": const.OK,
                        "id_vm": id_vm,
                        "id": id,
                       "result": result
                        }
        
        raise MiddlewareException(res.get('message', 'unknown'), 'json',
                                      state=const.ERROR,
                                      code=400)

    def put(self, action, cloud="default"):
        """
        Assign or Release resources
        """
        data = request.get_json()

        LOG.warn("Requested %(action)s %(cloud)s data: %(data)s" % locals())
        if action == "assign":
            if request.get_json().get('emulate', False):
                # only for documenting purpose!
                response = self._assign_doc_purpose(cloud)
            else:
                response = self._assign(cloud)

        elif action == "release":
            if request.get_json().get('emulate', False):
                # only for documenting purpose!
                response = self._assign_doc_purpose(cloud)
            else:
                response = self._release(cloud)

        else:
            not_implemented()

        return jsonify(**response)


class ManageFirewall(VMManageAPI):

    """
    Firewall management class, used to open and close ports
    """

    def get(self):
        pass
        # driver.ex_list_security_groups()

    def put(self):
        pass

    def post(self):
        pass


class ManageStorage(VMManageAPI):

    """
    ToDo class
    """
    pass


class SystemStatus(VMManageAPI):

    """
    Status management class, used to get the status of VMs
    """

    def _get_nodes(self, cloud):
        """
        Support routine to get nodes
        """
        node_list = CloudConnection.make_query(cloud, const.list_nodes)
        nodes = []
        for node in node_list:
                nodes.append({'name': node.name,
                              'uuid': node.get_uuid(),
                              'id': node.id,
                              'provider': node.driver.type,
                              'public_ips': node.public_ips,
                              'private_ips': node.private_ips,
                              'cloud_type': node.driver.name,
                              'state': node.state,
                              'extra': node.extra
                              })
        return {'status': const.OK, 'nodes': nodes}

    def _get_flavors(self, cloud):
        """
        Support routine to get flavors
        """
        # a little patch to
        # https://issues.apache.org/jira/browse/LIBCLOUD-119
        flavor_list = CloudConnection.make_query(cloud, const.list_sizes)
        flavors = []
        for flavor in flavor_list:
            flavors.append({'id': flavor.id,
                            'name': flavor.name,
                            'ram': flavor.ram,
                            'cpu': flavor.__dict__.get('cpu', 0),
                            'disk': flavor.disk,
                            'provider': flavor.driver.type,
                            'cloud_type': flavor.driver.name,
                            })
        return {'status': const.OK, 'flavors': flavors}

    def _get_images(self, cloud):
        """
        Support routine to get images
        """
        images_list = CloudConnection.make_query(cloud, const.list_images)
        images = []
        for image in images_list:
            images.append({'id': image.id,
                           'name': image.name,
                           'provider': image.driver.type,
                           'cloud_type': image.driver.name,
                           })
        return {'status': const.OK, 'images': images}

    def _get_tenants(self, cloud):
        """
        support routine for tenants

        ... *BUT* it's just an ugly workaround

        *** warning *** kludge

        .. WARNING::
            this is a kludge ! this because libcloud doesn't support tenants
        """

        tenants = [{}, ]
        if cloud == "default":
            tenants = [{'id': "f122fd1685b142d6830ee970900b2151",
                        'name': "demo",
                        'provider': "openstack",
                        'cloud_type': "OpenStack"
                        }]

        return {'status': const.OK, 'tenants': tenants}

    def get(self, action, cloud='default'):
        """ Factory GET routine, it accepts:

        action: {flavors,images,nodes}

        cloud: the source where we get data from, if not specified "default"
        is choosen
        """

        response = {}
        if action in ("flavors", "sizes"):
            response = self._get_flavors(cloud)

        elif action == "images":
            response = self._get_images(cloud)

        elif action == "tenants":
            response = self._get_tenants(cloud)

        elif action == "nodes":
            response = self._get_nodes(cloud)

        else:
            raise MiddlewareException(const.action_not_valid, 'json',
                                      state=const.ERROR,
                                      code=400)
        return jsonify(**response)


class CloudServed(VMManageAPI):

    """
    Provides a list of the served cloud pool
    """

    def get(self):
        """
        Routine to have a list of served clouds
        """
        driver_list = []
        app = current_app
        for driver in app.config['POOL']:
            driver_list.append({'name': driver.name,
                                'type': driver.type,
                                'host': driver.host
                                })
        response = {'status': const.OK, 'served_cloud': driver_list}
        return jsonify(**response)


class FooClass(VMManageAPI):

    """
    test foo class
    """
    #@login_required
    @auth_required('token')
    def put(self):
        app = current_app
        # nodes = app.config['POOL'].pool[0].driver.list_nodes()
        # nodes = app.config['POOL'][0].driver.list_nodes()
        nodes = app.config['POOL']['default'].driver.list_nodes()
        return jsonify(status=const.OK, test='passed', authenticated='yes')


class HomeAPI(VMManageAPI):

    """
    Generic root endpoint class
    """

    def get(self):
        return jsonify(status=const.OK)

    def post(self):
        d = json.loads(request.data)
        return jsonify(status=const.OK)


#
# URL
#

# home
apiv1.add_url_rule('/', view_func=HomeAPI.as_view('apiv1'))

# cloud
apiv1.add_url_rule('/cloud', view_func=CloudServed.as_view('apiv1_cloud'))

# auth
apiv1.add_url_rule('/auth', view_func=AuthAPI.as_view('apiv1_auth'))

# vm status
apiv1.add_url_rule('/<action>',
                   view_func=SystemStatus.as_view(
                   'apiv1_system_status'))

apiv1.add_url_rule('/<action>/<cloud>',
                   view_func=SystemStatus.as_view(
                   'apiv1_system_status_cloud'))

# vm management api
apiv1.add_url_rule('/vm/start', view_func=RunAndStopVM.as_view('apiv1_vm_run'))

apiv1.add_url_rule('/vm/start/<cloud>',
                   view_func=RunAndStopVM.as_view(
                   'apiv1_vm_run_cloud'))


apiv1.add_url_rule('/vm/stop',
                   view_func=RunAndStopVM.as_view('apiv1_vm_stop'))

apiv1.add_url_rule('/vm/stop/<cloud>',
                   view_func=RunAndStopVM.as_view(
                   'apiv1_vm_stop_cloud'))

# actions
apiv1.add_url_rule('/vm/action/<action>',
                   view_func=AssignReleaseVM.as_view(
                   'apiv1_assign_and_release'))

apiv1.add_url_rule('/vm/action/<action>/<cloud>',
                   view_func=AssignReleaseVM.as_view(
                   'apiv1_assign_and_release_cloud'))

# status
apiv1.add_url_rule('/vm/status',
                   view_func=AssignmentStatusVM.as_view(
                   'apiv1_assignment_status'))

apiv1.add_url_rule('/vm/status/<cloud>',
                   view_func=AssignmentStatusVM.as_view(
                   'apiv1_assignment_status_cloud'))

# apiv1.add_url_rule('/vm/<action>',
    #view_func=AssignReleaseVM.as_view('apiv1_release'))
# apiv1.add_url_rule('/vm/<action>/<cloud>',
# view_func=AssignReleaseVM.as_view('apiv1_release_cloud'))

# firewall
apiv1.add_url_rule('/fw/open',
                   view_func=ManageFirewall.as_view(
                   'apiv1_firewall_open'))

apiv1.add_url_rule('/fw/close',
                   view_func=ManageFirewall.as_view(
                   'apiv1_firewall_close'))


# TEST TEST TEST TEST
apiv1.add_url_rule('/test/start', view_func=FooClass.as_view('apiv1k'))

apiv1.add_url_rule('/test/<int:user_id>/kill',
                   view_func=FooClass.as_view('apiv12'))


# some examples are in api_call_examples file
