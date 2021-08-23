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
periods =["today","tonight","day_2","day_2_night"]
periodNames = {
    "today":      {"en":"Today",   "fr":"Aujourd'hui"},
    "tonight":    {"en":"Tonight", "fr":"Ce soir et cette nuit"},
    "day_2":      {"en":"%A","fr":"Demain"},
    "day_2_night":{"en":"%A night","fr":"Demain soir et nuit"},
}

def get_period_name(dt,period,lang):
    if period.startswith("day_2"):
        locale.setlocale(locale.LC_ALL,"en_US" if lang=="en" else "fr_FR")
        return dt.strftime(periodNames[period][lang])
    return periodNames[period][lang]

##  table 5.3
time_periods = [
    ( 0, 3,"after midnight","après minuit"),
    ( 4, 6,"before morning","avant le matin"),
    ( 0, 6,"over night",    "dans la nuit"),
    ( 6, 9,"early morning", "tôt le matin"),
    ( 9,12,"late morning",  "tard le matin"),
    (11,13,"near noon",     "vers midi"),
    ( 6,12,"in the morning","le matin"),
    (12,15,"early afternoon","tôt l'après-midi" ),
    (15,18,"late afternoon", "tard l'après-midi"),
    (12,18,"in the afternoon","l'après-midi"),
    (18,21,"early evenig",    "tôt le soir" ),
    (21,24,"late evening",    "tard le soir"),
    (18,24,"in the evening",  "le soir"),
]


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
    
    