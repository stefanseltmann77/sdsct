from unittest import TestCase
from sdsct.exportadapter.export2generic import Export2Generic


class TestExport2Generic(TestCase):

    def setUp(self):
        self.obj = Export2Generic()

    def test__clean_path(self):
        self.obj.output_directory = 'c:/windows'
        self.assertEqual('c:/windows', self.obj.output_directory)
        self.obj.output_directory = 'c:/windows/'
        self.assertEqual('c:/windows', self.obj.output_directory)
        self.obj.output_directory = 'c:/windows\\'
        self.assertEqual('c:/windows', self.obj.output_directory)
        self.obj.output_directory = 'c:\\windows'
        self.assertEqual('c:/windows', self.obj.output_directory)
        self.obj.output_directory = 'c:/'
        self.assertEqual('c:/', self.obj.output_directory)