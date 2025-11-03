import asyncio
import os
import sys
import flask

from hypercorn.config import Config as hypercorn_Config
from hypercorn.asyncio import serve as hypercorn_serve
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from lighting_routines import Routine
import utils 

logger = utils.get_logger(__name__)

# https://sleep.urbandroid.org/docs/services/automation.html#events
TRACKING_STARTED = "sleep_tracking_started"
TRACKING_STOPPED = "sleep_tracking_stopped"
ALARM_START = "alarm_alert_start"
ALARM_SNOOZED = "alarm_snooze_clicked"
ALARM_DISMISSED = "alarm_alert_dismiss"
BEDTIME_NOTIFICATION = "time_to_bed_alarm_alert"

HIBERNATE_ON_SLEEP = False
COLOR_TEMP_SYNC_INTERVAL = 10  # minutes

app = flask.Flask(__name__)


async def periodic_light_check():
    zen = utils.get_zenith()
    logger.info("Current zenith: %f", zen)


# point to http://192.168.1.117:5000/sleep
@app.route("/sleep", methods=["POST"])
async def sleep():
    request_data = await flask.request.get_json() or {}
    logger.info(request_data)
    event = request_data.get("event")

    if event == TRACKING_STARTED:
        await Routine.tracking_start()
        return "OK", 200
    
    elif event == ALARM_START:
        await Routine.wake_up()
        return "OK", 200
    
    elif event == BEDTIME_NOTIFICATION:
        await Routine.bedtime()
        return "OK", 200
    
    else:
        return "Unknown event", 200


async def main():
    scheduler = AsyncIOScheduler(timezone="Europe/London")
    scheduler.add_job(periodic_light_check, 'interval', minutes=COLOR_TEMP_SYNC_INTERVAL)
    
    logger.info("starting scheduler")
    scheduler.start()
    
    try:
        bind = "0.0.0.0:5000" # Binds to all interfaces on port 5000
        config = hypercorn_Config()
        config.bind = [bind]
        logger.info("Starting Hypercorn ASGI server at http://%s", bind)
        await hypercorn_serve(app, config)
    finally:
        logger.info("Shutting down scheduler")
        scheduler.shutdown()

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application shut down by user.")