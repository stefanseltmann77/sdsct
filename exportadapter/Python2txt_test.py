# -*- coding: utf-8 -*-
import unittest
from Python2txt import Python2txt

class Python2txt_test(unittest.TestCase):

    def setUp(self):
        self.obj = Python2txt()
        self.outputDir = 'c:\\windows'
        self.outputDirFormated = 'c:/windows/'

    def test_sensible_exception_when_exporting_without_outputDir(self):
        obj = Python2txt()
        self.assertRaises(TypeError,self.obj.export,'Ergebnis')

    def test_setting_of_outputDir_with_open_ending(self):
        self.obj.outputDir = self.outputDir
        self.assertEqual(self.obj.outputDir, self.outputDirFormated)

    def test_setting_of_outputDir_with_closed_ending(self):
        self.obj.outputDir = self.outputDir+'\\'
        self.assertEqual(self.obj.outputDir, self.outputDirFormated)
    
    def test_export_of_string(self):
        self.obj.export('This is a \n dummystring', outputDir='c:/')
    
if __name__ == "__main__":
    unittest.main()