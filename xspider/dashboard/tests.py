from django.test import TestCase
from dashboard.handler import Query
from dashboard.handler import Handler
# Create your tests here.


class HandlerTest(TestCase):

	def setUp(self):
		pass

	def tearDump(self):
		pass


	# def test_query_nodes_in_redis(self):
	# 	query = Query()
	# 	local_ip_list, proxies_ip_list = query.query_nodes_in_redis()
	# 	print local_ip_list
	# 	print proxies_ip_list

	def test_query_nodes_in_redis_2(self):
		handler = Handler()
		result = handler.query_nodes_in_redis()
		print result