# -*- coding: utf-8 -*-
import os
import logging
import pandas as pd
from sdsct.ubiquitousreporting.dataobjects.report_tab import TabHead, TabReportDef, TabDef
from sdsct.ubiquitousreporting.dataobjects.report_generic import CodePlan, DataSet, ReportingSet
from pandas import DataFrame
from sdsct.ubiquitousreporting.generators.reportingsetbuilder import ReportingSetBuilder


class ReportingSetBuilder4Pandas(ReportingSetBuilder):

    def __init__(self, dataframe: DataFrame = None):
        super().__init__()
        self.dataframe = dataframe

    def get_data_column_names(self):
        return self.dataframe.columns

    def _calc_frequencies(self, vars_calculation, filter_string=None):
        """Dispatch required variables to adequate frequ function"""
        if self.filter_base:
            raise NotImplementedError()
        if filter_string:
            raise NotImplementedError()
        if len(vars_calculation) == 1:
            if filter_string:
                raise NotImplementedError()
            else:
                result_count = self.dataframe[vars_calculation[0]].astype('category').value_counts(dropna=False)
                result_pc = self.dataframe[vars_calculation[0]].astype('category').value_counts(normalize=True,
                                                                                                dropna=False)
                result = pd.DataFrame({'COUNT': result_count, 'PCT': result_pc})
            keys = [str(key) for key in result.index]
        else:
            raise NotImplementedError()
            # result_base = sum(self.dataframe[vars_calculation[0]].astype('category').value_counts())
            # result = [self.dataframe[var].astype('category').value_counts()[1] for var in vars_calculation]
            # result_pc = dict(zip(vars_calculation, list(result / result_base * 100)))
            # result = dict(zip(vars_calculation, list(result)))
            # result = DataSet({'COUNT': result, 'PCT': result_pc})
            # if result and result is not None:  # XXX why both
            #     result = DataSet(result)
            # else:
            #     result = DataSet()
        return result

    def check_setup(self, tabdef):
        """Check the preconditions before starting the calculation"""
        pass

    def build_rs_frequs(self, variables_calculation: list, filter_string: str = None,
                        variables_calculation_avg: list = None, title: str = None,
                        codeplan: CodePlan = None) -> ReportingSet:
        df_column_names = self.dataframe.columns
        for variable_name in variables_calculation:
            if variable_name not in df_column_names:
                raise Exception("Variable '{}' not found in Dataframe!".format(variable_name))
        rs = ReportingSet(title=title)
        rs['TOTAL'] = self._calc_frequencies(vars_calculation=variables_calculation, filter_string=filter_string)
        return rs


    def check_tabdef_setup(self, tabdef):
        table_column_names = self.get_data_column_names()
        for var_name in tabdef.variables:
            if var_name not in table_column_names:
                raise Exception("Variable '{}' not found in dataframe!".format(var_name))
