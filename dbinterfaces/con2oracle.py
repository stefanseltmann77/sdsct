# -*- coding: utf-8 -*-
from sdsct.dbinterfaces.con2database import Con2Database
import cx_Oracle


class Con2Oracle(Con2Database):
    def connect(self, user=None, password=None, dsn=None, host=None, port=None, sid=None):
        """Start the connection to a DataBase.
        Keyword arguments:
        user -- string, username of database account
        password -- string, password
        dsn -- string, data source name 
        """
        if not dsn and host and port and sid:
            dsn = cx_Oracle.makedsn(host, port, sid)
        try:
            self.conn = cx_Oracle.connect(user, password, dsn)
        except cx_Oracle.DatabaseError:
            raise
        if self.conn:
            self._cursor = cx_Oracle.Cursor(self.conn)
        else:
            raise Exception('No cursor to Oracle available')

    def drop_table(self, table_name: str, affirmation: bool = True) -> bool:
        """Drop a table.

        :param table_name: name of table to be dropped
        :param affirmation: if affirmation is not true, it will be done automatically, else you have to affirm.
        :return: true if actually dropped
        """
        table_name, owner = self._resolve_table_name(table_name)
        if 1 == self.query_value("SELECT count(*) "
                                 "FROM user_tables "
                                 "WHERE table_name = upper(:1)",
                                 params=(table_name,),echo=False, is_meta=True):
            if affirmation:
                if input('Do you really want to drop table :{}? Please type YES:\n'.format(table_name)) != 'YES':
                    return False
            self.query("DROP TABLE {} PURGE".format(table_name))
            return True
        else:
            return False

    # def build_createTableQuery(self, sourceTable, targetTable=None):
    #     """XXXXX beta"""
    #     oracleVarNames = []
    #     for field in self.get_tableFields('assets'):
    #         if tableDescription[field]['Type'].find('int'):
    #             oracleVarNames.append(field + ' number(20) ')
    #         elif tableDescription[field]['Type'].find('char'):
    #             oracleVarNames.append(field + ' varchar(255) ')
    #     createSyntax = "CREATE TABLE %s (%s)" % (targetTable, ','.join(oracleVarNames))
    #     return createSyntax

    def query_schema_table_names(self, schema_name=None):
        raise NotImplementedError

    def query_table_column_names(self, table_name: str,
                                 schema_name: str = None) -> list:  # XXX todo: needs refinement default
        """Query the names of all columns of a table.

        If the schema name is provided in different ways, this priority will be used:
        schema name extracted from table name > schema name stated in second argument >
            default schema name of connection

        :param table_name: name of the table, either like 'schema.table' or with schema in the second argument
        :param schema_name: name of the schema, if not already stated in the table name.
        :return: list of columns"""
        table_name, schema_name = self._resolve_table_name(table_name, schema_name)
        return self.query_list("SELECT column_name FROM all_tab_columns "
                               "WHERE owner = upper(:1) and table_name = upper(:2) "
                               "ORDER BY column_id", params=(schema_name, table_name), is_meta=True)

    def query_schema_current(self):
        raise NotImplementedError

    def insert_row(self):
        raise NotImplementedError

    def import_table(self, sourceDB, tableName):
        self.drop_table(tableName, affirmation='NO')
        self.query(sourceDB.build_createQuery(tableName, type='Oracle'))
        self.insert_rows(tableName, sourceDB.query('SELECT * FROM ' + tableName), echo=False)
        self.commit()

    def _execute(self, sql_txt: str, params) -> None:
        """Hook to facilitate customized error message!

        :param sql_txt: complete query as a string
        :param params: dictionary or tuple or list containing the data
        :type params: dict | list | tuple
        """
        sql_txt = sql_txt.rstrip().rstrip(';')
        if not params:
            self._cursor.execute(sql_txt)
        else:
            self._cursor.execute(sql_txt, params)

    def query_list(self, sql_txt: str, params=None, echo: bool = None, is_meta: bool = False) -> list:
        """Return a single column query as a list object

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
