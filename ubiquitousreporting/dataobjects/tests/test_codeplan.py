from unittest import TestCase

__author__ = 's.seltmann'

from sdsct.ubiquitousreporting.dataobjects.report_generic import CodePlan

class TestCodePlan(TestCase):

    def test_variables_with_string(self):
        cp = CodePlan(variables='test')
        self.assertEqual(cp.variables, ('test',))

    def test_variables_with_tuple(self):
        cp = CodePlan(variables=('test',))
        self.assertEqual(cp.variables, ('test',))

    def test_variables_with_list(self):
        cp = CodePlan(variables=['test'],)
        self.assertEqual(cp.variables, ('test',))

    def test_read_data_convert_float(self):
        cp = CodePlan(data=[{'code': 1.0, 'label': 'first'}, {'code': 2.0, 'label': 'second'}])
        self.assertEqual(cp, {'1': 'first', '2': 'second'})
        self.assertEqual(cp.key_order, ['1', '2'])

    def test_read_data_tuple(self):
        cp = CodePlan(data=[(1, 'first'), (2, 'second')])
        self.assertEqual(cp, {'1': 'first', '2': 'second'})
        self.assertEqual(cp.key_order, ['1', '2'])
