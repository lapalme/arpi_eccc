## implement the organization of EC Public Weather Forecasts and Warning
##   we (try to) follow the terminology of the PUBPRO document
## Currently only the "Regular Public Forecast Bulletin" is implemented

## the input is the json version of the Meteocode (mc) used for the ARPI-EC workshop
##    in August 2021

## This version only uses Python string formatting for the templates

import sys,re,textwrap, json, locale
from time import process_time

from datetime import datetime,timedelta
from ECdata import get_forecast_area, periods, get_period_name
# from arpi_eccc.utils import get_delta_with_utc, get_time_interval_for_period
from MeteoCode import MeteoCode
from forecast import forecast_period
from ppJson import ppJson

from levenshtein import compareLevenshtein


trace=False

## each block should return a list of string corresponding to a line in the output
## if a string is None, it is ignored

def communication_header(mc,lang):
    if trace: print("communication_header")
    hdr=mc.get_header()
    return ["",f"{hdr[0]} {hdr[1]} {hdr[5]:02d}{hdr[6]:02d}{hdr[7]:04d}"]
    
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
    for period in mc.data[lang]["tok"]:
        periodFC.append(get_period_name(tomorrow,period,lang)+".."+
                        forecast_period(mc,period,lang))
    return periodFC

def end_statement(lang):
    if trace: print("end_statement")
    return ["","End"]

def regular_forecast(mc,lang):
    """ Sect 2.2 """
    text=[
#         communication_header(mc,lang),
#         title_block(mc,lang),
        forecast_regions(mc,lang),
        forecast_text(mc,lang),
#         end_statement(lang),
     ]    
    gen="\n".join([textwrap.fill(line,width=70, subsequent_indent=" ") 
                   for lines in text for line in lines if line!=None])
    return gen

## only produce full bulletins
def generate_bulletin(mc,lang):
    text=[
        communication_header(mc,lang),
        title_block(mc,lang),
        forecast_regions(mc,lang),
        forecast_text(mc,lang),
        end_statement(lang),
     ]    
    return "\n".join([textwrap.fill(line,width=70, subsequent_indent=" ") 
                   for lines in text for line in lines if line!=None])
    
def generate_bulletins(jsonlFN,max=-1):
    """ Sect 2.2 """
    for line in open(jsonlFN,"r",encoding="utf-8"):
        mc=MeteoCode(json.loads(line))    
        print(generate_bulletin(mc,"en"))
        print(generate_bulletin(mc,"fr"))
        print("===")
        max-=1
        if max==0:
            break

##  compare three periods only and display result and  original in parallel 
def compare_with_orig(mc,lang):
    origB=mc.get_original_bulletin(lang)
    text=[
#         communication_header(mc,lang),
#         title_block(mc,lang),
        forecast_regions(mc,lang),
        forecast_text(mc,lang),
#         end_statement(lang),
     ]    
    genB = "\n".join([textwrap.fill(line,width=70, subsequent_indent=" ") 
                   for lines in text for line in lines if line!=None])
    ### output comparaison with original
    
    fmt="%-72s|%s"
    res=[fmt%("*** Generated ***","*** Original ***")]
    periodSplitRE=re.compile(r"\n(?=[A-Z])")
    for gen,orig in zip(periodSplitRE.split(genB),periodSplitRE.split(origB)):
        genL=gen.split("\n")
        origL=orig.split("\n")
        lg=len(genL)
        lo=len(origL)
        for i in range(0,min(lg,lo)):
            res.append(fmt%(genL[i],origL[i]))
        if lg<lo:
            for i in range(lg,lo):
                res.append(fmt%("",origL[i]))
        elif lg>lo:
            for i in range(lo,lg):
                res.append(fmt%(genL[i],""))
    return "\n".join(res)

def compare_all_with_orig(jsonlFN,max=-1):
    no=0
    for line in open(jsonlFN,"r",encoding="utf-8"):
        no+=1
        mc=MeteoCode(json.loads(line))
        if re.match(r"fpcn74-2019-12-.*",mc.data["id"]):
            print("%d :: %s"%(no,mc.data["id"]))
            # ppJson(sys.stdout,mc.data)   
            print(compare_with_orig(mc, "en"))
            # print("---")
            # print(compare_with_orig(mc, "fr"))
            print("===")
        max-=1
        if max==0:break


##  For evaluation
def getNumericTokens(toks):
    return [tok for period in toks 
             for sent in toks[period] 
                 for tok in sent if re.fullmatch(r"\b\d+(\.\d+)?\b",tok)]

def compareNT(refNT,jsrNT):
    (editDist,editOps)=compareLevenshtein(" ".join(jsrNT)," ".join(refNT),equals=lambda s1,s2:s1==s2)
    # print("ref:",refNT)
    # print("gen:",jsrNT)
    # print("dist:%d score=%5.2f"%(editDist,editDist/len(refNT)))
    # print(editOps)
    return editDist/len(refNT)

            
startTime=process_time()

def evaluate(jsonlFN,lang,max=-1):
    from nltk.tokenize import word_tokenize,sent_tokenize
    from arpi_eccc.nlg_evaluation import bleu_evaluation
    nltkLang={'en':'english','fr':'french'}[lang]
    reference=[]
    gen_results=[]
    numericDiffs=0
    for line in open(jsonlFN,"r",encoding="utf-8"):
        mc=MeteoCode(json.loads(line))
        reference.append(mc.data[lang]["tok"])
        refNT=getNumericTokens(mc.data[lang]["tok"])
        genTok={}
        for period in mc.data[lang]["tok"]:
            period_text=forecast_period(mc,period,lang)
            genTok[period]=[word_tokenize(sent,nltkLang) for sent in sent_tokenize(period_text, nltkLang)]
        gen_results.append(genTok)
        # print(genTok)
        genNT=getNumericTokens(genTok)
        numericDiffs+=compareNT(refNT,genNT)
        if len(reference)%100==0:
            print("%6.2f :: %d %5.2f"%(process_time()-startTime,len(reference),numericDiffs/len(reference)))
        if len(reference) >= 100:
            break
    print("*** reference:%d"%len(reference))
    # ppJson(sys.stdout,reference)
    print("*** jsRealB results:%d"%len(gen_results))
    # ppJson(sys.stdout,gen_results)
    print("%6.2f ::*** numeric differences:%5.3f %5.2f"%(process_time()-startTime,numericDiffs,numericDiffs/len(reference)))
    # ...now we can evaluate jsRealB using the two lists created above.
    evaluation = bleu_evaluation(gen_results, reference)
    for period in ['today', 'tonight', 'tomorrow', 'tomorrow_night']:
        if evaluation[period]!=-1:
            print(f"For bulletin period {period}, BLEU score is {evaluation[period]:.3f} on a scale from 0 to 1")
    print()
    print(f"Global score is {evaluation['global']:.3f}")
    


def main(jsonlFN,max):
    # generate_bulletins(jsonlFN,max)
    compare_all_with_orig(jsonlFN,max)
    # evaluate(jsonlFN,"en",max)

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv)>1 else
        "/Users/lapalme/Documents/GitHub/arpi_eccc/data/arpi-2021-train-1000.jsonl",100)