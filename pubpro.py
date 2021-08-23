## implement the organization of EC Public Weather Forecasts and Warning
##   we (try to) follow the terminology of the PUBPRO document
## Currently only the "Regular Public Forecast Bulletin" is implemented

## the input is the json version of the Meteocode (mc) used for the ARPI-EC workshop
##    in August 2021

## This version only uses Python string formatting for the templates

import sys,re,textwrap, json, locale

from datetime import datetime,timedelta
from ECdata import get_forecast_area, periods, get_period_name, uv_ranges
from arpi_eccc.utils import get_delta_with_utc, get_time_interval_for_period
from MeteoCode import MeteoCode
from forecast import forecast_period

trace=False

## each block should return a list of string corresponding to a line in the output
## if a string is None, it is ignored

def communication_header(mc,lang):
    if trace: print("communication_header")
    hdr=mc.get_header()
    return [f"{hdr[0]} {hdr[1]} {hdr[5]:02d}{hdr[6]:02d}{hdr[7]:04d}"]
    
def getTimeDateDay(dt,lang):
    locale.setlocale(locale.LC_ALL,"en_US" if lang=="en" else "fr_FR")
    return (dt.strftime("%H.%M") if lang=="fr" else re.sub(r'^0','',dt.strftime("%I:%M %p")),
            re.sub(r"^0","",dt.strftime("%A %d %B %Y")),
            dt.strftime(" %A"))

    
def title_block(mc,lang):
    if trace: print("title_block")
    hdr=mc.get_header()
    tzS = mc.get_timezone(lang)
    area=get_forecast_area(hdr[0],lang)
    issueDate = mc.get_issue_date()
    (bTime,bDate,_bDay)=getTimeDateDay(issueDate,lang)
    (nTime,_nDate,_nDay)=getTimeDateDay(mc.get_next_issue_date(),lang)
    (_tTime,_tDate,tDay)=getTimeDateDay(issueDate+timedelta(days=1),lang)
    if lang=="en":
        s1=f"Forecasts for {area} issued by Environment Canada "+\
           f"at {bTime} {tzS} {bDate} for today and {tDay}."
        s2=f"The next scheduled forecast will be issued at {nTime} {tzS}." 
    else:
        s1=f"Prévisions pour {area} émises par Environnement Canada "+\
           f"à {bTime} {tzS} {bDate} pour aujourd'hui et {tDay}."
        s2=f"Les prochaines prévisions seront émises à {nTime} {tzS}." 
    return [s1,s2,""]

def forecast_regions(mc,lang):
    if trace: print("forecast_regions")
    regions=mc.get_region_names(lang)
    regions[-1]=regions[-1]+"."# add full stop at the end of regions
    return regions


def forecast_text(mc,lang):
    """ Section 2.2.2 """
    if trace: print("forecast_text")
    issueDT=mc.get_issue_date()
    periodsFC=periods[:3] if issueDT.hour<15 else periods[1:]
    tomorrow=issueDT+timedelta(days=1)
    periodFC=[]
    for period in periodsFC:
        periodFC.append(get_period_name(tomorrow,period,lang)+".."+
                        forecast_period(mc,period,lang))
    return periodFC

def end_statement(lang):
    if trace: print("end_statement")
    return ["","End"]
    return [None] 

def regular_forecast(mc,lang):
    """ Sect 2.2 """
    text=[
        communication_header(mc,lang),
        title_block(mc,lang),
        forecast_regions(mc,lang),
        forecast_text(mc,lang),
        end_statement(lang),
    ]
    res="\n".join([textwrap.fill(line,width=70, subsequent_indent=" ") 
                   for lines in text for line in lines if line!=None])
    orig=mc.get_original_bulletin(lang)
    if orig!=None: res+="\n** original\n"+orig
    return res


def main(jsonlFN):
    for line in open(jsonlFN,"r",encoding="utf-8"):
        fc_text=regular_forecast(MeteoCode(json.loads(line)),"en")
        print(fc_text)
        fc_text=regular_forecast(MeteoCode(json.loads(line)),"fr")
        print(fc_text)
        print("===")
        break

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv)>1 else
         "/Users/lapalme/Documents/GitHub/arpi_eccc/data/arpi-2021-train-10.jsonl")