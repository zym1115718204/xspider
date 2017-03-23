from django.test import TestCase
from dashboard.handler import Query
from dashboard.handler import Handler
# Create your tests here.


class HandlerTest(TestCase):

	def setUp(self):
		pass

	def tearDump(self):
		pass


	def test_query_nodes_in_redis(self):
		query = Query()
		result = query.query_nodes_in_redis(node='122.0.0.1')
		print result
		

	def test_query_nodes_in_redis_2(self):
		handler = Handler()
		result = handler.query_nodes_in_redis()
		print result