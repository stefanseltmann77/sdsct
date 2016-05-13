# -*- coding: utf-8 -*-
import sys
import mysql.connector
from .con2mysql import con2mysql
from .con2database import SqlResultTable


class Con2MysqlOracle(con2mysql):
    """Basic class for access to a MySql-database using the genuine Oracle driver."""

    def connect(self, host, user, passwd='', db='', port=3306):
        """Start the connection to a MysqlDatabase.

        :param string host: address of database server, e.g. 127.0.0.1
        :param string user: username of database account
        :param passwd: password
        :param string db: selected database
        :param port: port for service
        :return:
        """
        try:
            self.conn = mysql.connector.connect(host=host, user=user, passwd=passwd, db=db, use_unicode=True, charset='utf8', port=port)  # TODO: work with args?
        except mysql.connector.errors.InterfaceError as exc:
            raise Exception(exc)
        self._cursor = self.conn.cursor(buffered=True)
        self._cursor.execute("SET NAMES 'utf8'")  # TODO: cursor-methoden verwenden
        self._cursor.execute("SET CHARACTER SET 'utf8'")  # TODO: cursor-methoden verwenden

    def insert_row(self, table_name: str, params, echo: bool=None, mode: int=con2mysql.IM_INSERT, debug: bool=False,
                   column_names: tuple=None):
        """Insert a single row into the given table based on a dictionary.

        :param table_name: name of the target table
        :param params: dict, list or tuple of values
        :param echo: printback of SQL-statment
        :param mode:
        :param debug:
        :param column_names: names for the columns only if no dict is passed for the values
        :return:
        """
        if sys.version.startswith('3'): #bug with different interpretation of %s in the drivers of different versions.
            if not isinstance(params, dict):  # TODO: rework for params!
                if column_names:
                    query_txt = " INTO  {} ({}) \n\tVALUES ({})".format(table_name,
                                                                        ','.join(['`{}`'.format(name) for name in column_names]),
                                                                        ','.join(['%s' for value in params]))
                    if mode == con2mysql.IM_INSERT:
                        return self._execute_query('INSERT' + query_txt, echo=echo, params=params, is_meta=False)
                    elif mode == con2mysql.IM_REPLACE:
                        return self._execute_query('REPLACE' + query_txt, echo=echo, params=params)
                    else:
                        raise Exception ('wrong insert mode. Only "insert" or "replace" allowed!')
                else:
                    raise Exception('You have to pass the values either as dicts or you have to provide column_names!')
            else:
                insert_array = {key: params[key] for key in params.keys() if params[key] != None} #clean empty keys
                query_txt = " INTO  {} ({}) \n\tVALUES ({})".format(table_name, ','.join(['`' + key + '`' for key in insert_array.keys()]), ','.join(["%({})s".format(key) for key in insert_array]))
                if mode == con2mysql.IM_INSERT:
                    return self._execute_query('INSERT' + query_txt, echo=echo, params=insert_array, is_meta=False)
                elif mode == con2mysql.IM_REPLACE:
                    return self._execute_query('REPLACE' + query_txt, echo=echo, params=insert_array, is_meta=False)
                else:
                    raise Exception ('wrong insert mode. Only "insert" or "replace" allowed!')
        else:
            # TODO entfernen
            insert_array = {key: params[key] for key in params.keys() if params[key] != None} #clean empty keys
            query_txt = " INTO  {} ({}) \n\tVALUES ({})".format(table_name, ','.join(['`' + key + '`' for key in insert_array.keys()]), ','.join(["%s" for val in insert_array.values()]))
            if mode == 'insert':
                return self._execute_query('INSERT'+query_txt, echo=echo, params=insert_array.values())
            elif mode == 'replace':
                return self._execute_query('REPLACE'+query_txt, echo=echo, params=insert_array.values())
            else:
                raise Exception ('wrong insert mode. Only "insert" or "replace" allowed!')

    def upload_file(self, filename, table_name, delimiter='\t', linebreak='\r\n'):
        if len(table_name.split('.'))==2:
            schema = table_name.split('.')[0]
            if not self.schema_exists(schema):
                raise Exception( "Schema/database '{}' doesn't exist! ".format(schema))
        f = open(filename, 'r')
        columnnames = f.readline().decode('UTF-8-sig').strip().split(delimiter)
        self.query("""
CREATE TABLE IF NOT EXISTS {tableName} (
	{vars}
)
COLLATE='utf8_unicode_ci'
ENGINE=MyISAM
ROW_FORMAT=DYNAMIC;""".format(tableName=table_name, vars =','.join (['`{var}` VARCHAR(255) NULL DEFAULT NULL'.format(var=var) for var in columnnames])))

        self.query("""
LOAD DATA LOCAL INFILE '{file_name}'
    IGNORE
    INTO TABLE {table_name}
    FIELDS
        TERMINATED BY '{delimiter}'
    LINES
        TERMINATED BY '{linebreak}'
    IGNORE 1 LINES""".format(file_name=filename, table_name = table_name, delimiter=delimiter, linebreak=linebreak))

    def _resolve_params_for_output(self, sql_txt: str, params) -> str:
        return sql_txt