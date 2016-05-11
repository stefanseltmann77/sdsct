# -*- coding: utf-8 -*-
import datetime
import sys
import xlwt
from Python2Exportfile import Python2Exportfile

class Python2xls(Python2Exportfile):

    def export(self, result, output):
        self.exportSqlResult(result, output)

    def exportSqlResult(self, result, output):
        try: 
            colnames = result.fieldNames
        except AttributeError:
            raise AttributeError(str(sys.exc_info()[1])+'. You have to pass a proper result as a parameter!')
        
        wb = xlwt.Workbook()
        sheet = wb.add_sheet('table01')
        y = 0
        x = 0
        for title in colnames:
            sheet.write(y,x,title)
            x+=1
        y+=1
        for row in result:
            x = 0
            for content in colnames:
                cell = str(row[content]) if type(row[content]) in [datetime.datetime, datetime.timedelta] else row[content] 
                sheet.write(y,x,cell)
                x+=1
            y+=1
        wb.save(self.outputDir+'/'+output)

if __name__ == '__main__':
    pass


#        tabNames = querys.keys()
#        tabNames.sort()
#        for tabName in tabNames:        
#            array = self.db.query(querys[tabName], cursorType ='tuple')
#            descr = self.db.cursor.description
#    
#            colnames = []
#            for element in descr:
#                colnames.append(element[0])
#    
#            
#            for row in array:
#                x = 0
#                for content in row:
#                    if type(content) in [datetime.datetime]:
#                        cell = str(content)
#                    else:
#                        cell = content
#                    sheet.write(y,x,cell)
#                    x+=1
#                y+=1
#        try:
#            if output[-4:] == ".xls":
#                wb.save(output)
#            else:
#                wb.save(output+'pythonExport.xls')
#
#        except IOError, e:
#            print e
#            starttime =  datetime.date.today()
#            sys.exit(output +" konnte nicht erstellt werden. Vermutlich ist die Datei geöffnet!")
#
#    def exportSqlTabs(self, querys, output):
#        """XXXXXXXXXXXXXXXveraletet"""
#        """
#        Exportiert mehrere Sql-Abfragen direkt in eine Excel-Datei.
#        Die Abfragen muessen als Dict uebergeben werden. Die Schluessel dienen dabei als Labels fuer die Tabellenblaetter.
#        Die Tabellenblattlables werden automatisch aufsteigend alphabetisch sortiert.
#        Da die Beschriftungszeilen je nach Abfrage variieren koennen, muessen die Ueberschriften aus der 
#        jeweiligen Abfrage abgeleitet werden.
#        """
#
#        wb = Workbook()
#        
#        tabNames = querys.keys()
#        tabNames.sort()
#        for tabName in tabNames:        
#            array = self.db.query(querys[tabName], cursorType ='tuple')
#            descr = self.db.cursor.description
#    
#            colnames = []
#            for element in descr:
#                colnames.append(element[0])
#    
#    
#            sheet = wb.add_sheet(tabName)
#    
#            y = 0
#          
#    
#            x = 0
#            for title in colnames:
#                sheet.write(y,x,title)
#                x+=1
#            y+=1
#            
#            for row in array:
#                x = 0
#                for content in row:
#                    if type(content) in [datetime.datetime]:
#                        cell = str(content)
#                    else:
#                        cell = content
#                    sheet.write(y,x,cell)
#                    x+=1
#                y+=1
#        try:
#            if output[-4:] == ".xls":
#                wb.save(output)
#            else:
#                wb.save(output+'pythonExport.xls')
#
#        except IOError, e:
#            print e
#            sys.exit(output +" konnte nicht erstellt werden. Vermutlich ist die Datei geöffnet!")
#
#
#    def exportSql(self, query, output, header = None):
#        """XXXXXXXXXXXXXXXveraletet"""
#        """
#        Exportiert eine Sql-Abfragen direkt in eine Excel-Datei.
#        Mit dem tuple 'header' kann man die Ueberschriften neu vergeben.
#        """
#        
#        array = self.db.query(query, cursorType ='tuple')
#        descr = self.db.cursor.description
#
#        if header != None:
#            colnames = header
#        else:
#            colnames = []
#            for element in descr:
#                colnames.append(element[0])
#
#
#        wb = Workbook()
#        sheet = wb.add_sheet('table01')
#
#        y = 0
#      
#
#        x = 0
#        for title in colnames:
#            sheet.write(y,x,title)
#            x+=1
#        y+=1
#        
#        for row in array:
#            x = 0
#            for content in row:
#                if type(content) in [datetime.datetime]:
#                    cell = str(content)
#                else:
#                    cell = content
#                sheet.write(y,x,cell)
#                x+=1
#            y+=1
#        try:
#            if output[-4:] == ".xls":
#                wb.save(output)
#            else:
#                wb.save(output+'pythonExport.xls')
#        except IOError, e:
#            print e
#            sys.exit(output +" konnte nicht erstellt werden. Vermutlich ist die Datei geöffnet!")
#            #wb.save(output+'xlstext'+str(starttime)+'.xls')