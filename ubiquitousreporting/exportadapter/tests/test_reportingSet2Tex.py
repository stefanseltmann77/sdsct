from unittest import TestCase
from sdsct.ubiquitousreporting.exportadapter.reportingset2tex import ReportingSet2Tex
from sdsct.ubiquitousreporting.dataobjects.report_generic import ReportingSet

__author__ = 'Stefan Seltmann'


class TestReportingSet2Tex(TestCase):
    def test__build_table_tex_empty_rs(self):
        r2t = ReportingSet2Tex('c:/')
        rs = ReportingSet()
        r2t._build_table_tex(rs)
        # throw no error!
