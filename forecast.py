'''
Created on 21 août 2021

@author: lapalme
'''
import sys
from ECdata import get_period_name, time_periods,get_time_period_name, \
                   wind_directions, dir_diff, uv_ranges, precipitation_types
from arpi_eccc.utils import get_delta_with_utc, get_time_interval_for_period
from ppJson import ppJson

# join all non empty parameter in a sentence
# then capitalize first letter and add full stop at the end 
def make_sentence(*s):
    s=" ".join(e for e in s if e!=None and e!="")
    if len(s)>0:
        s = s[0].upper()+s[1:]
        if not s.endswith("."):s+="."
    return s

def get_term_at(terms,hour):
    if terms==None or len(terms)==0:return None  
    for term in terms:
        if hour<=term[1]:
            return term
    return None
    # print("should never happen: get_value_at(%d) not found\n%s"%(hour,terms))
    # tb = sys.exc_info()[2]
    # raise IndexError().with_traceback(tb)
        
def get_fn_term(terms,idx,cmp):
    if terms==None or len(terms)==0 :return None 
    maxTerm=terms[0]
    for i in range(1,len(terms)):
        if cmp(terms[i][idx],maxTerm[idx]):
            maxTerm=terms[i]
    return maxTerm

def get_max_term(terms,idx):
    return get_fn_term(terms,idx,lambda x,y:x>y)

def get_min_term(terms,idx):
    return get_fn_term(terms,idx,lambda x,y:x<y)

trace=False

### Pubpro: section 2.3.6, 5.8
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
    def addNoRepeat(list,newVal): # avoid generating same sentence twice
        if newVal not in list:
            list.append(newVal)
    """ Section 2.3.6 and 5.8"""
    ### ciel: start end neb-start neb-end {ceiling-height}
    sc_terms=mc.get_sky_condition(period)
    if sc_terms==None: return None
    if trace: print(period,"sky_condition\n",sc_terms)
    sents=[]
    delta=mc.get_delta_with_utc()
    for sc_term in sc_terms:
        valStart=sc_term[2]
        valEnd  =sc_term[3]        
        dayNight = 0 if period in ["today","tomorrow"] else 1 
        if valStart==valEnd:
            if valStart in [0,1]: 
                addNoRepeat(sents,sky_condition_terminology["r1"][lang][dayNight])
            if valStart in [2,3]: 
                addNoRepeat(sents,sky_condition_terminology["r2"][lang][dayNight])
            if valStart in [4,5,6]: 
                addNoRepeat(sents, sky_condition_terminology["r3"][lang][dayNight])
            if valStart in [7,8]: 
                addNoRepeat(sents,sky_condition_terminology["r4"][lang][dayNight])
            if valStart in [9]: 
                addNoRepeat(sents,sky_condition_terminology["r5"][lang][dayNight])
            if valStart in [10]: 
                addNoRepeat(sents,sky_condition_terminology["r6"][lang][dayNight])
        elif valStart in [0,1,2,3] and valEnd in [7,8,9,10]:
            addNoRepeat(sents,sky_condition_terminology["r7"][lang][dayNight]+
                         " "+get_time_period_name((sc_term[0]-delta)%24, lang))
        elif (valStart in [7,8,9,10] and valEnd in [0,1,2,3]) or \
             (valStart in [5,6]      and valEnd in [0,1]):
            addNoRepeat(sents,sky_condition_terminology["r8"][lang][dayNight]+
                         " "+get_time_period_name((sc_term[0]-delta)%24, lang))
    return " ".join(make_sentence(sent) for sent in sents)

###   Pubpro : sect 2.3.1, 2.3.2, 2.3.3
### precipitation
# pcpn : start end certainty code type intensity frequency exception?
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

