import os
import sys
from dotenv import load_dotenv
import requests
import logging

from reading.Reading import Reading
from display.Display import Display

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
API_URL = os.environ.get("WEATHERVANE_API_URL")

r = requests.get(url= API_URL)
data = r.json()
reading = Reading(data)
reading.get_changes_and_save()
display = Display(reading)

try:
    # If dev arg passed, skip everything else and just draw_reading in dev mode
    if sys.argv[1] == "dev":
        display.draw_reading(True)
    else:
        display.init_display()
        display.draw_reading(False)
        display.sleep(False)
        display.cleanup()
    
    sys.exit()

except IOError as e:
    logger.error(e)