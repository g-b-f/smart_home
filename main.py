import argparse
import asyncio
from bulb_wrapper import Bulb

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--temp", type=int)
parser.add_argument("-b", "--brightness", type=int)
args = parser.parse_args()

async def main():
    bulb = Bulb()
    await bulb.turn_on(brightness=args.brightness, colortemp=args.temp)
    del bulb

asyncio.run(main())
