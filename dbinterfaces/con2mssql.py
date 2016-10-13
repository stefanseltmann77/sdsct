# -*- coding: utf-8 -*-
from sdsct.dbinterfaces.con2database import Con2Database
import pymssql


class Con2MSSql(Con2Database):
    """Basic class for access to a Python2MSSql-database."""

    DEFAULT_PORT = 1433

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
        self.conn = pymssql.connect(server=host, user=user, password=password, database=database, port=port)
        self._cursor = self.conn.cursor()
        if not self._cursor:
            raise Exception("No connection established to {}".format(host))

    def query_list(self, sql_txt: str, params=None, echo: bool = None, is_meta: bool = False) -> list:
        """Return a single column query as a list object

        The function overrides the parent function due to the different behaviour of the rowcount on the used cursor.
        pymssql only sets the rowcount if all columns are already fetched.

        :param sql_txt: complete query as a string
        :param params: dictionary or tuple or list containing the data
        :type params: dict | list | tuple
        :param echo: trigger echo of SQL statement
        :param is_meta: when is_meta, then query will be executed always, even in debug or plain text mode.
                used for queries that provide the metadata for other queries.
        """
        self._execute_query(sql_txt, echo=echo, params=params, is_meta=is_meta)  # query_type=self.QT_SELECT,
        result = self._cursor.fetchall()
        if len(result) > 0 and len(result[0]) > 1:  # TODO why two conditions
            msg_error = "ERROR: For the creation of the result list multiple columns " \
                        "where used instead of just one. Query aborted!"
            raise Exception(msg_error)
        return [row[0] for row in result] if result else None

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
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE
                    UPPER(table_name)   = UPPER(%(table_name)s)
                and UPPER(table_schema) = UPPER(%(schema_name)s)
            ORDER BY ordinal_position """,
                               params=dict(table_name=table_name, schema_name=schema_name),
                               echo=False, is_meta=True)
