# -*- coding: utf-8 -*-
__author__ = 's.seltmann'
import datetime
import winsound

class ETLWrapper(object):

    # def signal_completed_with_success(self):
    #     for i in range(4):
    #         winsound.Beep(300+i*100,100+i*100)

    # def run(self):
    #     self.signal_completed_with_success()

    analysis_dt = None # TODO add decorator

    @staticmethod
    def _parse_date(date_string):
        """Converts a unix date string, e.g. '2015-03-02' to a date object.

        :param date_string:
        :type date_string: str
        :return:
        """
        return datetime.datetime.strptime(date_string, "%Y-%m-%d")
