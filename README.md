# A prototype text generator for Weather Bulletins

This project was prompted by an exercise suggested by **Environment and Climate Change Canada** (ECCC) in the context of the [Industrial Problem Solving Workshop 2021](http://crm.umontreal.ca/probindustrielsEn2021/index.php/eccc-eng/). Its goal was to develop a weather bulletin generator using a neural approach from the information contained in the Meteocode, an specialized data format developed by ECCC.

Before the workshop, Guy Lapalme and Fabrizio Gotti created a [jsonl](https://jsonlines.org) version of more than 200K bulletins made available in MeteoCode by ECCC. They also developed an API for managing time zones and for evaluation using the BLEU metric. They are described in [this document](https://docs.google.com/document/d/1pWlu6HgMO8CztO_x4OpW7X2ItaWxJi5I2hMgCg4QbyM/edit#).

During the workshop, a neural text generator was developed only for temperature.

Before the workshop, Guy Lapalme intended to develop an alternative rule-based approach to the problem to serve as baseline, but time constraints in the workshop did not allow such comparisons.

After the workshop, Guy Lapalme decided to pursue the development in Python of a generator of complete bulletins in both French and English. He also made the display of its output more easily comparable with the original bulletin. For the generator, he also wanted to use this exercise as a use-case of [jsRealB](https://github.com/rali-udem/jsRealB), a bilingual text realizer that he has been maintaining over the last years.

But, as a first step, Guy Lapalme decided to simply rely on Python string manipulation and formatting. This explain why some sentences are somewhat awkward.

## Program call

	pubpro [-b int] [-c float] [-e] jsonl_file

where
	
	-b int  : number of full bulletins that are generated
	-c float: proportion of bulletins that are generated
	-e      : perform BLEU evaluation

## Source Programs

* `pubpro.py` : main program that drives the whole system
* `ECdata.py` : linguistic information about weather systems
* `forecast.py` : generate text for different aspects of the Meteocode
* `jsRealBclass.py` : Python interface to jsRealB (currently not used)
* `Meteocode.py` : Class that interface the json API of the Meteocode
* `ppJson.py`  : compact pretty-print of a json structure (useful for debugging)
* in the `arpi_eccc` directory 
 
	*  `nlg_evaluation.py` : BLEU evaluation of the results
	*  `timeranges.txt` : data indicating the time zone shift for a given type of bulletin
	* `utils.py` : utilities functions for dealing with time zones
* in the `jsRealB` directory : tools for interfacing with the jsRealB text realizer in JavaScript 


## Bulletins in json (in the `data` directory)
* `arpi-2021-train-1.jsonl`    : pretty-printed version of a json entry
* `arpi-2021-train-10.jsonl`   : 10 first lines of the train corpus
* `arpi-2021-train-1000.jsonl`  : 1000 first lines of the train corpus
* `Fields.md` : description of the fields of Meteocode

  