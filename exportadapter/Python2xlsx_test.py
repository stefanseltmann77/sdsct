# -*- coding: utf-8 -*-
import unittest
from sdsct.exportadapter.export2xlsx import Export2xlsx

from Export2xlsx import Export2xlsx


class Python2xls_test(unittest.TestCase):
    def setUp(self):
        self.obj = Python2xls()
        pass

    def test_save_xls_file_string_exception(self):
        self.assertRaises(AttributeError, self.obj.export, 'Result', 'Output')
        pass

    def test_save_xls_file(self):
        # self.obj.export('Ergebnis', 'Output')
        pass


if __name__ == "__main__":
    unittest.main()
