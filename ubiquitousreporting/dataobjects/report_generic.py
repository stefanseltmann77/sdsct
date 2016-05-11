# -*- coding: utf-8 -*-
import sys
import unittest


class CodePlan(dict):
    """
    Extended Dictionary that serves as a container for sorted mappings used to describe a data dimension.
    """
    _variables = None

    def __init__(self, name: str=None, variables=None, data=None, title: str=None, key_order=None):
        """
        :param name: name of the codeplan, most times a technical name
        :param variables: tuple of variables linked to the codeplan, will default to 'name'
        :type variables: tuple|list|str
        :param data:
        :param title: title of the codeplan used for display, will default to 'name'
        :param key_order: ordered list of the dictionary keys
        :type key_order: list|tuple
        :return:
        """
        super(CodePlan, self).__init__()
        #  TODO key_oder reihenfolge überarbeiten. Datanur ableiten, wnen nicht gegeben.
        self.key_order = []
        self.name = name
        self.title = title if title else name
        if variables:
            self.variables = variables
        self.data = data if data else []
        self.key_order = tuple(key_order) if key_order else self.key_order if self.key_order else []

    @property
    def variables(self):
        return self._variables or (self.name,)

    @variables.setter
    def variables(self, value):
        """convert single string variables to a tuple

        :param value:
        :type value: list|tuple|str|dict
        :return:
        """
        if isinstance(value, list) or isinstance(value, tuple):
            self._variables = tuple(value)
        elif isinstance(value, str):
            self._variables = (value,)
        elif isinstance(value, dict):
            self._variables = tuple(value.keys())
        else:
            raise TypeError('Only list, tuple or str allowed!')

    @property
    def data(self):
        return self

    @data.setter
    def data(self, data_input):
        """
        TODO Kann nicht mit directer Eingabe von Dicts umgehenn

        :param data_input:
        :type data_input: list|dict
        :return:
        """
        if len(data_input) > 0:
            if isinstance(data_input, list) and (isinstance(data_input[0], str)):
                self.update({element: element for element in data_input})
                self.key_order = data_input
            elif isinstance(data_input, list) and (isinstance(data_input[0], tuple)):
                for row in data_input:
                    self.update({str(row[0]): row[1]})
                    self.key_order.append(str(row[0]))
            elif isinstance(data_input, dict):
                self.update(data_input)
                self.key_order = list(self.keys())
            else:
                try:
                    self.update({element: str(element) for element in data_input})
                    self.key_order = [str(key) for key in self.keys()]
                except TypeError:
                    for element in data_input:
                        self.update({str(int(element['code'])): str(element['label'])})
                        self.key_order.append(str(int(element['code'])))
                        # self.update({element['code']:str(element['label']) for element in dataInput})

    def check_contents(self):
        if len(self) == 0:
            raise Exception("Codeplan '{}' has no data.".format(self.title))
        else:
            if len(self.key_order) == 0:  # TODO muss woanders passieren
                self.key_order = list(self.keys())
                self.key_order.sort()
                raise Exception()
            for key in self.key_order:  # TODO alle fehlenden ausweisen.
                if str(key) not in self:
                    raise Exception("Codeplan '{}' misses elements from key_order! Key : {} \n!".format(self.title, str(key)))


class DataSet(dict):
    """
    Small named dictionary that holds results on low level.
    """

    def __init__(self, *args, **kwargs):
        """
        :param kwargs:
        """
        super(DataSet, self).__init__(*args, **kwargs)
        self.sql_result_str = None
        self.sql_base_str = None


class ReportingSet(dict):
    """
    Data object to collect the result of a query. It is generic by design, that means it can be used for any textual or graphical output.
    """

    timestamp = None
    """timestamp of creation and therefor of the stored result"""

    def __init__(self, title=None):
        super(ReportingSet, self).__init__()
        self.title = title
        self.split_main = CodePlan()
        if self.title:
            self.split_main.title = title
        self.splits_sub = {}
        self.source_sql_str = None
        self.content_misc = {}

    # def order_by_value(self, orderVar, direction='desc', codes_last=(96, 99)):
    #     """Diese funktion muesste noch drastisch verbessert werden. XXX"""
    #     key_order = []
    #     values = self.datasets[0].data[orderVar].values()
    #     values.sort()
    #     values.reverse()
    #
    #     tempDict = self.datasets[0].data[orderVar].copy()
    #     for value in values:
    #         for item in tempDict:
    #             if tempDict[item] == value:
    #                 key_order.append(item)
    #
    #     for code in codes_last:
    #         if code in key_order:
    #             key_order.remove(code)
    #             key_order.append(code)
    #     self.split_main.keyOrder = key_order

    def add_dataset(self, name, data=None):  # TODO rework reporticset as dict.
        """Add a DataSet to the Reportingset

        :param name:
        :type name: str
        :param data:
        :return:
        """
        if data:   # TODO rework
            if isinstance(data, DataSet):
                dataset = data
            else:
                dataset = DataSet(data)
        else:
            dataset = DataSet()
        self[name] = dataset
        return dataset  # why return

    def split_sub_to_crosstab(self, split_sub_variables):
        crosstab_temp = {}
        crosstab = {}
        split_sub_keys = {}
        for split_sub_key in self.splits_sub:
            split_sub = self.splits_sub[split_sub_key]
            if split_sub_variables == split_sub.variables:
                split_sub_keys = split_sub.data
                for key in split_sub_keys:
                    crosstab_temp[key] = {}
                    if self[split_sub_variables + "_" + str(key)]:
                        try:
                            crosstab_temp[key] = self[split_sub_variables + "_" + str(key)].data['COUNT']  # TODO getDefault!!
                        except:
                            crosstab_temp[key] = {}
        if split_sub_keys:
            for key in self.split_main.key_order:
                crosstab[key] = {}
                for subkey in split_sub_keys:
                    if key in crosstab_temp[subkey]:
                        crosstab[key][subkey] = crosstab_temp[subkey][key]  # XXXXXXXXXXX ausbessenr
                    else:
                        crosstab[key][subkey] = 0
        return crosstab
