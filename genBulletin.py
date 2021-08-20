##  generate Bilingual Weather Reports according to the "rules" described in
##   https://www.canada.ca/en/environment-climate-change/services/types-weather-forecasts-use/public/guide/elements.html#c1

from jsRealBclass import *
from datetime import timedelta,datetime
from weatherData import WeatherData
from arpi_eccc.utils import get_delta_with_utc, get_time_interval_for_period

import json, textwrap, re, sys, random, locale
from ppJson import ppJson
from nltk.tokenize import word_tokenize


### Text generation
def fmt(jsrExp,lang):
    exp=jsrExp.lang(lang).pp() # pretty-print the json format
    # print(exp)
    # return textwrap.fill(,width=70);
    genText=jsRealB(exp)
    if genText.startswith("@@@:") or genText.startswith("SyntaxError:"):
        print(exp,file=sys.stderr)
        print(genText,file=sys.stderr)
        sys.exit(1)
    return genText

### time generation
def jsrTime(dt,lang):
    return PP(P("at" if lang =="en" else "à"),
              DT(dt).dOpt({"year":False , "month": False , "date":False , "day":False , 
                           "hour":True , "minute":True , "second":False , 
                           "nat":False, "det":False, "rtime":False}),
              Q(tzS))

def jsrDay(dt):
    return  DT(dt).dOpt({"year":False , "month": False , "date":False , "day":True , 
                           "hour":False , "minute":False , "second":False , 
                           "nat":False, "det":False, "rtime":False})
    
def jsrDate(dt):
    return  DT(dt).dOpt({"year":True , "month": True , "date":True , "day":False , 
                           "hour":False , "minute":False , "second":False , 
                           "nat":True, "det":True, "rtime":False})


def jsrHour(h,lang):
    if h in [0,6]:
        return PP(P("during"),NP(D("the"),N("night"))) if lang=="en" else \
               PP(P("durant"),NP(D("le"),N("nuit")))
    if h in [7,10]:
        return PP(P("in"),NP(D("the"),N("morning"))) if lang=="en" else \
               NP(D("le"),N("matin"))
    if h in [11,12,13]:
        return PP(P("around"),N("noon")) if lang=="en" else \
               PP(P("vers"),N("midi"))
    if h in [14,18]:
        return PP(P("in"),NP(D("the"),N("afternoon"))) if lang=="en"  else \
               PP(P("durant"),NP(D("le"),N("après-midi")))
    if h in [19,24]:
        return PP(P("in"),NP(D("the"),N("evening"))) if lang=="en"  else \
               PP(P("dans"),NP(D("le"),N("soirée"))) 
    
dayPeriods=[(0,5,{"en":lambda:NP(N("night")),"fr":lambda:NP(N("nuit"))}),
            (5,9,{"en":lambda:NP(Adv("early"),N("morning")),"fr":lambda:NP(N("début"),PP(P("de"),N("matinée")))}),
            (9,12,{"en":lambda:NP(N("morning")),"fr":lambda:NP(N("matin"))}),
            (12,18,{"en":lambda:NP(N("afternoon")),"fr":lambda:NP(N("après-midi"))}),
            (18,24,{"en":lambda:NP(N("tonight")),"fr":lambda:NP(N("soir"))}),
            ]

def jsrDayPeriod(data,lang,hour):
    # print("hour",hour)
    hour=hour-data.tzH;
    isTomorrow=hour>23
    for (s,e,jsrExp) in dayPeriods:
        if hour in range(s,e):
            exp=jsrExp[lang]()
            if isTomorrow:
                return exp.add(N("tomorrow" if lang=="en" else "demain"),0)
            elif s!=18:
                return exp.add(D("this" if lang=="en" else "ce"),0)
    
###   global header information
bulletinRegionNames = {
    "FPTO11":{"en":"Southern Ontario and the National Capital Region",
              "fr":"le sud de l'Ontario et la région de la capitale nationale"},
    "FPTO12":{"en":"Northern Ontario",    "fr":"le nord de l'Ontario"},
    "FPTO13":{"en":"Far Northern Ontario","fr":"l'extrême nord de l'Ontario"},
    "FPCN71":{"en":"Western Quebec",      "fr":"l'ouest du Québec"},
    "FPCN73":{"en":"Central Quebec",      "fr":"le centre du Québec"},
    "FPCN74":{"en":"Western Quebec",      "fr":"l'est du Québec"},
}

