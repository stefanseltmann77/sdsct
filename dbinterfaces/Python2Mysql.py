# -*- coding: utf-8 -*-
import codecs
from sdsct.dbinterfaces.Python2Database import Python2Database
from abc import ABCMeta, abstractmethod


class Python2Mysql(Python2Database): #XXX abstract class
    __metaclass__ = ABCMeta
    """Basic class for access to a MySql-database."""
    
    DEFAULT_PORT = 3306

    def build_createTableQuery(self, sourceTable, targetTable = None):
        return self.query("SHOW CREATE TABLE {}".format(sourceTable), echo=False)[0][1]    

    def get_tableFields(self, tableName, echo=False): #XXXX veraltet!!!
        raise DeprecationWarning
        """Returns all names of fields or columns from the given table in correct order"""
        return [row[0] for row in self.query("DESCRIBE {}".format(tableName), echo=echo)]
    
    def get_tableDescription(self, table): ##XXXX veraltet!!
        raise DeprecationWarning
        """Query the descripton of a database table and reformat the output to a dictionary with fieldnames as keys."""
        tableDescription = self.query_result("DESCRIBE {}".format(table), echo = False)
        if 'Field' in tableDescription[0]:
            return {row['Field']:row for row in tableDescription}
        else:
            raise Exception("Table description contains no fields! You probable inserted a select-query instead of a tablename!")             
        
    def query_primaryKey(self, tableName):
        tableDescription = self.query_result("DESCRIBE {}".format(tableName), False)
        for row in tableDescription:
            if row['Key'] == 'PRI':
                return row['Field']
        else:
            return None        

    def get_primaryKey(self,tableName):
        raise DeprecationWarning
        return self.query_primaryKey(tableName)

    ###XXX decorator für tablename check einbaucen
    def query_tableColumns(self, tableName):
        return self.query_result("SELECT * FROM information_schema.`COLUMNS` WHERE table_schema = %s and table_name = %s", values= tableName.split('.'))

    def query_tableColumnNames(self, tableName):
        raise DeprecationWarning
        try:
            schema, table = tableName.split('.')
        except ValueError:
            raise Exception('Please provide the table name complete with its schema, e.g. schema.table!')
        return self.query_list("SELECT column_name FROM information_schema.`COLUMNS` WHERE table_schema = %s and table_name = %s", values=(schema, table))

    def schema_exists(self, schemaName):
        """Checks the existence of a schema in the metadata of the db-server"""
        if self.query_value("SELECT count(*) FROM information_schema.schemata WHERE schema_name = '{}'".format(schemaName), echo = False)==0:
            return False
        else:
            return True

    def upload_table(self, filename, target, separator = '\t', encoding='utf-8', lineSeparator = '\r\n', qualifier = None):
        f = codecs.open(filename, "r", encoding)
        #content = f.read().split(lineSeparator)
        content = f.readline().split(lineSeparator)
        f.close()
        columnnames = content[0].replace('/','').split(separator)
        columnnames = [chunk.replace('ß','ss').replace(' ','').replace(r'\r\n','').replace('\r\n','').replace(r'\n','').replace('\n','').replace('\r','').replace('.','').replace('-','_').replace('%','') for chunk in columnnames]
        columnnames = [chunk.replace('ä','ae').replace('ü','ue').replace('ö','oe') for chunk in columnnames  if chunk !='']
        columns=[]
        target = '.'.join(["`{}`".format(chunk)  for chunk in target.split('.')]) 
        for name in columnnames:
            columns.append("`{}` VARCHAR(160) COLLATE utf8_unicode_ci DEFAULT NULL".format(name))
        varString = ',\n'.join(columns)
        self.query("DROP TABLE IF EXISTS "+target)
        query = """
        CREATE TABLE {}(
                {}
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci""".format(target, varString)
        self.query(query)

        if qualifier:
            qualifier = " ENCLOSED BY '{}' ".format(qualifier)
        else:
            qualifier= ''
        
        query = """LOAD DATA LOCAL INFILE  '{filename}' 
                INTO TABLE {target} FIELDS terminated BY '{separator}' {qualifier} IGNORE 1 LINES""".format(filename=filename, target=target, separator=separator, qualifier=qualifier)
        self.query(query)
        self.commit()                

    def query_schemaTables(self):
        raise DeprecationWarning

    def query_schema_table_names(self, schema_name=None):# todo XXX current Schema als default!
        """Query the names of all tables of a schema and return them as a list.

        If the schema_name is omitted, the name of the currently used default schema will be used.

        :param schema_name: name of the schema
        :type schema_name: str
        :return: list of table names
        :type return: list
        """
        table_names = self.query_list("SELECT table_name FROM information_schema.`TABLES` WHERE table_schema = %s",
                                      params=(schema_name,))
        return table_names

    def query_table_column_names(self, table_name, schema_name=None):# todo XXX current Schema als default!
        """Query the names of all columns of a table.

        If the schema name is provided in different ways, this priority will be used:
        schema name extracted from table name > schema name stated in second argument > default schema name of connection

        :param table_name: name of the table, either like 'schema.table' or with schema in the second argument
        :type table_name: str
        :param schema_name: name of the schema, if not already stated in the table name.
        :type schema_name: str
        :return:
        """
        if schema_name:
            raise NotImplementedError
        try:
            schema, table = table_name.split('.')
        except ValueError:
            raise Exception('Please provide the table name complete with its schema, e.g. schema.table!')
        return self.query_list("SELECT column_name "
                               "FROM information_schema.`COLUMNS` "
                               "WHERE table_schema = %s and table_name = %s",
                               params=(schema, table), is_meta=True)

    def drop_table(self, table_name, affirmation = True):
        if affirmation:
            if input('Do you really want to drop table :{}? Please type YES:\n'.format(table_name)) == 'YES':
                self.query("DROP TABLE IF EXISTS {}".format(table_name))
                return True
            else:
                return False
        else:
            self.query("DROP TABLE IF EXISTS {}".format(table_name))
            return True

    def query_schema_current(self):
        return self.query_value('SELECT DATABASE()', echo=False, is_meta=True)

    def _resolve_params_for_output(self, sql_txt, params):
        return sql_txt

class MYSQL_DBTable(object):
    def __init__(self, schemaName, tableName, dbHandle):
        self.db = dbHandle
        self.schemaName, self.tableName = schemaName, tableName
        self.columnNames = self.db.query_tableColumnNames(tableName, echo=False)
        self.columns = {}

    def truncate(self, affirmation=False, echo=True):
        if affirmation==False:
            self.db.query('TRUNCATE `{}`.`{}`'.format(self.schemaName,self.tableName), echo=echo);

    def insert_row(self, data, echo=False):
        self.db.insert_row(self.tableName, data, echo)

    def insert_rows(self, data, echo=False):
        for row in data:
            self.insert_row(self.tableName, row, echo)
