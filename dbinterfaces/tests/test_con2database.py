from unittest import TestCase
from sdsct.dbinterfaces.con2sqlite import con2sqlite
import io
import sys

__author__ = 's.seltmann'


class TestCon2Database(TestCase):
    def setUp(self):
        self.db = con2sqlite(database=':memory:')
        self.db.query("CREATE TABLE testtable (id int, name CHAR); ")
        self.db.query("SELECT * FROM testtable")
        self.db.query("INSERT INTO testtable (id, name) values (1, 'one')")
        self.db.query("INSERT INTO testtable (id, name) values (2, 'two')")
        self.db.query("INSERT INTO testtable (id, name) values (3, 'three')")
        self.db.query("INSERT INTO testtable (id, name) values (4, 'four')")
        self.db.commit()


    def test_connect(self):
        print(self.db._cursor)
        self.assertIsNotNone(self.db._cursor)

    def test_close(self):
        self.db.close()
        self.assertIsNone(self.db._cursor)

    def test_commit(self):
        self.fail()

    def test_rollback(self):
        self.fail()

    def test__execute_query(self):
        self.fail()

    def test__execute(self):
        self.fail()

    def test_query(self):
        self.fail()

    def test_query_result(self):
        self.fail()

    def test_query_list(self):
        self.fail()

    def test_query_dict(self):
        self.fail()

    def test_query_resource(self):
        self.fail()

    def test_query_table_column_names(self):
        self.fail()

    def test_drop_table(self):
        self.fail()

    def test_insert_rows(self):
        self.fail()

    def test_schema_exists(self):

        self.fail()

    def test_get_fields_of_cursor(self):
        self.fail()

    def test_beautify_sql(self):
        self.fail()

    def test__resolve_params_for_output(self):
        self.fail()

    def test_clear_query_buffer(self):
        self.fail()

    def test__resolve_table_name(self):
        self.fail()

    def test_query_buffer(self):
        self.fail()

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

    def test_silent_mode_1(self):
        console = io.StringIO()
        sys.stdout = console
        self.db._output_streams = {self.db.OS_DATABASE}
        self.db.query("SELECT 1")
        self.assertEqual("", console.getvalue())

    def test_silent_mode_2(self):
        console = io.StringIO()
        sys.stdout = console
        self.db._output_streams = {self.db.OS_DATABASE}
        self.db.echo_sql = True
        self.db.query("SELECT 1")
        self.assertEqual("", console.getvalue())

    def test_silent_mode_3(self):
        console = io.StringIO()
        sys.stdout = console
        self.db._output_streams = {self.db.OS_DATABASE, self.db.OS_STDOUT}
        self.db.echo_sql = False
        self.db.query("SELECT 1")
        self.assertEqual("", console.getvalue())

    def test_silent_mode_4(self):
        console = io.StringIO()
        sys.stdout = console
        self.db._output_streams = {self.db.OS_DATABASE, self.db.OS_STDOUT}
        self.db.echo_sql = True
        self.db.query("SELECT 1", echo=False)
        self.assertEqual("", console.getvalue())

    def test_silent_mode_5(self):
        console = io.StringIO()
        sys.stdout = console
        self.db._output_streams = {self.db.OS_DATABASE, self.db.OS_STDOUT}
        self.db.echo_sql = False
        self.db.query("SELECT 1", echo=False)
        self.assertEqual("", console.getvalue())

    def test_echo_mode_1(self):
        console = io.StringIO()
        sys.stdout = console
        self.db._output_streams = {self.db.OS_DATABASE, self.db.OS_STDOUT}
        self.db.echo_sql = False
        self.db.query("SELECT 1", echo=True)
        self.assertNotEqual("", console.getvalue())

    def test_echo_mode_2(self):
        console = io.StringIO()
        sys.stdout = console
        self.db._output_streams = {self.db.OS_STDOUT}
        self.db.echo_sql = False
        self.db.query("SELECT 1", echo=True)
        self.assertNotEqual("", console.getvalue())

    def test_echo_mode_3(self):
        console = io.StringIO()
        sys.stdout = console
        self.db._output_streams = {self.db.OS_STDOUT}
        self.db.echo_sql = True
        self.db.query("SELECT 1")
        self.assertNotEqual("", console.getvalue())

    def test_echo_mode_4(self):
        console = io.StringIO()
        sys.stdout = console
        self.db._output_streams = {self.db.OS_STDOUT}
        self.db.query("SELECT 1")
        self.assertNotEqual("", console.getvalue())

    def test_echo_mode_5(self):
        console = io.StringIO()
        sys.stdout = console
        self.db._output_streams = {self.db.OS_STDOUT}
        self.db.echo_sql = True
        self.db.query("SELECT 1", is_meta=False)
        self.assertNotEqual("", console.getvalue())

    def test_echo_mode_6(self):
        console = io.StringIO()
        sys.stdout = console
        self.db._output_streams = {self.db.OS_STDOUT}
        self.db.query("SELECT 1", is_meta=False)
        self.assertNotEqual("", console.getvalue())
