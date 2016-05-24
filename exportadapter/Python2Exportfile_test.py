# -*- coding: utf-8 -*-
import unittest
from sdsct.exportadapter.Python2Exportfile import Python2Exportfile


class Python2ExportfileTest(unittest.TestCase):

    def setUp(self):
        self.obj = Python2Exportfile()
        self.output_directory = 'c:\\windows'
        self.outputDirFormated = 'c:/windows'

    def test_sensible_exception_when_exporting_without_outputDir(self):
        obj = Python2Exportfile()
        self.assertRaises(TypeError, self.obj.export, 'Result')

    def test_setting_of_outputDir_with_open_ending(self):
        self.obj.output_directory = self.output_directory
        self.assertEqual(self.obj.output_directory, self.outputDirFormated)

    def test_setting_of_outputDir_with_closed_ending(se lf):
        self.obj.output_directory = self.output_directory + '\\'
        self.assertEqual(self.obj.output_directory, self.outputDirFormated)



    def test_export_of_string(self):
        self.obj.export('This is a \n dummystring', output_directory='c:/')
    
if __name__ == "__main__":
    unittest.main()