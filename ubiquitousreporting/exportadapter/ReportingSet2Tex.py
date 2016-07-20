# -*- coding: utf-8 -*-
import codecs
import os
import locale
from datetime import datetime
import logging
import sys

from sdsct.ubiquitousreporting.dataobjects.report_generic import CodePlan
from sdsct.ubiquitousreporting.dataobjects.report_generic import ReportingSet
from sdsct.ubiquitousreporting.dataobjects.report_tab import TabHead, TabReportDef
from sdsct.ubiquitousreporting.exportadapter.reportingset2export import ReportingSet2Export


class TexPage(object):
    def __init__(self):
        raise NotImplementedError()


class TexTableReport(object):
    def __init__(self):
        self.preamble = u"""
\documentclass[a4paper, 10pt, landscape, captions=nooneline]{scrreprt} 
\\usepackage{ngerman}
\\usepackage{longtable}
\\usepackage{booktabs}
\\usepackage{graphicx}
\\usepackage{array}
\\usepackage{scrpage2}
\\usepackage[labelfont=bf, font=large]{caption}
\\usepackage[utf8]{inputenc} 
%\\usepackage[latin1]{inputenc} 
\\usepackage[a4paper, left=7mm,right=7mm,top=10mm,bottom=20mm,landscape]{geometry}
\special{papersize=210mm,297mm}
\\usepackage[colorlinks=true,linkcolor=black]{hyperref}
\captionsetup{tablewithin=none}  %% setzt die Nummerierung auf Fortlaufend.
\\renewcommand{\\sfdefault}{phv} 
\\renewcommand*\\familydefault{\\sfdefault} 
\clearscrheadings
\clearscrplain
\clearscrheadfoot
\pagestyle{scrheadings}
"""