def getTimeDateDay(dt,lang):
    locale.setlocale(locale.LC_ALL,"en_US" if lang=="en" else "fr_FR")
    return (dt.strftime("%Hh%M") if lang=="fr" else re.sub(r'^0','',dt.strftime("%I:%M %p")),
            re.sub(r"^0","",dt.strftime("%A %d %B %Y")),
            dt.strftime("%A"))

def header(lang,bulletinName,beginTime,nextIssue):
    (bTime,bDate,bDay)=getTimeDateDay(beginTime,lang)
    (nTime,nDate,nDay)=getTimeDateDay(nextIssue,lang)
    (tTime,tDate,tDay)=getTimeDateDay(beginTime+timedelta(days=1),lang)
    if lang=="en":
        s1=f"Forecasts for {bulletinRegionNames[bulletinName][lang]} issued by Environment Canada "+\
           f"at {bTime} {tzS} {bDate} for today and {tDay}."
        s2=f"The next scheduled forecast will be issued at {nTime} {tzS}." 
    else:
        s1=f"Prévisions pour {bulletinRegionNames[bulletinName][lang]} émises par Environnement Canada "+\
           f"à {bTime} {tzS} {bDate} pour aujourd'hui et {tDay}."
        s2=f"Les prochaines prévisions seront émises à {nTime} {tzS}." 
    return ["===",fmt(Q(s1),lang),fmt(Q(s2),lang),""]

## same as header but using jsRealB    
def jsrHeader(lang,bulletinName,beginTime,nextIssue):
    forecast={"en":N("forecast"),
              "fr":N("prévision").n("p")}
    ec= {"en":NP(N("environment").cap(True),Q("Canada")),
         "fr":NP(N("environnement").cap(True),Q("Canada"))}
    issue = {"en":lambda:V("issue"),
             "fr":lambda:V("émettre")}
    by=   {"en":P("by"),"fr":P("par")}
    for_= {"en":P("for"),"fr":P("pour")}
    and_= {"en":C("and"),"fr":C("et")}
    today={"en":N("today"),"fr":Adv("aujourd'hui")}
    the=  {"en":D("the"),"fr":D("le")}
    next_={"en":AdvP(Adv("next"),V("schedule").t("pp")),"fr":A("prochain").pos("pre")}
    be=   {"en":V("be"),"fr":V("être")}

    s1=S(forecast[lang],
         VP(issue[lang]().t("pp"),
            PP(by[lang],ec[lang]),
            PP(for_[lang],Q(bulletinRegionNames[bulletinName][lang])),
            jsrDay(beginTime),jsrTime(beginTime,lang),jsrDate(beginTime),
            PP(for_[lang],
               CP(and_[lang],today[lang],jsrDay(beginTime+timedelta(days=1)))))) 

    s2=S(VP(issue[lang]().t("f"),
            NP(the[lang],next_[lang],forecast[lang])).typ({"pas":True}),
          jsrTime(nextIssue,lang))
    return ["===",fmt(s1,lang),fmt(s2,lang),""]

## taken from https://stackoverflow.com/questions/31364464/python-3-find-the-mode-of-a-list/31364691#31364691
from collections import Counter
def mode(l):
    counter = Counter(l)
    max_count = max(counter.values())
    return [item for item, count in counter.items() if count == max_count]

### generate each aspect of the bulletin
#  ciel: start end neb-start neb-end {ceiling-height}
def clouds(data,lang):
    """
    TODO::Sky Condition is replaced by a precipitation term when the Chance of Precipitation (COP) 
    is equal or greater than 80 per cent. It is also replaced by the following terms when they 
    are expected to occur: Fog, Ice Fog, Blowing Snow, Local Blowing Snow, Blizzard, or Snow Squalls.
    """
    if showData:print(data)
    if data.empty():return None
    nebs = data["neb-start"]
    cloudLevel=mode(nebs)[0]
    if cloudLevel>4:
        return S(NP(Adv("mainly"),A("cloudy"))) if lang=="en" else S(NP(Adv("principalement"),A("nuageux")))
    elif cloudLevel in [3,4]:
        return S(A("clear")) if lang=="en" else S(A("dégagé"))
    elif cloudLevel in [0,1,2]:        
        return S(A("sunny")) if lang=="en" else S(A("ensoleillé"))
    else:
        return S(NP(A("variable"),Q("cloudiness"))) if lang=="en" else \
               S(NP(N("nébulosité"),A("variable")))
    return None


