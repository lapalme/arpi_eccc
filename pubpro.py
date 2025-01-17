## implement the organization of EC Public Weather Forecasts and Warning
##   we (try to) follow the terminology of the PUBPRO document
## Currently only the "Regular Public Forecast Bulletin" is implemented

## the input is the json version of the Meteocode (mc) used for the ARPI-EC workshop
##    in August 2021

## This version only uses Python string formatting for the templates

import sys,re,textwrap, json, locale,random
from time import process_time

from datetime import datetime,timedelta
from ECdata import get_forecast_area, periods, get_period_name, warnings
from arpi_eccc.utils import get_delta_with_utc, get_time_interval_for_period
from MeteoCode import MeteoCode
from forecast import forecast_period
from ppJson import ppJson

# from levenshtein import compareLevenshtein

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

    def addWarning(w): # recursive adding of possible embedded warnings
        message=warnings[w[4]][lang]
        regions.append(f"{message[0].upper()+message[1:]} warning in effect." if lang=="en" else
                       f"Avertissement de {message} en vigueur.")
        if len(w)>5 and isinstance(w[5],list):
            print("*** embedded warning")
            addWarning(w[5])
        
    warning=mc.get_warning()
    if warning!=None:# add warning at the end of the regions
        # check that the warning is in effect in the range of the bulletins of the day
        warningStart=warning[0]
        warningEnd  =warning[1]
        bulletinPeriods=list(mc.data["en"]["tok"].keys())
        bulletinsStart=get_time_interval_for_period(mc.data, bulletinPeriods[0])[0]
        bulletinsEnd  =get_time_interval_for_period(mc.data, bulletinPeriods[2])[1]
        # print("*** WARNING: %s: warning(%s,%s): bulletin(%s,%s)"
              # %(warning,warningStart,warningEnd,bulletinsStart,bulletinsEnd))
        if warningEnd < bulletinsStart or warningStart>bulletinsEnd:
            return regions
        addWarning(warning)
        
    return regions


def forecast_text(mc,lang):
    """ Section 2.2.2 """
    if trace: print("forecast_text")
    issueDT=mc.get_issue_date()
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
        forecast_regions(mc,lang),
        forecast_text(mc,lang),
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
    
def generate_bulletins(jsonlFile,nb):
    """ Sect 2.2 """
    for line in jsonlFile:
        mc=MeteoCode(json.loads(line))    
        print(generate_bulletin(mc,"en"))
        print(generate_bulletin(mc,"fr"))
        print("===")
        nb-=1
        if nb==0:
            break

##  compare three periods only and display result and  original in parallel 
def compare_with_orig(mc,lang):
    origB=mc.get_original_bulletin(lang)
    text=[
        forecast_regions(mc,lang),
        forecast_text(mc,lang),
    ]    
    genB = "\n".join([textwrap.fill(line,width=70, subsequent_indent=" ") 
                   for lines in text for line in lines if line!=None])
    ### output comparison with original
    
    fmt="%-72s|%s"
    res=[fmt%("*** Generated ***" if lang=="en" else "*** Généré ***",
              "*** Original ***")]
    periodSplitRE=re.compile(r"\n(?=[A-Z][-' A-Za-z]+\.\.)")
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
    return "\n"+"\n".join(res)

def compare_all_with_orig(jsonlFile,rateCompare):
    no=0
    nb=0
    for line in jsonlFile:
        no+=1
        mc=MeteoCode(json.loads(line))
        # if mc.data["id"]=="fpcn73-2019-02-08-2045-r73.5":
        if random.random()<rateCompare:
            print("%d :: %s"%(no,mc.data["id"]))
            for period in mc.data["en"]["tok"]:
                mc.show_data(period)
            print(compare_with_orig(mc, "en"))
            print(compare_with_orig(mc, "fr"))
            print("="*145,"\n")
            nb+=1
    return nb

