# -*- coding: utf-8 -*-
import datetime
import re
import sys
from collections import namedtuple
from io import StringIO
from abc import ABCMeta, abstractmethod


class Python2Database(object):
    """Basic declarative wrapper for database access.

    Must be derived for DB-specific adapters. The goal of this wrapper is
    to give easy and readable access to a database regardless which technology it uses.

    # TODO strict mode, so that the schema has to be posted always
    """

    __metaclass__ = ABCMeta

    QT_SELECT = 1
    """Constants for query types"""
    OS_DATABASE, OS_STDOUT, OS_STRINGIO = 1, 2, 3
    """Constants for OutputStreams"""
    RF_NAMEDTUPLE, RF_DICT = 1, 2
    """Constants for return formats"""
    IM_INSERT, IM_REPLACE = 1, 2
    """Constants for insert modes"""
    echo_sql = True
    """if True, sql-Statements will be posted by default at execution time."""
    text_only = False  # Deprecated
    """if True, sql-Statements will only be posted to output instead of run as a query."""
    _output_streams = {OS_DATABASE, OS_STDOUT}
    """three possibilities to direct SQL-statements.
    Send it to the "database", send it to the console via 'stdout' and/or send it to 'StringIO'."""
    commit_on_close = False
    """bool, if True, all pending transactions will be committed when closing the connection."""
    _query_buffer = None
    """StringIO-writable that can be chosen as a target for all processed sql queries."""
    namedtuples_used = False
    """if True, all results with multiple rows will be returned as named tuples."""
    _cursor = None
    """Cursor object, provided by the system specific module."""
    conn = None
    """Connection object, provided by the system specific module."""
    records_num = 0
    """contains the number of affected records of the latest query"""
    _records_affected_minimum = -1  # TODO implement check on minimum affected rows
    """if set to a number > 0 it can be used to check whether queries run empty or with to few rows."""

    def __init__(self):
        self._query_buffer = StringIO()

    def __del__(self) -> None:
        """Make sure to close all connections when ending script by calling close()"""
        self.close()

    @abstractmethod
    def connect(self, dsn: str, user: str, password: str, host: str, database: str) -> None:
        """Establish a connection to a database

        :param dsn:
        :param user:
        :param password:
        :param host: ip or address of host
        :param database: name of database schema
        """

    @abstractmethod
    def insert_row(self, table_name: str, params: dict, echo: bool = None, mode: int = IM_INSERT):
        """Insert a single row into the given table based on a dictionary or named tuple.

        :param table_name: name of the target table
        :param params: dictionary or tuple or list containing the data
        :type params: dict | namedtuple
        :param echo: trigger echo of SQL statement
        :param mode: IM_INSERT | IM_REPLACE
        :return:
        """

    def close(self, commit: bool = commit_on_close):
        """Close all connections and commit, if set by default.

        :param commit:
        """
        if commit:
            self.commit()
        # Code split for different python versions.
        if self._cursor and sys.version_info[0] == 2:
            self._cursor.close()
        if self.conn and sys.version_info[0] == 2:
            self.conn.close()

    def commit(self):
        """Commit all pending transaction on the current connection."""
        self.conn.commit()

    def rollback(self):
        """Perform a rollback on all pending transactions."""
        self.conn.rollback()

    def _execute_query(self, sql_txt: str, params: dict, echo: bool, is_meta: bool):
        """Internal interface that sends all queries to a database or output buffers.

        :param sql_txt: complete query as a string
        :param params: dictionary or tuple or list containing the data
        :type params: dict | namedtuple
        :param echo: trigger echo of SQL statement
        :param is_meta: when is_meta, then query will be executed always, even in debug or plain text mode.
                        used for queries that provide the metadata for other queries.
        :return:
        """
        self.params = params  # TODO replace with other solution. is just for mogrify in postgresql

        if (self.OS_STRINGIO in self._output_streams or self.OS_STDOUT in self._output_streams) \
                and not is_meta and (echo or (echo is None and self.echo_sql)):
            sql_txt_output = self.beautify_sql(sql_txt, params)
        else:
            sql_txt_output = None
        if self.OS_DATABASE in self._output_streams:
            if not self._cursor:
                raise Exception('No _cursor, no connection open!')
            else:
                start_dts = datetime.datetime.now()
                if sql_txt_output:
                    if self.OS_STDOUT in self._output_streams:
                        print(sql_txt_output, file=sys.stdout)
                    if self.OS_STRINGIO in self._output_streams:
                        self._query_buffer.write(sql_txt_output + "\n\n")
                self._execute(sql_txt, params)

                self.records_num = self._cursor.rowcount
                if sql_txt_output:
                    end_dts = datetime.datetime.now()
                    sql_txt_footer = "--Affected Rows: {}, Duration: {}, Finished: {}".format(self.records_num,
                                                                                              str(end_dts - start_dts),
                                                                                              datetime.datetime.now())
                    if self.OS_STDOUT in self._output_streams:
                        print(sql_txt_footer, file=sys.stdout)
                    if self.OS_STRINGIO in self._output_streams:
                        self._query_buffer.write(sql_txt_footer + "\n\n")
        else:
            if sql_txt_output:
                if self.OS_STDOUT in self._output_streams:
                    print(sql_txt_output, file=sys.stdout)
                if self.OS_STRINGIO in self._output_streams:
                    self._query_buffer.write(sql_txt_output + "\n\n")
            return None

    def _execute(self, sql_txt: str, params):
        """Hook to facilitate customized error message!

        :param sql_txt: complete query as a string
        :param params: dictionary or tuple or list containing the data
        :type params: dict | list | tuple
        :return:
        """
        self._cursor.execute(sql_txt, params)

    def query(self, sql_txt: str, params=None, echo: bool = None, is_meta: bool = False):  # , query_type: bool = None):
        """Execute a query, without further refinement of the return values.

        Use this for queries without return values. e.g. DDL and Updates.
        :param sql_txt: complete query as a string
        :param params: dictionary or tuple or list containing the data
        :type params: dict | list | tuple
        :param echo: trigger echo of SQL statement
        :param is_meta: when is_meta, then query will be executed always, even in debug or plain text mode.
                             used for queries that provide the metadata for other queries.
        :return: None | dict | namedtuple
        """
        self._execute_query(sql_txt=sql_txt, params=params, echo=echo, is_meta=is_meta)  # , query_type=query_type)
        return self._cursor.fetchall() if self._cursor and self._cursor.description else None

    def query_value(self, sql_txt: str, params=None, echo: bool = None, is_meta: bool = False):
        """Returns the result of a query producing a single value

        :param sql_txt: complete query as a string
        :param params: dictionary or tuple or list containing the data
        :type params: dict | list | tuple
        :param echo: trigger echo of SQL statement
        :param is_meta: when is_meta, then query will be executed always, even in debug or plain text mode.
                        used for queries that provide the metadata for other queries.
        :return:"""
        self._execute_query(sql_txt, echo=echo, params=params, is_meta=is_meta)  # query_type=self.QT_SELECT,
        result = self._cursor.fetchone() if self._cursor else None
        if result:
            if len(result) > 1:
                msg_error = "ABORT: For the query of a single value, multiple columns have been detected" \
                            "in the resultset!\n\nQUERY: {}".format(sql_txt)
                raise Exception(msg_error)
            else:
                return result[0]
        else:
            return None

    def query_row(self, sql_txt: str, params=None, echo: bool = None, is_meta: bool = False,
                  return_format: int = RF_NAMEDTUPLE):
        """Return a single row query as a dict or named tuple

        :param sql_txt: complete query as a string
        :param params: dictionary or tuple or list containing the data
        :type params: dict | list | tuple
        :param echo: trigger echo of SQL statement
        :param is_meta: when is_meta, then query will be executed always, even in debug or plain text mode.
                used for queries that provide the metadata for other queries.
        :param return_format:
        :return:
        """
        self._execute_query(sql_txt, echo=echo, params=params, is_meta=is_meta)  # query_type=self.QT_SELECT,
        field_names, result = self.get_fields_of_cursor(), self._cursor.fetchone()
        if not self.namedtuples_used or return_format == self.RF_DICT:
            return {fieldName: result[field_names.index(fieldName)] for fieldName in field_names} if result else None
        else:
            record = namedtuple('record', field_names)
            return record(*result)

    def query_result(self, sql_txt: str, params=None, echo: bool = None, is_meta: bool = False,
                     return_format: int = RF_NAMEDTUPLE):
        """Return a multi-row-query as a list of dicts or named tuples

        :param sql_txt: complete query as a string
        :param params: dictionary or tuple or list containing the data
        :type params: dict | list | tuple
        :param echo: trigger echo of SQL statement
        :param is_meta: when is_meta, then query will be executed always, even in debug or plain text mode.
                used for queries that provide the metadata for other queries.
        :param return_format:
        :return:
        """
        self._execute_query(sql_txt, echo=echo, params=params, is_meta=is_meta)  # query_type=self.QT_SELECT,
        field_names = self.get_fields_of_cursor()
        result = self._cursor.fetchall()
        if not self.namedtuples_used or return_format == self.RF_DICT:
            return SqlResultTable(sql_txt, field_names, [{field_name: row[field_names.index(field_name)]
                                                          for field_name in field_names}
                                                         for row in result]) if result else None
        else:
            record = namedtuple('record', field_names)
            return SqlResultTable(sql_txt, field_names, [record(*row) for row in result]) if result else None

    def query_list(self, sql_txt: str, params=None, echo: bool = None, is_meta: bool = False):
        """Return a single column query as a list object

        :param sql_txt: complete query as a string
        :param params: dictionary or tuple or list containing the data
        :type params: dict | list | tuple
        :param echo: trigger echo of SQL statement
        :param is_meta: when is_meta, then query will be executed always, even in debug or plain text mode.
                used for queries that provide the metadata for other queries.
        :return:
        """
        self._execute_query(sql_txt, echo=echo, params=params, is_meta=is_meta)  # query_type=self.QT_SELECT,
        if self._cursor.rowcount != -1 and self._cursor.rowcount != 0 and self._cursor.rowcount is not None:
            # TODO simplify
            result = self._cursor.fetchall()
        else:
            result = []
        if len(result) > 0 and len(result[0]) > 1:  # TODO why two conditions
            msg_error = "ERROR: For the creation of the result list multiple columns " \
                        "where used instead of just one. Query aborted!"
            raise Exception(msg_error)
        return [row[0] for row in result] if result else None

    def query_dict(self, sql_txt: str, params=None, echo: bool = None, is_meta: bool = False) -> dict:
        """Return a dual column query as a dict/mapping

        :param sql_txt: complete query as a string
        :param params: dictionary or tuple or list containing the data
        :type params: dict | list | tuple
        :param echo: trigger echo of SQL statement
        :param is_meta: when is_meta, then query will be executed always, even in debug or plain text mode.
                used for queries that provide the metadata for other queries.
        """
        self._execute_query(sql_txt, echo=echo, params=params, is_meta=is_meta)  # query_type=self.QT_SELECT, i
        result = self._cursor.fetchall()
        if result and len(result[0]) != 2:
            msg_error = "ERROR: For he creation of the dict mapping only two columns are allowed. Query aborted! "
            raise Exception(msg_error)
        return {row[0]: row[1] for row in result} if result else None

    def query_resource(self, sql_txt: str, params=None, echo: bool = None, is_meta: bool = False) -> _cursor:
        """Execute a query and return the raw cursor as a result

        :param sql_txt: complete query as a string
        :param params: dictionary or tuple or list containing the data
        :type params: dict | list | tuple
        :param echo: trigger echo of SQL statement
        :param is_meta: when is_meta, then query will be executed always, even in debug or plain text mode.
                used for queries that provide the metadata for other queries.
        """
        self._execute_query(sql_txt=sql_txt, params=params, echo=echo, is_meta=is_meta)  # , query_type=self.QT_SELECT
        return self._cursor

    @abstractmethod
    def query_schema_table_names(self, schema_name: str = None) -> list:
        """Query the names of all tables of a schema and return them as a list.

        If the schema_name is omitted, the name of the currently used default schema will be used.

        :param schema_name: name of the schema
        :return: list of table names
        """
        raise NotImplementedError

    @abstractmethod
    def query_table_column_names(self, table_name: str, schema_name: str = None) -> list:
        """Query the names of all columns of a table.

        If the schema name is provided in different ways, this priority will be used:
        schema name extracted from table name > schema name stated in second argument >
            default schema name of connection

        :param table_name: name of the table, either like 'schema.table' or with schema in the second argument
        :param schema_name: name of the schema, if not already stated in the table name.
        :return: list of columns
        """
        raise NotImplementedError

    @abstractmethod
    def drop_table(self, table_name: str, affirmation: bool=True) -> bool:
        """Drop a table.

        :param table_name: name of table to be dropped
        :param affirmation: if affirmation is not true, it will be done automatically, else you have to affirm.
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def query_schema_current(self) -> str:
        """Query name of current schema or database"""
        raise NotImplementedError

    def insert_rows(self, table_name: str, rows, echo: bool = None, mode: int = IM_INSERT) -> None:
        """Insert multiple rows into the given table based on a list or tuple of dictionaries or named tuples.

        :param table_name: name of the target table
        :param rows: a tuple or list of rows
        :param echo: trigger echo of SQL statement
        :param mode: IM_INSERT | IM_REPLACE
        """
        for row in rows:
            self.insert_row(table_name, row, echo=echo, mode=mode)

    def schema_exists(self, schema_name: str) -> bool:
        """check if a schema or database already exists

        :param schema_name: name of database
        """
        raise NotImplementedError

    def get_fields_of_cursor(self):  # rework content
        """Return all names of fields or columns form the last query"""
        return [row[0] for row in self._cursor.description] if self._cursor.description else None

    def beautify_sql(self, sql_txt: str, params=None) -> str:
        """Reformat a sql query for better readability.

        This method should be overridden to implement the platform specific parameter styles.
        The resulting string should only be used for readable output and not for query execution
        for the parameters might be resolved differently.

        :param sql_txt: complete query as a string
        :param params: dictionary or tuple or list containing the parameters to insert into the query
        :type params: dict | list | tuple
        :return: reformatted string of sql statement.
        """
        sql_txt = sql_txt.strip()
        sql_txt = sql_txt + ';' if not sql_txt.endswith(';') else sql_txt
        sql_txt = '\n'.join([line.strip() for line in sql_txt.split('\n')]) + '\n\n'
        sql_txt = re.sub(' +', ' ', sql_txt)
        sql_txt = sql_txt.replace('\n, ', '\n,    ')
        sql_txt = sql_txt.replace('\nUSING', '\n    USING')
        sql_txt = self._resolve_params_for_output(sql_txt, params)
        sql_txt = "\n".join([line for line in [line.strip() for line in sql_txt.split("\n")]])
        return sql_txt

    @abstractmethod
    def _resolve_params_for_output(self, sql_txt: str, params) -> str:
        return sql_txt

    def clear_query_buffer(self):
        """Resets the query buffer and deletes stored sql-statements

        :return:
        """
        self._query_buffer.truncate(0)
        self._query_buffer.seek(0)

    def _resolve_table_name(self, table_name: str, schema_name: str = None) -> tuple:
        """Parses the schema_name from the table_name or fills in the current schema

        :param table_name: name of database table, with or without schema_name
        :param schema_name: name of the database
        :return:
        """
        if not schema_name:
            try:
                schema_name, table_name = table_name.split('.')
            except ValueError:
                schema_name, table_name = self.query_schema_current, table_name
        return table_name, schema_name

    @property
    def query_buffer(self):
        return self._query_buffer.getvalue()

    @query_buffer.setter
    def query_buffer(self, input_buffer):
        raise Exception('Readonly!')


class SqlResultTable(list):
    def __init__(self, sql_txt: str, field_names=None, *args, **kwargs):
        super(SqlResultTable, self).__init__(*args, **kwargs)
        self.sql_txt = sql_txt
        self.field_names = field_names
        self.query_duration = 0  # TODO add content
        self.query_timestamp = 0  # TODO add content

    def __str__(self):
        str_output = ""
        if self.__len__() <= 20:
            str_output += "\n".join([str(row) for row in self])
        else:
            str_output += "\n".join([str(row) for row in self[0:10]])
            str_output += "\n...\n"
            str_output += "\n".join([str(row) for row in self[-10:]])
        return str_output