precipitationTypes = {
    "averses":{"en":N("shower").n("p"), 
               "fr":N("averse").n("p")},
    "averses_neige":{"en":N("flurry").n("p"), 
                     "fr":NP(N("averse").n("p"),PP("de",N("neige")))},
    "averses_neige_fondante":{"en":NP(A("wet"),N("flurry").n("p")), 
                              "fr":NP(N("averse").n("p"),PP("de",N("neige"),A("fondante")))},
    "blizzard":{"en":N("blizzard"), 
                "fr":N("blizzard")},
    "bourrasques_neige":{"en":NP(N("snow"),N("squall").n("p")), 
                         "fr":NP(N("bourrasque").n("p"),PP(D("de"),N("neige")))},
    "bruine":{"en":N("drizzle"), 
              "fr":N("bruine")},
    "bruine_verglacante" :{"en":NP(V("freeze").t("pr"),N("drizzle")), 
                           "fr":NP(N("bruine"),A("verglaçant"))},
    "cristaux_glace" :{"en":NP(N("ice"),N("crystal").n("p")), 
                       "fr":NP(N("cristal").n("p"),PP(P("de"),N("glace")))},
    "grele":{"en":N("hail"), 
             "fr":N("grêle")},
    "gresil":{"en":NP(N("ice"),N("pellet").n("p")), 
              "fr":N("grésil")},
    "neige":{"en":N("snow"), 
             "fr":N("neige")},
    "neige_fondante" :{"en":NP(A("wet"),N("snow")), 
                       "fr":NP(N("neige"),N("fondante"))},
    "orages":{"en":N("thunderstorm"), 
              "fr":N("orage").n("p")},
    "pluie":{"en":N("rain"), 
             "fr":N("pluie")},
    "pluie_verglacante":{"en":NP(V("freeze").t("pr"),N("rain")), 
                         "fr":NP(N("pluie"),A("verglaçant"))},
    "poudrerie" :{"en":NP(V("blow").t("pr"),N("snow")), 
                  "fr":N("poudrerie")},
}

# pcpn : start end certainty code type intensity frequency exception?
def precipitations(data,lang):
    """
    The Chance of Precipitation (COP) is the chance that measurable precipitation 
    (0.2 mm of rain or 0.2 cm of snow) will fall on “any random point of the forecast region”
    during the forecast period.
    
    Whenever the COP is expected to be between 30 and 70 per cent inclusive, it is indicated 
    in the forecast. The COP values are stated in increments of 10 per cent.
    
    TODO:: The term Risk is used in association with the terms Thunderstorm(s), Thundershower(s), 
    Hail, Freezing Rain and Freezing Drizzle, when there is a 30 or 40 per cent chance of 
    occurrence of these phenomena. In these cases, the percentage value is not stated.
    
    The use of 50 per cent is not permitted.
    Precipitation is included in the forecast when the Chance of Precipitation (COP) is 
    equal to or greater than 30 per cent.
    
    Rainfall amounts for the full length of the forecast (Day One, Day Two, and Day Two night) 
    shall be reported when they are expected to be:
    Region(s)	Amounts must be equal to or greater than
    Coastal British Columbia, Ontario, and Quebec	25 mm    
    """
    if showData:print(data)
    if data.empty():return None
    certainty=data["certainty"]
    maxCertainty=max(certainty)
    if maxCertainty >= 30:
        iMax=certainty.index(maxCertainty)
        pType=data["type"][iMax]
        if pType==None:pType="pluie"
        jsrPType=precipitationTypes[pType][lang]
        maxCertainty=maxCertainty//10*10
        if maxCertainty <= 70:
            if maxCertainty!=50:
                probExp= NP(NO(maxCertainty), Q("percent"),
                            PP(P("of"),N("chance"),PP(P("of"),jsrPType))) if lang=="en" else \
                         NP(NO(maxCertainty), P("pour"),N("cent"),
                            PP(P("de"),N("chance").n("p"),PP(P("de"),jsrPType)))
                return S(probExp,jsrDayPeriod(data,lang,data["start"][iMax]))
        else:
            return 
    return None
    
