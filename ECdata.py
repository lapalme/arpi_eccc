## information that should come from a database or an text file
import locale
###   global header information
forecastAreas = {
    "FPTO11":{"en":"Southern Ontario and the National Capital Region",
              "fr":"le sud de l'Ontario et la région de la capitale nationale"},
    "FPTO12":{"en":"Northern Ontario",    "fr":"le nord de l'Ontario"},
    "FPTO13":{"en":"Far Northern Ontario","fr":"l'extrême nord de l'Ontario"},
    "FPCN71":{"en":"Western Quebec",      "fr":"l'ouest du Québec"},
    "FPCN73":{"en":"Central Quebec",      "fr":"le centre du Québec"},
    "FPCN74":{"en":"Western Quebec",      "fr":"l'est du Québec"},
}

def get_forecast_area(code,lang):
    return forecastAreas[code][lang]

### periods
periods =["today","tonight","tomorrow","tomorrow_night"]
periodNames = {
    "today":      {"en":"Today",   "fr":"Aujourd'hui"},
    "tonight":    {"en":"Tonight", "fr":"Ce soir et cette nuit"},
    "tomorrow":      {"en":"%A","fr":"%A"},
    "tomorrow_night":{"en":"%A night","fr":"%A soir et nuit"},
}

def get_period_name(dt,period,lang):
    if period.startswith("tomorrow"):
        locale.setlocale(locale.LC_ALL,"en_US" if lang=="en" else "fr_FR")
        return dt.strftime(periodNames[period][lang])
    return periodNames[period][lang]

##  table 5.3
time_periods = [
    ( 0, 3,{"en":"after midnight","fr":"après minuit"}),
    ( 4, 6,{"en":"before morning","fr":"avant le matin"}),
    ( 0, 6,{"en":"over night","fr":"dans la nuit"}),
    ( 6, 9,{"en":"early morning","fr":"tôt le matin"}),
    ( 9,12,{"en":"late morning","fr":"tard le matin"}),
    (11,13,{"en":"near noon","fr":"vers midi"}),
    ( 6,12,{"en":"in the morning","fr":"le matin"}),
    (12,15,{"en":"early afternoon","fr":"tôt l'après-midi"} ),
    (15,18,{"en":"late afternoon","fr":"tard l'après-midi"}),
    (12,18,{"en":"in the afternoon","fr":"l'après-midi"}),
    (18,21,{"en":"early evening","fr":"tôt le soir"} ),
    (23,24,{"en":"near midnight", "fr":"vers minuit"}),
    (21,24,{"en":"late evening","fr":"tard le soir"}),
    (18,24,{"en":"in the evening","fr":"le soir"}),
]

def get_time_period_name(h,lang):
    h=h%24
    for (begin,end,expr) in time_periods:
        if begin<=h and h<end:
            return expr[lang]
    return ""

# e | nil | n | ne | nw | w | ely | nly | nely | nwly | wly | sly| sely | swly | sly | sely | sw | vrbl
wind_directions = {
    "e":    {"en":"east",         "fr":"de l'est",          "deg":90},
    "n":    {"en":"north",        "fr":"du nord",           "deg":0},
    "ne":   {"en":"northeast",    "fr":"du nord-est",       "deg":45},
    "nw":   {"en":"northwest",    "fr":"du nord-ouest",     "deg":315},
    "w":    {"en":"west",         "fr":"de l'ouest",        "deg":290},
    "ely":  {"en":"easterly",     "fr":"secteur est",       "deg":90},
    "nly":  {"en":"northerly",    "fr":"secteur nord",      "deg":0},
    "nely": {"en":"northeasterly","fr":"secteur nord-est",  "deg":45},
    "nwly": {"en":"northwesterly","fr":"secteur nord-ouest","deg":315},
    "wly":  {"en":"westerly",     "fr":"secteur ouest",     "deg":270},
    "sly":  {"en":"southerly",    "fr":"secteur sud",       "deg":180},
    "sely": {"en":"southeasterly","fr":"secteur sud-est",   "deg":135},
    "swly": {"en":"southwesterly","fr":"secteur sud-ouest", "deg":225},
    "sly":  {"en":"southerly",    "fr":"secteur sud",       "deg":180},
    "se":   {"en":"southeast",    "fr":"du sud-est",        "deg":135},
    "s":    {"en":"south",        "fr":"du sud",            "deg":180},
    "sw":   {"en":"southwest",    "fr":"du sud-ouest",      "deg":225},
    # "vrbl": {"en":"variable",     "fr":"variable"},
}

# find the difference between compass direction differences
# adapted from https://www.mrexcel.com/board/threads/compass-direction-differences.213199
def dir_diff(dir1,dir2):
    dir1=wind_directions[dir1]["deg"]
    dir2=wind_directions[dir2]["deg"]
    if dir1 >180 : dir1-=180
    else: dir1+=180
    if dir2 >180 : dir2-=180
    else: dir2+=180
    return abs(dir1-dir2)

## UV_index values: info taken from
#  https://www.canada.ca/en/environment-climate-change/services/weather-health/uv-index-sun-safety/about.html
#      Low (0-2), Moderate (3-5), High (6-7), Very High (8-10), and Extreme (11+)
uv_ranges= [(2,   {"en":"low",                     "fr":"bas"}), 
            (5,   {"en":"moderate",                "fr":"modéré"}), 
            (7,   {"en":"high",                    "fr":"élevé"}), 
            (10,  {"en":"very high",               "fr":"très élevé"}), 
            (1000,{"en":"extreme",                 "fr":"extrême"})
           ]
    
 
