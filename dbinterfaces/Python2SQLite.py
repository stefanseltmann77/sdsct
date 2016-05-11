# -*- coding: utf-8 -*-
from sdsct.dbinterfaces.Python2Database import Python2Database
import sqlite3

class Python2SQLite(Python2Database):
    """Basic class for access to a sqlite-database."""

    def __init__(self, database=None):
        super(Python2SQLite, self).__init__()
        if database:
            self.connect(database)

    def connect(self, database):
        self.conn = sqlite3.connect(database)
        self._cursor = self.conn.cursor()

    def _execute(self, sql_txt: str, params):
        """Hook to facilitate customized error message!

        :param sql_txt: complete query as a string
        :param params: dictionary or tuple or list containing the data
        :type params: dict | list | tuple
        :return:
        """
        if params:
            self._cursor.execute(sql_txt, params)
        else:
            self._cursor.execute(sql_txt)

    def query_schema_table_names(self, schema_name: str = None) -> list:
        """Query the names of all tables of a schema and return them as a list.

        If the schema_name is omitted, the name of the currently used default schema will be used.

        :param schema_name: name of the schema
        :return: list of table names
        """
        tbl_names = self.query("SELECT tbl_name FROM sqlite_master WHERE type='table'", echo=False, is_meta=True)
        return [name[0] for name in tbl_names]

    def query_table_column_names(self, table_name: str, schema_name: str = None) -> list:
        """Query the names of all columns of a table.

        If the schema name is provided in different ways, this priority will be used:
        schema name extracted from table name > schema name stated in second argument >
            default schema name of connection

        :param table_name: name of the table, either like 'schema.table' or with schema in the second argument
        :param schema_name: name of the schema, if not already stated in the table name.
        :return: list of columns
        """
        tbl_description = self.query("Pragma table_info({})".format(table_name), echo=False, is_meta=True)
        return [column[1] for column in tbl_description]

