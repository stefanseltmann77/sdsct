# -*- coding: utf-8 -*-
import datetime
import sys
import os
from openpyxl import Workbook
from sdsct.exportadapter.export2generic import Export2Generic


class Export2xlsx(Export2Generic):

    def export(self, result, file_name: str="pythonexport.exp", result_title: str='table'):
        """

        :param result:
        :param file_name:
        :param result_title:
        :return:
        """
        try:
            column_names = result.field_names
        except AttributeError:
            raise AttributeError(str(sys.exc_info()[1])+'. You have to pass a proper result as a parameter!')
        
        wb = Workbook()
        sheet = wb.get_sheet_by_name('Sheet')
        sheet.title = result_title
        sheet.append(column_names)
        for row in result:
            row = [element if not isinstance(element, set) else None for element in row]
            sheet.append(row)
        wb.save(filename=self.output_directory+os.sep+file_name)
