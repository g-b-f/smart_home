import argparse
import asyncio
import sys
from datetime import datetime

import flask
from apscheduler.schedulers.asyncio import (
    AsyncIOScheduler,  # type: ignore[import-untyped]
)
from hypercorn.asyncio import serve
from hypercorn.config import Config as HypercornConfig

import lighting_routines as Routine
from periodic_tasks import periodic_light_check
from utils import get_logger, mutable_globals, config_to_bool_op, format_time

logger = get_logger(__name__)
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


@app.route("/config", methods=["POST"])
async def config():
    request_data = flask.request.get_json() or {}
    logger.debug(request_data)
    valid_requests = request_data.keys() & mutable_globals.data.keys()
    if not valid_requests:
        logger.warning("No valid config options provided in request\n%s", request_data)
        return "No valid config options provided", 400
    
    for key, value in request_data.items():
        assert isinstance(key, str)
        if key in mutable_globals:

            if key == "last_sleep":
                try:
                    from_iso = datetime.fromisoformat(value)
                    mutable_globals.last_sleep = from_iso
                    logger.info("Updating last_sleep to %s", format_time(from_iso))
                except ValueError:
                    logger.warning("Invalid datetime format for last_sleep: %s", value)
                    return "Invalid datetime format for last_sleep, expected ISO format", 400
                except Exception as e:
                    logger.warning("Error updating last_sleep: %s", e)
                    return f"Error updating last_sleep: {e}", 500
                continue

            mut_key = key.replace("_", " ")
            try:
                op = config_to_bool_op(value)
                old_value = mutable_globals[key]
                new_value = op(old_value, key)
                mutable_globals[key] = new_value

                if len(valid_requests) == 1:
                    return f"{mut_key} was {old_value}, now {new_value}", 200
            except ValueError as e:
                logger.warning("Invalid value for %s: %s", key, value)
                return str(e), 400
        else:
            logger.warning("Unknown config option: %s", key)        
    

    return f"Updated {len(valid_requests)} config options", 200



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
        config.accesslog = get_logger("hypercorn.access", level="WARNING")
        config.errorlog = get_logger("hypercorn.error", level="WARNING")

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
            mutable_globals.visitor_present = True
            logger.info("Visitor mode enabled: Wake-up routines are disabled.")
        else:
            mutable_globals.visitor_present = False
        asyncio.run(start())
    except KeyboardInterrupt:
        logger.info("Application shut down by user.")

if __name__ == "__main__":
    main()
