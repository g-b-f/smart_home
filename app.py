import asyncio
import sys
from datetime import datetime

import flask
from apscheduler.schedulers.asyncio import (
    AsyncIOScheduler,  # type: ignore[import-untyped]
)
from hypercorn.asyncio import serve
from hypercorn.config import Config as HypercornConfig

import global_vars as gbl
import lighting_routines as Routine
import utils

logger = utils.get_logger(__name__, level="DEBUG")
logger.debug("beginning smart home app")

# https://sleep.urbandroid.org/docs/services/automation.html#events
TRACKING_STARTED = "sleep_tracking_started"
TRACKING_STOPPED = "sleep_tracking_stopped"
ALARM_START = "alarm_alert_start"
ALARM_SNOOZED = "alarm_snooze_clicked"
ALARM_DISMISSED = "alarm_alert_dismiss"
BEDTIME_NOTIFICATION = "time_to_bed_alarm_alert"

COLOR_TEMP_SYNC_INTERVAL = 60  # minutes
I_HAVE_COMPANY = False


app = flask.Flask(__name__)

async def periodic_light_check():
    zen = utils.get_zenith()
    logger.debug("Current zenith: %f", zen)

# point to http://192.168.1.117:5000/sleep
@app.route("/sleep", methods=["POST"])
async def sleep():
    request_data = flask.request.get_json() or {}
    logger.debug(request_data)
    event = request_data.get("event")
    current_time = datetime.now().time()

    logger.info("Received sleep event: %s", event)

    if event == TRACKING_STARTED:
        await Routine.tracking_start()
        return "OK", 200

    elif event == TRACKING_STOPPED:
        if current_time > gbl.WAKE_UP_TIME:
            logger.debug(
                    "%s is greater than %s, turning on light",
                     current_time, gbl.WAKE_UP_TIME
                     )
            if not I_HAVE_COMPANY:
                await Routine.wake_up()
        else:
            logger.debug(
                    "%s is less than %s, turning on nightlight",
                    current_time, gbl.WAKE_UP_TIME
                    )

            await Routine.nightlight()
        return "OK", 200
    
    elif event == ALARM_START:
        await Routine.wake_up()
        return "OK", 200
    
    elif event == BEDTIME_NOTIFICATION:
        await Routine.bedtime()
        return "OK", 200
    elif event ==  ALARM_SNOOZED:
       await Routine.snooze():
       return "OK", 200
    else:
        logger.debug("unknown event: %s", event)
        return "Unknown event", 200

@app.route("/test", methods=["POST"])
async def test():
    logger.info("test endpoint hit with args:\n%s", flask.request.get_json() or {})
    return "OK", 200

async def main():
    scheduler = AsyncIOScheduler(timezone="Europe/London")
    scheduler.add_job(periodic_light_check, 'interval', minutes=COLOR_TEMP_SYNC_INTERVAL)
    
    logger.info("starting scheduler")
    scheduler.start()
    logger.debug("scheduler started")
    
    try:
        logger.debug("setting up server")
        config = HypercornConfig()
        config.bind = ["0.0.0.0:5000"] # Binds to all interfaces on port 5000
        config.accesslog = utils.get_logger("hypercorn.access", level="WARNING")
        config.errorlog = utils.get_logger("hypercorn.error", level="WARNING")

        logger.info("Starting Hypercorn ASGI server at http://%s", config.bind[0])
        await serve(app, config)
        logger.debug("finished serving")
    except Exception as e: # noqa: BLE001
        logger.info("exception %s", e) 
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
