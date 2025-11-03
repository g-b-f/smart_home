import asyncio
import os
import sys

import flask

from lighting_routines import Routine
from utils import get_logger

logger = get_logger(__name__)

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
    logger.info(flask.request.json)
    request_data = flask.request.json or {}
    event = request_data.get("event")
    if event == TRACKING_STARTED:
        logger.info("Turning off light")
        asyncio.run(Routine.turn_off_light())
        if HIBERNATE_ON_SLEEP:
            logger.info("hibernating")
            os.system("shutdown.exe /h")
            sys.exit()
        return "OK", 200
    elif event == ALARM_START:
        logger.info("waking up")
        asyncio.run(Routine.wake_up())
        return "OK", 200
    elif event == BEDTIME_NOTIFICATION:
        logger.info("bedtime")
        asyncio.run(Routine.bedtime())
        return "OK", 200
    else:
        return "Unknown event", 200


app.run(host="0.0.0.0")