# e | nil | n | ne | nw | w | ely | nly | nely | nwly | wly | sly| sely | swly | sly | sely | sw | vrbl
jsrDirection = {
    "e":    {"en":Adv("east"),       "fr":N("est")},
    "n":    {"en":Adv("north"),      "fr":N("nord")},
    "ne":   {"en":Adv("northeast"),  "fr":N("nord-est")},
    "nw":   {"en":Adv("northwest"),  "fr":N("nord-ouest")},
    "w":    {"en":Adv("west"),       "fr":N("ouest")},
    "ely":  {"en":Adv("easterly"),   "fr":NP(N("secteur"),N("est"))},
    "nly":  {"en":Adv("northerly"),  "fr":NP(N("secteur"),N("nord"))},
    "nely": {"en":A("northeasterly"),"fr":NP(N("secteur"),N("nord-est"))},
    "nwly": {"en":A("northwesterly"),"fr":NP(N("secteur"),N("nord-ouest"))},
    "wly":  {"en":Adv("westerly"),   "fr":NP(N("secteur"),N("ouest"))},
    "sly":  {"en":Adv("southerly"),  "fr":NP(N("secteur"),N("sud"))},
    "sely": {"en":A("southeasterly"),"fr":NP(N("secteur"),N("sud-est"))},
    "swly": {"en":A("southwesterly"),"fr":NP(N("secteur"),N("sud-ouest"))},
    "sly":  {"en":Adv("southerly"),  "fr":NP(N("secteur"),N("sud"))},
    "se":   {"en":Adv("southeast"),  "fr":N("sud-est")},
    "s":    {"en":Adv("south"),      "fr":N("sud")},
    "sw":   {"en":Adv("southwest"),  "fr":N("sud-ouest")},
    "vrbl": {"en":A("variable"),     "fr":A("variable")},
}

# vents : start end direction modif? speed value exception?
def winds(data,hasWindChill,lang):
    """
    Wind is included when the mean speed is greater than or equal to 20 km/h.
    
    TODO: The terms Light or Calm are only used in a diminishing wind situation. For example: 
    “Wind west at 20 km/h becoming light this evening.”
    
    A wind speed change is indicated only when the average sustained speed is expected 
    to change by at least 20 km/h. (i.e. “Wind south 20 km/h increasing to 40 this evening.”)
    
    Wind is always included when wind chill is mentioned in the forecast. If the mean wind speed 
    is less than 20 km/h and the wind chill criteria are met, then the phrase: "Wind up to 15 km/h," is used.
    """
    if showData:print(data)
    if data.empty():return None
    speed=data["speed"]
    if len(speed)==0:return None
    maxS=max(speed)
    if maxS<20:
        if hasWindChill:
            return S(N("wind"),PP(P("up"),P("to"),NO(maxS),Q("km/h"))) if lang=="en" else\
                   S(N("vent").n("p"),PP(P("jusque"),P("à"),NO(maxS),Q("km/h")))
        else: return None
    iMax=speed.index(maxS)
    directionMax=data["direction"][iMax]
    if directionMax =="nil" : return None
    windDir=jsrDirection[directionMax][lang]
    s=S(N("wind") if lang=="en" else N("vent").n("p"),
        VP(V("become" if lang=="en" else "devenir").t("pr"),
           windDir if lang=="en" else PP(P("de"),D("le"),windDir),
           NO(maxS),Q("km/h"),
           jsrDayPeriod(data,lang,data["start"][iMax])))
    lineMax=data.line(iMax)
    valCol=data.colIndex["value"]
    if valCol<len(lineMax) and type(lineMax[valCol]) is list:
         # process gust ....
         [gStart,gEnd,gKind,gSpeed]=lineMax[valCol]
         if gKind== "rafales":
             s.add(VP(V("gust").t("pr"),PP(P("to"),NO(gSpeed))) if lang=="en" else
                   NP(N("rafale").n("p"),PP(P("jusqu'à"),NO(gSpeed)))
             )
    return s

