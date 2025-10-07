import flask
from pywizlight import wizlight, PilotBuilder
import logging
import asyncio
logging.basicConfig(level=logging.WARNING)

# Store connection details instead of the object
LIGHT_IP = "192.168.1.100"
LIGHT_PORT = 38899
LIGHT_MAC = "cc408525d286"

# https://sleep.urbandroid.org/docs/services/automation.html#events
TRACKING_STARTED = "sleep_tracking_started"
TRACKING_STOPPED = "sleep_tracking_stopped"
ALARM_START = "alarm_alert_start"
ALARM_SNOOZED = "alarm_snooze_clicked"
ALARM_DISMISSED = "alarm_alert_dismiss"
BEDTIME_NOTIFICATION = "time_to_bed_alarm_alert"




app = flask.Flask(__name__)


async def turn_off_light():
    """turn off the light"""
    light = wizlight(LIGHT_IP, port=LIGHT_PORT, mac=LIGHT_MAC)
    await light.turn_off()

async def bedtime():
    """sset the light to a dim, warm color"""
    light = wizlight(LIGHT_IP, port=LIGHT_PORT, mac=LIGHT_MAC)
    await light.turn_on(PilotBuilder(brightness=10, rgb=(255, 96, 0)))

async def wake_up(total_time=60, time_step=0.1):
    """gradually brighten the light over total_time seconds"""
    light = wizlight(LIGHT_IP, port=LIGHT_PORT, mac=LIGHT_MAC)
    start = 2200
    end = 6500
    temp_step = (end - start) / (total_time / time_step)
    
    for i in range(int(total_time/time_step)):
        temp = int(start + temp_step * i)
        brightness = int(1 + (99 * i) / total_time)
        await light.turn_on(PilotBuilder(brightness=brightness, colortemp=temp))
        await asyncio.sleep(time_step)

# point to http://192.168.1.110:5000/sleep
@app.route("/sleep", methods=["POST"])
def sleep():
    logging.debug(flask.request.json)
    request_data = flask.request.json or {}
    event = request_data.get("event")
    if event == TRACKING_STARTED:
        logging.info("Turning off light")
        asyncio.run(turn_off_light())
        return "OK", 200
    elif event == ALARM_START:
        logging.info("waking up")
        asyncio.run(wake_up())
        return "OK", 200
    elif event == BEDTIME_NOTIFICATION:
        logging.info("bedtime")
        asyncio.run(bedtime())
        return "OK", 200
    else:
        return "Unknown event", 400


app.run(host="0.0.0.0")