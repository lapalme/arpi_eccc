## information that should come from a database or an text file
from arpi_eccc.utils import get_delta_with_utc, get_time_interval_for_period



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

        