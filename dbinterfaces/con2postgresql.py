# -*- coding: utf-8 -*-
from sdsct.dbinterfaces.con2database import Con2Database
import psycopg2


class Con2PostgreSQL(Con2Database):
    """Basic class for access to a Python2PostgreSQL-database."""
    
    DEFAULT_PORT = 5432

    def connect(self, dsn: str = None,
                user: str = None, password: str = None,
                host: str = None, database: str = None, port: int = DEFAULT_PORT) -> None:
        """Establish a connection to a database

        :param dsn: complete dsn string or name
        :param user: username
        :param password: password for username
        :param host: ip or address of host
        :param database: name of database schema
        :param port: port if not default port of db application
        """
        self.conn = psycopg2.connect(host=host, user=user, password=password, database=database, port=port)
        self._cursor = self.conn.cursor()
        if not self._cursor:
            raise Exception("No connection established to {}".format(host))

    def query_schema_table_names(self, schema_name: str = None) -> list:
        """Query the names of all tables of a schema and return them as a list.

        If the schema_name is omitted, the name of the currently used default schema will be used.

        :param schema_name: name of the schema
        :return: list of table names
        """
        return self.query_list("""-- noinspection SqlNoDataSourceInspection
            SELECT table_name
            FROM information_schema.tables
            WHERE   table_type = 'BASE TABLE'
                and UPPER(table_schema) = UPPER(%s)
            """, params=(schema_name,), echo=False, is_meta=True)

    def query_schema_current(self) -> str:
        """Query name of current schema or database"""
        return self.query_value('SELECT current_schema()', echo=False, is_meta=True)

    def query_table_column_names(self, table_name: str, schema_name: str = None) -> list:
        """Query the names of all columns of a table.

        If the schema name is provided in different ways, this priority will be used:
        schema name extracted from table name > schema name stated in second argument >
            default schema name of connection

        :param table_name: name of the table, either like 'schema.table' or with schema in the second argument
        :param schema_name: name of the schema, if not already stated in the table name.
        :return: list of columns
        """
        table_name, schema_name = self._resolve_table_name(table_name, schema_name)
        return self.query_list("""-- noinspection SqlNoDataSourceInspection
            SELECT column_name
            FROM information_schema.columns
            WHERE
                    UPPER(table_name)   = UPPER(%(table_name)s)
                and UPPER(table_schema) = UPPER(%(schema_name)s)
            ORDER BY ordinal_position """,
                               params=dict(table_name=table_name, schema_name=schema_name),
                               echo=False, is_meta=True)

    def drop_table(self, table_name: str, affirmation: bool = True) -> bool:
        """Drop a table.

        :param table_name:
        :param affirmation: if affirmation is not true, it will be done automatically, else you have to affirm.
        :return: true if actually dropped
        """
        if affirmation:
            if input('Do you really want to drop table :{}? Please type YES:\n'.format(table_name)) == 'YES':
                self.query("DROP TABLE IF EXISTS {} CASCADE ".format(table_name))
                return True
            else:
                return False
        else:
            self.query("DROP TABLE IF EXISTS " + table_name)
            return True

    def insert_row(self, table_name: str, params: dict, echo: bool = None, mode: int = Con2Database.IM_INSERT):
        """Insert a single row into the given table based on a dictionary or named tuple.

        :param table_name: name of the target table
        :param params: dictionary or tuple or list containing the data
        :type params: dict | namedtuple
        :param echo: trigger echo of SQL statement
        :param mode: IM_INSERT | IM_REPLACE
        :return: None or new insert ID, depending on implementation
        """
        raise NotImplemented()

    def insert_rows(self, table_name: str, rows, echo: bool = None, mode: int = Con2Database.IM_INSERT) -> None:
        """Insert multiple rows into the given table based on a list or tuple of dictionaries or named tuples.

        :param table_name: name of the target table
        :param rows: a tuple or list of rows
        :param echo: trigger echo of SQL statement
        :param mode: IM_INSERT | IM_REPLACE
        """
        super().insert_rows(table_name, rows, echo, mode)

    def _resolve_params_for_output(self, sql_txt: str, params) -> str:
        return self._cursor.mogrify(sql_txt, params).decode("utf-8")