#    temp : start end trend value
def temperatures(data,lang):
    """
    A single value of temperature is used. The following applies to both the maximum and minimum temperature:

    Temperature equal to 0ºC, write the term "zero"
    Temperature below 0ºC, add the qualifier "minus"
    Temperature from 1 to 5ºC, add the qualifier "plus"
    Temperature above 5ºC, no qualifier added
    Days One and Two: In cases where temperatures are anticipated to remain steady or undergo an abnormal trend for the time period (i.e. the temperature drops during the day or rises overnight by at least 3°C), this will be indicated in lieu of a forecast maximum or minimum.

    A second temperature can be given if the conditions exist in a way that there is a difference in temperature within a forecast region. These conditions usually exist in a forecast region which has shoreline and/or large elevation changes. 

    The difference must be at least 1°C when the temperature is from plus 5°C to minus 5°C, otherwise the difference has to be at least 3°C. 

    An example would be: “Friday..Mainly sunny. High 24 except 12 along the coast.”
    
    When the minimum temperature is forecast to be at, or close to, the freezing point, the term Frost may be used to describe where freezing is expected. The usage of this term is dependent on the extent of the freezing conditions.

    For the chance of local frost, the following phrases are used: "Risk of frost," "Patchy frost," "Frost in low lying areas," and "Frost in valleys."

    For extensive frost or when frost is likely, the following phrases are used: "Frost," "Widespread frost," "Extensive frost," and "Frost likely."
    """
    def jsrTemp(val):
        if val==0: return N("zero") if lang=="en" else N("zéro")
        if val<0 : return AdvP(A("minus") if lang=="en" else Adv("moins"),NO(abs(val)))
        if val<=5 : return AP(A("plus"), NO(val)) if lang=="en" else AdvP(Adv("plus"),NO(val))
        return NO(val)
    
    if showData:print(data)
    if data.empty():return None
    trend=data["trend"]
    values=data["value"]
    iMin=trend.index("min") if "min" in trend else -1
    iMax=trend.index("max") if "max" in trend else -1
    
    if iMin<0 and iMax<0: # only intermediary points only indicate high or low
        if random.random()>0.5: 
            return S(NP(N("low" if lang=="en" else "minimum"),jsrTemp(min(values))))
        else:
            return S(NP(Adv("high") if lang=="en" else N("maximum")),jsrTemp(max(values)))
    if iMin>=0 and iMax>=0:
        return S(N("temperature" if lang=="en" else "température"),
                    PP(P("between" if lang=="en" else "entre"),jsrTemp(values[iMin])),
                       C("and" if lang=="en" else "et"),jsrTemp(values[iMax]))
    if iMin>=0:
        return S(NP(N("low" if lang=="en" else "minimum"),jsrTemp(data["value"][iMin])),
                 jsrDayPeriod(data,lang,data["start"][iMin]))
    if iMax>=0:
        return S(NP(Adv("high") if lang=="en" else N("maximum"),jsrTemp(data["value"][iMax])),
                 jsrDayPeriod(data,lang,data["start"][iMax]))
    return None

## wind chill index:  https://www.canada.ca/en/environment-climate-change/services/weather-health/wind-chill-cold-weather/wind-chill-index.html#X-2015011511230218

wcIndex=[ # each line is a wind speed 10,20...60
# 0, - 5, -10, -15, -20, -25, -30, -35, -40, -45, -50   # temperatures
(-3, - 9, -15, -21, -27, -33, -39, -45, -51, -57, -63), # 10, Wind felt on face - wind vane begins to move
(-3, - 9, -15, -21, -27, -33, -39, -45, -51, -57, -63), # 20, Small flags extended, 
(-6, -13, -20, -26, -33, -39, -45, -52, -59, -65, -72), # 30, Wind raises loose paper, large flags flap and small tree branches move, 
(-7, -14, -21, -27, -34, -41, -48, -54, -61, -68, -74), # 40, Small trees begin to sway and large flags extend and flap strongly, 
(-8, -15, -22, -29, -35, -42, -49, -56, -63, -69, -76), # 50, Large branches of trees move, telephone wires whistle and it is hard to use an umbrella, 
(-9, -16, -23, -30, -36, -43, -50, -57, -64, -71, -78), # 60, Trees bend and walking against the wind is hard, 
]

