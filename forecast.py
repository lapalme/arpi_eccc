'''
Created on 21 août 2021

@author: lapalme
'''
# import sys
from ECdata import get_period_name, time_periods, wind_directions, dir_diff, uv_ranges
from arpi_eccc.utils import get_delta_with_utc, get_time_interval_for_period

# capitalize first letter and add period 
def make_sentence(*s):
    s=" ".join(e for e in s if e!=None and e!="")
    s = s[0].upper()+s[1:]
    if not s.endswith("."):s+="."
    return s

## sky condition

sky_condition_terminology = { ## row numbers in the table of section 5.8
    "r1":{"en":("Sunny","Clear"),
          "fr":("Ensoleillé","Dégagé")},
    "r2":{"en":("Mainly Sunny","A few clouds"),
          "fr":("Généralement ensoleillé","Quelques nuages")},
    "r3":{"en":("A mix of sun and cloud","Partly cloudy"),
          "fr":("Alternance de soleil et de nuages","Partiellement couvert")},
    "r4":{"en":("Mainly cloudy","Mainly cloudy"),
          "fr":("Généralement nuageux","Généralement nuageux")},
    "r5":{"en":("Cloudy","Cloudy"),
          "fr":("Nuageux","Nuageux")},
    "r6":{"en":("Overcast","Overcast"),
          "fr":("Couvert","Couvert")},
    "r7":{"en":("Increasing cloudiness","Increasing cloudiness"),
          "fr":("Ennuagement","Ennuagement")},
    "r8":{"en":("Clearing","Clearing"),
          "fr":("Dégagement","Dégagement")},
}

def sky_condition(mc,period,lang):
    """ Section 2.3.6 and 5.8"""
    ### ciel: start end neb-start neb-end {ceiling-height}
    sc=mc.get_sky_condition(period)
    if sc==None: return None
    # print(period,sc)
    dayNight = 0 if period in ["today","tomorrow"] else 1 
    valStart=sc[0][2]
    valEnd  =sc[-1][3]
    if valStart==valEnd:
        if valStart in [0,1]: 
            return sky_condition_terminology["r1"][lang][dayNight]+"."
        if valStart in [2,3]: 
            return sky_condition_terminology["r2"][lang][dayNight]+"."
        if valStart in [4,5,6]: 
            return sky_condition_terminology["r3"][lang][dayNight]+"."
        if valStart in [7,8]: 
            return sky_condition_terminology["r4"][lang][dayNight]+"."
        if valStart in [9]: 
            return sky_condition_terminology["r5"][lang][dayNight]+"."
        if valStart in [10]: 
            return sky_condition_terminology["r6"][lang][dayNight]+"."
    elif valStart in [0,1,2,3] and valEnd in [7,8,9,10]:
        return sky_condition_terminology["r7"][lang][dayNight]+"."
    elif (valStart in [7,8,9,10] and valEnd in [0,1,2,3]) or \
         (valStart in [5,6]      and valEnd in [0,1]):
        return sky_condition_terminology["r8"][lang][dayNight]+"."
    return None

### temperature

def tVal(val,lang):
    if val==0 : return "zero" if lang=="en" else "zéro"
    if val< 0 : return ("minus" if lang=="en" else "moins") +str(-val)
    if val<=5 : return "plus"+str(val)
    return str(val)

def pVal(p):    
    return "this" if p in ["today","tonight"] else "in the"