class ReportingSet2Tex(ReportingSet2Export):
    def __init__(self, output_directory: str):
        super(ReportingSet2Tex, self).__init__(output_directory)
        self._display_label = 'label'  # # 'label', 'both', 'code'
        self.split_main_codes_max = 1000
        self.split_main_width_cm = 8
        """Width in cm for the first column in every table"""
        self.encoding_target = 'utf-8'
        self.table_heads = []  # XXX replace with none?
        self.lagTitle = ""
        locale.setlocale(locale.LC_ALL, '')
        self.TableReport = TexTableReport()
        self.output_directory = output_directory
        self.enable_headSplitting = True
        self.dataSepLines_enabled = False
        self.debug_content = True

    @property
    def display_label(self):
        return self._display_label

    @display_label.setter
    def display_label(self, value: str):
        if value not in ('label', 'both', 'code'):  ##XXX with constants?
            raise Exception('Only one of the following is allowed: label, both or code')
        else:
            self._display_label = value

    def _build_table_tex(self, rs: ReportingSet, head=None):
        """
        :param rs: ReportingSet to be texed
        :param head:
        :return:
        """
        rs_txt = ""
        codes_displayed_max_number = 90  # FIXME XXX not working.
        mainsplit_width = self.split_main_width_cm
        mainsplit_columns_count = 1

        table_heads = []
        data_columns_count = len(self.columns_reporting)
        if not head:
            table_heads.append(CodePlan())  # add empty codeplan if no head is present
        elif isinstance(head, CodePlan):
            data_columns_count *= len(head) + 1  # + 1 for total
            table_heads.append(head)
        elif isinstance(head, TabHead):
            if head.is_subhead:  # unschön  FIXME
                table_heads = head
                data_columns_count = len(self.columns_reporting) * (sum([len(element) for element in table_heads]) + 1)
            else:  # unschön
                raise Exception("WTF")
        else:
            raise Exception("Unkown type found as table head." + str(type(head)))

        """Filtern auf relevante Datensets, 'TOTAL' gehört immer dazu."""
        datasets_names_relevant = [head_sub.variables[0] + "_" + str(code)
                                   for head_sub in table_heads
                                   for code in head_sub.key_order]

        datasets_names_relevant.insert(0, 'TOTAL')
        datasets = {name: rs[name] for name in datasets_names_relevant if name in rs}
        # Bereinigen der Labels. Wenn mehr als 8 labels, dann nur die Labels mit Werten.
        if len(rs.split_main.key_order) >= codes_displayed_max_number:
            tempOrder = []
            for key in rs.split_main.key_order:
                if datasets['TOTAL']['COUNT'] and key in datasets['TOTAL']['COUNT'].keys():
                    tempOrder.append(key)
            codes_trailing = (96, 99)  # 'Weiß' nicht und 'keine Angabe' werden an das Ende gesetzt. TODO parametrisiere
            for code in codes_trailing:
                if code in tempOrder:
                    tempOrder.pop(tempOrder.index(code))
                    tempOrder.append(code)
            rs.split_main.key_order = tempOrder

        # Sonderschleife fuer den Titel. Der Titel wird nur einmal in das Inhaltsverzeichnis übernommen.
        if len(table_heads) == 0:
            raise Exception("Warum ist der Tablehead nicht >0?")
        tableHead_tex = len(self.columns_reporting) * "&"
        subHeadDataCols = 0
        for head_sub in table_heads:
            if len(head_sub) > 0:
                tableHead_tex += r"&\multicolumn{" + str(len(self.columns_reporting) * len(head_sub)) + "}{l}{" + str(
                    self._convert_symbols2tex(head_sub.title)) + "}"
                subHeadDataCols += len(head_sub)
        tableHead_tex += r"\\" + "\n "
        if data_columns_count - len(self.columns_reporting) > 0:
            midrule_start = len(self.columns_reporting) + mainsplit_columns_count + 1
            midrule_end = midrule_start + subHeadDataCols * len(self.columns_reporting) - 1
            tableHead_tex += r"\cmidrule(l){" + str(midrule_start) + "-" + str(midrule_end) + "}"

        #########################################
        # ## Zeile mit Codes als Spaltennamen
        #########################################
        tableHead_tex += r"&\multicolumn{{{span}}}{{l}}{{GESAMT}}".format(span=len(self.columns_reporting))

        codes_head = ['TOTAL'] + [head_sub.variables[0] + "_" + str(key)
                                  for head_sub in table_heads
                                  for key in head_sub.key_order]
        # ## Kopfbeschriftung
        if len(self.columns_reporting) < 3:
            width = "1.9cm"
        elif len(self.columns_reporting) == 3:
            width = "4cm"
        else:
            width = "6cm"
        for head_sub in table_heads:  ####XXXXX warum fuer alle unterkoepfe?
            for code in head_sub.key_order:
                insert = self._convert_symbols2tex(head_sub[code])
                if self._display_label == "both" and str(code) != insert:
                    insert = str(code) + " " + insert
                tableHead_tex += r"&\multicolumn{{{columns}}}{{p{{{width}}}}}{{{insert}}}".format(
                    columns=str(len(self.columns_reporting)), width=width, insert=insert)

        # ##XXXXXXXXXX brauche ich die rs vor dem STring??
        tableHead_tex += r"\\ " + "\n "
        ##### Unterste Kopfzeile mit Spalteninhalt.
        tableHead_tex += "Code Label" if self._display_label == "both" else "Kategorie"
        tableHead_tex += ''.join(
            ["&\multicolumn{1}{c}{" + r"\footnotesize{" + self.column_type_labels[reporting_column_type] + "}}" for
             reporting_column_type in
             self.columns_reporting])
        tableHead_tex += ''.join(
            ["&\multicolumn{1}{c}{" + r"\footnotesize{" + self.column_type_labels[reporting_column_type] + "}}" for code
             in head_sub.key_order
             for subHead in table_heads for reporting_column_type in self.columns_reporting])
        #        for subHead in tableHeads:
        #            for code in subHead.key_order:
        #                for column in self.reportingColumns:
        #                    dummy += "&\multicolumn{1}{c}{"+r"\footnotesize{"+self.columnType[column]+"}}"
        tableHead_tex += r"\\"

        rs_txt += r"\begin{longtable}[l]{"
        #### Spaltenbreite in Abhaengigkeit der dargestellten Codes.
        rs_txt += "p{1cm}" if self._display_label == "code" else r">{{\raggedright}}p{{{width}cm}}".format(
            width=mainsplit_width)
        rs_txt += "r" * data_columns_count + "}\n"
        # ## Ueberschrift, mit Pruefung, dass nur die erste Tabelle jeweils in Inhaltsverzeichnis kommt.
        rs_txt += r"\caption"
        if self.lagTitle == rs.title:
            rs_txt += r"[]"

        insert = None
        if not rs.title:
            rs.title = rs.split_main.variables[0]  # falsche reihenfolge??? #XXXX  waru mnicht alles;
        elif self.debug_content:
            insert = " [{}]".format(rs.split_main.variables[0])  # reihenfolge??? #XXXX  waru mnicht alles;
            pass
        if not insert:
            insert = ""
        self.lagTitle = str(rs.title)
        if 'section' in rs.content_misc.keys():
            rs_txt += r"{" + self._convert_symbols2tex(rs.content_misc['section'] + " -- " + rs.title) + r"}\\ "
        else:
            if rs.title is None:
                rs.title = ''
            rs_txt += r"{" + self._convert_symbols2tex(rs.title + insert) + r"}\\ "
        rs_txt += r"\toprule[1.5pt]\\ " + tableHead_tex + r"\midrule[1pt]\addlinespace \endfirsthead "
        head_last = r"\caption[]{" + self._convert_symbols2tex(rs.title) + r" \dots (Fortsetzung)}\\ "
        head_last += r"\toprule[1.5pt]\\ " + tableHead_tex + r"\midrule[1pt]\addlinespace \endhead "
        foot_first = r"\bottomrule[1.5pt] "
        foot_first += r"\multicolumn{" + str(data_columns_count + 1) + r"} {l} {\textit{Fortsetzung \ldots}}\\"
        foot_first += r"\endfoot "
        foot_last = r"\bottomrule[1.5pt] "
        if rs.content_misc.get('subTitle'):
            foot_last += r" \multicolumn{" + str(
                data_columns_count + 1) + r"}{p{0.5\linewidth}}{\footnotesize{" + self._convert_symbols2tex(
                rs.content_misc['subTitle']) + r" }}  \\"
        if rs.content_misc.get('comment'):
            foot_last += r" \multicolumn{" + str(
                data_columns_count + 1) + r"}{p{0.5\linewidth}}{\footnotesize{" + self._convert_symbols2tex(
                rs.content_misc['comment']) + r" }}  \\"
        if rs.content_misc.get('filterText'):  # TODO wieso get?
            foot_last += r" \multicolumn{{{columnCount}}}{{p{{0.5\linewidth}}}}{{\footnotesize{{Filter: ".format(
                columnCount=str(data_columns_count + 1)) + self._convert_symbols2tex(
                rs.content_misc['filterText']) + r" }}  \\"
        if rs.timestamp:
            foot_last += r" \multicolumn{" + str(
                data_columns_count + 1) + r"}{p{0.5\linewidth}}{\footnotesize{" + \
                         self._convert_symbols2tex(rs.timestamp) + r" }}  \\"
        foot_last += r"\endlastfoot "

        ###############
        ############### Ab hier Daten
        ############### 

        data_block = ""
        total = {column: {} for column in self.columns_reporting}
        i = 0

        for row in rs.split_main.key_order:
            """zeile fuer zeile Daten eintragen """
            if i > self.split_main_codes_max:
                break  # XXX TODO: sdfasd
            i = i + 1
            if self._display_label == "both":
                # dataBlock += str(row)+" "+self._convertSympols2Tex(rs.mainSplit.data[row])
                try:
                    data_block += self._convert_symbols2tex(str(row)) + " " + self._convert_symbols2tex(
                        rs.split_main[row])
                except KeyError:
                    data_block += self._convert_symbols2tex(str(row)) + " " + self._convert_symbols2tex(
                        rs.split_main.get(row, ''))

            else:
                # if isinstance(rs.mainSplit.data[row], int):
                # if isinstance(rs.mainSplit[row], int):
                data_block += rs.split_main[str(row)] if isinstance(rs.split_main[(row)],
                                                                    int) else self._convert_symbols2tex(
                    rs.split_main[row])
                # try:
                #     data_block += unicode(rs.split_main[str(row)]) if isinstance(rs.split_main[(row)], int) else self._convert_symbols2tex(
                #         rs.split_main[row])
                # except KeyError:  # ##XXXX iuebergang
                #     row = int(row)
                #     tempval = rs.split_main.get(row, '')
                #     data_block += unicode(tempval) if isinstance(tempval, int) else self._convert_symbols2tex(tempval)

                # dataBlock += unicode(rs.mainSplit.data[row])
                # else:
                #    dataBlock += self._convertSympols2Tex(rs.mainSplit[row])
                # dataBlock += self._convertSympols2Tex(rs.mainSplit.data[row])
            column_counter = 1  # # XXX kann ich das auch anders machen?
            for code in codes_head:
                for reporting_column_type in self.columns_reporting:
                    if not column_counter in total[reporting_column_type]:
                        total[reporting_column_type][column_counter] = 0
                    # # XXXXX der Abgleich mit str hier ist wohl nur aufgrund eines Fehlers notwendig. ???
                    row = str(row)
                    if code in datasets and reporting_column_type in datasets[code] and str(row) in datasets[code][
                        reporting_column_type]:
                        total[reporting_column_type][column_counter] += datasets[code][reporting_column_type][str(row)]
                        if reporting_column_type == 'COUNT':
                            data_block += "&" + str(
                                locale.format("%.0f", datasets[code][reporting_column_type][row], True))
                        else:
                            data_block += "&" + str(locale.format("%." + str(self.decimals) + "f",
                                                                  round(datasets[code][reporting_column_type][row],
                                                                        self.decimals),
                                                                  grouping=True))
                    else:
                        total[reporting_column_type][column_counter] += 0
                        data_block += "&"
                column_counter += 1
                self.columns_reporting
            data_block += "\\\\ \n \\addlinespace "
            if self.dataSepLines_enabled:
                data_block += r"   \midrule[0.2pt]"
        if self.dataSepLines_enabled:
            data_block = data_block[0:-15]

        block_summary_tex = r"\midrule\addlinespace "
        block_summary_tex += "GESAMT"
        column_counter = 1

        for code in codes_head:
            for reporting_column_type in self.columns_reporting:
                try:
                    if reporting_column_type == 'COUNT':
                        block_summary_tex += r"&" + str(
                            locale.format("%.0f", total[reporting_column_type][column_counter], True))
                    elif reporting_column_type == 'PCT':
                        block_summary_tex += r"&" + str(locale.format("%." + str(self.decimals) + "f", round(
                            total[reporting_column_type][column_counter], self.decimals)))
                    else:
                        block_summary_tex += r"&" + str(locale.format("%." + str(self.decimals) + "f", round(
                            total[reporting_column_type][column_counter], self.decimals), True))
                except:
                    block_summary_tex += r"&"
            column_counter += 1
        block_summary_tex += r"\\ \addlinespace "

        if 'TOTAL' in datasets and datasets['TOTAL']:
            if 'COUNT_TOTAL' in datasets['TOTAL']:
                block_summary_tex += "Fallzahl"
                for code in codes_head:
                    if self.columns_reporting == ['PCT_GN_W']:
                        datasets[code]['COUNT_TOTAL'] = datasets[code]['COUNT_GN_TOTAL']
                        datasets[code]['COUNT_W_TOTAL'] = datasets[code]['COUNT_GN_W_TOTAL']
                    # print(datasets.keys())
                    if datasets[code]:
                        count_total = str(locale.format("%.0f", datasets[code]['COUNT_TOTAL'], True))
                    else:
                        count_total = str(0)
                    for reporting_column_type in self.columns_reporting:
                        if reporting_column_type == "COUNT":
                            block_summary_tex += r"&" + count_total
                        elif reporting_column_type == "COUNT_W":
                            try:
                                block_summary_tex += r"&" + str(locale.format("%." + str(self.decimals) + "f",
                                                                              round(datasets[code]['COUNT_W_TOTAL'],
                                                                                    self.decimals), True))
                            except:
                                block_summary_tex += r"&"
                        else:
                            block_summary_tex += r"&"

                            # if len(self.reportingColumns) > 1:
                            #    summaryBlock_tex += r"&\multicolumn{"+str(len(self.reportingColumns))+"}{l}{"
                            #                 if datasets[code].data:
                            #                     summaryBlock_tex += count_total
                            # summaryBlock_tex += str(datasets[code].data['COUNT_TOTAL']) #### nachbessern
                            # except:
                            #    summaryBlock_tex += str(0)
                            #                 else:
                            #                     summaryBlock_tex += str(0)
                            #                 summaryBlock_tex += r"}"

                            #             else:
                            #                 summaryBlock_tex += r"&"+count_total
                block_summary_tex += r"\\ \addlinespace "

            if 'AVG_TOTAL' in datasets['TOTAL']:
                block_summary_tex += "Durchschnitt"
                for code in codes_head:
                    if datasets[code]:
                        count_total = str(
                            locale.format("%." + str(self.decimals) + "f", datasets[code]['AVG_TOTAL'], True))
                    else:
                        count_total = str(0)
                    for reporting_column_type in self.columns_reporting:
                        if reporting_column_type == "COUNT":
                            block_summary_tex += r"&" + count_total
                        elif reporting_column_type == "COUNT_W":
                            try:
                                block_summary_tex += r"&" + str(locale.format("%." + str(self.decimals) + "f",
                                                                              round(datasets[code]['COUNT_W_TOTAL'],
                                                                                    self.decimals), True))
                            except:
                                block_summary_tex += r"&"
                        else:
                            block_summary_tex += r"&"

                            # if len(self.reportingColumns) > 1:
                            #    summaryBlock_tex += r"&\multicolumn{"+str(len(self.reportingColumns))+"}{l}{"
                            #
                            #                 if datasets[code].data:
                            #                     summaryBlock_tex += count_total
                            # summaryBlock_tex += str(datasets[code].data['COUNT_TOTAL']) #### nachbessern
                            # except:
                            #    summaryBlock_tex += str(0)
                            #                 else:
                            #                     summaryBlock_tex += str(0)
                            #                 summaryBlock_tex += r"}"

                            #             else:
                            #                 summaryBlock_tex += r"&"+count_total

                block_summary_tex += r"\\ \addlinespace "

            # if 'COUNT_W_TOTAL'  in datasets['TOTAL'].data.keys():
            #    summaryBlock_tex += "Fallzahl gewichtet"
            #    for code in codes_head:
            #       if len(self.reportingColumns) > 1:
            #            summaryBlock_tex += r"&\multicolumn{"+str(len(self.reportingColumns))+"}{l}{"
            #            summaryBlock_tex += str(locale.format("%."+str(self.decimals)+"f", round(datasets[code].data['COUNT_W_TOTAL'], self.decimals)))
            #            summaryBlock_tex += r"}"
            #        else:
            #            summaryBlock_tex += r"&"+str(locale.format("%."+str(self.decimals)+"f", round(datasets[code].data['COUNT_W_TOTAL'], self.decimals)))
            #                    #summaryBlock_tex += r"&0"
            #    summaryBlock_tex +=r"\\ \addlinespace "

            if False:
                aready_displayed = ["TOTAL", ]
                block_summary_tex += "Zusammenhang"
                for code in codes_head:
                    if code == "TOTAL":
                        block_summary_tex += r"&\multicolumn{" + str(len(self.columns_reporting)) + "}{l}{/}"
                    elif code[0:code.rfind('_')] not in aready_displayed:
                        aready_displayed.append(code[0:code.rfind('_')])
                        statistics = rs.subSplits[code[0:code.rfind('_')]].statistics
                        block_summary_tex += r"&\multicolumn{" + str(len(self.columns_reporting) * len(
                            rs.subSplits[code[0:code.rfind('_')]].key_order)) + "}{l}{"
                        block_summary_tex += "P($\chi2$): " + str(
                            round(statistics["chi2P"] * 100, 1)) + "\%, CramersV: " + str(
                            round(statistics["CramersV"], 2))
                        block_summary_tex += r"}"
                    else:
                        pass
                block_summary_tex += r"\\ \addlinespace "

        rs_txt += head_last + block_summary_tex + foot_first + block_summary_tex + foot_last + data_block
        rs_txt += " \end{longtable}\n\r\\newpage\n\r"
        return rs_txt

    def _compose_first_foot(self):
        pass

    def _compose_last_foot(self):
        pass

    def _compose_summary_block(self):
        pass

    def _compose_data_block(self):
        pass

    @staticmethod
    def _convert_symbols2tex(string):
        string = str(string)  # TODO: extend to generic tag stripping
        string = string.replace('<strong>', '').replace('</strong>', '')
        string = string.replace('$', '\$').replace('%', '\%').replace('_', '\_').replace('&', '\&').replace('"',
                                                                                                            '').replace(
            '#', '\#').replace('>', '\\textgreater ').replace('<', '\\textless ')
        return string

    def split_head(self, head, reportingColumnCount):
        if isinstance(head, CodePlan):  # TODO 2. Bedingung kaputt.
            head = TabHead(head)
        if isinstance(head[0], TabHead):
            return self.split_head(head[0])  # recursive
        elif isinstance(head[0], CodePlan):
            columns_count_max = 14  # TODO relocate!!
            code_count = 1  # Total
            for codeplan_head in head:
                code_count += len(codeplan_head.key_order)
            columns_count_original = code_count * reportingColumnCount
            if columns_count_original <= columns_count_max:  # # Nichts zu tun. Gesamtlänge der Codepläne unter maximumg
                return head
            else:
                newHeads = []
                if len(head) == 1:
                    head_new = TabHead()
                    newHeads.append(head_new)
                    i = 1
                    remainingColmuns = columns_count_max - reportingColumnCount
                    remainingCodes = len(head[0].key_order)
                    try:  # TODO: ausbessern!!
                        newCodePlan = CodePlan(title=head[0].title + " (%d)" % i, variables=head[0].variables)
                    except:
                        newCodePlan = CodePlan(title=head[0].title.encode('utf8') + " (%d)" % i,
                                               variables=head[0].variables)
                    for key in head[0].key_order:
                        remainingColmuns -= reportingColumnCount
                        newCodePlan.data = {}
                        newCodePlan.data[key] = head[0][key]
                        newCodePlan[key] = head[0][key]
                        newCodePlan.key_order.append(key)
                        remainingCodes -= 1
                        if remainingColmuns <= reportingColumnCount and remainingCodes > 0:
                            i += 1
                            remainingColmuns = columns_count_max - reportingColumnCount
                            head_new = TabHead()
                            newHeads.append(head_new)
                            head_new.append(newCodePlan)
                            newCodePlan = CodePlan(title=head[0].title + " (%d)" % i, variables=head[0].variables)
                    head_new.append(newCodePlan)
            return newHeads
            # Erstellt eine Tex-Datei basierend auf einem TabellenbandsDefinitionsobjektes.
            #
            # Der Testmode verhindert das tatsaechliche Texen. Man kann aber pruefen, ob das Bauen des Tex-Codes funtioniert.

    def export_tabreport(self, tabreport: TabReportDef, output_name: str = 'tabband', testmode: bool = False):
        """
        :param tabreport:
        :param output_name:
        :param testmode:
        :return:
        """
        tabreport.fill_contents_inert()
        tex = r"""
\begin{{document}}
\makebox(600,300)[l]{{}}\\
\Large{{{preTitle}}}\\
\\
\Huge{{{title}}}
\\
\\
\normalsize
{subTitle}
\listoftables
\newpage
\clearpage
\ofoot{{\pagemark}}
\ifoot{{{footer}}}
""".format(preTitle=self._convert_symbols2tex(tabreport.title_pre)  # XXX funktionen auslagern
           , title=self._convert_symbols2tex(tabreport.title)
           , subTitle=self._convert_symbols2tex(tabreport.title_sub)
           , footer=self._convert_symbols2tex(tabreport.footer))
        for tabdef_name in tabreport.tabdef_order:
            tabdef = tabreport[tabdef_name]
            if tabdef.filter_rs:
                if tabdef.filter_rs and isinstance(tabdef.filter_rs, str):
                    tabdef.reportingset.content_misc['filterText'] = tabdef.filter_rs
                else:
                    raise Exception('WTF')  # TODO ausbessern
                tabdef.reportingset.content_misc['filterText'] = tabdef.filter_rs  # .label
            if tabdef.section:
                tabdef.reportingset.content_misc['section'] = tabdef.section
            if tabdef.reporting_columns:
                self.columns_reporting = tabdef.reportingColumns
            if tabdef.reportingset:
                if tabdef.table_head:
                    for head in tabdef.table_head:
                        if self.enable_headSplitting is not True:
                            if isinstance(head, CodePlan) or (isinstance(head, TabHead) and head.is_subhead):
                                tex += self._build_table_tex(tabdef.reportingset, head)
                            else:
                                print(type(head))  # TODO ausbessern
                                raise Exception("WTF")
                        else:
                            head_new = self.split_head(head, len(self.columns_reporting))
                            for subhead in head_new:  # # neue list comp
                                if type(subhead) == TabHead:
                                    tex += ''.join(
                                        [self._build_table_tex(tabdef.reportingset, subSubhead) for subSubhead in
                                         subhead])
                                elif type(subhead) == CodePlan:
                                    tex += self._build_table_tex(tabdef.reportingset, head)
                                else:
                                    print(subhead)
                                    print(type(subhead))  # TODO ausbessern
                                    raise Exception('WTF')
                else:
                    tex += self._build_table_tex(tabdef.reportingset)
                    # Test fuer trennseite:
                    #            tex += r"""
                    # \newpage
                    # \clearpage
                    # \makebox(600,300)[l]{}\\
                    # #\Huge{Trennseite}
                    # \\
                    # \\
                    # \normalsize """
        tex += """
\end{document}"""
        if not testmode:
            self.tex_table(tex, output_name)

    def tex_table(self, txt, output_name: str, with_timestamp: bool = False):  # fixme rename
        """
        Finale Funktion zur Ausgabe der getexten Tabellen in eine Datei.
        """
        encoding = 'utf-8'
        if self.filename_with_timestamp or with_timestamp:
            output_name += '_' + str(datetime.now())[:19].replace('-', '').replace(':', '').replace(' ', '_')
        tex_file = codecs.open(self.output_directory + r'/' + output_name + '.tex', 'w', encoding=encoding)
        tex_text = self.TableReport.preamble + txt
        if sys.version_info[0] == 2:
            try:
                tex_file.write(tex_text.decode(self.encoding_target))
            except UnicodeEncodeError:
                tex_file.write(tex_text)
        else:
            tex_file.write(tex_text)
        tex_file.close()

        os.chdir(self.output_directory)
        for i in range(1, 4):
            print(" Tex run {}".format(i))
            os.system("pdflatex {}.tex ".format(output_name))

        # #aufraeumen
        os.system(r"del *.aux ")
        os.system(r"del *.log ")
        os.system(r"del *.lot ")
        # os.system(r"del *.tex ")
        os.system(r"del *.out ")

        # os.system(r"latex table.tex ")
        # os.system(r"latex table.tex ")
        # os.system(r"dvips -t landscape  table.dvi ")
        # os.system(r"dvips table.dvi ")
        # os.system(r"ps2pdf  table.ps ")
        # os.system(r"ps2pdf -sPAPERSIZE#a4 -dOptimize#true -dEmbedAllFonts#true  table.ps ")
        # os.system(self.outputName)


class TexPackage(object):
    def __init__(self, title, options={}):
        self.title = title
        self.options = {}
