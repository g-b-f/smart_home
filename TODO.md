# Todo list

Errors and logging

- Change all loggers to fit basicConfig
- wrap `Routine.turn_off()` in try/ except
- make wrappers throw same exceptions

Change temp on switch

- refactor state checking from lines 109-121 in `bulb_wrapper.py` into function 
- use that function in `set_temp_on_switch()` in `lighting_routines.py`
- if light is reachable but wasn't before, change temp using `utils.get_colourtemp_for_time()`
- figure out something involving globals

Fail gracefully wuhen unable to connect

- maybe use annotations on functions
- check for `.is_connected()`
- emit `logger.warning()` upon failure
- somehow convert class into ineffective version if unable to connect
    - replace `__get_atribute__`?

Add tests

- each of the sleep POST requests should call the appropriate routine
- routines should call the appropriate methods
- control flow continues when one of the objects is unable to connect

Refactor routines

- dictionary of methods
- or of objects/ classes
- if objects then could call other functions as appropriate
- regardless, as much stuff as possible should be abstracted away into config etc
