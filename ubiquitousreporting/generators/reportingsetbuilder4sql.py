# -*- coding: utf-8 -*-
import logging
import copy
import datetime
import operator
from sdsct.ubiquitousreporting.dataobjects.report_tab import TabDef
from sdsct.ubiquitousreporting.dataobjects.report_generic import CodePlan, ReportingSet
from sdsct.ubiquitousreporting.generators.reportingsetbuilder import ReportingSetBuilder
from sdsct.dbinterfaces.con2database import Con2Database


class ReportingSetBuilder4SQL(ReportingSetBuilder):

    def __init__(self, db: Con2Database, database_table: str = None):
        """
        :param db: database handle from sdsct
        :param database_table: string for the table to be analyzed
        : return:
        """
        super(ReportingSetBuilder4SQL, self).__init__()
        self.db = db  # database handle
        self.database_table = database_table  # source data table

    def get_data_column_names(self, data_source=None):
        return self.db.query_table_column_names(data_source)

    def check_tabdef_setup(self, tabdef: TabDef):
        table_column_names = self.get_data_column_names(tabdef.database_table)
        for var_name in tabdef.variables:
            if var_name not in table_column_names:
                raise Exception("Variable '{}' not found in {}!".format(var_name, tabdef.database_table))

    def build_rs_frequs(self, variables_calculation: list, filter_string: str = None,
                        variables_calculation_avg: list = None, title: str = None,
                        codeplan: CodePlan = None) -> ReportingSet:
        """Build a reportingset based on frequencies.

        :param variables_calculation:
        :param filter_string:
        :param variables_calculation_avg:
        :param title:
        :param codeplan:
        """
        table_column_names = self.db.query_table_column_names(self.database_table)
        for variable_name in variables_calculation:
            if variable_name not in table_column_names:
                raise Exception("Variable '{}' not found in {}!".format(variable_name, self.database_table))
        self.variables_calculation_avg = variables_calculation_avg  # XXX umbenennen
        rs = ReportingSet(title=title)
        rs['TOTAL'] = self._calc_frequencies(variables_calculation=variables_calculation, filter_string=filter_string)
        if codeplan:
            rs.split_main = codeplan
            # TODO rework as sets
            rs.split_main.key_order = rs.split_main.key_order + [key for key in rs['TOTAL']['COUNT'] if key not in codeplan]  # # Add missing codes
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

