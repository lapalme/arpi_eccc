import json,sys,re

from ppJson import ppJson
from genBulletin import forecast
from time import process_time

from arpi_eccc.nlg_evaluation import bleu_evaluation
from arpi_eccc.utils import get_nb_tokens, get_time_interval_for_period
from nltk.tokenize import word_tokenize

from levenshtein import compareLevenshtein

def countWords(input_filename):
    # read the bulletins and count words
    print(f"Reading all bulletins in {input_filename}", flush=True)

    nb_bulletins = 0
    nb_toks_english = 0
    nb_toks_french = 0
    with open(input_filename, 'rt', encoding='utf-8') as fin:
        for cur_line in fin:
            bulletin = json.loads(cur_line)
            nb_bulletins += 1
            nb_toks_english += get_nb_tokens(bulletin, 'en')
            nb_toks_french += get_nb_tokens(bulletin, 'fr')

    print(f"Read {nb_bulletins} bulletins. {nb_toks_english} English tokens, {nb_toks_french} French tokens.")
    print("\n\n")

def getSampleBulletin(input_filename):
    with open(input_filename, 'rt', encoding='utf-8') as fin:
        cur_line = next(fin)
        return json.loads(cur_line)

def getNumericTokens(toks):
    return [tok for period in toks 
             for sent in toks[period] 
                 for tok in sent if re.fullmatch(r"\b\d+(\.\d+)?\b",tok)]

def compareNT(refNT,jsrNT):
    (editDist,editOps)=compareLevenshtein(" ".join(jsrNT)," ".join(refNT),equals=lambda s1,s2:s1==s2)
    print("ref:",refNT)
    print("gen:",jsrNT)
    print("dist:%d score=%5.2f"%(editDist,editDist/len(refNT)))
    print(editOps)
    return editDist/len(refNT)

startTime=process_time()
def main():
    """A quick demo to show how to start this project."""
    if len(sys.argv) != 2:
        input_filename="/Users/lapalme/Documents/GitHub/arpi_eccc/data/arpi-2021-train-10.jsonl"
    else:
        input_filename = sys.argv[1]

    # countWords(input_filename)
    #
    # # show a sample bulletin
    # print("A sample bulletin:")
    # sample_bulletin=getSampleBulletin(input_filename)
    # ppJson(sys.stdout,sample_bulletin)
    # print('\n\n')
    #
    # # demonstrate what periods correspond to which time intervals in the data
    # bulletin_periods = sample_bulletin['en']['tok'].keys()
    # print(f"The sample bulletin has the following periods: {bulletin_periods}")
    # print(f"These periods correspond to the following time intervals in the weather data:")
    # for period in bulletin_periods:
    #     time_interval = get_time_interval_for_period(sample_bulletin, period)
    #     print(f"Period '{period}' corresponds to time interval [{time_interval[0]}, {time_interval[1]}] (in hours)")
    # print('\n\n')

    # # =============================================================================================
    # try and evaluate the jsRealB generation system for English
    ### make sure that a jsRealB server is started in a terminal, using the following call
    ###    node jsRealB/dist/jsRealB-server-dme.js ../data/weatherLexicon.js
    
    print("%6.2f :: Running jsRealB on :%s"%(process_time()-startTime,input_filename))
    
    reference   = []
    jsr_results = []
    lang = "en"
    numericDiffs=0
    
    with open(input_filename, 'rt', encoding='utf-8') as fin:
        for cur_line in fin:
            bulletin = json.loads(cur_line)
            reference.append(bulletin['en']["tok"])
            refNT=getNumericTokens(bulletin['en']["tok"])
            jsrTok={}
            bulletin_periods = bulletin['en']['tok'].keys()
            for period in bulletin_periods:
                (beginHour,endHour)=get_time_interval_for_period(bulletin, period)
                jsrSents=forecast(bulletin,"en","*title*",beginHour,endHour,"")
                jsrTok[period]=[word_tokenize(sent,{'en':'english','fr':'french'}[lang]) for sent in jsrSents]
            jsr_results.append(jsrTok)
            jsrNT=getNumericTokens(jsrTok)
            numericDiffs+=compareNT(refNT,jsrNT)
            if len(reference)%100==0:
                print("%6.2f :: %d %5.2f"%(process_time()-startTime,len(reference),numericDiffs/len(reference)))
            # if len(reference) >= 1000:
            #     break
    print("*** reference:%d"%len(reference))
    # ppJson(sys.stdout,reference)
    print("*** jsRealB results:%d"%len(jsr_results))
    # ppJson(sys.stdout,jsr_results)
    print("%6.2f ::*** numeric differences:%5.3f %5.2f"%(process_time()-startTime,numericDiffs,numericDiffs/len(reference)))
    # ...now we can evaluate jsRealB using the two lists created above.
    evaluation = bleu_evaluation(jsr_results, reference)
    for period in ['today', 'tonight', 'tomorrow', 'tomorrow_night']:
        if evaluation[period]!=-1:
            print(f"For bulletin period {period}, BLEU score is {evaluation[period]:.3f} on a scale from 0 to 1")
    print()
    print(f"Global score is {evaluation['global']:.3f}")


if __name__ == '__main__':
    main()
