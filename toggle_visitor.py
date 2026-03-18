from utils import mutable_globals

present = mutable_globals.visitor_present
mutable_globals.visitor_present = not present
print(f"visitor_present was {present}, now {not present}")

