# -*- coding: utf-8 -*-
import copy
import collections
from sdsct.ubiquitousreporting.dataobjects.report_generic import CodePlan


class TabDef(object):
    """Abstract object describing the metadata of a table and stores the tables actual data
    """
    _aggr_variables = None
    _variables = None
    _filter_rs = None
    reportingset = None

    def __init__(self, name: str, title: str = None, split_main: CodePlan = None, variables=None,
                 database_table: str = None, table_head=None, aggr_variables=None, reporting_columns=None,
                 filter_rs=None, section=None, database_table_linked=None, title_sub: str=None):
        """
        :param name:
        :param title:
        :param split_main:
        :param database_table:
        :param variables:
        :param table_head:
        :type table_head: TabHead
        :param aggr_variables:
        :param reporting_columns:
        :param filter_rs: filter string for recordsets
        :type filter_rs: str
        :param section:
        :param database_table_linked:
        :param title_sub:
        :return:
        """
        self.name = name
        self.title = title
        self.split_main = split_main
        self.database_table = database_table
        self.title_sub = title_sub
        if variables:
            self.variables = variables
        self.aggr_variables = aggr_variables
        self.database_table_linked = database_table_linked
        self.table_head = table_head
        self.reporting_columns = reporting_columns
        self.filter_rs = filter_rs
        self.section = section

    @property
    def variables(self):
        return self._variables if self._variables else (self.name,)

    @variables.setter
    def variables(self, variables_input: tuple or list or str) -> None:
        """convert single string variables to a tuple"""
        self._variables = (variables_input,) if not (isinstance(variables_input, tuple)
                                                     or isinstance(variables_input, list)) else variables_input

    @property
    def aggr_variables(self):
        return self._aggr_variables

    @aggr_variables.setter
    def aggr_variables(self, aggr_variables_input):
        """convert single string aggr_variables to a tuple"""
        self._aggr_variables = (aggr_variables_input,) if not (isinstance(aggr_variables_input, tuple)
                                                               or isinstance(aggr_variables_input, list)) else aggr_variables_input

    @property
    def filter_rs(self):
        return self._filter_rs

    @filter_rs.setter
    def filter_rs(self, filter_input):
        self._filter_rs = str(filter_input).strip() if filter_input else None


class TabReportDef(dict):
    """Collection Object, containing the different crosstab definitions of a tabular report."""

    _keys_inert = ('table_head', 'database_table', 'aggregation_variables', 'reporting_columns')

    def __init__(self, title: str='TabReport', title_sub: str=None, footer: str=None, title_pre: str=None) -> None:
        """
        :param title: main title of the report
        :param title_sub: subtitle
        :param footer: comment at the bottom of the page
        :param title_pre: introductory title to the main title
        """
        super(TabReportDef, self).__init__()
        self.title = title
        self.title_pre = title_pre or ''
        self.title_sub = title_sub or ''
        self.footer = footer or title
        self._cache_inert = {"reporting_columns": None}  # TODO warum so halb befuellt  # FIXME columns_reporting
        self._tabdef_order = []
        """retrieval order for stored table definitions"""

    def add_tabdef(self, tabdef: TabDef, after: str=None, before: str=None):
        """Add a table definition to the report

        :param tabdef: table definition
        :param after: name of existing table definition to insert after
        :param before: name of existing table definition to insert before
        :return:
        """
        if not isinstance(tabdef, TabDef):
            raise TypeError('Only TabDefs can be added to TabReportDef!')
        if tabdef.name in self.tabdef_order:
            raise Exception('No duplicates allowed for names of tabdefs ({})'.format(tabdef.name))
        tabdef = copy.deepcopy(tabdef)  # prevent 'by reference'
        for element in self._cache_inert:
            if self._cache_inert[element] and (getattr(tabdef, element) is None or getattr(tabdef, element) == []):  # XXX brauch ich die zweite klammer?
                setattr(tabdef, element, self._cache_inert[element])
        self[tabdef.name] = tabdef
        if not after and not before:
            self._tabdef_order.append(tabdef.name)
        else:
            index = self._tabdef_order.index(after) + 1 if after else self._tabdef_order.index(before)
            self._tabdef_order.insert(index, tabdef.name)

    def add_tabdefs(self, *args):
        """Add multiple tabdefs at once.

        :param args: a listing of TabDef
        :type args: list
        :return:
        """
        for tabdef in args:
            self.add_tabdef(tabdef)

    @property
    def tabdef_order(self):
        return self._tabdef_order

    @tabdef_order.setter
    def tabdef_order(self, tabdef_order):
        """Setter for tabdef_order that ensures that it is stored as a list

        :param tabdef_order:
        :type tabdef_order: list
        :return:
        """
        self._tabdef_order = list(tabdef_order)

    def set_inert(self, **args):
        """Set the given value as a inert setting for all following tabledefs

        This method is used e.g. for setting a global filter or table heads.
        :param args: key->value pairs of values to set for example 'table_head', 'database_table'
                     or 'aggregation_variables', 'reporting_columns'
        :return:
        """
        for key in args:
            if key in self._keys_inert:
                self._cache_inert[key] = args[key]
            else:
                raise Exception("Wrong inert-Key '{}', try something from {} ".format(key, str(self._keys_inert)))

    def fill_contents_inert(self) -> None:
        """Fills missing attributes for all tabdefs with the values of the preceding tabdef"""
        database_table_last, columns_reporting_last, table_head_last = None, None, None
        for tabdef_name in self._tabdef_order:
            tabdef = self[tabdef_name]
            if tabdef.database_table:  # always take most recent
                database_table_last = tabdef.database_table
            elif database_table_last:  # fill with last if missing
                tabdef.database_table = database_table_last
            if tabdef.reporting_columns:  # always take most recent
                columns_reporting_last = tabdef.reporting_columns
            elif columns_reporting_last:  # fill with last if missing
                tabdef.reporting_columns = columns_reporting_last
            if tabdef.table_head:  # always take most recent
                table_head_last = tabdef.table_head
            elif table_head_last:  # fill with last if missing
                tabdef.table_head = table_head_last

    def __getitem__(self, tabdef_name: str) -> TabDef:
        tabdef = dict.__getitem__(self, tabdef_name)
        return tabdef

    def __delitem__(self, item_name):
        dict.__delitem__(self, item_name)
        del(self._tabdef_order[self._tabdef_order.index(item_name)])

