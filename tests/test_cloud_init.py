import unittest
from dispatcher.lib import Provider
from dispatcher.lib.cloud_init import prepare_cloud_environment


fake_driver_setting =  { 'fake_driver': { 'ENGINE': Provider.DUMMY } }


class TestFakeCloud(unittest.TestCase):
	def __init__(self):
		super(TestFakeCloud, self).__init__(*args, **kwargs)
		self.type = 'dummy'
		self.name = 'fake_driver'

	def setUp(self):
		self.driver_setting =  {'fake_driver': {'ENGINE': Provider.DUMMY } }
		self.cloud_pool = prepare_cloud_environment(self.driver_setting)

	def test_len_pool(self):
		self.assertEqual(len(self.cloud_pool), 1)

	def test_quality_driver(self):
		self.assertEqual(self.cloud_pool[0].name, self.name)
		self.assertEqual(self.cloud_pool[0].type, self.type)


if __name__ == "__main__":
	unittest.main()