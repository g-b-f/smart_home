import flask
from pywizlight import wizlight, PilotBuilder
import logging
import asyncio
# logging.basicConfig(level=logging.INFO)

# Store connection details instead of the object
LIGHT_IP = "192.168.1.100"
LIGHT_PORT = 38899
LIGHT_MAC = "cc408525d286"

TRACKING_STARTED = "sleep_tracking_started"
TRACKING_STOPPED = "sleep_tracking_stopped"

app = flask.Flask(__name__)


# point to http://192.168.1.110:5000/sleep
async def turn_off_light():
    """Helper function to turn off the light in an async context"""
    light = wizlight(LIGHT_IP, port=LIGHT_PORT, mac=LIGHT_MAC)
    await light.turn_off()

@app.route("/sleep", methods=["POST"])
def sleep():
    logging.debug(flask.request.json)
    request_data = flask.request.json or {}
    match request_data.get("event"):
        case TRACKING_STARTED:
            logging.info("Turning off light")
            asyncio.run(turn_off_light())
            return "OK", 200
    return "OK", 200






app.run(host="0.0.0.0")