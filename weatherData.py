## Weather data
##   the organization and notation is loosely adapted from Python Pandas

class WeatherData:
    """
WeatherData: 
  parameters
    title   : used for labeling the data
    columns : column names
    fc      : all lines of a forecast (the first two values must be start and end "hour" in UTC)
    beginHour : start time of the forecast
    endHour   : end time of the forecast 
    beginTime : datetime of the issue time
    text      : text of the scribe forecast
    
  instances variables:
    data    : selected lines within [beginHour,endHour)
    colIndex : mapping between names and column index
"""
    def __init__(self, title, columns, fc, beginHour,endHour,beginTime,tzH,text):
        self.title=title;
        self.columns=["start","  end"]+columns
        self.colIndex={key:i for key,i in zip(self.columns,range(0,len(self.columns)))}
        ## extract lines between beginHour and endHour 
        ## taking for granted that start,end are sorted in increasing order
        self.data=[]
        nb=len(fc)
        i=0
        while i<nb and fc[i][1] < beginHour:
            i+=1
        while i<nb and fc[i][0] < endHour:
            self.data.append(fc[i])
            i+=1
        self.size=len(self.data)
        self.beginTime=beginTime
        self.tzH=tzH
        self.text=text

    ##  hour string in more readable manner suffixed with "h"
    def hour(self,h):
        return str(h)
        # h=h-self.tzH
        # if h<24: return str(h)+"h" # negative numbers are output as is
        # # output with a prefix indicating the day
        # return ["","+","⧺","⧻"][int(h/24)]+str(h%24)+"h"

    ## data with aligned columns values and titles
    def __str__(self):
        res = ["**"+self.title]
        if not self.empty():
            nbCols=len(self.columns)
            colWidths=[len(col) for col in self.columns[:nbCols]]
            ## compute max width of columns
            for line in self.data:
                for i in range(2,min(nbCols,len(line))):
                    colWidths[i]=max(len(str(line[i])),colWidths[i])
            fmtL=[f"%{colWidths[i]}s" for i in range(0,nbCols)]
            # output column names and values
            fmt=" ".join(fmtL)
            res.append(fmt%tuple(self.columns[:nbCols]))
            for line in self.data:
                fmt=" ".join(fmtL[:len(line)])
                res.append(fmt%tuple([self.hour(line[0]),self.hour(line[1])]+line[2:nbCols]))
        res.append("===")
        return "\n".join(res)
    
    ## useful for debugging
    def __repr__(self):
        """ Show raw data: as rows without hour shift (useful for debugging)"""
        res=[str(self.columns)]
        for line in self.data:
            res.append(str(line))
        return "\n".join(res)

    ## get a serie corresponding to a column (index by number or column name)
    def __getitem__(self,key):
        if type(key) is str: key=self.colIndex[key]
        return [(line[key] if key<len(line) else None) for line in self.data ]
    
    def line(self,i):
        return self.data[i]
        
    def empty(self):
        return self.size==0
    
    def size(self):
        return self.size
            
    def getText(self):
        return self.text
