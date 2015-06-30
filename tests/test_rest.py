import sys
import os

sys.path.insert(0, os.path.abspath('../'))

import unittest
import requests
import json
import tempfile
import multiprocessing
import dispatcher

from dispatcher import user_datastore, app
from dispatcher.models import db
from dispatcher.scripts import ResetDB

# to monkey patch
import dispatcher.components.api_v1
import dispatcher.lib.helpers
# stop

from flask.ext.script import Manager

from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

from file_fixtures import ComputeFileFixtures

# future reference
# http://docs.python.org/2/library/unittest.html
# http://stackoverflow.com/questions/9559963/unit-testing-a-python-app-that-uses-the-requests-library
# http://www.voidspace.org.uk/python/mock/



class MockCaller(object):
    """ This class emulates an http caller """
    def __init__(self):
        self.headers = {'content-type': 'application/json; charset=UTF-8'}
        self.last_status = 200
        self.last_message = None

    def get_a_page(self, url, **kwargs):
        pass

def mock_get_a_caller(something):
    """ This function is to monkey patch the function `get_a_caller` and avoid
    to use actual running Cistern project.
    """
    caller = MockCaller()
    return caller

dispatcher.lib.helpers.get_a_caller = mock_get_a_caller


class  MonkeyCisternConnection(dispatcher.components.api_v1.CisternConnection):
    """ This function is to monkey patch the class `CisternConnection` and avoid 
    to use actual running Cistern project.
    """
    fixtures = ComputeFileFixtures('cistern')
    def __init__(self, cloud):
        self.cloud = cloud
        self.caller = MockCaller()

    def get_all_nodes(self, faulty=True):
        body = self.fixtures.load('_all_nodes.json')
        return json.loads(body).get('nodes')
    
    def get_node_by_field(self, field, value):
        nodes = self.get_all_nodes()
        for node in nodes:
            if node.get(field) == value:
                return node
        return None

    def get_page(self, url, **kwargs):
        """ Rough way to understand which json to reply back ( instead 
            HTTP replies )"""
        action = url.split("/")

        if "assign" in action:
            body = self.fixtures.load('_assign.json')
        elif "release" in action:
            body = self.fixtures.load('_release.json')
        else:
            body = self.fixtures.load('_none.json')

        #body_clean = json.dumps(body)
        body_clean = body
        return json.loads(body_clean)


class MockProcess(object):
    """
    This class is used to mock the default environment & behaviour
    """
    mockprocess = None 
    def startmock(self):
        dispatcher.components.api_v1.CisternConnection = MonkeyCisternConnection
        # create a process, point it at the "run()" method of the     flask app
        self.mockprocess = multiprocessing.Process(target=app.run, args=(None,
                                                    4009, False))
        # make the process exit with the parent process
        self.mockprocess.daemon = True

        # ...and lets go! this starts the process in the background
        self.mockprocess.start()

    def stopmock(self):
        # tell the background process to stop
        self.mockprocess.terminate()


class InitClass(object):
    """
    Initialization class, here is initialized a new db with a test account
    """

    def _create_db(self):
        self.db_fd, self.temp_name = tempfile.mkstemp()
        return self.db_fd, self.temp_name

    def _destroy_db(self):
        """
        cleaning db routine
        """
        try:
            os.close(self.db_fd)
            os.unlink(self.temp_name)
        except Exception as e:
            pass

    def _initialize_fake_cloud(self):
        """
        force to use a Dummy cloud
        """

        farm = app.config.get('CLOUD_FARM', {})
        if 'default' not in farm:
            app.config['CLOUD_FARM']['default'] = {}

        app.config['CLOUD_FARM']['default']['ENGINE'] = 'Dummy'

    def _initialize_db(self, *args, **kwargs):
        """
        DB creation routine with user population
        """

        self.db_fd, self.temp_name = self._create_db()
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////%s' % self.temp_name

        ResetDB().run()

        for role in ('admin', 'agent'):
            user_datastore.create_role(name=role, description=role)

        db.session.commit()

        self.test_user_list = (('test123', 'test@crs4.it', 'password',
                                ['agent'], True),)
        u = self.test_user_list[0]

        self.user = user_datastore.create_user(username=u[0], email=u[1],
                                               password=u[2], roles=u[3],
                                               active=u[4])
        InitClass.user = self.user
        #self.user = user_datastore.find_user(username=u[0])
        db.session.commit()

    def initialize(self):
        """
        Let's init ...
        """
        self._initialize_db()
        self._initialize_fake_cloud()
        self.mockprocess = MockProcess()
        self.mockprocess.startmock()

    def destroy(self):
        """
        Let's destroy ...
        """
        user_datastore.delete_user(self.user)
        db.session.commit()
        self._destroy_db()
        self.mockprocess.stopmock()

    @staticmethod
    def getUser():
        """
        Workaround to get the initialization user available for all classes
        """
        return InitClass.user