abnormal = {
    "night":{
        "a":{
            "en":lambda t,_:(f"Temperature rising to {tVal(t,'en')} by morning."),
            "fr":lambda t,_:(f"Températures à la hausse pour atteindre {tVal(t,'fr')} en matinée.")
        },
        "b":{
            "en":lambda t,u,_:(f"Low {tVal(u,'en')} with temperature rising to {tVal(t,'en')} by morning."),
            "fr":lambda t,u,_:(f"Minimum {tVal(u,'fr')}. Températures à la hausse pour atteindre {tVal(t,'fr')} en matinée.")
        },
        "c":{
            "en":lambda t,p:(f"Temperature rising to {tVal(t,'en')} {pVal(p)} evening then steady."),
            "fr":lambda t,_:(f"Températures à la hausse pour atteindre {tVal(t,'fr')} en soirée "+
                              f"pour ensuite demeurer stables.")
        },
        "d":{
            "en":lambda t,p:(f"Temperature rising to {tVal(t,'en')} {pVal(p)} evening then rising slowly."),
            "fr":lambda t,_:(f"Températures à la hausse pour atteindre {tVal(t,'fr')} en soirée, "+
                              f"puis hausse graduelle.")
        },
        "e":{
            "en":lambda t,p:(f"Temperature rising to {tVal(t,'en')} {pVal(p)} evening then falling."),
            "fr":lambda t,_:(f"Températures à la hausse pour atteindre {tVal(t,'fr')} en soirée,"+
                              f" pour ensuite être à la baisse.")
        },
    },
    "day":{
        "a":{
            "en":lambda t,p:(f"Temperature falling to {tVal(t,'en')} {pVal(p)} afternoon."),
            "fr":lambda t,_:(f"Températures à la baisse pour atteindre {tVal(t,'fr')} en après-midi.")
        },
        "b":{
            "en":lambda t,u,p:(f"High {tVal(u,'en')} with temperature falling to {tVal(t,'en')} {pVal(p)} afternoon."),
            "fr":lambda t,u,p:(f"Minimum {tVal(u,'fr')}. Températures à la baisse pour atteindre {tVal(t,'fr')} en matinée.")
        },
        "c":{
            "en":lambda t,p:(f"Temperature falling to {tVal(t,'en')} {pVal(p)} morning then steady."),
            "fr":lambda t,_:(f"Températures à la baisse pour atteindre {tVal(t,'fr')} en soirée "+
                              f"pour ensuite demeurer stables.")
        },
        "d":{
            "en":lambda t,p:(f"Temperature falling to {tVal(t,'en')} {pVal(p)} evening then falling slowly."),
            "fr":lambda t,_:(f"Températures à la hausse pour atteindre {tVal(t,'fr')} en soirée, "+
                              f"puis baisse graduelle,")
        },
        "e":{
            "en":lambda t,p:(f"Temperature falling to {tVal(t,'en')} {pVal(p)} evening then rising."),
            "fr":lambda t,_:(f"Températures à la hausse pour atteindre {tVal(t,'fr')} en soirée,"+
                              f" pour ensuite être à la hausse.")
        },
    }
}    
 
def temperature(mc,period,lang):    
    ## tVals is an array of temperature values from beginHour to endHour
    tVals=mc.get_temperature(period)
    if tVals==None: return None
    maxTemp=max(tVals)
    iMax=tVals.index(maxTemp)
    minTemp=min(tVals)
    iMin=tVals.index(minTemp)
    # print(period,"min:",minTemp,iMin,"max:",maxTemp,iMax,tVals)
    dn= "night" if period in ["tonight","tomorrow_night"] else "day"
    (t1,t2,i1,i2)=(maxTemp,minTemp,iMax,iMin) if dn=="night" else (minTemp,maxTemp,iMin,iMax)
    if t1 >= t2+3:
        # abnormal change time
        if i1 <=1 :
            return abnormal[dn]["a"][lang](t1, period)
        else:
            if i1 < 6:
                rest=tVals[iMin:]
                if all([abs(t-t1)<=2 for t in rest]):
                    # c) remains +/- 2 for the rest
                    return abnormal[dn]["c"][lang](t1,period)
                elif any([t-t1>2 for t in rest]):
                    # d) rises more than 2 for the rest 
                    return abnormal[dn]["d"][lang](t1,period)
                elif any([t1-t>2 for t in rest]):
                    # e) falls more than 2 for the rest (this should never happen!!!)
                    return abnormal[dn]["e"][lang](t1,period)
            else:
                # b) low temperature after the beginning (but no special case)
                return abnormal[dn]["b"][lang](t2,t1,period)
    return make_sentence(("high" if lang=="en" else "maximum")+" "+tVal(maxTemp,lang))

### precipitation
# pcpn : start end certainty code type intensity frequency exception?

## very simplified method: we take each info and output its type...

#     certainty : "certain" | "possible" | "risque" =>
#                 "certain" | "possible" | "risk"
#     code : "debut" | "debut_fin" | "exact" | "fin" =>
#            "start" | "start_end" | "exact" | "end"
#     type : "averses" | "averses_neige" | "averses_neige_fondante" | "blizzard" | 
#            "bourrasques_neige" | "bruine" | "bruine_verglacante" | 
#            "cristaux_glace" |"grele"| "gresil" | "neige" | "neige_fondante" | 
#            "orages" | "pluie" | "pluie_verglacante" | "poudrerie" 
#            =>
#            "showers" | "flurries" | "wet flurries" | "blizzard" | 
#            "snow squalls" | "drizzle" | "freezing drizzle" | 
#            "ice crystals" |"hail"| "ice pellets" | "snow" | "wet snow" | 
#            "thunderstorm" | "rain" | "freezing rain" | "blowing snow"
#     intensity : "faible" | "fort" | "modere" | "nil" | "tres_faible" =>
#                 "light" | "heavy" | "moderate" | *implicit* | "very light"
#     frequency : "bref" | "continuel" | "frequent" | "occasionnel" | "peu" =>
#                 "brief" | "continual" | "frequent" | "occasionnal" | "few"
#     exception : embedded list of pcpn

