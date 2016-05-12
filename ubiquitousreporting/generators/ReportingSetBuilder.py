# -*- coding: utf-8 -*-
import os
import copy
import logging
import operator
import datetime
import pickle
from sdsct.ubiquitousreporting.dataobjects.report_tab import TabHead, TabReportDef, TabDef
from sdsct.ubiquitousreporting.dataobjects.report_generic import CodePlan, DataSet, ReportingSet
from sdsct.dbinterfaces.Python2Database import Python2Database

class ReportingSetBuilder(object):
    column_types = ('COUNT', 'COUNT_ABS', 'PCT', 'PCT_SUM', 'SUM_ABS', 'AVG_', 'COUNT_W', 'PCT_W', 'SUM_W', 'AVG_W', 'PCT_GN', 'PCT_GN_W')  # TODO: Replace COUNT with COUNT_ABS
    order_freq_desc = True
    COUNT_W_TOTAL = 'COUNT_W_TOTAL'   # TODO ???
    T_OTHERCODES, T_TOTAL = range(2)
    labels = {T_OTHERCODES: 'Sonstige Werte'}
    categories_number_max = 100
    _caching_mode = None

    def __init__(self, db: Python2Database, database_table: str=None):
        """
        :param db: database handle from sdsct
        :param database_table: string for the table to be analyzed
        : return:
        """
        self.db = db  # database handle
        self.database_table = database_table  # source data table
        self.filter_base = None   # global filter for all possible subsplits
        self.variables_weight = None   # variable used for weighting the data
        self.variables_calculation_avg = None
        self.cases_number_global = None   # global count of cases if custom value is needed
        self.cases_key = None   # Variable fuer das Identifizieren eines einzelnen Falles XXX???
        self.result_subsplits = None
        self.echoSql = False
        self.debug_enable = False
        self._caching_enabled = False
        self._cache_directory = None

    def debug(self, content):
        if self.debug_enable:
            print(content)

    @staticmethod
    def log_info(content):
        logging.info(content)

    @staticmethod
    def log_debug(content):
        logging.debug(content)

    def cache_reportingsets(self, path: str, mode: str='rw') -> None:
        """Cache the computed reportingsets by storing them in the given path

        :param path: path to the folder that stores the rs-dumps
        :param mode: r (read only) | rw (read and compute/write if missing) | w (always compute/write)
        """
        if mode not in ('w', 'r', 'rw'):
            raise Exception("Only 'w', 'r', 'rw' allowed!")
        self._caching_enabled = True
        self._caching_mode = mode
        self._cache_directory = path

    def fill_tabreportdef_from_tablecolumns(self, tabreportdef, database_table):
        column_names = self.db.query_table_column_names(database_table)
        for column_name in column_names:
            tabreportdef.add_tabdef(TabDef(name=column_name))

    def query_mean_single(self, variable_name, filter_string=None):
        raise NotImplementedError()

    def query_frequ_single(self, variable_name: str, filter_string: str) -> tuple:
        """Query the frequencies of a single column

        :param variable_name:
        :param filter_string:
        """
        logging.debug("query_SP")
        insert_dict = {"varName": variable_name,
                       "filter": " WHERE ({})".format(filter_string) if filter_string else '',
                       "database_table": self.database_table,
                       "weightVar": self.variables_weight,
                       "avgInsert": " avg({avg_varName}) AVG , sum({avg_varName}) SUM , ".format(avg_varName=self.variables_calculation_avg) if self.variables_calculation_avg else '',
                       "order": " ORDER BY count(*) DESC, {varName} ASC ".format(varName=variable_name) if self.order_freq_desc else ''}
        if self.cases_key:  # hat mit deduplizierung zu tun.
            insert_dict['source'] = "(SELECT * FROM {database_table} GROUP BY {varName} , {key}) as temp ".format(key=self.cases_key, **insert_dict)
            insert_dict['sourceN'] = "(SELECT * FROM {database_table} {filter} GROUP BY {key}) as temp ".format(key=self.cases_key, **insert_dict)
        else:
            insert_dict['source'] = insert_dict['sourceN'] = self.database_table
        insert_dict['globalNinsert'] = ", sum({weightVar})*100/ ({globalN})  PCT_GN_W ,  count(*)*100/ ({globalN})  PCT_GN  ".format(globalN=self.cases_number_global, **insert_dict) if self.cases_number_global else ''
        insert_dict['weightInsert'] = """, sum(%(weightVar)s) 'COUNT_W',round(sum(%(weightVar)s)*100/ (SELECT sum(%(weightVar)s)  FROM %(sourceN)s %(filter)s), 10)  PCT_W ,
                    (SELECT sum(%(weightVar)s)  FROM %(sourceN)s %(filter)s) COUNT_W_TOTAL """ % insert_dict if self.variables_weight else ''
        insert_dict['avgInsert'] = ", avg({avg_varName}) AVG , sum({avg_varName}) SUM  ".format(avg_varName=self.variables_calculation_avg) if self.variables_calculation_avg else ''
        result_query_txt = """
            SELECT
                {varName} CODE
            ,   count(*) COUNT
            {weightInsert}
            {globalNinsert}
            {avgInsert}
            FROM {source} {filter}
            GROUP BY {varName} {order}
            """.format(**insert_dict)
        if not self.variables_weight:
            result_base_txt = "SELECT count(*), min({varName}), max({varName}) FROM {source} {filter} ".format(**insert_dict)
        else:
            result_base_txt = "SELECT count(*), sum({weightVar}) FROM {source} {filter} ".format(**insert_dict)
        result = self._query_result(result_query_txt, result_base_txt)
        return result, result_query_txt, result_base_txt

    def query_frequ_multi(self, variables, filter_string: str=None):
        """Query the frequencies of multiple columns

        :param variables:
        :type variables: tuple|list
        :param filter_string:
        : return:
        """
        self.log_debug("query_frequ_multi")
        insert_dict = {"varList": variables,
                       "filter": " WHERE ({})".format(filter_string) if filter_string else '',
                       "database_table": self.database_table,
                       "weightVar": self.variables_weight,
                       "avgInsert": " avg({avg_varName}) AVG , sum({avg_varName}) SUM , ".format(
                           avg_varName=self.variables_calculation_avg) if self.variables_calculation_avg else '',
                       # "order": " ORDER BY count(*) DESC, {varName} ASC ".format(varName = varName) if self.orderFreqDesc else ''
                       }

        weightInsert = " " + self.variables_weight + " weightvar, " if self.variables_weight else ""
        query = ""
        # primaryKey = self.db.query_primaryKey(self.database_table)
        key_primary = 'data_id'  ## TODO: umbauen1!  # FIXME

        if self.cases_key:  # hat mit deduplizierung zu tun.
            insert_dict['source'] = "(SELECT * FROM {database_table} GROUP BY {varName} , {key}) as temp ".format(
                key=self.cases_key, **insert_dict)
            insert_dict['sourceN'] = "(SELECT * FROM {database_table} {filter} GROUP BY {key}) as temp ".format(
                key=self.cases_key, **insert_dict)
        else:
            insert_dict['source'] = insert_dict['sourceN'] = self.database_table

        if not key_primary:
            raise Exception("No primary key found in {}. A primary key is necessary!".format(self.database_table))
        if not self.variables_weight:
            query += " UNION ".join([
                                        "SELECT {var} CODE, {primaryKey} FROM {database_table} {filter} {var} > '0' ".format(
                                            var=var, primaryKey=key_primary,
                                            filter=" WHERE " if not insert_dict['filter'] else insert_dict['filter'] + ' and ',
                                            database_table=insert_dict['database_table'])
                                        for var in variables])
        else:
            query += " UNION ".join([
                                        "SELECT {var} CODE, {weightVar} weightvar, {primaryKey} FROM {database_table} {filter} {var} > '0' ".format(
                                            var=var, weightVar=self.variables_weight, primaryKey=key_primary,
                                            filter=" WHERE " if not insert_dict['filter'] else insert_dict[
                                                                                                   'filter'] + ' and ',
                                            database_table=insert_dict['database_table'])
                                        for var in variables])
        query = " SELECT * FROM ({unionQuery}) AS temp GROUP BY code, {PK}".format(unionQuery=query, PK=key_primary)
        if not self.variables_weight:
            resultQuery = """ SELECT CODE, count(*) COUNT_ABS, count(*)*100/(SELECT count(*)  FROM {database_table} {filter} )  PCT,
                             (SELECT count(*) FROM {database_table} {filter} ) COUNT_TOTAL
                              FROM ({query}) as temp GROUP BY code """.format(query=query, **insert_dict)
            countQuery = "SELECT count(*) FROM {source} {filter} ".format(**insert_dict)
        else:
            resultQuery = """
            SELECT CODE
            ,     count(*)                                                    COUNT_ABS
            ,     sum(weightvar) 'COUNT_W'
            ,     sum(weightvar) * 100/ (SELECT sum(weightvar)  FROM {database_table} {filter} )  PCT_W
            ,     count(*)*100/(SELECT count(*)  FROM {database_table}  {filter} )    PCT
            ,    (SELECT sum(weightvar)  FROM {database_table} {filter} )             COUNT_W_TOTAL
            ,    (SELECT count(*) FROM  {database_table}  {filter} )                  COUNT_TOTAL
            FROM ({query}) as temp
            GROUP BY code """.format(query=query, **insert_dict)
            countQuery = "SELECT count(*) countTotal, sum(weightvar) countTotalW FROM {source} {filter} ".format(
                **insert_dict)
        result = self._query_result(resultQuery, countQuery)
        logging.debug(result)
        return result, resultQuery, countQuery

    def _query_result(self, query_result_txt: str, query_count_txt: str):
        """

        :param query_result_txt:
        :param query_count_txt:
        :return:
        """
        self.log_debug('_query_result')
        if not self.variables_weight:
            # sumRow = self.db.query_row(countQueryTxt, echo = self.echoSql)
            row_count = self.db.query_resource(query_count_txt, echo=self.echoSql).fetchall()[0][0]
            resource = self.db.query_resource(query_result_txt, echo=False)
            result = [{'COUNT': row[1], 'COUNT_TOTAL': row_count, 'CODE': row[0]} for row in resource.fetchmany(self.categories_number_max)]
        else:
            row_count, row_count_weight = self.db.query_resource(query_count_txt, echo=self.echoSql).fetchall()[0]
            resource = self.db.query_resource(query_result_txt, echo=False)
            result = [{'COUNT': row[1], 'COUNT_TOTAL': row_count, 'COUNT_W_TOTAL': row_count_weight, 'CODE': row[0],
                       'COUNT_W': row[2]} for row in resource.fetchmany(self.categories_number_max)]
        row = resource.fetchone()  # fetch next one
        if row:
            otherCounts = 0
            # while row and row[1]!=1:
            #    otherCounts += row[1]
            #    row = resource.fetchone()
            # result.append({'CODE':'OTHER', 'COUNT':(rowcount- otherCounts-sum([i['COUNT'] for i in result]))})
            if not self.variables_weight:
                row_count = self.db.query_resource(query_count_txt, echo=self.echoSql).fetchall()[0][0]
                result.append({'CODE': 'OTHER', 'COUNT_TOTAL': row_count, 'COUNT': (row_count - sum([i['COUNT'] for i in result]))})
            else:
                row_count, row_count_weight = self.db.query_resource(query_count_txt, echo=self.echoSql).fetchall()[0]
                result.append({'CODE': 'OTHER', 'COUNT_TOTAL': row_count, 'COUNT_W_TOTAL': row_count_weight,
                               'COUNT': (row_count - sum([i['COUNT'] for i in result])), 'COUNT_W': (row_count_weight - sum([i['COUNT'] for i in result]))})
        return result

    def _calc_frequencies(self, variables_calculation, filter_string=None):
        """dispatch required variables to adequate frequ function"""
        if self.filter_base:
            filter_string = "({}) and ({})".format(filter_string, self.filter_base) if filter_string else self.filter_base
        if len(variables_calculation) == 1:
            result, result_query_txt, county_query_txt = self.query_frequ_single(variables_calculation[0], filter_string)
            result = self._transform_grouping(result)
            if result and result is not None:  # XXX why both
                result = DataSet(result)
                result.sql_result_str = result_query_txt
            else:
                result = DataSet()
                result.sql_result_str = result_query_txt
        else:
            result, result_query_txt, county_query_txt = self.query_frequ_multi(variables_calculation, filter_string)
            result = self._transform_grouping(result)
            if result and result is not None:  # XXX why both
                result = DataSet(result)
                result.sql_result_str = result_query_txt
            else:
                result = DataSet()
                result.sql_result_str = result_query_txt
        return result

    def _transform_grouping(self, result):
        """Transpose results to a structure ordered by codes"""
        if result:
            columns_result = list(set(result[0].keys()) & set(self.column_types))  # used column_types, setdiff
            data = {column: {str(row['CODE']): row[column] for row in result} for column in columns_result}
            if self.variables_weight:
                data['COUNT_W_TOTAL'] = result[0]['COUNT_W_TOTAL'] if 'COUNT_W_TOTAL' in result[0] else sum(
                    data['COUNT_W'].values())   # FIXME
            if self.cases_number_global and self.cases_number_global > 0:
                data['COUNT_GN_TOTAL'] = data['COUNT_GN_W_TOTAL'] = self.cases_number_global   # FIXME
                raise Exception('weight war')
            data['COUNT_TOTAL'] = result[0]['COUNT_TOTAL'] if 'COUNT_TOTAL' in result[0] else sum(data['COUNT'].values())
            data['PCT'] = {code: data['COUNT'][code] / data['COUNT_TOTAL'] * 100 for code in data['COUNT']} if data['COUNT_TOTAL'] > 0  else None  # #XXXX spaeter?
            if self.variables_weight:
                data['PCT_W'] = {code: data['COUNT_W'][code] / data['COUNT_W_TOTAL'] * 100 for code in data['COUNT']} if data['COUNT_W_TOTAL'] > 0 else None  # #XXXX spaeter?
            return data
        else:
            self.log_info("No results found.")
            return None

    def sort_mainsplit(self, codePlan, sort=None):
        """sorts the mainsplit according to a criteria"""
        # keys = codePlan.keys() ### XXXcopy
        # keys.sort()
        # self.rs.mainSplit.keyOrder = keys
        # if sort == 'COUNT_W_DESC':
        raise Exception('not yet implemented')

    def check_setup(self):
        """Check the preconditions before starting the calculation"""
        if not self.database_table:
            raise Exception("Please define a data_table first. ->database_table")

    def build_rs_frequs(self, variables_calculation: list, filter_string: str=None, variables_calculation_avg: list=None, title: str=None,
                        codeplan: CodePlan=None) -> ReportingSet:
        """Build a reportingset based on frequencies.

        :param variables_calculation:
        :param filter_string:
        :param variables_calculation_avg:
        :param title:
        :param codeplan:
        """
        self.check_setup()
        table_column_names = self.db.query_table_column_names(self.database_table)
        for variable_name in variables_calculation:
            if variable_name not in table_column_names:
                raise Exception("Variable '{}' not found in {}!".format(variable_name, self.database_table))
        self.variables_calculation_avg = variables_calculation_avg  # XXX umbenennen
        rs = ReportingSet(title=title)
        rs['TOTAL'] = self._calc_frequencies(variables_calculation=variables_calculation, filter_string=filter_string)
        if codeplan:
            rs.split_main = codeplan
            rs.split_main.key_order + [key for key in rs['TOTAL']['COUNT'] if key not in codeplan]  # # Add missing codes
            keys_sorted = None
        else:
            if len(rs['TOTAL']) > 0:
                rs.split_main.data = list(rs['TOTAL']['COUNT'].keys())
                keys_sorted = None
                if self.order_freq_desc:
                    keys_sorted = sorted(copy.copy(rs['TOTAL']['COUNT']).items(), key=operator.itemgetter(1))
                    keys_sorted.reverse()
                    rs.split_main.key_order = [chunk[0] for chunk in keys_sorted]
                    if 'OTHER' in rs.split_main.key_order:
                        rs.split_main.key_order.remove('OTHER')
                        rs.split_main.key_order.append('OTHER')
                rs.split_main.variables = variables_calculation
        if self.result_subsplits:
            self.calc_splits_sub(rs, filter_string, variables_calculation)
        rs.timestamp = datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        return rs

    def calc_splits_sub(self, rs: ReportingSet, filter_string: str, variables_calculation):
        """calculation of dataset crossed with a codeplan, similar to a crosstable.

        :param rs:
        :param filter_string:
        :param variables_calculation:
        :return:
        """
        for result_split in self.result_subsplits:
            if isinstance(result_split, str):  # TODO check if functional
                """Einfache Kreuztabelle mit Nennung von Kreuzvariable als string. Codes werden aus Bestehendem abgeleitet."""
                filter_string = " WHERE " + filter_string if filter_string else ""
                result_split_new = CodePlan()
                result_split_new.data = self.db.query_list("SELECT " + result_split + " FROM " + self.database_table + filter + " GROUP BY " + result_split, echo=False)
                result_split_new.variables = [result_split, ]
                result_split = result_split_new
            elif isinstance(result_split, CodePlan) and len(result_split) > 0:
                for code in result_split:
                    filter_string_split = " ({})".format(' OR '.join(["{}='{}' ".format(var, code) for var in result_split.variables]))
                    if filter_string:
                        filter_string_split += " and ({}) ".format(filter_string)
                    rs['{}_{}'.format(result_split.variables[0], code)] = self._calc_frequencies(variables_calculation, filter_string_split)
                    rs.splits_sub[result_split.variables[0]] = copy.copy(result_split)

    def compute_reportingsets_for_tabreportdef(self, tabreport_def: TabReportDef):
        """Augment the definition of a table report with calculated ReportingSets."""
        start_time = datetime.datetime.now()
        tabdef_count = len(tabreport_def)
        tabreport_def.fill_contents_inert()
        tabdef_counter = 0
        for tabdef_name in tabreport_def.tabdef_order:
            tabdef = tabreport_def[tabdef_name]
            tabdef_counter += 1
            rs = None
            if self._caching_enabled and self._caching_mode in ('r', 'rw'):
                rs_dump = "{}/rs_{}.rsd".format(self._cache_directory, tabdef_name)
                try:
                    with open(rs_dump, 'rb') as f:
                        rs = pickle.load(f)
                    logging.info("\t\t{} has been loaded.\t\t{}/{}".format(tabdef_name,
                                                                           tabdef_counter,
                                                                           tabdef_count))
                except FileNotFoundError:
                    logging.info("\t\t{} not found in cache.".format(tabdef_name))

            if not rs:
                logging.info("\t\t{} is being calculated.\t\t{}/{}, \t\truntime: {} ".format(tabdef_name,
                                                                                             tabdef_counter,
                                                                                             tabdef_count,
                                                                                             str(datetime.datetime.now() - start_time)))
                self.filter_base = tabdef.filter_rs if tabdef.filter_rs else None
                if tabdef.table_head:
                    self.result_subsplits = []      # TODO warum self, warum nicht local
                    for head in tabdef.table_head:
                        if isinstance(head, TabHead):
                            for subhead in head:
                                self.result_subsplits.append(subhead)
                        elif isinstance(head, CodePlan):
                            self.result_subsplits.append(head)
                        else:
                            raise TypeError('Only TabHead or CodePlan allowed as a table head. Found: ', type(head))
                if tabdef.database_table:
                    self.database_table = tabdef.database_table
                else:
                    raise Exception("No database_table in TabDef defined!")
                if tabdef.aggr_variables:
                    self.variables_calculation_avg = tabdef.aggr_variables[0]  # unclear?
                rs = self.build_rs_frequs(variables_calculation=tabdef.variables, variables_calculation_avg=self.variables_calculation_avg)
                if tabdef.split_main:
                    rs.split_main = tabdef.split_main
                    rs.split_main.variables = tabdef.variables
                if tabdef.title:
                    rs.title = tabdef.title
                if tabdef.title_sub:
                    rs.content_misc['subTitle'] = tabdef.title_sub
                if self._caching_enabled and self._caching_mode in ('w', 'rw'):
                    f = open("{}/rs_{}.rsd".format(self._cache_directory, tabdef_name), 'wb')
                    pickle.dump(rs, f)
                    f.close()
            tabdef.reportingset = rs
        self.log_info("Tabreport calculated. Duration: {}".format(str(datetime.datetime.now() - start_time)))
