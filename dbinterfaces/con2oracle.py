# -*- coding: utf-8 -*-
from sdsct.dbinterfaces.con2database import Con2Database
import cx_Oracle

class Python2Oracle(Con2Database):
    def connect (self, user=None, password=None, dsn=None, host=None, port=None, sid=None):
        """Start the connection to a DataBase.
        Keyword arguments:
        user -- string, username of database account
        password -- string, password
        dsn -- string, data source name 
        """
        if not dsn and host and port and sid:
            dsn = cx_Oracle.makedsn(host, port , sid)
#            self.conn = cx_Oracle.connect(user, "ae_hds", cx_Oracle.makedsn(host, port , sid))
#            self._cursor = cx_Oracle.Cursor(self.conn)
#        elif dsn:
        self.conn = cx_Oracle.connect(user, password, dsn)
        if self.conn:
            self._cursor = cx_Oracle.Cursor(self.conn)
        else:
            raise Exception #XXXX

    def drop_table(self, table, affirmation = True): ## TODO corrigieren!
        """Drops a table if the table already exists"""
        if 1 == self.query_value("SELECT count(*) FROM user_tables WHERE table_name = upper('{}')".format(table), echo = False, is_meta=True): # FIXME Rework with params
            if affirmation:
                if input('Do you really want to drop table :'+table+'? Please type YES:\n') != 'YES':
                    return False
            self.query("DROP TABLE %s PURGE" % table)
            return True # FIXME rework auslagenr
        else:
            return False

    def build_createTableQuery(self, sourceTable, targetTable = None):
        """XXXXX beta"""
        oracleVarNames = []
        for field in self.get_tableFields('assets'):
            if tableDescription[field]['Type'].find('int'):
                oracleVarNames.append( field+' number(20) ')
            elif tableDescription[field]['Type'].find('char'):
                oracleVarNames.append( field+' varchar(255) ')
        createSyntax = "CREATE TABLE %s (%s)" % (targetTable,','.join(oracleVarNames))
        return createSyntax

    def query_tableColumns(self, tableName):
        raise NotImplementedError

    def query_schema_table_names(self, schema_name=None):
        raise NotImplementedError

    def query_table_column_names(self, table_name, schema_name=None):# XXX todo: needs refinement default, TODO: change as params
        table_name, schema_name = self._resolve_table_name(table_name, schema_name)
        return self.query_list("SELECT column_name FROM all_tab_columns "
                               "WHERE owner = upper('{}') and table_name = upper('{}') "
                               "ORDER BY column_id".format(table_name, schema_name), is_meta=True)

    def query_schema_current(self):
        raise NotImplementedError

    def insert_row(self):
        raise NotImplementedError

    def import_table(self, sourceDB, tableName):
        self.drop_table(tableName, affirmation = 'NO')
        self.query(sourceDB.build_createQuery(tableName, type ='Oracle'))
        self.insert_rows(tableName, sourceDB.query('SELECT * FROM '+tableName), echo = False)    
        self.commit()

        