##  For evaluation
# def getNumericTokens(toks):
    # return [tok for period in toks 
             # for sent in toks[period] 
                 # for tok in sent if re.fullmatch(r"\b\d+(\.\d+)?\b",tok)]
                 #
# def compareNT(refNT,jsrNT):
    # (editDist,editOps)=compareLevenshtein(" ".join(jsrNT)," ".join(refNT),equals=lambda s1,s2:s1==s2)
    # # print("ref:",refNT)
    # # print("gen:",jsrNT)
    # # print("dist:%d score=%5.2f"%(editDist,editDist/len(refNT)))
    # # print(editOps)
    # return editDist/len(refNT)

            
startTime=process_time()

def evaluate(jsonlFile,lang):
    from nltk.tokenize import word_tokenize,sent_tokenize
    from arpi_eccc.nlg_evaluation import bleu_evaluation
    nltkLang={'en':'english','fr':'french'}[lang]
    reference=[]
    gen_results=[]
    # numericDiffs=0
    jsonlFile.seek(0) # ensure to start at the beginning of the file when called the second time
    for line in jsonlFile:
        mc=MeteoCode(json.loads(line))
        reference.append(mc.data[lang]["tok"])
        # refNT=getNumericTokens(mc.data[lang]["tok"])
        genTok={}
        for period in mc.data[lang]["tok"]:
            period_text=forecast_period(mc,period,lang)
            genTok[period]=[word_tokenize(sent,nltkLang) for sent in sent_tokenize(period_text, nltkLang)]
        gen_results.append(genTok)
        # print(genTok)
        # genNT=getNumericTokens(genTok)
        # numericDiffs+=compareNT(refNT,genNT)
        if len(reference)%1000==0:
            print("%6.2f :: %6d"%(process_time()-startTime,len(reference)))
    print("*** reference:%d generated:%d"%(len(reference),len(gen_results)))
    # print("%6.2f ::*** numeric differences:%5.3f %5.2f"%(process_time()-startTime,numericDiffs,numericDiffs/len(reference)))
    evaluation = bleu_evaluation(gen_results, reference)
    for period in ['today', 'tonight', 'tomorrow', 'tomorrow_night']:
        if evaluation[period]!=-1:
            print(f"For bulletin period {period}, BLEU score is {evaluation[period]:.3f} on a scale from 0 to 1")
    print()
    print(f"{(process_time()-startTime):6.2f} Global score is {evaluation['global']:.3f}")
    
def usage(mess):
    print(mess)
    print("usage: pubpro [-b int] [-c float] [-e] [jsonl file]")
    sys.exit()

def main(jsonlFile,nbBulletins,rateCompare,doEval):
    if nbBulletins!=0:
        generate_bulletins(jsonlFile,nbBulletins)
    if rateCompare!=0:
        nb=compare_all_with_orig(jsonlFile,rateCompare)
        print(f"{nb} compared bulletins")
    if doEval:
        print("English")
        evaluate(jsonlFile,"en")
        print("Français")
        evaluate(jsonlFile,"fr")

if __name__ == '__main__':
    argv=sys.argv
    nb=len(argv)
    if nb==1:
        main(open("data/arpi-2021-train-1000.jsonl","r",encoding="utf-8"),0,0.01,False)
    else:
        # parse arguments
        nbBulletins=0
        rateCompare=0
        doEval=False
        jsonlFile=sys.stdin
        i=1
        while i<nb:
            argi=argv[i]
            if argi.startswith("-"):
                if argi=="-h": usage("")
                elif argi=="-b":
                    i+=1
                    if i==nb : usage("missing number after -b")
                    else: nbBulletins=int(argv[i])
                elif argi=="-c":
                    i+=1
                    if i==nb : usage("missing number after -c")
                    else: rateCompare=float(argv[i])
                elif argi=="-e":
                    doEval=True
                else: usage ("unknown argument:",argi)
            i+=1
        if i<nb:
            jsonlFile=open(argv[i],"r",encoding="utf-8")                    
        main(jsonlFile,nbBulletins,rateCompare,doEval)
    