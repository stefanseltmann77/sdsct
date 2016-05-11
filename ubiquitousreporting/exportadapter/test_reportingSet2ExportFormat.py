import unittest
from unittest import TestCase

__author__ = 's.seltmann'

from sdsct.ubiquitousreporting.exportadapter.ReportingSet2ExportFormat import ReportingSet2ExportFormat


class TestReportingSet2ExportFormat(TestCase):

    def setUp(self):
        self.RSE = ReportingSet2ExportFormat('c:/')

    def test_decimals_in_valid_range(self):
        self.RSE.decimals = 1

    def test_decimals_non_numeric(self):
        with self.assertRaises(ValueError):
            testvalue = 'foo'
            self.RSE.decimals = testvalue

    def test_decimals_not_in_valid_range(self):
        with self.assertRaises(ValueError):
            self.RSE.decimals = 8
            self.RSE.decimals = -1

    def test_directory_always_without_end_sep_except_root(self):
        self.RSE.output_directory = 'c:/'
        self.assertEqual(self.RSE.output_directory, 'c:/')
        self.RSE.output_directory = 'c:'
        self.assertEqual(self.RSE.output_directory, 'c:/')
        self.RSE.output_directory = 'c:\\'
        self.assertEqual(self.RSE.output_directory, 'c:/')

    def test_directory_always_without_end_sep(self):
        self.RSE.output_directory = 'c:/test/'
        self.assertEqual(self.RSE.output_directory, 'c:/test')
        self.RSE.output_directory = 'c:/test'
        self.assertEqual(self.RSE.output_directory, 'c:/test')
        self.RSE.output_directory = 'c:\\test'
        self.assertEqual(self.RSE.output_directory, 'c:/test')
        self.RSE.output_directory = 'c:\\test\\'
        self.assertEqual(self.RSE.output_directory, 'c:/test')

    def test_non_existing_path(self):
        self.assertRaises(Exception, self.RSE.output_directory, 'A:\test')

