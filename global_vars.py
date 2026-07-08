from datetime import time, timedelta

USE_BULB = True
USE_WLED = False

LOG_LEVEL = "INFO"
IS_VISITOR_PRESENT = False # turns off routines related to waking up

CHILL_START = time(22, 0) # 10:00 PM
EARLY_WAKE_TIME = time(6, 0) # 6:00 AM
LATE_WAKE_UP_TIME = time(10, 0) # 10:00 AM
EARLIEST_SLEEP_TIME = time(20, 0) # 8:00 PM

MINIMUM_SLEEP_LENGTH = timedelta(hours=7, minutes=30)

CHILL_COLOURTEMP = 2500
SUNRISE_COLOURTEMP = 3000
DAY_COLOURTEMP = 6500
SUNSET_COLOURTEMP = 3000
NIGHT_COLOURTEMP = 2000

WARM_COLOURTEMP = 2700
WARMER_COLOURTEMP = 2000
BEDTIME_COLORTEMP = 1320

MIN_COLORTEMP = 2200
MAX_COLORTEMP = 6500

ZENITH_WAYPOINTS = {
    0.0: 6500,    # Solar noon (Cool Daylight)
    60.0: 5500,   # Afternoon 
    85.0: 3500,   # Golden Hour
    90.0: 2700,   # Sunset (Warm White)
    96.0: 2000,   # Dawn/ Dusk
    # 108.0: 1800   # Astronomical Dusk / Night
    102.0: BEDTIME_COLORTEMP   # Night
}
# https://www.researchgate.net/publication/266389024_Dynamic_Lighting_System_for_Workplaces_at_Northern_Latitudes
# suggests something like:
zenith_to_temp = lambda zen: 4100 - 2500/ 2**((90-zen)/8.5)