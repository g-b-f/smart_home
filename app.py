import flask
from pywizlight import wizlight, PilotBuilder, PilotParser
import logging
import asyncio
import os
import sys
from typing import Optional
from lighting_routines import Routine

logging.basicConfig(level=logging.INFO, datefmt="%H:%M:%S", format="%(asctime)s %(name)s - %(message)s")

# https://sleep.urbandroid.org/docs/services/automation.html#events
TRACKING_STARTED = "sleep_tracking_started"
TRACKING_STOPPED = "sleep_tracking_stopped"
ALARM_START = "alarm_alert_start"
ALARM_SNOOZED = "alarm_snooze_clicked"
ALARM_DISMISSED = "alarm_alert_dismiss"
BEDTIME_NOTIFICATION = "time_to_bed_alarm_alert"

HIBERNATE_ON_SLEEP = False

app = flask.Flask(__name__)

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


# point to http://192.168.1.117:5000/sleep
@app.route("/sleep", methods=["POST"])
def sleep():
    logging.info(flask.request.json)
    request_data = flask.request.json or {}
    event = request_data.get("event")
    if event == TRACKING_STARTED:
        logging.info("Turning off light")
        asyncio.run(Routine.turn_off_light())
        if HIBERNATE_ON_SLEEP:
            logging.info("hibernating")
            os.system("shutdown.exe /h")
            sys.exit()
        return "OK", 200
    elif event == ALARM_START:
        logging.info("waking up")
        asyncio.run(Routine.wake_up())
        return "OK", 200
    elif event == BEDTIME_NOTIFICATION:
        logging.info("bedtime")
        asyncio.run(Routine.bedtime())
        return "OK", 200
    else:
        return "Unknown event", 200


app.run(host="0.0.0.0")