warnings = {
    "air_arctique": {"en":"artic outflow","fr":"air arctique"},
    "blizzard": {"en":"blizzard","fr":"blizzard"},
    "bourrasques_neige": {"en":"snow qualls","fr":"bourrasques de neige"},
    "brouillard": {"en":"fog","fr":"brouillard"},
    "bruine_verglacante": {"en":"freezing drizzle","fr":"bruine verglacante"},
    "chaleur": {"en":"heat","fr":"chaleur"},
    "chaleur_extreme": {"en":"extreme heat","fr":"chaleur extrême"},
    "chaleur_humidite": {"en":"high heat and humidiy","fr":"chaleur et humidité"},
    "chasse_poussiere": {"en":"blowind dust","fr":"chasse poussière"},
    "coup_vent": {"en":"gale","fr":"coups de vent"},
    "divers": {"en":"weather warning","fr":"divers"},
    "embrun_verglacant": {"en":"freezing spray","fr":"embrun verglaçant"},
    "froid_extreme": {"en":"extreme cold","fr":"froid extrême"},
    "froid_intense": {"en":"wind chill","fr":"froid intense"},
    "gel_general": {"en":"frost","fr":"gel général"},
    "gel_sol": {"en":"groud frost","fr":"gel au sol"},
    "grele": {"en":"hail storm","fr":"grêle"},
    "gresil": {"en":"ice pellets","fr":"grésil"},
    "humidex": {"en":"humidex","fr":"humidex"},
    "ligne_grain": {"en":"squall line","fr":"ligne de grain"},
    "neige": {"en":"snow","fr":"neige"},
    "neige_abondante": {"en":"heavy snow","fr":"neige abondante"},
    "neige_abondante_poudrerie": {"en":"heavy snow and blowing snow","fr":"neige abondante et poudrerie"},
    "neige_gresil": {"en":"snow and ice pellets","fr":"neige et grésil"},
    "neige_poudrerie": {"en":"snow and blowing snow","fr":"neige et poudrerie"},
    "nil": {"en":"nil","fr":"nil"},
    "niveau_eleve_eau": {"en":"high water level","fr":"niveau élevé d'eau"},
    "onde_tempete": {"en":"storm surge","fr":"onde de tempête"},
    "orage_marine": {"en":"orage_marine","fr":"orage maritime"},
    "orage_violent": {"en":"severe thunderstorm","fr":"orage violent"},
    "ouragan": {"en":"hurrican","fr":"ouragan"},
    "pluie_abondante": {"en":"heavy rain","fr":"pluie abondante"},
    "pluie_bruine_verglacante": {"en":"freezing (rain or drizzle)","fr":"pluie bruine verglaçante"},
    "pluie_verglacante": {"en":"freezing rain","fr":"pluie verglaçante"},
    "poudrerie": {"en":"blowing snow","fr":"poudrerie"},
    "qualite_air": {"en":"air quality","fr":"qualité de l'air"},
    "refroidissement_soudain": {"en":"temperature drop","fr":"refroidissement soudain"},
    "sante_publique": {"en":"air quality and health","fr":"santé publique"},
    "smog": {"en":"smog","fr":"smog"},
    "special_marine": {"en":"marine special","fr":"spécial_maritime"},
    "tempete_hivernale": {"en":"winter storm","fr":"tempête hivernale"},
    "tempete_tropicale": {"en":"tropical storm","fr":"tempête tropicale"},
    "tornade": {"en":"tornado","fr":"tornade"},
    "trombe_marine": {"en":"waterspout","fr":"trombe marine"},
    "vague_chaleur": {"en":"heat wave","fr":"vague de chaleur"},
    "vague_froid": {"en":"cold wave","fr":"vague de froid"},
    "vents_marine": {"en":"vents_marine","fr":"vents maritimes"},
    "vents_suetes": {"en":"Suetes winds","fr":"vents suètes"},
    "vents_tempete": {"en":"storm","fr":"vents de tempete"},
    "vents_violents": {"en":"strong winds","fr":"vents violents"},
    "wreckhouse": {"en":"Wreckhouse winds","fr":"wreckhouse"},
}

precipitation_types = {
    "averses":{"en":"showers","fr":"averses"},
    "averses_neige":{"en":"flurries","fr":"averses de neige"},
    "averses_neige_fondante":{"en":"wet flurries","fr":"averses de neige fondante"},
    "blizzard":{"en":"blizzard","fr":"blizzard"},
    "bourrasques_neige":{"en":"snow squalls","fr":"bourrasques de neige"},
    "bruine":{"en":"drizzle","fr":"bruine"},
    "bruine_verglacante":{"en":"freezing drizzle","fr":"bruine verglaçante"},
    "cristaux_glace":{"en":"ice crystals","fr":"cristaux de glace"},
    "grele":{"en":"hail","fr":"grêle"},
    "gresil":{"en":"ice pellets","fr":"grésil"},
    "neige":{"en":"snow","fr":"neige"},
    "neige_fondante":{"en":"wet snow","fr":"neige fondante"},
    "orages":{"en":"thunderstorm","fr":"orages"},
    "pluie":{"en":"rain","fr":"pluie"},
    "pluie_verglacante":{"en":"freezing rain","fr":"pluie verglaçante"},
    "poudrerie":{"en":"blowing snow","fr":"poudrerie"},
}
   