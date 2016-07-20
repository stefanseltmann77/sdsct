# -*- coding: utf-8 -*-
import os
import logging
from sdsct.ubiquitousreporting.dataobjects.report_tab import TabHead, TabReportDef, TabDef
from sdsct.ubiquitousreporting.dataobjects.report_generic import CodePlan, DataSet, ReportingSet
from pandas import DataFrame
from sdsct.ubiquitousreporting.generators.reportingsetbuilder import ReportingSetBuilder


class ReportingSetBuilder4SQL(ReportingSetBuilder):

    def get_data_column_names(self, data_source=None):
        return self.db.query_table_column_names(data_source)

    def check_tabdef_setup(self, tabdef: TabDef):
        table_column_names = self.get_data_column_names(tabdef.database_table)
        for var_name in tabdef.variables:
            if var_name not in table_column_names:
                raise Exception("Variable '{}' not found in {}!".format(var_name, tabdef.database_table))