class HTTPConnection(object):
    """
    Support class to provide supporting routines to tests
    """
    def __init__(self):
        self.server = 'http://localhost:4009'
        self.auth_url = self.server + '/api/v1/auth'
        self.headers = {'content-type': 'application/json'}
        self.token = ""
        self.user = InitClass.getUser()

    def get_connection_token(self):
        """
        get the connection token
        """
        payload = {"username": self.user.username,
                   "password": self.user.password}

        r = requests.post(self.auth_url, data=json.dumps(payload),
                          headers=self.headers)
        res = r.json()
        self.token = res.get('token', None)
        return res.get('token', None)

    def get_page(self, url, method='get', payload=None):
        """
        make a generic call with a json response
        """
        url = self.server + url
        r = requests.__dict__[method](url, data=json.dumps(payload),
                                      headers=self.headers)
        res = r.json()
        return res

###############################################
# Tests !


class TestConnectionV1(unittest.TestCase):
    """
    Connection and authentication test suite
    """
    def __init__(self, *args, **kwargs):
        super(TestConnectionV1, self).__init__(*args, **kwargs)
        self.conn_obj = HTTPConnection()

    def setUp(self):
        super(TestConnectionV1, self).setUp()
        #self.initialize()

    def tearDown(self):
        super(TestConnectionV1, self).tearDown()
        #self.destroy()

    def test_a_authentication(self):
        """
        Tries an authentication
        """
        token = self.conn_obj.get_connection_token()
        self.assertNotEqual(token, None)

    def test_b_connection(self):
        token = self.conn_obj.get_connection_token()
        url = "/api/v1/test/start"
        payload = {"auth_token": token}
        data = self.conn_obj.get_page(url, method='put', payload=payload)
        self.assertEqual(data['status'], 'ok')


class TestFakeCloudStatusV1(unittest.TestCase):

    """
    Test fake cloud status
    """

    def __init__(self, *args, **kwargs):
        super(TestFakeCloudStatusV1, self).__init__(*args, **kwargs)
        self.conn_obj = HTTPConnection()

    def test_nodes(self):
        url = "/api/v1/nodes/fake_driver"
        payload = {}
        data = self.conn_obj.get_page(url, method='get', payload=payload)
        self.assertEqual(data['status'], 'ok')

    def test_flavors(self):
        url = "/api/v1/flavors/fake_driver"
        payload = {}
        data = self.conn_obj.get_page(url, method='get', payload=payload)
        self.assertEqual(data['status'], 'ok')

    def test_images(self):
        url = "/api/v1/images/fake_driver"
        payload = {}
        data = self.conn_obj.get_page(url, method='get', payload=payload)
        self.assertEqual(data['status'], 'ok')


class TestFakeCloudMNGV1(unittest.TestCase):
    """
    Test fake cloud run / stop / assign
    """
    def __init__(self, *args, **kwargs):
        super(TestFakeCloudMNGV1, self).__init__(*args, **kwargs)
        self.conn_obj = HTTPConnection()

    def test_run_and_close_vm(self):
        url = "/api/v1/vm/start/fake_driver"
        payload = { "name": "cloud", "image": "1", "size" : "1"}
        # start
        method = "post"
        data = self.conn_obj.get_page(url, method=method, payload=payload)
        self.assertEqual(data['status'], 'ok')
        # stop
        url = "/api/v1/vm/stop/fake_driver"
        payload = { "node": data.get('nodes').get('id')}
        method = "put"
        data = self.conn_obj.get_page(url, method=method, payload=payload)
        self.assertEqual(data['status'], 'ok')

    def test_assign_and_release_vm(self):
        # START
        url = "/api/v1/vm/start/fake_driver"
        payload = { "name": "cloud", "image": "1", "size" : "1"}
        # start
        method = "post"
        data = self.conn_obj.get_page(url, method=method, payload=payload)
        # ASSIGN
        url = "/api/v1/vm/action/assign/fake_driver"
        payload = {"node": "3", "user": "fake_test", "vm_type" : "test" }
        method = "put"
        data = self.conn_obj.get_page(url, method=method, payload=payload)
        self.assertEqual(data['status'], 'ok')

        # release
        url = "/api/v1/vm/action/release/fake_driver"
        payload = {"node": "3"}
        method = "put"
        data = self.conn_obj.get_page(url, method=method, payload=payload)
        self.assertEqual(data['status'], 'ok')



if __name__ == "__main__":
    # arm the weaponry !
    test_environment = InitClass()
    test_environment.initialize()
    # test!
    unittest.main(exit=False)
    # release
    test_environment.destroy()