def wind_chill(temp, windSpeed,lang):
    """Wind Chill is included in the forecast when temperatures are below zero and wind speeds are 5 km/h or greater. Both the minimum and maximum wind chill value can be indicated in the forecast.
"""
    if temp >=0 or windSpeed < 5: return None
    iWind=(windSpeed-10)//10 if windSpeed <60 else 5
    iDegree= abs(temp)//5
    wcVal=NO(wcIndex[iWind][iDegree])
    if lang=="en":
        return S(NP(D("the"),N("wind"),N("chill")),VP(V("be"),wcVal))
    else:
        return S(NP(D("le"),N("facteur"),A("éolien")),VP(V("être"),P("de"),wcVal))

def humidex(data,lang):
    """
    TODO: The Humidex is included in the 24 hour forecast, when the Humidex is 25 or higher, 
    the dewpoint temperature is above zero, and the temperature is 20° C or higher.
    """
    pass

## UV_index values: info taken from
#  https://www.canada.ca/en/environment-climate-change/services/weather-health/uv-index-sun-safety/about.html
#      Low (0-2), Moderate (3-5), High (6-7), Very High (8-10), and Extreme (11+)
uv_ranges= [(2,   {"en":A("low"),                     "fr":A("bas")}), 
            (5,   {"en":A("moderate"),                "fr":A("modéré")}), 
            (7,   {"en":A("high"),                    "fr":A("élevé")}), 
            (10,  {"en":AdvP(Adv("very"),Adv("high")),"fr":AdvP(Adv("très"),A("élevé"))}), 
            (1000,{"en":A("extreme"),                 "fr":A("extrême")})
           ]
#     indice_uv : start end value
def uv_index(data,lang):
    if showData:print(data)
    if data.empty():return None
    uvVal=round(max(data["value"]))
    for high,expr in uv_ranges:
        if uvVal<=high: 
            return S(Q("UV index" if lang=="en" else "index UV"),
                     None if lang=="en" else P("de"),
                     NO(uvVal),
                     C("or" if lang=="en" else "ou"),expr[lang])
    return None

### 
    
### generate a paragraph for a given period of time
def forecast(fc,lang,title,beginHour,endHour,text):
    if showData:print("\n** %s [%d,%d["%(title,beginHour,endHour))
    tzHours=get_delta_with_utc(fc)
    windWD=WeatherData("winds-fc['vents']",["direction", "modif?", "speed", "value", "exception?"],
                       fc["vents"],beginHour,endHour,beginTime,tzHours,text)
    tempWD=WeatherData("temperatures-fc['temp']",["trend", "value"],
                       fc["temp"],beginHour,endHour,beginTime,tzHours,text)
    windChill=wind_chill(max(tempWD["value"]),max(windWD["speed"]),lang)
    res=[
        clouds        (WeatherData("clouds-fc['ciel]",["neb-start","neb-end","ceiling-height"],
                                   fc["ciel"],beginHour,endHour,beginTime,tzHours,text),lang),
        precipitations(WeatherData("precipitations-fc['prob'][0][2:]",
                                   ["certainty","code","type","intensity", "frequency", "exception"],
                                   fc["prob"][0][2:],beginHour,endHour,beginTime,tzHours,text),lang),
        winds         (windWD,windChill!=None,lang),
        temperatures  (tempWD,lang),
        windChill,
        uv_index      (WeatherData("indice_uv-fc['indice_uv']",["value"],
                                   fc["indice_uv"],beginHour,endHour,beginTime,tzHours,text),lang)
    ]
    # return textwrap.fill(title+".."+" ".join([fmt(s,lang) for s in res if s!=None]),width=70)
    return [fmt(s,lang) for s in res if s!=None]

titles = {
    "today":   {"en":"Today",   "fr":"Aujourd'hui"},
    "tonight": {"en":"Tonight", "fr":"Ce soir et cette nuit"},
    "tomorrow":{"en":"Tomorrow","fr":"Demain"},
    "tomorrow_night":{"en":"Tomorrow night","fr":"Demain soir et nuit"},
}

tz    = None
tzS   = None
beginTime=None
tzHours=None
tzShift=None  