class TabHead(list):
    """Collection object for codeplans that describe the header of a table and its subsplits."""

    def __init__(self, *arguments):
        super(TabHead, self).__init__()
        self.is_subhead = False  # XXX Flag, ob es sich um einen Verschachtelten Kopf handelt.
        for arg in arguments:
            self.append(arg)

    def append(self, head: CodePlan) -> None:
        """Append function of list object is overridden in order to add a check for the CodePlan

        :param head:
        """
        if isinstance(head, CodePlan):
            head.check_contents()
            super(TabHead, self).append(head)
        elif isinstance(head, TabHead):
            if self.is_subhead:
                raise TypeError("Nested TabHeads only for 1 level allowed!")
            else:
                head.is_subhead = True
                super(TabHead, self).append(head)
        else:
            raise TypeError("Wrong object added to TabHead ({}). Only CodePlan or TabHead allowed!".format(type(head)))


#     def split_head(self,reportingColumnCount):
#         ###XXXXXXX Baustelle
#         maxColumns = 10
#
#         ## pruefen, weiviele codes es insgesammt werden.
#         totalCodes = 1 # Gesamtspalte
#         for subHead in self:
#             totalCodes += len(subHead.keyOrder)
#
#         if totalCodes * reportingColumnCount > maxColumns: ## pruefen ob breite ueberschritten wird.
#             newHead = []
#             remainingCodes = math.floor((maxColumns - reportingColumnCount)/ reportingColumnCount) ##fuer gesamt
#             remainingColumns = maxColumns - reportingColumnCount
#             codeCache = {}
#             i = 1
#             codeCache[1] = []
#             for subHead in self:
#                 for code in subHead.keyOrder:
#                     if remainingColumns <  reportingColumnCount:
#                         remainingColumns = maxColumns - reportingColumnCount
#                         i += 1
#                         codeCache[i] = []
#                     codeCache[i].append(code)
#                     remainingColumns -=reportingColumnCount
#                     print code, remainingCodes, reportingColumnCount
#
#             for row in  codeCache:
#                 cp = copy.copy(subHead)
#                 cp.name = cp.name + " (%d)" %row
#                 cp.data = {}
#                 for code in codeCache[row]:
#                     cp.data[code] = subHead.data[code]
#                 cp.keyOrder = codeCache[row]
#                 self.append(cp)
#             for temphead in newHead:
#                 self.append(temphead)
#             self = newHead