def precipitation_at(prob,pcpn_term,delta,amount_terms,lang):
    sents=[]
    pCode=pcpn_term[3]
    pType=pcpn_term[4]
    amount_term=None
    timePeriod=None
    if pCode.startswith("debut"):
        tp=get_time_period_name((pcpn_term[0]-delta)%24,lang)
        if tp!=None:
            timePeriod=("beginning "+tp) if lang=="en" else ("débutant "+tp)
            amount_term=get_term_at(amount_terms,pcpn_term[0])
    elif pCode=="fin":
        tp=get_time_period_name((pcpn_term[1]-delta)%24,lang)
        if tp!=None:
            timePeriod=("ending "+tp) if lang=="en" else ("finissant "+tp)
            amount_term=get_term_at(amount_terms,pcpn_term[0])
    if pType in precipitation_types:
        sents.append(make_sentence(prob,precipitation_types[pType][lang],timePeriod))
    else:
        sents.append("[["+pType+"]].")
    ## add amount
    if amount_term!=None:
        pcpnType=amount_term[2]
        if pcpnType=="pluie":
            if amount_term[5]>20:
                sents.append(make_sentence(("amount " if lang=="en" else "accumulation de ")+
                             str(round(amount_term[5]))+" mm"))
        elif pcpnType=="neige":
            if amount_term[5]>2:
                sents.append(make_sentence(("amount " if lang=="en" else "accumulation de ")+
                             str(round(amount_term[5]))+" cm"))
    return " ".join(sents)
    

def precipitation(mc,period,lang):
    pcpn_terms=mc.get_precipitation(period)
    if pcpn_terms==None: return None
    delta=mc.get_delta_with_utc()
    prob_terms=mc.get_precipitation_probabilities(period)
    maxProbTerm=get_max_term(prob_terms,2)
    if maxProbTerm!=None and maxProbTerm[2]<=10:
        maxProbTerm=None
    amount_terms=mc.get_precipitation_amount(period)
    if trace: 
        print(period,"pcpns\n",pcpn_terms)
        print("prob\n",prob_terms)
        print("amount\n",amount_terms)
    if maxProbTerm != None:
        ## output information associated with maxProb
        maxProbVal=maxProbTerm[2]
        if maxProbVal < 100:
            prob= f"{maxProbVal} percent chance of" if lang=="en" else\
                  f"{maxProbVal} pour cent de probabilité de"
        else:
            prob=None
        pcpn_term=get_term_at(pcpn_terms, maxProbTerm[0])
        return precipitation_at(prob,pcpn_term,delta,amount_terms,lang)
    else:
        ## show information associated with all precipitation values
        strings=[]
        for pcpn_term in pcpn_terms:
            strings.append(precipitation_at(None,pcpn_term,delta,amount_terms,lang))
    return " ".join(strings)


### Pubpro sec 2.3.4
## vents : start end direction modif? speed value exception?
def wind(mc,period,lang):
    wind_terms=mc.get_wind(period)
    if wind_terms==None:return None
    if trace: print(period,"winds\n",wind_terms)
    delta=mc.get_delta_with_utc()
    lastSpeed=None 
    lastDir=None
    sent=""
    for wind_term in wind_terms:
        wSpeed = wind_term[4]
        wDir= wind_term[2]
        if wSpeed>=15 and wDir in wind_directions:
            if lastSpeed!=None and abs(wSpeed-lastSpeed)>=20:
                lastSpeed=wSpeed
                sent+=(" increasing to " if lang=="en" else " augmentant à ")+str(wSpeed)
            elif lastDir!=None and dir_diff(wDir, lastDir):
                sent+=(" becoming " if lang=="en" else " devenant ")+wind_directions[wDir][lang]
                lastDir=wDir
            else:
                lastSpeed=wSpeed
                lastDir=wDir
                sent=("wind" if lang=="en" else "vents")+" "+wind_directions[wDir][lang]+\
                      " "+str(wSpeed)+" km/h"                       
            # show gust or time
            if len(wind_term)>5:
                gust=wind_term[5]
                if gust[2]=='rafales':
                    sent +=(" gusting to " if lang=="en" else " avec rafales à ")+str(gust[3])
            else:
                sent+=" "+get_time_period_name(wind_term[0]-delta,lang)
    return make_sentence(sent) if len(sent)>0 else None

### temperature  (PubPro sec 2.3.5)

