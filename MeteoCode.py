'''
Created on 21 août 2021

@author: lapalme
'''
from datetime import datetime, timedelta
from arpi_eccc.utils import get_delta_with_utc, get_time_interval_for_period
from ppJson import ppJson
from ECdata import warnings
import json, sys

class MeteoCode(object):
    '''
    Keep info about the Meteocode and provide methods to query it
    on top of the "administrative information", 
    weather info encoded into fields
    a field is a fieldname associated with a list of terms
    a term is a list of values 
       the first value is the beginHour
       the second value is the endHour
       other values depending of the field kind
       can be terminated by a possible embedded list which describes an "exception".
    
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
    
    def get_warning(self):
        if "avert" not in self.data: return None 
        return self.data["avert"][0]
    
    #### HACK: specific for Ontario and Québec
    def get_timezone(self,lang):
        if lang=="en":
            return "DST" if self.delta==4 else "EST"
        else:
            return "HAE" if self.delta==4 else "HNE"
    
    ### show all info for a given period
    ###    times (ending with h) are shown in local time 
    ignoredFields=set(["header","names-en","names-fr","regions","en","fr","id"])
    def show_data(self,period):
        def hour(h): ##  hour string in more readable manner suffixed with "h"
            h=h-self.delta
            if h<24: return str(h)+"h" # negative numbers are output as is
            h24=h//24 # output with a prefix indicating the day
            return (["","+","⧺","⧻"][h24] if h24<4 else "%d*"%h24)+str(h%24)+"h"
        def show_terms(terms):
            return ", ".join(["(%4s,%4s):[%s]"%(hour(term[0]),hour(term[1])," ".join(map(str,term[2:]))) for term in terms])
            
        (beginHour,endHour)=get_time_interval_for_period(self.data, period)
        print("%s (%4s,%4s):[%d,%d) delta=%d  :: %s :: %s"%(
                period,hour(beginHour),hour(endHour), beginHour,endHour,self.delta,self.data["id"],self.get_issue_date()))
        for field in self.data:
            if field not in self.ignoredFields:
                terms=self.extract_terms(period,field)
                if terms!=None:
                    print("%-11s : %s"%(field,show_terms(terms)))
        print("----")
            
    ### query information
    
    def extract_terms(self,period, field):
        (beginHour,endHour)=get_time_interval_for_period(self.data, period)
        if field not in self.data: return None
        terms=self.data[field]
        if field=="prob": # prob has a peculiar structure (ignore first two elements
            terms=terms[0][2:]
        nb=len(terms)
        i=0
        while i<nb and terms[i][1] <= beginHour:i+=1
        startI=i
        while i<nb and terms[i][0] < endHour:
            i+=1
        if startI==i:return None ## no line found
        terms=terms[startI:i]
        return terms
    

    ## expand value given at idx in tuples for each hour for all hours within a range
    def expand_range(self,tuples,idx,beginHour,endHour):
        if len(tuples)==1: # all in the first tuple
            return [tuples[0][idx]]*(endHour-beginHour)
        res=[tuples[0][idx]]*(tuples[0][1]-beginHour)
        i=1
        while i<len(tuples)-1:
            res.extend([tuples[i][idx]]*(tuples[i][1]-tuples[i][0]))
            i+=1
        res.extend([tuples[i][idx]]*(endHour-tuples[i][0]))
        return res
    
    # def get_line(self,line,columns):
        # res=[line[0],line[1]]
        # res.extend([line[c] for c in columns])
        # return res
     
    def build_table(self,period,field,col):
        (beginHour,endHour)=get_time_interval_for_period(self.data, period)
        if field not in self.data: return None
        terms=self.extract_terms(period, field)
        if field=="prob": # prob has a peculiar structure (ignore first two elements
            terms=terms[0][2:]
        nb=len(terms)
        if nb==0: return None
        if nb==1:
            return [terms[0][col]]*(endHour-beginHour)
        res=[terms[0][col]]*(terms[0][1]-beginHour)
        i=1
        while i<nb-1:
            res.extend([terms[i][col]]*(terms[i][1]-terms[i][0]))
            i+=1
        res.extend([terms[i][col]]*(endHour-terms[i][0]))
        return res
        
    ### ciel: start end neb-start neb-end {ceiling-height}
    def get_sky_condition(self,period):
        return self.extract_terms(period,"ciel")
    
    def get_precipitation(self,period):
        return self.extract_terms(period, "pcpn")

    def get_precipitation_probabilities(self,period):
        return self.extract_terms(period, "prob")
    
    def get_precipitation_amount(self,period):
        return self.extract_terms(period,"accum")
    
    # temp : start end trend value
        # trend : "baisse" | "hausse" | "pi" | "max" | "min" | "stationnaire" =>
        #         "falling" | "rising" | "middle point" | "high" | "low" | "steady"
        # value : int degree Celsius
    # returns a table of all temperatures by hour, from beginHour to endHour
    # it expands intermediate values to ease their analysis
    
    def get_temperature_values(self,period):
        return self.build_table(period,"temp",3)
        
    def get_climat_temp(self,period):
        return self.extract_terms(period,"climat_temp")
        
    def get_temperature(self,period):
        return self.extract_terms(period,"temp")
        
    def get_wind(self,period):
        return self.extract_terms(period, "vents")
    
    def get_uv_index(self,period):
        return self.extract_terms(period,"indice_uv")
    