precipitation_types = { 
    "averses":{"en":"showers",     "fr":"averses"},
    "neige"  :{"en":"snow",        "fr":"neige"},
    "pluie"  :{"en":"rain",        "fr":"pluie"},
    "orages" :{"en":"thunderstorm","fr":"orages"},
    #TODO: add all other types
}


def get_time_period(time):
    for tp in time_periods:
        if tp[0]<=time and time < tp[1]:
            return tp
    return None
    

def precipitation(mc,period,lang):
    pcpns=mc.get_precipitation(period)
    delta=mc.get_delta_with_utc()
#     print("pcpns\n",pcpns)
    if pcpns==None: return None
    sents=[]
    timePeriod=""
    for pcpn in pcpns:
        pType=pcpn[4]
        pCode=pcpn[3]
        if pCode.startswith("debut"):
            tp=get_time_period((pcpn[0]-delta)%24)
            if tp!=None:
                timePeriod=("beginning "+tp[2]) if lang=="en" else ("débutant "+tp[3])
        elif pCode=="fin":
            tp=get_time_period((pcpn[1]-delta)%24)
            if tp!=None:
                timePeriod=("ending "+tp[2]) if lang=="en" else ("finissant "+tp[3])
        if pType in precipitation_types:
            sents.append(make_sentence(precipitation_types[pType][lang],timePeriod))
        else:
            sents.append("[["+pType+"]].")
    return " ".join(sents)

def weather_events(mc,period,lang):
    return None

def obstruction_to_visibility(mc,period,lang):
    return None


## vents : start end direction modif? speed value exception?
def wind(mc,period,lang):
    winds=mc.get_wind_direction(period)
    # print(period,"winds\n",winds)
    if winds==None:return None
    lastSpeed=None 
    lastDir=None
    sent=""
    # TODO: deal with "gust"...
    for wnd in winds:
        wSpeed = wnd[4]
        wDir= wnd[2]
        if wSpeed>=20 and wDir in wind_directions:
            if lastSpeed!=None and abs(wSpeed-lastSpeed)>=20:
                lastSpeed=wSpeed
                wSpeed=round(wSpeed/10)*10
                sent+=(" increasing to " if lang=="en" else " augmentant à ")+str(wSpeed)
            elif lastSpeed!=None and dir_diff(wDir, lastDir):
                sent+=(" becoming " if lang=="en" else " devenant ")+wind_directions[wDir][lang]
                lastDir=wDir
            else:
                lastSpeed=wSpeed
                lastDir=wDir
                wSpeed=round(wSpeed/10)*10
                sent=("wind" if lang=="en" else "vents")+" "+str(wSpeed)+" km/h "+\
                       wind_directions[wDir][lang]   
    return make_sentence(sent)

def thermal_indices(mc,period,lang):
    return None

# indice_uv : start end value
def UV_index(mc,period,lang):
    uvi=mc.get_uv_index(period)
#     print(period,"uvi\n",uvi)
    if uvi==None:return None 
    ## modulate uv with sky condition (as suggestion par Jacques Marcoux EC)
    uvVal=round(uvi[0][2])
    sc=mc.get_sky_condition(period)
    if sc!=None:
#         print(period,"ciel\n",sc)
        valStart=sc[0][2]
        valEnd  =sc[-1][3]
        coverVal=(valStart+valEnd)/2*0.1 # 0= clear 10: covered
        if coverVal>0.2:
            uvVal=round(uvVal*(1-coverVal))
#         print("corrected uval",uvVal)
    for high,expr in uv_ranges:
        if uvVal<=high:
            return make_sentence(f"UV index {uvVal} or {expr[lang]}" if lang=="en" else 
                                 f"Indice UV de {uvVal} ou {expr[lang]}")
    return None

def forecast_period(mc,period,lang):
#     print("period:",period)
#     print(get_time_interval_for_period(mc.data, period))
    return " ".join(filter(lambda l:l!=None,[
        sky_condition(mc, period, lang),
        precipitation(mc, period, lang),
        wind(mc, period, lang),
        weather_events(mc, period, lang),
        obstruction_to_visibility(mc, period, lang),
        temperature(mc, period, lang),
        thermal_indices(mc, period, lang),
        UV_index(mc, period, lang)
    ]))