def tVal(val,lang):
    val=round(val) # some temperatures are given as float...
    if val==0 : return "zero" if lang=="en" else "zéro"
    if val< 0 : return ("minus " if lang=="en" else "moins ") +str(-val)
    if val<=5 : return "plus "+str(val)
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
    temperature_terms=mc.get_temperature(period)
    if temperature_terms == None : return None
    maxTemp=get_max_term(temperature_terms,3)[3]
    minTemp=get_min_term(temperature_terms,3)[3]
    # for climat_term in climat_terms:
        # if climat_term[2]=="max":maxTemp=climat_term[3]
        # elif climat_term[2]=="min":minTemp=climat_term[3]
    if trace: print(period,"min:",minTemp,"max:",maxTemp)
    dn= "night" if period in ["tonight","tomorrow_night"] else "day"
    tempVals=mc.get_temperature_values(period)
    if isinstance(tempVals,int):
        print("tempVals",tempVals)
        print(period)
        print(temperature_terms)
        ppJson(sys.stdout,mc.data)
    try:
        (t1,t2,i1,i2)=(maxTemp,minTemp,tempVals.index(maxTemp),tempVals.index(minTemp)) if dn=="night" else\
                      (minTemp,maxTemp,tempVals.index(minTemp),tempVals.index(maxTemp))
        if t1 >= t2+3:
            # abnormal change time
            if i1 <=1 :
                return abnormal[dn]["a"][lang](t1, period)
            else:
                if i1 < 6:
                    rest=tempVals[i1:]
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
    except ValueError:
        print(tempVals)
        print(temperature_terms)
        tb = sys.exc_info()[2]
        raise Exception().with_traceback(tb)

        raise 
    res=[]
    res.append(make_sentence(("high" if lang=="en" else "maximum")+" "+tVal(maxTemp,lang)))
    if minTemp < maxTemp-2:
        res.append(make_sentence(("low" if lang=="en" else "minimum")+" "+tVal(minTemp,lang)))
    return " ".join(res)


def weather_events(mc,period,lang):
    return None

def obstruction_to_visibility(mc,period,lang):
    return None


def wind_chill(t,v):
    " Équation from section 3.2.1"
    return round(13.12+0.6215*t-11.37*v**0.16+0.3965*t*v**0.16)

def thermal_indices(mc,period,lang):
    temperature_terms=mc.get_temperature(period)
    if temperature_terms == None : return None
    # maxTempTerm=get_max_term(temperature_terms,3)
    minTempTerm=get_min_term(temperature_terms,3)
    # climat_terms=mc.get_climat_temp(period)
    # if climat_terms==None:return None
    # minTempTerm=None
    # for climat_term in climat_terms:
        # if climat_term[2]=="min":minTempTerm=climat_term
    # if minTempTerm==None:return None
    wind_terms=mc.get_wind(period)
    windMaxTerm=get_term_at(wind_terms, minTempTerm[0])
    if windMaxTerm==None:return None
    windSpeed=windMaxTerm[4]
    if minTempTerm[3] < 0 and windSpeed>=5:
        return make_sentence(("wind chill " if lang=="en" else "refroidissement éolien de ")+\
                tVal(wind_chill(minTempTerm[3],windSpeed),lang))
    
    return None

# indice_uv : start end value
def UV_index(mc,period,lang):
    if period in ["tonight","tomorrow_night"]: # no UV index in the night
        return None
    uvi_terms=mc.get_uv_index(period)
    if uvi_terms==None:return None 
    if trace: print(period,"uvi\n",uvi_terms)
    uvVal=uvi_terms[0][2] # consider only the first uvi_term
    if uvVal<1: return None  ## too low
    ## modulate uv with sky condition (suggested by Jacques Marcoux EC)
    ## as I am not sure of the formula, I leave it as is
    # sc_terms=mc.get_sky_condition(period)
    # if sc_terms!=None:
        # if trace: print(period,"ciel\n",sc_terms)
        # coverVal=get_term_at(sc_terms,uvi_terms[0][0])[2]
        # if coverVal>0.2:
            # uvVal=round(uvVal*(1-coverVal))
        # else:
            # uvVal=round(uvVal)
        # if trace: print("corrected uval",uvVal)
    uvVal=round(uvVal)
    if uvVal==0:return None
    for high,expr in uv_ranges:
        if uvVal<=high:
            return make_sentence(f"UV index {uvVal} or {expr[lang]}" if lang=="en" else 
                                 f"Indice UV de {uvVal} ou {expr[lang]}")
    return None

def forecast_period(mc,period,lang):
    if trace:  
        print("period:",period)
        print(get_time_interval_for_period(mc.data, period))
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
