# Documentation on the Meteocode fields
Information taken from *Météocode Coding standard Version 3.9.1* (Meteocode38.doc)
We only give frequently occurring values, refer to the document for  undocumented values. The original being in French, we give equivalent English terms after `=>`.

**Important**:
Most fields start with `start` and `end` which are given in *hours*. 
An *hour* expressed in Universal Coordinated Time (UTC). The hours are accumulated from “0” hour corresponding to 00Z of day 1 (UTC date) of the forecast; for example day 1 of the time zone EST is: [5..29[, day 2: [29..53[, day 3: [53..77[ ...]. Negative hours refer to historical data.

## `accum` : precipitation accumulation (sect 3.4.4, p. 22)
    accum: start end type code certainty value-start value-end?
        code : "additionnelle" | "partielle" | "totale" =>
               "additionnal" | "partial" | "total"
        certainty : "moins_de" | "plus_de" | "possible" | "pouvant_atteindre" | "pouvant_depasser" | "pres_de" =>
                    "less than" | "more than" | "possible" | "possibly reaching" | "possibly exceeding" | "near"

## `avert` : warning (section 3.4.5, p 24)
    avert : start end type status code
        type : "avertissement" | "avis" | "veille" =>  
               "warning" | "advisory" | "watch"
        status : "annule" | "baisse" | "emis" | "en_vigueur" | "fin" | "hausse" | "maintenu" | "mis_a_jour" | "nil" =>
                 "cancelled" | "downgraded" | "issued" | "in effect" | "ended" | "upgraded" | "continued" | "updated" | "nil"
        code : "air_arctique"| "blizzard" | "bourrasques_neige" |  "brouillard" | "bruine_verglacante" |
               "chaleur_extreme" | "chaleur_humidite" | "chasse_poussiere" | "coup_vent" | "divers" | 
               "embrun_verglacant" | "froid_extreme" | "froid_intense" | "gel_general" | "gel_sol" | 
               "grele" | "gresil" | "humidex" | "ligne_grain" | "neige" | "neige_abondante" | 
               "neige_abondante_poudrerie" | "neige_gresil" | "neige_poudrerie" | "nil" | "niveau_eleve_eau" | 
               "onde_tempete" | "orage_marine" | "orage_violent" | "ouragan" | "pluie_abondante" | 
               "pluie_bruine_verglacante" | "pluie_verglacante" | "poudrerie" | "qualite_air"|
               "refroidissement_soudain" | "sante_publique" | "smog" | "special_marine" | "tempete_hivernale" | 
               "tempete_tropicale" |  "tornade" | "trombe_marine" | "vague_chaleur" | "vague_froid" | "vents_marine"| 
               "vents_suetes" | "vents_tempete" | "vents_violents" | "wreckhouse"
               =>
               "artic outflow"| "blizzard" | "snow qualls" |  "fog" | "freezing drizzle" |
               "extreme heat" | "high heat and humidiy" | "blowind dust" | "gale" | "weather warning" | 
               "freezing spray" | "extreme cold" | "wind chill" | "frost" | "groud frost" | 
               "hail storm" | "ice pellets" | "humidex" | "squall line" | "snow" | "heavy snow" | 
               "heavy snow and blowing snow" | "snow and ice pellets" | "snow and blowing snow" | "nil" | "high water level" | 
               "storm surge" | "orage_marine" | "severe thunderstorm" | "hurrican" | "heavy rain" | 
               "freezing (rain or drizzle)" | "freezing rain" | "blowing snow" | "air quality"|
               "temperature drop" | "air quality and health" | "smog" | "marine special" | "winter storm" | 
               "tropical storm" |  "tornado" | "waterspout" | "heat wave" | "cold wave" | "vents_marine"| 
               "Suetes winds" | "storm" | "strong winds" | "Wreckhouse winds"

## `ciel` : cloud cover (sect 3.4.6, p. 28)
    ciel: start end neb-start neb-end {ceiling-height}
        neb-start,neb-end : cloud cover in tenths of cloud-cover at start and end time
        ceiling-height` : 1..10 (1 being low and 10 high)

## `climat_temp` : climatological data for temperature (sect 3.4.9, p 31)
    climat_temp : start end type value
        type : "max" | "min" | "moy" =>
               "max" | "min" | "average"
        value : degree in Celsius

## `indice_qa` : air quality index (sect 3.4.14, p 35)
    indice_qa : start end value
        value : 0..100 (float)

##  `indice_uv` _: UV index (sect 3.4.16, p 36)
    indice_uv : start end value
        value : float with one decimal

##  `niveau_neige` : level for solid precipitations
    niveau_neige : start end code value
        code   : type of the value
        value  : number of meters (rounded at 100) in altitude at which the precipitations start to solidify

## `pcpn` : precipitations (sect 3.4.18, p 37)
    pcpn : start end certainty code type intensity frequency exception?
        certainty : "certain" | "possible" | "risque" =>
                    "certain" | "possible" | "risk"
        code : "debut" | "debut_fin" | "exact" | "fin" =>
               "start" | "start_end" | "exact" | "end"
        type : "averses" | "averses_neige" | "averses_neige_fondante" | "blizzard" | 
               "bourrasques_neige" | "bruine" | "bruine_verglacante" | 
               "cristaux_glace" |"grele"| "gresil" | "neige" | "neige_fondante" | 
               "orages" | "pluie" | "pluie_verglacante" | "poudrerie" 
               =>
               "showers" | "flurries" | "wet flurries" | "blizzard" | 
               "snow squalls" | "drizzle" | "freezing drizzle" | 
               "ice crystals" |"hail"| "ice pellets" | "snow" | "wet snow" | 
               "thunderstorm" | "rain" | "freezing rain" | "blowing snow"
        intensity : "faible" | "fort" | "modere" | "nil" | "tres_faible" =>
                    "light" | "heavy" | "moderate" | *implicit* | "very light"
        frequency : "bref" | "continuel" | "frequent" | "occasionnel" | "peu" =>
                    "brief" | "continual" | "frequent" | "occasionnal" | "few"
        exception : embedded list of pcpn

## `prob`: precipitation probability (sect 3.4.20, p 41)
    prob : "seuil" value [start end prob]+
        value :  threshold (“seuil”) defining a probability of precipitation of a trace or more.
        prob : 0..100 percentage of probability

##  `rosee` : dew point (sect 3.4.24, p 43)
    rosee : start end trend value
         trend : "baisse" | "hausse" | "point_intermediaire" | "max" | "min" | "stationnaire" =>
                 "falling" | "rising" | "middle point" | "high" | "low" | "steady"
         value : int degree Celsius

## `temp` : temperature (sect 3.4.25, p 44)
    temp : start end trend value
         trend : "baisse" | "hausse" | "point_intermediaire" | "max" | "min" | "stationnaire" =>
                 "falling" | "rising" | "middle point" | "high" | "low" | "steady"
         value : int degree Celsius

##  `vents` : winds (sect 3.4.27, p 47)
    vents : start end direction modif? speed value exception?
         direction : "e" | "nil" | "n" | "ne" | "nw" | "w" | "ely" | "nly" | "nely" | "nwly" | 
                     "wly" | "sly"| "sely" | "swly" | "sly" | "sely" | "sw" | "vrbl"
                     =>
                     "e" | "nil" | "n" | "ne" | "nw" | "w" | "ely" | "nly" | "nely" | "nwly" | 
                      "wly" | "sly"| "sely" | "swly" | "sly" | "sely" | "sw" | "vrbl"
                     *cardinal points with "erly"*
         exception : start end excType excvalue (within a list)
             excType : "rafales" | "bourrasques" => "gust" | "squall"

## `visib` : visibility (sect 3.4.28, p 50)
    visib : start end type freq
        type : "bancs_brouillard" | "bancs_brouillard_glace" | "brouillard" | "brouillard_glace"|
                "brume" | "brume_seche" | "brumeux" | "brumeux_endroits" | "chasse_poussiere" | 
                "fumee" | "fumee_endroits" | "fumee_mer" | "pcpn" | "poudrerie" | "poudrerie_basse" |
                "poudrerie_endroits" | "poudrerie_haute_endroits" | "smog"
                =>
               "fog banks" | "ice fog banks" | "fog" | "brouillard_glace"|
                "mist" | "hazy" | "foggy" | "fog patches" | "blowing dust" | 
                "smoke" | "local smoke" | "see smoke" | "due to precipitation" | "blowind snow" | "drifting snow" |
                "local drifting snow" | "local blowing snow" | "smog"
        freq : "bref" | "continu" | "frequent" | "occasionnel" | "peu" =>
               "brief" | "continuous" | "frequent" | "occasionnal" | "low"
