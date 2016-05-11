# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from abc import ABCMeta, abstractmethod
import locale
import os
from sdsct.ubiquitousreporting.dataobjects.report_tab import TabReportDef


class ReportingSet2ExportFormat(object):
    __metaclass__ = ABCMeta

    C_REPCOL_COUNT = 'COUNT'
    C_REPCOL_PCT = 'PCT'
    C_REPCOL_SUM = 'SUM'
    C_REPCOL_AVG = 'AVG'
    C_REPCOL_COUNT_W = 'COUNT_W'
    C_REPCOL_PCT_SUM = 'PCT_SUM'
    C_REPCOL_PCT_W = 'PCT_W'
    C_REPCOL_PCT_GN_W = 'PCT_GN_W'
    C_REPCOL_SUM_W = 'SUM_W'
    C_REPCOL_AVG_W = 'AVG_W'

    columns_reporting = [C_REPCOL_COUNT, C_REPCOL_PCT]

    column_type_labels = {C_REPCOL_COUNT: 'Anzahl',
                          C_REPCOL_PCT: 'Prozent',
                          C_REPCOL_SUM: 'Summe',
                          C_REPCOL_AVG: 'Durchschnitt',
                          C_REPCOL_COUNT_W: 'Anzahl gew.',
                          C_REPCOL_PCT_SUM: 'SummeProz',
                          C_REPCOL_PCT_W: 'Proz. gew.',
                          C_REPCOL_PCT_GN_W: 'ProzentBasis gew.',
                          C_REPCOL_SUM_W: 'Summe gew.',
                          C_REPCOL_AVG_W: 'Durchschnitt gew.'}

    _output_directory = None

    filename_with_timestamp = False

    def __init__(self, output_directory):
        self.labelDisplay = 'label'  # # 'label', 'both', 'code'
        self.show_total = False
        self._decimals = 2
        locale.setlocale(locale.LC_ALL, '')
        self.output_directory = output_directory

    @property
    def output_directory(self):
        return self._output_directory

    @output_directory.setter
    def output_directory(self, directory: str):
        """

        :param directory:
        :return:
        """
        directory = directory.replace(os.sep, '/')
        if directory.endswith('/') and len(directory) > 3:  # second condition in order to exclude root directories.
            directory = directory[:-1]
        elif not directory.endswith('/') and directory.endswith(':') and len(directory) == 2:
            directory += '/'
        if not os.path.exists(directory):
            raise Exception("Path {} does not exist.".format(directory))
        self._output_directory = directory

    @property
    def decimals(self):
        return self._decimals

    @decimals.setter
    def decimals(self, value):
        if not isinstance(value, int) or value < 0 or value > 6:
            raise ValueError('Decimals must be an integer between 0 and 6!')
        self._decimals = value

    @abstractmethod
    def export_tabreport(self, tabreport, output_name: str='tabband', testmode: bool=False):
        """Export a precalculated table report to the specific outputformat.

        :param tabreport:
        :type tabreport: TabReportDef
        :param output_name:
        :param testmode:
        :return:
        """
        pass

