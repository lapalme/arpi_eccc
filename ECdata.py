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
