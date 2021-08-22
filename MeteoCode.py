'''
Created on 21 août 2021

@author: lapalme
'''
from datetime import datetime, timedelta
from arpi_eccc.utils import get_delta_with_utc, get_time_interval_for_period

class MeteoCode(object):
    '''
    Keep info about the Meteocode and provide methods to query it
    '''

    def __init__(self, json):
        '''
        Build a Meteocode data structure from a data
        '''
        self.data=json
        hdr=json["header"]
        self.issue_date=datetime(hdr[4],hdr[5],hdr[6],hour=hdr[7]//100,minute=hdr[7]%100)
        self.next_issue_date=datetime(hdr[10],hdr[11],hdr[12],hour=hdr[13]//100,minute=hdr[13]%100)
        self.delta=get_delta_with_utc(json)
    
    def get_header(self):
        return self.data["header"]

    def get_region_names(self,lang):
        return self.data["names-"+lang]
    
    def get_issue_date(self):
        return self.issue_date
    
    def get_next_issue_date(self):
        return self.next_issue_date
    
    def get_delta_with_utc(self):
        return self.delta
    
    def get_original_bulletin(self,lang):
        if lang in self.data:
            return self.data[lang]["orig"]
        else:
            return None
    
    #### HACK: specific for Ontario and Québec
    def get_timezone(self,lang):
        if lang=="en":
            return "DST" if self.delta==4 else "EST"
        else:
            return "HAE" if self.delta==4 else "HNE"
    
    
    ### query information
    def extract_range(self,period, field,column=None):
        (beginHour,endHour)=get_time_interval_for_period(self.data, period)
        infos=self.data[field]
        nb=len(infos)
        i=0
        while i<nb and infos[i][1] < beginHour:i+=1
        startI=i
        while i<nb and infos[i][0] < endHour:
            i+=1
        if startI==i:return None ## no line found
        lines=infos[startI:i]
        if column==None:return lines
        return [line[column] for line in lines]
    
    
    ### ciel: start end neb-start neb-end {ceiling-height}
    def get_sky_condition(self,period,column=None):
        return self.extract_range(period,"ciel",column)

    # temp : start end trend value
        # trend : "baisse" | "hausse" | "pi" | "max" | "min" | "stationnaire" =>
        #         "falling" | "rising" | "middle point" | "high" | "low" | "steady"
        # value : int degree Celsius
    # returns a table of all temperatures by hour, from beginHour to endHour
    # it expands intermediate values to ease their analysis
    def get_temperature(self,period):
        (beginHour,endHour)=get_time_interval_for_period(self.data, period)
        temps=[]
        tempRanges=self.extract_range(period, "temp")
        # print("tempRanges")
        # print(tempRanges)
        if tempRanges==None: return None
        i=0
        temps.extend([tempRanges[0][3]]*(tempRanges[0][1]-beginHour))
        for i in range(1,len(tempRanges)-1):
            temps.extend([tempRanges[i][3]]*(tempRanges[i][1]-tempRanges[i][0]))
        i=len(tempRanges)-1
        temps.extend([tempRanges[i][3]]*(endHour-tempRanges[i][1]))
        # print("temps")
        # print(temps)
        return temps
    
    def get_precipitation(self,period):
        return self.extract_range(period,"pcpn")
    