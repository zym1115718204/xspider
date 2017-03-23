#coding:utf8
from django.test import TestCase
from django.conf import settings
import redis
from manager import Manager


# Create your tests here.
class ManagerTestCase(TestCase):

	def setUp(self):
		self.nodes = settings.NODES
		self.r = redis.Redis.from_url(settings.NODES_REDIS)

	# def test_redis_hash(self):
	# 	self.r.hset(self.ip_rule_key, '127.0.0.1', '{}')
	# 	self.assertEqual(self.r.hget(self.ip_rule_key, '127.0.0.1'), '{}')
	# 	self.r.hdel(self.ip_rule_key, '127.0.0.1')

	def test_get_ip(self):
		c = Manager(ip='123.0.0.1', project_name='guangdong')
		result = c.get_ip()
		c = Manager(ip='122.0.0.1', project_name='baidu')
		result = c.get_ip()
		# self.assertEqual(type(result), dict)
		# self.assertEqual(result.get('is_granted', 'False'), True)

	def test_get_reference_dict(self):
		pass
		# self.r.hset(self.ip_rule_key, '127.0.0.1', '{"baidu":}')

if __name__ == '__main__':
	m = ManagerTestCase()
	m.run()