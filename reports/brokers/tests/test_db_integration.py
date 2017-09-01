# # coding=utf-8
# import os
# from unittest import TestCase
#
#
# class TestDB(TestCase):
#     def setUp(self):
#         url = os.getenv("DB_TEST_URL")
#         if not url:
#             self.skipTest("No database URL set")
#         self.engine = sqlalchemy.create_engine(url)
#         self.connection = self.engine.connect()
#         self.connection.execute("CREATE DATABASE testdb")
#
#     def tearDown(self):
#         self.connection.execute("DROP DATABASE testdb")
