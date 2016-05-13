# -*- coding: utf-8 -*-
import os
import logging
from sdsct.ubiquitousreporting.dataobjects.report_tab import TabHead, TabReportDef, TabDef
from sdsct.ubiquitousreporting.dataobjects.report_generic import CodePlan, DataSet, ReportingSet
from pandas import DataFrame
from sdsct.ubiquitousreporting.generators.reportingsetbuilder import ReportingSetBuilder


class ReportingSetBuilder4Pandas(ReportingSetBuilder):

    def __init__(self, dataframe: DataFrame = None):
        self.dataframe = dataframe

    def get_data_column_names(self):
        return self.dataframe.columns

    def _calc_frequencies(self, vars_calculation, filter_string=None):
        """dispatch required variables to adequate frequ function"""
        if self.filter_base:
            filter_string = "({}) and ({})".format(filter_string, self.filter_base) \
                if filter_string else self.filter_base

        if filter_string:
            print(filter_string)
            filter_string = filter_string.replace('(', '').replace(')', '').replace(' ', '').replace("'", '')
            print(filter_string)
            _, filtervalue = filter_string.split('=')


        if len(vars_calculation) == 1:
            if filter_string:
                result = self.dataframe[vars_calculation[0]].astype('category')[self.dataframe['yearmonth']==filtervalue].value_counts()
            else:
                result = self.dataframe[vars_calculation[0]].astype('category').value_counts()
            result_pc = result / sum(result) * 100
            keys = [str(key) for key in result.index]
            result = dict(zip(keys, list(result)))
            result_pc = dict(zip(keys, list(result_pc)))

            if result and result is not None:  # XXX why both
                result = DataSet({'COUNT': result, 'PCT': result_pc})

        else:
            result_base = sum(self.dataframe[vars_calculation[0]].astype('category').value_counts())
            result = [self.dataframe[var].astype('category').value_counts()[1] for var in vars_calculation]
            result_pc = dict(zip(vars_calculation, list(result / result_base * 100)))
            result = dict(zip(vars_calculation, list(result)))
            result = DataSet({'COUNT': result, 'PCT': result_pc})
            if result and result is not None:  # XXX why both
                result = DataSet(result)
            else:
                result = DataSet()
        return result

    def check_tabdef_setup(self, tabdef):
        table_column_names = self.get_data_column_names()
        for var_name in tabdef.variables:
            if var_name not in table_column_names:
                raise Exception("Variable '{}' not found in dataframe!".format(var_name))
