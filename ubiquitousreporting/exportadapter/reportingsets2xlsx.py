# -*- coding: utf-8 -*-
from sdsct.ubiquitousreporting.dataobjects.report_generic import CodePlan
from sdsct.ubiquitousreporting.dataobjects.report_tab import TabHead
from sdsct.ubiquitousreporting.dataobjects.report_tab import TabReportDef
from sdsct.ubiquitousreporting.dataobjects.report_tab import TabDef
from sdsct.ubiquitousreporting.exportadapter.reportingset2export import ReportingSet2Export
import openpyxl
from openpyxl.workbook import Workbook
import logging

logging.basicConfig(level=logging.INFO)


class ReportingSets2Xlsx(ReportingSet2Export):
    # def __init__(self, output_directory):
    #     self.title = "Tabellenbandtitel"
    #     self.subtitle = "Tabellenbanduntertitel"
    #     output_directory = output_directory.replace('\\', '/')  # TODO: put global
    #     self.outputDir = output_directory if output_directory.endswith('/') else output_directory
    #     self.columnType = {'COUNT': 'Anzahl',
    #                        'PCT': 'Prozent',
    #                        'SUM': 'Summe',
    #                        'AVG': 'Durchschnitt',
    #                        'COUNT_W': 'Anzahl gew.',
    #                        'PCT_W': 'Prozent gew.',
    #                        'PCT_GN_W': 'ProzentBasis gew.',
    #                        'SUM_W': 'Summe gew.',
    #                        'AVG_W': 'Durchschnitt gew.'}

    def export_tabreport(self, tabreport: TabReportDef, output_name='tabband', testmode=False):
        logging.info('EXPORT tabreport to XLS')
        wb = Workbook()
        sheet = wb.active
        x, y = (1, 1)
        spacing_between_tables = 3  # cells
        table_offset = 0
        for tabdef_name in tabreport.tabdef_order:
            table_offset += spacing_between_tables + self.plot_tabdef(tabdef=tabreport[tabdef_name],
                                                                      sheet=sheet, x=x, y=y + table_offset)




            #         if tabdef.filter_rs:
            #             if tabdef.filter_rs and isinstance(tabdef.filter_rs, str):
            #                 tabdef.reportingset.content_misc['filterText'] = tabdef.filter_rs
            #             else:
            #                 tabdef.reportingset.content_misc['filterText'] = tabdef.filter_rs.label
            #         if tabdef.section:
            #             tabdef.reportingset.content_misc['section'] = tabdef.section
            #         if tabdef.reporting_columns:
            #             self.reporting_columns = tabdef.reporting_columns

            #         # try:
            #         #     sheet.write(y+tabOffset,0, tabDef.title.decode('utf-8'))
            #         # except UnicodeEncodeError:
            #         #     sheet.write(y+tabOffset,0, tabDef.title.encode('utf-8').decode('utf-8'))
            #
            #         if tabdef.table_head:
            #             i = 0
            #             for head in tabdef.table_head:
            #                 if i == 0:
            #                     if isinstance(head, CodePlan):
            #                         table_offset += self.plot_tabdef(tabdef, head, sheet, x, y + table_offset) + 6
            #                     elif isinstance(head, TabHead) and head.is_subhead is True:
            #                         table_offset += self.plot_tabdef(tabdef, head, sheet, x, y + table_offset) + 6
            #                     else:
            #                         print(type(head))
            #                         raise Exception("WTF")
            #                 i += 1
        wb.save(self.output_directory + '/' +  output_name + '.xlsx')

    #     if output_name[-4:] == ".xls":  # todo auslagern
    #         wb.save(self.outputDir + '/' +  output_name)
    #     else:
    #         wb.save(self.outputDir + '/' +  output_name + '.xls')
    #     logging.info('Tabreport to XLS exported!')
    #

    def plot_tabdef(self, tabdef: TabDef, sheet, x, y, head: TabHead = None):
        height_of_header = 3
        sheet.cell(row=y, column=x).value = tabdef.title or tabdef.name  ## fixme push to tabdef.
        reportingset = tabdef.reportingset
        tabhead_xlsx = TabHead()
        tabhead_xlsx.append(CodePlan(name='TOTAL', data=['TOTAL']))
        for head in tabdef.table_head:
            if isinstance(head, TabHead):
                for cp in head:
                    tabhead_xlsx.append(cp)
            elif isinstance(head, CodePlan):
                tabhead_xlsx.append(head)

        # plot code labels
        code_order = reportingset.split_main.key_order
        for code_count, code in enumerate(code_order):
            print(tabdef.reportingset.split_main.keys())
            code_label = tabdef.reportingset.split_main[str(int(code))]

            sheet.cell(column=x, row=y + height_of_header + code_count).value = code_label

        # plot headers
        head_offset = x + 1
        for head_count, head in enumerate(tabhead_xlsx):
            sheet.cell(row=y, column=head_offset).value = head.title
            for headcode in head.key_order:
                sheet.cell(row=y + 1, column=head_offset).value = head[headcode]
                for column_reporting in self.columns_reporting:
                    sheet.cell(row=y + 2, column=head_offset).value = column_reporting
                    for code_count, code in enumerate(code_order):
                        dataset_name = headcode if headcode == 'TOTAL' else (head.variables[0] + '_'+str(headcode))
                        dataset_relevant = reportingset[dataset_name]
                        try:
                            value_display = dataset_relevant[column_reporting][code]
                        except KeyError:
                            try:
                                value_display = dataset_relevant[column_reporting][str(code)]
                            except KeyError:
                                value_display = 0
                        sheet.cell(row=y + height_of_header + code_count, column=head_offset).value = value_display
                    head_offset += 1
        return len(code_order) + height_of_header
