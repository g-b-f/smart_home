import argparse
import asyncio
import os

import pywizlight

from wrappers.bulb_wrapper import Bulb

if os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

parser = argparse.ArgumentParser(description="Control smart bulb")
parser.add_argument("-t", "--temp", help="Color temperature to set", type=int)
parser.add_argument("-b", "--brightness", help="Brightness to set", type=int)
args = parser.parse_args()

def bulb_control():
    del pywizlight.wizlight.__del__
    if args.temp is None and args.brightness is None:
        parser.error("must provide at least one of --temp or --brightness")
    bulb = Bulb()
    bulb.turn_on(brightness=args.brightness, colortemp=args.temp)

if __name__ == "__main__":
    bulb_control()