from unittest import TestCase
from sdsct.dbinterfaces.con2sqlite import con2sqlite

__author__ = 's.seltmann'


class TestCon2Database(TestCase):
    def setUp(self):
        self.db = con2sqlite(database=':memory:')

    def test_connect(self):
        self.fail()

    def test_insert_row(self):
        self.fail()

    def test_close(self):
        self.fail()

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

    def test_query_value(self):
        self.fail()

    def test_query_row(self):
        self.fail()

    def test_query_result(self):
        self.fail()

    def test_query_list(self):
        self.fail()

    def test_query_dict(self):
        self.fail()

    def test_query_resource(self):
        self.fail()

    def test_query_schema_table_names(self):
        self.fail()

    def test_query_table_column_names(self):
        self.fail()

    def test_drop_table(self):
        self.fail()

    def test_query_schema_current(self):
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
