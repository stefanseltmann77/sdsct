# -*- coding: utf-8 -*-
import os, sys
from numpy import *
import matplotlib.pyplot as plt

class ReportingSet2MatLibPlot(object):
    def __init__(self):
        import matplotlib.pyplot as plt
        self.title = None
        self.xlabel = None
        self.ylabel = None
        self.chartType = 'barh'
        self.reportetCalc = 'COUNT'
        self.rs = None
        self.plt = plt
        self.dataRows = []
        self.colors = ('#113388', '#426BB3', '#819CCC', '#C6CEE2')
        self.mainSplitLabels = []
        self.sizeMM = (100,100)
        self.fontSize = 10
        self.chartPadding = (5,5,5,5)
        self.labelDecimals = 0
        self.exportPath = r"c:\\"
        pass 
    
    def set_colors(self, colors):
          self.colors = colors
    
    def set_size(self, width, height):
          """Setzt die Groesse in Millimeter"""
          self.sizeMM = (width, height) 
    
    def set_fontSize(self, size):
          self.fontSize = size 
    
    
    def set_reportedCalc(self, calc):
          """Bestimmt welche Vorberechung in der Grafik dargestellt werden soll"""
          self.reportetCalc = calc
    
    def sizeInch(self):
          """Rechnet die Groesse in Inch um"""
          return (self.sizeMM[0] * 0.039370078740157477, self.sizeMM[1] * 0.039370078740157477)
    
    def load_reportingSet(self, rs):
          self.rs = rs
          self.title = rs.title
         
          self.mainSplitSize = len(rs.mainSplit.data)
    
          i = len(rs.dataSets) - 1
          while i >= 0:
                dataSet = rs.dataSets[i]
                dataRow = []
                for key in rs.mainSplit.keyOrder: ##XXXXXXXXXX hier muss gefixt werden.
                      self.mainSplitLabels.append(rs.mainSplit.data[key])
                      dataRow.append(dataSet.data[self.reportetCalc][key])  ## XXX fehler, da noch pct_W.
                self.dataRows.append(dataRow)
                self.xlabel = "Prozent"
                i -= 1
    
    def build_barChart(self, rs, xScope = (0,100)):
        plt = self.plt
        plt.rcParams['ytick.major.size'] = 0
        plt.rcParams['xtick.direction'] = "out"

        fig = plt.figure()
        fig.set_size_inches(self.sizeInch())
        ax = fig.add_axes(self.padding2axes(self.chartPadding))
        
        self.mainSplitSize = len(rs.mainSplit.keyOrder)
        
        plt.axis([xScope[0],xScope[1],0,self.mainSplitSize])
        
        barData= []
        mainSplitLabels = []
        rs.mainSplit.keyOrder.reverse()
        for key in rs.mainSplit.keyOrder:
              mainSplitLabels.append(rs.mainSplit.data[key])
              barData.append(rs.dataSets['TOTAL'].data[self.reportetCalc][key])
        
        bars = ax.barh(arange(self.mainSplitSize)+ .5,  barData,  align='center', color=self.colors[1])
        
        if self.title:
              ax.set_title(self.title)
        if self.xlabel:
              ax.set_xlabel(self.xlabel)
        if self.ylabel:
              ax.set_ylabel(self.ylabel)
        ax.set_yticks(arange(self.mainSplitSize)+ .5)
        ax.set_yticklabels(mainSplitLabels)
        
        for bar in bars:
              ax.text(float(bar.get_width())+0.8, bar.get_y()+bar.get_height()/2, int(round(bar.get_width(),self.labelDecimals)), va='center', ha='left')
        
        ax.spines['right']._visible = False
        ax.spines['top']._visible = False
        ticks =  ax.xaxis.get_major_ticks()
        for tick in ticks:
              tick.tick2On = False
    
    def transpose_dataRows(self, dataRows):
          tempDataRows = []
          i = 0
          for i in range(len(dataRows[0])):
                tempRow = []
                for y in range(len(dataRows)):
                      tempRow.append(dataRows[y][i])
                tempDataRows.append(tempRow)
          return tempDataRows
    
    def padding2axes(self, padding):            
          ## [top, right, bottom, left]
          axisBottom =  float(float(padding[2])/float(self.sizeMM[1])) 
          axisLeft =  float(float(padding[3])/float(self.sizeMM[0])) 
          axisHeight =  (float(self.sizeMM[1]) - float(padding[0]) - float(padding[2]))/float(self.sizeMM[1]) 
          axisWidth  =  (float(self.sizeMM[0]) - float(padding[1]) - float(padding[3]))/float(self.sizeMM[0])
          return (axisLeft, axisBottom, axisWidth, axisHeight) 

    def build_barchart_stacked_legendeOben_old(self):
    
          plt = self.plt
          plt.rcParams['font.sans-serif'] = 'Arial'
          plt.rcParams['font.size'] = 10
          plt.rcParams['legend.fontsize'] = 10
          plt.rcParams['legend.markerscale'] = 0.1
          
          fig = plt.figure()
          fig.set_size_inches(self.sizeInch())
    
          ## [top, right, bottom, left]
          ax = fig.add_axes(self.padding2axes((7,4,6,2)))
    
          rs = self.rs
          
          rs.dataSets.reverse()  ## Chartspezifisch umsortieren.
          
          dataRows = []
          
               
          mainSplitLabels = [] 
    
    
          categoryLabels = []
          dataSetNames = []
          if rs.subSplits:
                rs.subSplits[0].keyOrder.reverse()
                rs.subSplits[0].variables
                for key in rs.subSplits[0].keyOrder:
                      dataSetNames.append(rs.subSplits[0].variables+"_"+str(key))
                      categoryLabels.append(rs.subSplits[0].data[key])
          categoryLabels.append('Gesamt')
          dataSetNames.append('TOTAL')
          
          for dataSetName in dataSetNames:
                for dataSet in rs.dataSets:
                      if dataSet.name == dataSetName:
                            
                            dataRow = []
                            for key in rs.mainSplit.keyOrder:
                                  mainSplitLabels.append(rs.mainSplit.data[key])
                                  try:
                                        dataRow.append(dataSet.data[self.reportedCalc][key])
                                  except:
                                        dataRow.append(0)
                            dataRows.append(dataRow)
          
          
                
          dataRows = self.transpose_dataRows(dataRows)
    
          ax.axis([0,100,0,len(dataRows[0])])
    
          barSets = []
          lastDataRow = None
          leftOffset = []
          for i in range(len(dataRows)):
                if lastDataRow:
                      for y in range(len(lastDataRow)):
                            leftOffset[y] = leftOffset[y] + lastDataRow[y]  
                else :
                      for value in dataRows[0]:
                            leftOffset.append(0) 
                barSets.append(ax.barh(arange(len(dataRows[0]))+ .5,  dataRows[i],  left=leftOffset, height=0.6, align='center', color=self.colors[i]))
                lastDataRow = dataRows[i]
                
          
          legendentrys = []
          for key in rs.mainSplit.keyOrder:
                legendentrys.append(rs.mainSplit.data[key]) 
          legendSympols = []
          for barSet in barSets:
                legendSympols.append(barSet[0])
          
          
          legend = plt.legend( legendSympols,  
                      legendentrys, 
                      bbox_to_anchor=(0, 1.1, 1, 0), #(x, y, width, height of the bbox) 
                      handlelength = 1, 
                      handletextpad = 0.3,
                      columnspacing = 1,
                      mode="expand",
                      ncol = len(barSets))
                      #legendentrys, bbox_to_anchor=(0.0, 0.90, 0.9, .202),  ncol = len(barSets))
    
          legend.set_frame_on(False)
          
    
          
          if self.title:
                ax.set_title(self.title)
          if self.xlabel:
                ax.set_xlabel(self.xlabel)
          if self.ylabel:
                ax.set_ylabel(self.ylabel)
          ax.set_yticks(arange(len(dataRows[0]))+ .5)
          
          ax.set_yticklabels(categoryLabels)
    
    
          lastOffset = []
          for bar in barSets[0]:
          
                lastOffset.append(0)
          barSetCount = 0
          for barSet in barSets:
                i = 0
                for bar in barSet:
                      if self.colors[barSetCount] in ('#C6CEE2', '#FFFFFF', '#D8D8D5'):
                            textColor = '#000000'
                      else:
                            textColor = '#FFFFFF' 
                             
                      ax.text(lastOffset[i]+ float(bar.get_width())*0.5, bar.get_y()+bar.get_height()/2,  int(round(bar.get_width(),0)), va='center', ha='center', color=textColor )
                      lastOffset[i] += bar.get_width()
                      i += 1
                      pass
                barSetCount += 1
                
          ax.set_yticklabels(())

    
    def build_barchart_stacked(self, rs):
          plt = self.plt
          plt.rcParams['font.sans-serif'] = 'Arial'
          plt.rcParams['font.size'] = 10
          plt.rcParams['legend.fontsize'] = 10
          plt.rcParams['legend.markerscale'] = 0.1
          
          fig = plt.figure()
          fig.set_size_inches(self.sizeInch())
    
          ## [top, right, bottom, left]
          ax = fig.add_axes(self.padding2axes((7,4,6,2)))
    
          rs.dataSets.reverse()  ## Chartspezifisch umsortieren.
          
          dataRows = []
          
               
          mainSplitLabels = [] 
    
    
          categoryLabels = []
          dataSetNames = []
          if rs.subSplits:
                rs.subSplits[0].keyOrder.reverse()
                rs.subSplits[0].variables
                for key in rs.subSplits[0].keyOrder:
                      dataSetNames.append(rs.subSplits[0].variables+"_"+str(key))
                      categoryLabels.append(rs.subSplits[0].data[key])
          categoryLabels.append('Gesamt')
          dataSetNames.append('TOTAL')
          
          for dataSetName in dataSetNames:
                for dataSet in rs.dataSets:
                      if dataSet.name == dataSetName:
                            
                            dataRow = []
                            for key in rs.mainSplit.keyOrder:
                                  mainSplitLabels.append(rs.mainSplit.data[key])
                                  try:
                                        dataRow.append(dataSet.data[self.reportedCalc][key])
                                  except:
                                        dataRow.append(0)
                            dataRows.append(dataRow)
          
          
                
          dataRows = self.transpose_dataRows(dataRows)
    
          ax.axis([0,100,0,len(dataRows[0])])
    
          barSets = []
          lastDataRow = None
          leftOffset = []
          for i in range(len(dataRows)):
                if lastDataRow:
                      for y in range(len(lastDataRow)):
                            leftOffset[y] = leftOffset[y] + lastDataRow[y]  
                else :
                      for value in dataRows[0]:
                            leftOffset.append(0) 
                barSets.append(ax.barh(arange(len(dataRows[0]))+ .5,  dataRows[i],  left=leftOffset, height=0.6, align='center', color=self.colors[i]))
                lastDataRow = dataRows[i]
                
          
          legendentrys = []
          for key in rs.mainSplit.keyOrder:
                legendentrys.append(rs.mainSplit.data[key]) 
          legendSympols = []
          for barSet in barSets:
                legendSympols.append(barSet[0])
          
          
          legend = plt.legend( legendSympols,  
                      legendentrys, 
                      bbox_to_anchor=(0, 1.1, 1, 0), #(x, y, width, height of the bbox) 
                      handlelength = 1, 
                      handletextpad = 0.3,
                      columnspacing = 1,
                      mode="expand",
                      ncol = len(barSets))
                      #legendentrys, bbox_to_anchor=(0.0, 0.90, 0.9, .202),  ncol = len(barSets))
    
          legend.set_frame_on(False)
          
    
          
          if self.title:
                ax.set_title(self.title)
          if self.xlabel:
                ax.set_xlabel(self.xlabel)
          if self.ylabel:
                ax.set_ylabel(self.ylabel)
          ax.set_yticks(arange(len(dataRows[0]))+ .5)
          
          ax.set_yticklabels(categoryLabels)
    
    
          lastOffset = []
          for bar in barSets[0]:
          
                lastOffset.append(0)
          barSetCount = 0
          for barSet in barSets:
                i = 0
                for bar in barSet:
                      if self.colors[barSetCount] in ('#C6CEE2', '#FFFFFF', '#D8D8D5'):
                            textColor = '#000000'
                      else:
                            textColor = '#FFFFFF' 
                             
                      ax.text(lastOffset[i]+ float(bar.get_width())*0.5, bar.get_y()+bar.get_height()/2,  int(round(bar.get_width(),0)), va='center', ha='center', color=textColor )
                      lastOffset[i] += bar.get_width()
                      i += 1
                      pass
                barSetCount += 1
                
          ax.set_yticklabels(())
                
    def build_linegraph(self, rs):
          plt = self.plt
          plt.rcParams['font.sans-serif'] = 'Arial'
          plt.rcParams['font.size'] = self.fontSize
          plt.rcParams['legend.fontsize'] = self.fontSize
          plt.rcParams['grid.linestyle'] = 'solid'
          rs= rs
          
          if len(rs.subSplits) == 0:
              sys.exit("Tut mir leid, ohne SubSplit im ReportingSet kann die Grafik nicht erstellt werden.")
          
          
          fig = plt.figure()
          fig.set_size_inches(self.sizeInch())
    
          #axex [left, bottom, width, height]
          ax = fig.add_axes(self.padding2axes(self.chartPadding))
          ax.axis([0.5,4.5,0,100])
    
          ax.set_xticks(range(1,len(rs.subSplits[0].keyOrder)+1))
          ticklables = []
          for key in rs.subSplits[0].keyOrder:
                ticklables.append(rs.subSplits[0].data[key])
                
          ax.set_xticklabels(ticklables)
          lineColors = ('#FFCC00', '#113388', '#FF6600', '#819CCC', '#C6CEE2','#000000','#7A7A7A', '#FFCC00','#FFCC00')
          lineSymbols = ('D', 's', 'o', '^', '*', 'v', 'p', 'o', 'o', 'o')
          
          ax.yaxis.grid(True, which='major', color='grey')
    
          zaehler = 0
          legendLabels = []
    
          
          for key in rs.mainSplit.keyOrder:
                legendLabels.append(rs.mainSplit.data[key])
                if key != 99:
                      points = []
                      for dataSet in rs.dataSets:
                          if dataSet.name != 'TOTAL' and key in dataSet.data['PCT_W']:
                              points.append(dataSet.data['PCT_W'][key])
                      if (len(points)) >0:
                          ax.plot(range(1,len(rs.subSplits[0].keyOrder)+1), points, '-'+lineSymbols[zaehler], color = lineColors[zaehler])
                      zaehler += 1
          legend = plt.legend( legendLabels, 
                               ###(,0.9,je mehr desto weiter rechts, weiter anch oben)
                               bbox_to_anchor=(0.5, 0.8, 0.9, .240), 
                      ncol = 1)
          legend.set_frame_on(False)
    
    def build_linegraph_tmp(self):
          plt = self.plt
          plt.rcParams['font.sans-serif'] = 'Arial'
          plt.rcParams['font.size'] = self.fontSize
          plt.rcParams['legend.fontsize'] = self.fontSize
          plt.rcParams['grid.linestyle'] = 'solid'
          plt.rcParams['lines.markersize'] = 3
          rs= self.rs
          
          if len(rs.subSplits) == 0:
              sys.exit("Tut mir leid, ohne SubSplit im ReportingSet kann die Grafik nicht erstellt werden.")
          
          
          fig = plt.figure()
          fig.set_size_inches(self.sizeInch())
    
          #axex [left, bottom, width, height]
          ax = fig.add_axes(self.padding2axes(self.chartPadding))
          ax.axis([0.5,4.5,0,100])
    
          ax.set_xticks(range(1,len(rs.subSplits[0].keyOrder)+1))
          ticklables = []
          for key in rs.subSplits[0].keyOrder:
                ticklables.append(rs.subSplits[0].data[key])
                
          ax.set_xticklabels(ticklables)
          lineColors = ('#113388', '#113388', '#FF6600', '#819CCC', '#C6CEE2','#000000','#7A7A7A', '#FFCC00','#FFCC00')
          lineSymbols = ('s', 'D', 'o', '^', '*', 'v', 'p', 'o', 'o', 'o')
          
          ax.yaxis.grid(True, which='major', color='grey')
    
          zaehler = 0
    
          
          for key in rs.mainSplit.keyOrder:
                if key == 15:
                      points = []
                      textX= 1
                      for dataSet in rs.dataSets:
                          if dataSet.name != 'TOTAL' and key in dataSet.data['PCT_W']:
                              points.append(dataSet.data['PCT_W'][key])
                              ax.text(textX, dataSet.data['PCT_W'][key]-10,  str(round(dataSet.data['PCT_W'][key],1))+"%", va='center', ha='center' )
                              textX += 1
                      if (len(points)) >0:
                          ax.plot(range(1,len(rs.subSplits[0].keyOrder)+1), points, '-'+lineSymbols[zaehler], color = lineColors[zaehler])
                      #ax.text(lastOffset[i]+ float(bar.get_width())*0.5, bar.get_y()+bar.get_height()/2,  int(round(bar.get_width(),0)), va='center', ha='center', color='w' )
    
                      zaehler += 1
          
    def build_barcharttems(self, rs):
        plt = self.plt
        plt.rcParams['font.sans-serif'] = 'Arial'
        plt.rcParams['font.size'] = self.fontSize
        plt.rcParams['legend.fontsize'] = self.fontSize
        plt.rcParams['legend.markerscale'] = 0.1
        plt.rcParams['ytick.major.size'] = 0
        
        fig = plt.figure()
        fig.set_size_inches(self.sizeInch())
        
        #axex [left, bottom, width, height]
        ax = fig.add_axes((0.40,0.15,.55,.80))
        
        
        rs = rs
        #rs.print_content()
        #rs.dataSets.reverse()  ## Chartspezifisch umsortieren.
        
        dataRows = []
        mainSplitLabels = [] 
        categoryLabels = []
        dataSetNames = []
        
        if rs.subSplits:
              rs.subSplits[0].keyOrder.reverse()
              rs.subSplits[0].variables
              for key in rs.subSplits[0].keyOrder:
                    dataSetNames.append(rs.subSplits[0].variables+"_"+str(key))
                    categoryLabels.append(rs.subSplits[0].data[key])
        
        categoryLabels.append('Gesamt')
        dataSetNames.append('TOTAL')
        
        for dataSetName in dataSetNames:
            for dataSetKey in rs.dataSets:
                dataSet = rs.dataSets[dataSetKey]
                if dataSet.name == dataSetName:
                    dataRow = []
                    for key in rs.mainSplit.keyOrder:
                        mainSplitLabels.append(rs.mainSplit.data[key])
                        try:
                            dataRow.append(dataSet.data[self.reportedCalc][key])
                        except:
                            dataRow.append(0)
                    dataRows.append(dataRow)
              
        dataRows = self.transpose_dataRows(dataRows)
        
        ax.axis([0,100,0,len(dataRows[0])])
        
        barSets = []
        lastDataRow = None
        leftOffset = []
        for i in range(len(dataRows)):
            pass
                
    def build_barchart_stacked__(self):
          plt = self.plt
          plt.rcParams['font.sans-serif'] = 'Arial'
          plt.rcParams['font.size'] = self.fontSize
          plt.rcParams['legend.fontsize'] = self.fontSize
          plt.rcParams['legend.markerscale'] = 0.1
          plt.rcParams['ytick.major.size'] = 0
          
          fig = plt.figure()
          fig.set_size_inches(self.sizeInch())
    
          #axex [left, bottom, width, height]
          ax = fig.add_axes((0.40,0.15,.55,.80))
          
    
          rs = self.rs
          
          rs.dataSets.reverse()  ## Chartspezifisch umsortieren.
          
          dataRows = []
          
               
          mainSplitLabels = [] 
    
    
          categoryLabels = []
          dataSetNames = []
          if rs.subSplits:
                rs.subSplits[0].keyOrder.reverse()
                rs.subSplits[0].variables
                for key in rs.subSplits[0].keyOrder:
                      dataSetNames.append(rs.subSplits[0].variables+"_"+str(key))
                      categoryLabels.append(rs.subSplits[0].data[key])
          categoryLabels.append('Gesamt')
          dataSetNames.append('TOTAL')
          
          for dataSetName in dataSetNames:
                for dataSet in rs.dataSets:
                      if dataSet.name == dataSetName:
                            
                            dataRow = []
                            for key in rs.mainSplit.keyOrder:
                                  mainSplitLabels.append(rs.mainSplit.data[key])
                                  try:
                                        dataRow.append(dataSet.data[self.reportedCalc][key])
                                  except:
                                        dataRow.append(0)
                            dataRows.append(dataRow)
          
          
                
          dataRows = self.transpose_dataRows(dataRows)
    
          ax.axis([0,100,0,len(dataRows[0])])
    
          barSets = []
          lastDataRow = None
          leftOffset = []
          for i in range(len(dataRows)):
                if lastDataRow:
                      for y in range(len(lastDataRow)):
                            leftOffset[y] = leftOffset[y] + lastDataRow[y]  
                else :
                      for value in dataRows[0]:
                            leftOffset.append(0) 
                barSets.append(ax.barh(arange(len(dataRows[0]))+ .5,  dataRows[i],  left=leftOffset, align='center', color=self.colors[i]))
                lastDataRow = dataRows[i]
          
          
          legend = plt.legend( (barSets[0][0], barSets[1][0], barSets[2][0]),  
                      ('Ja', 'Nein', 'keine Angabe'), bbox_to_anchor=(0.2, -0.25, 0.9, .202),
                      ncol = 3)
    
          legend.set_frame_on(False)
          
    
          
          if self.title:
                ax.set_title(self.title)
          if self.xlabel:
                ax.set_xlabel(self.xlabel)
          if self.ylabel:
                ax.set_ylabel(self.ylabel)
          ax.set_yticks(arange(len(dataRows[0]))+ .5)
          
          ax.set_yticklabels(categoryLabels)
    
    
          lastOffset = []
          for bar in barSets[0]:
          
                lastOffset.append(0)
          for barSet in barSets:
                i = 0
                for bar in barSet:
                      ax.text(lastOffset[i]+ float(bar.get_width())*0.5, bar.get_y()+bar.get_height()/2,  int(round(bar.get_width(),0)), va='center', ha='center', color='w' )
                      lastOffset[i] += bar.get_width()
                      i += 1
                      pass
                      
    def build_barchart_diffs(self):
          plt = self.plt
          plt.rcParams['font.sans-serif'] = 'Arial'
          plt.rcParams['font.size'] = 10
          plt.rcParams['axes.grid'] = False
          plt.rcParams['ytick.major.size'] = 0
          plt.rcParams['grid.linestyle'] = 'solid'
          #plt.rcParams['ytick.major.size'] = 1
          
          fig = plt.figure()
          fig.set_size_inches(self.sizeInch())
    
          ax = fig.add_axes((0.05,0.05,0.90,0.94) )
          
          rs = self.rs
          
          dataRow = []
    
          keyOrder = rs.mainSplit.keyOrder
          keyOrder.reverse()
          for key in keyOrder:
                try:
                      dataRow.append(rs.dataSets[0].data[self.reportedCalc][key])
                except:
                      dataRow.append(0)
          
          axisvar = ax.axis([0,100,0,len(dataRow)])
          ax.set_xlim(-40,40)
          #ax.set_ylim(-1.1,1.1)
          barSet = ax.barh(arange(len(dataRow))+ .5,  dataRow, height=0.6, align='center', color=self.colors[0])
          l = plt.axvline(x=0, ymin=0,  color='#000000',linewidth=1, zorder = 4)
          background = plt.axhspan(0, len(dataRow), xmin=0, xmax=1, color='#EAEAEA', zorder = -4)
    
          ax.set_xticks((-40,-20,0,20,40))
    
          ax.yaxis.set_ticks_position('none')
          ax.xaxis.grid(True, which='major', color='grey')
    
          ax.set_yticklabels(())
    
          for bar in barSet:
                if bar.get_x() < 0:
                      bar.set_facecolor(self.colors[2])
                      ax.text(float(bar.get_x())-2, bar.get_y()+bar.get_height()/2,  int(round(bar.get_x(),0)), va='center', ha='right' )
                else:
                      ax.text(float(bar.get_width())+2, bar.get_y()+bar.get_height()/2,  int(round(bar.get_width(),0)), va='center', ha='left' )
    
    def build_barchart_diss(self, xScope = (0,100)):
          plt = self.plt
          plt.rcParams['font.sans-serif'] = 'Arial'
          plt.rcParams['font.size'] = 10
          plt.rcParams['axes.grid'] = False
          plt.rcParams['ytick.major.size'] = 0
          plt.rcParams['grid.linestyle'] = 'solid'
          #plt.rcParams['ytick.major.size'] = 1
          
          fig = plt.figure()
          fig.set_size_inches(self.sizeInch())
    
          ax = fig.add_axes(self.padding2axes(self.chartPadding))
          
          rs = self.rs
          
          dataRow = []
    
          keyOrder = list(rs.mainSplit.keyOrder)
          #keyOrder.reverse()
          dataRow = []
          for key in keyOrder:
    
                try:
                      dataRow.append(rs.dataSets[0].data[self.reportedCalc][key])
                except:
                      dataRow.append(0)
          
          axisvar = ax.axis([0,100,0,len(dataRow)])
          ax.set_xlim(xScope[0],xScope[1])
    
          ax.set_xticks((-60,-40,-20,0,20,40,60))
    
          ax.yaxis.set_ticks_position('none')
          ax.xaxis.grid(True, which='major', color='grey')
          yLabels = []
          for key in rs.mainSplit.keyOrder:
                yLabels.append(rs.mainSplit.data[key])
          
          ax.set_yticklabels(yLabels)
          ax.set_xticklabels(("-60%","-40%","-20%","0%","20%","40%","60%"))
          ax.set_yticks(arange(6)+ .5)
    
          
          barSet = ax.barh(arange(len(dataRow))+ .5,  dataRow, height=0.6, align='center', color='g')
          l = plt.axvline(x=0, ymin=0,  color='#000000',linewidth=1, zorder = 4)
          background = plt.axhspan(0, len(dataRow), xmin=0, xmax=1, color='#EAEAEA', zorder = -4)
    
          for bar in barSet:
                if bar.get_x() < 0:
                      bar.set_facecolor('g')
                      ax.text(float(bar.get_x())-2, bar.get_y()+bar.get_height()/2,  float(round(bar.get_x(),self.labelDecimals)), va='center', ha='right' )
                else:
                      ax.text(float(bar.get_width())+2, bar.get_y()+bar.get_height()/2,  unicode(round(bar.get_width(),self.labelDecimals)) +"%", va='center', ha='left' )
    
          dataRow = []
          for key in keyOrder:
                try:
                      dataRow.append(rs.dataSets[1].data[self.reportedCalc][key])
                except:
                      dataRow.append(0)
          barSet2 = ax.barh(arange(len(dataRow))+ .5,  dataRow, height=0.6, align='center', color='r')
          for bar in barSet2:
                if bar.get_x() < 0:
                      bar.set_facecolor('r')
                      ax.text(float(bar.get_x())-2, bar.get_y()+bar.get_height()/2,  unicode(round(bar.get_x(),self.labelDecimals)) +"%", va='center', ha='right' )
    
    def build_pieChart(self, rs):
        plt = self.plt
        fig = plt.figure()
        fig.set_size_inches(self.sizeInch())
        self.padding2axes(self.chartPadding)
        ax = fig.add_axes(self.padding2axes(self.chartPadding))
        ax.set_aspect(1)
              
        fracs = []
        for key in rs.mainSplit.keyOrder:
            fracs.append(rs.dataSets['TOTAL'].data['PCT'][key])
            #autopct='%1.f%%', 
        #wedges = plt.pie(fracs, colors=self.colors, autopct='%1.1f%%', labels=('a', 'b', 'C'))
        wedges = plt.pie(fracs, colors=self.colors, autopct='%1.0f%%')
          
    def build_pieChart_steps(self):
          plt = self.plt
          fig = plt.figure()
          fig.set_size_inches(self.sizeInch())
          print(self.padding2axes(self.chartPadding))
          ax = fig.add_axes(self.padding2axes(self.chartPadding))
    
          fracs = []
          rs = self.rs
          for key in rs.mainSplit.keyOrder:
                    fracs.append(rs.dataSets[0].data['PCT_W'][key])
                    #autopct='%1.f%%', 
          wedges = ax.pie(fracs, colors=self.colors)
          ax2 = fig.add_axes([0.3, 0.2, 0.4, 0.4])
    
          fracs = []
          rs = self.rs
          for key in rs.mainSplit.keyOrder:
                    fracs.append(rs.dataSets[0].data['PCT_W'][key])
                    #autopct='%1.f%%', 
          wedges2 = ax2.pie(fracs, colors=self.colors)
    
          
    #            for i in range(len(wedges[0])):
    #                  wedges[i].set_color('w')
    #                  for element in wedges[1]:
    #                        element.set_fontsize(14)
    #                  for element in wedges[2]:
    #                        color =  self.colors[i]
    #                        if color == "#C6CEE2":
    #                              element.set_color('w')
                #for text in wedges[2]:
                #      text.set_color('w')
          #plt.title('Raining Hogs and Dogs', bbox={'facecolor':'0.8', 'pad':5})
    
    def show_chart(self):
        self.plt.show()
    
    def export_chart(self, filename = "chart", format = 'png',  open = False):
        self.plt.savefig(self.exportPath +r"\\" + filename + "."+format, dpi= 300, transparent=True, format=format)
        if open:
            os.system(self.exportPath +r"\\" + filename + "."+format)
