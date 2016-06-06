import io
import sys
from unittest import TestCase
from sdsct.dbinterfaces.con2sqlite import con2sqlite

__author__ = 's.seltmann'


class TestCon2SQLite(TestCase):
    def setUp(self):
        self.db = con2sqlite(':memory:')
        self.db.query("CREATE TABLE testtable (id int, name CHAR); ")
        self.db.query("SELECT * FROM testtable")
        self.db.query("INSERT INTO testtable (id, name) values (1, 'one')")
        self.db.query("INSERT INTO testtable (id, name) values (2, 'two')")
        self.db.query("INSERT INTO testtable (id, name) values (3, 'three')")
        self.db.query("INSERT INTO testtable (id, name) values (4, 'four')")
        self.db.commit()

    def test_connect(self):
        self.db.query("SELECT 1")

    def test_query_schema_table_names(self):
        print(self.db._output_streams)
        self.assertIn('testtable', self.db.query_schema_table_names())

    def test_query_value(self):
        result = self.db.query_value("SELECT 1")
        self.assertEqual(result, 1)

    def test_query_row(self):
        result = self.db.query_row("SELECT 1, 2, 3")
        self.assertIsInstance(result, dict)
        self.assertEqual(result['1'], 1)

    def test_insert_row(self):
        self.db.insert_row(table_name='testtable', params=(1, 2))

    def test_query_schema_current(self):
        schema = self.db.query_schema_current()
        print(schema)

