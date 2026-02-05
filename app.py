import asyncio
import sys
import argparse


import flask
from apscheduler.schedulers.asyncio import (
    AsyncIOScheduler,  # type: ignore[import-untyped]
)
from hypercorn.asyncio import serve
from hypercorn.config import Config as HypercornConfig

import lighting_routines as Routine
import utils
from periodic_tasks import periodic_light_check
import global_vars as gbl

logger = utils.get_logger(__name__)
logger.debug("beginning smart home app")

# https://sleep.urbandroid.org/docs/services/automation.html#events
TRACKING_STARTED = "sleep_tracking_started"
TRACKING_STOPPED = "sleep_tracking_stopped"
ALARM_START = "alarm_alert_start"
ALARM_SNOOZED = "alarm_snooze_clicked"
ALARM_DISMISSED = "alarm_alert_dismiss"
BEDTIME_NOTIFICATION = "time_to_bed_alarm_alert"

COLOR_TEMP_SYNC_INTERVAL = 60  # minutes

app = flask.Flask(__name__)

event_mappings = {
    TRACKING_STARTED: Routine.tracking_start,
    TRACKING_STOPPED: Routine.tracking_stopped,
    ALARM_START: Routine.wake_up,
    ALARM_SNOOZED: Routine.snooze,
    ALARM_DISMISSED: Routine.wake_up,
    BEDTIME_NOTIFICATION: Routine.bedtime,
}

# point to http://192.168.1.117:5000/sleep
@app.route("/sleep", methods=["POST"])
async def sleep():
    request_data = flask.request.get_json() or {}
    logger.debug(request_data)
    event = request_data.get("event")

    logger.info("Received sleep event: %s", event)

    if event in event_mappings:
        await event_mappings[event]()
        return "OK", 200
    else:
        logger.debug("unknown event: %s", event)
        return "Unknown event", 501 # 501: Not Implemented

@app.route("/test", methods=["POST"])
async def test():
    logger.info("test endpoint hit with args:\n%s", flask.request.get_json() or {})
    return "OK", 200

async def start():
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


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smart Home Lighting Controller")
    parser.add_argument(
        "--visitor",
        action="store_true",
        help="Indicate that a visitor is present, disabling wake-up routines.",
    )
    return parser.parse_args()


def main():
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        args = get_args()
        if args.visitor:
            utils.mutable_globals["visitor_present"] = True
            logger.info("Visitor mode enabled: Wake-up routines are disabled.")
        else:
            utils.mutable_globals["visitor_present"] = False
        asyncio.run(start())
    except KeyboardInterrupt:
        logger.info("Application shut down by user.")

if __name__ == "__main__":
    main()
