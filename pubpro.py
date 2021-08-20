## implement the organization of EC Public Weather Forecasts and Warning
##   we (try to) follow the terminologyof the PUBPRO document
## Currently only the "Regular Public Forecast Bulletin" is implemented

## the input is the json version of the Meteocode (jsonMC) used for the ARPI-EC workshop
##    in August 2021

import sys,re,textwrap, json, locale

from datetime import datetime,timedelta
from ECdata import get_forecast_area, periods, periodNames
from arpi_eccc.utils import get_delta_with_utc, get_time_interval_for_period

trace=False

def get_issue_date(jsonMC):
    hdr=jsonMC["header"]
    return datetime(hdr[4],hdr[5],hdr[6])

#### HACK: specific for Ontario and Québec
def get_timezone(jsonMC,lang):
    delta=get_delta_with_utc(jsonMC)
    if lang=="en":
        return "DST" if delta==4 else "EST"
    else:
        return "HAE" if delta==4 else "HNE"


## each block should return a list of string corresponding to a line in the output
## if a string is None, it is ignored

def communication_header(jsonMC,lang):
    if trace: print("communication_header")
    hdr=jsonMC["header"]
    return [f"{hdr[0]} {hdr[1]} {hdr[5]:02d}{hdr[6]:02d}{hdr[7]:04d}"]
    
def getTimeDateDay(dt,lang):
    locale.setlocale(locale.LC_ALL,"en_US" if lang=="en" else "fr_FR")
    return (dt.strftime("%H.%M") if lang=="fr" else re.sub(r'^0','',dt.strftime("%I:%M %p")),
            re.sub(r"^0","",dt.strftime("%A %d %B %Y")),
            dt.strftime("%A"))

def get_period_name(dt,period,lang):
    if period.startswith("day2_"):
        locale.setlocale(locale.LC_ALL,"en_US" if lang=="en" else "fr_FR")
        return dt.strftime(periodNames[period][lang])
    return periodNames[period][lang]
    
def title_block(jsonMC,lang):
    if trace: print("title_block")
    hdr=jsonMC["header"]
    tzS = get_timezone(jsonMC,lang)
    area=get_forecast_area(hdr[0],lang)
    issueDate = datetime(hdr[4],hdr[5],hdr[6])
    (bTime,bDate,bDay)=getTimeDateDay(issueDate,lang)
    (nTime,nDate,nDay)=getTimeDateDay(datetime(hdr[10],hdr[11],hdr[12]),lang)
    (tTime,tDate,tDay)=getTimeDateDay(issueDate+timedelta(days=1),lang)
    if lang=="en":
        s1=f"Forecasts for {area} issued by Environment Canada "+\
           f"at {bTime} {tzS} {bDate} for today and {tDay}."
        s2=f"The next scheduled forecast will be issued at {nTime} {tzS}." 
    else:
        s1=f"Prévisions pour {area} émises par Environnement Canada "+\
           f"à {bTime} {tzS} {bDate} pour aujourd'hui et {tDay}."
        s2=f"Les prochaines prévisions seront émises à {nTime} {tzS}." 
    return [textwrap.fill(s1),s2,""]

def forecast_regions(jsonMC,lang):
    if trace: print("forecast_regions")
    regions=jsonMC["names-"+lang]
    regions[-1]=regions[-1]+"."# add full stop at the end of regions
    return regions

def forecast_text(jsonMC,lang):
    """ Section 2.2.2 """
    if trace: print("forecast_text")
    hdr=jsonMC["header"]
    periodsFC=periods[:3] if hdr[6]<1500 else periods[1:]
    tomorrow=datetime(hdr[4],hdr[5],hdr[6])+timedelta(days=1)
    periodFC=[]
    for period in periodsFC:
        periodFC.append(get_period_name(tomorrow,period,lang)+".."+forecast_period(jsonMC,period,lang))
    return periodFC

def forecast_period(jsonMC,period,lang):
    return f"**{period}**"

def end_statement(lang):
    if trace: print("end_statement")
    return ["","End"]
    return [None]

def regular_forecast(jsonMC,lang):
    """ Sect 2.2 """
    text=[]
    text.extend(communication_header(jsonMC,lang))
    text.extend(title_block(jsonMC,lang))
    text.extend(forecast_regions(jsonMC,lang))
    text.extend(forecast_text(jsonMC,lang))
    text.extend(end_statement(lang))
    return "\n".join(text)


def main(jsonlFN):
    for line in open(jsonlFN,"r",encoding="utf-8"):
        fc_text=regular_forecast(json.loads(line),"en")
        print(fc_text)
        print("===")
        break

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv)>1 else
         "/Users/lapalme/Documents/GitHub/arpi_eccc/data/arpi-2021-train-10.jsonl")