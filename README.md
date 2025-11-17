# Smart Home control


## Todo list

Change temp on switch

- refactor state checking from lines 109-121 in `bulb_wrapper.py` into function 
- use that function in `set_temp_on_switch()` in `lighting_routines.py`
- if light is reachable but wasn't before, change temp using `utils.get_colourtemp_for_time()`
- figure out something involving globals