def getTimeInfo(fc,lang):
    global tzHours,tzShift,tzS
    header=fc["header"]
    if len(header)==15:
        [bulletinName,emitter,tz,bType,issueYear,issueMonth,issueDay,issueTime,_1,
          _2,nextYear,nextMonth,nextDay,nextTime,_3]=header
        issueDate=datetime(issueYear,issueMonth,issueDay)
        tzHours=get_delta_with_utc(fc)
        if tzHours==5:
            tzS="EST" if lang=="en" else "HNE"
        else:
            tzS="DST" if lang=="en" else "HAE"
        tzShift=timedelta(hours=tzHours)
        beginTime=datetime(issueYear,issueMonth,issueDay,hour=int(issueTime/100),
                            minute=issueTime%100)-tzShift
        nextTime=datetime(nextYear,nextMonth,nextDay,hour=int(nextTime/100),
                            minute=nextTime%100)-tzShift
    else:
        print("bad header",header)
    return (bulletinName,beginTime,nextTime)

def genPeriods(fc,lang,origSents):
    global nbPeriods
    (bulletinName,beginTime,nextTime)=getTimeInfo(fc,lang)
    res = {"orig":{},"jsr":{},"tok":{}}
    m=re.match(r"(?P<bName>\w+)-(?P<year>\d+)-(?P<month>\d+)-(?P<day>\d+)-(?P<hour>\d+)",fc["id"])
    bulletin=m.group("bName").upper()
    hour=str(int(m.group("hour"))-tzHours*100).zfill(4)
    periods = fc[lang].keys()
    for i,period in zip(range(0,4),fc[lang]["tok"].keys()):
        origSent=origSents[i]
        res["orig"][period]=origSent
        if showData:
            print("%s: %s %s [%s]"%(fc["id"],bulletin,hour,period))
        (startHour,endHour)=get_time_interval_for_period(fc,period)
        jsrFC=forecast(fc,lang,period,startHour+tzHours,endHour+tzHours,"")
        res["jsr"][period]=jsrFC
        res["tok"][period]=[word_tokenize(sent,{'en':'english','fr':'french'}[lang]) for sent in jsrFC]
        if showData:print("**> "+" ".join(res["jsr"][period]))
    return res

        
def bulletin(fc,lang):
    (bulletinName,beginTime,nextTime)=getTimeInfo(fc,lang)
    origSents=[t.strip().replace('\n'," ") for t in re.split(r"(?m)^.+?\.\.",fc[lang]["orig"])][1:]
    res=header(lang,bulletinName,beginTime,nextTime)
    res.extend(fc["names-"+lang])
    res[-1]=res[-1]+"."  # add full stop at the end of regions
    sents=genPeriods(fc,lang,origSents)
    for period in sents["jsr"]:
        title=fmt(jsrDay(beginTime+timedelta(days=1)),lang) if period.startswith("tomorrow") else titles[period][lang]
        res.append(textwrap.fill(title+".."+" ".join(sents["jsr"][period])))
    print("\n** original\n",fc[lang]["orig"])
    print("\n** %s\n"%("generated" if lang=="en" else "généré"),"\n".join(res))

def bulletins(jsonlFN):
    print("\n *** Generating from:",jsonlFN)
    for line in open(jsonlFN,"r",encoding="utf-8"):
        fc=json.loads(line)
        bulletin(fc,"en")
        break
        bulletin(fc,"fr")

def processCorpus(inJsonlFN):
    def origSents(lang):
        return [t.strip().replace('\n'," ") for t in re.split(r"(?m)^.+?\.\.",fc[lang]["orig"])]
    print("\n *** Processing ",inJsonlFN)
    outJsonlFN=inJsonlFN.replace(".jsonl","-jsr.jsonl")
    outJsonl=open(outJsonlFN,"w",encoding="utf=8")
    for line in open(inJsonlFN,"r",encoding="utf-8"):
        fc=json.loads(line)
        res={"id":fc["id"]}
        res["en"]=genPeriods(fc,"en",origSents("en")[1:])
        res["fr"]=genPeriods(fc,"fr",origSents("fr")[1:])
        outJsonl.write(json.dumps(res,indent=None,ensure_ascii=False))
        outJsonl.write("\n")
        if nbPeriods>1000: break    
        
    
### make sure that a jsRealB server is started in a terminal, using the following call
##    node ../jsRealB/dist/jsRealB-server-dme.js ../data/weatherLexicon.js
showData=False

if __name__ == '__main__':
    inputFN = sys.argv[1] if len(sys.argv)>1 else \
              "/Users/lapalme/Documents/GitHub/arpi_eccc/data/arpi-2021-train-10.jsonl"
    bulletins(inputFN)
    # processCorpus(inputFN)
