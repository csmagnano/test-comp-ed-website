"""
Pulls any new events from subscribed calendars and creates trainings for each of them. 

CURRENTLY UNTESTED
"""

from importlib import import_module
from pathlib import Path
from util import *
import requests
import icalendar as ic
import pytz
EST = pytz.timezone("US/Eastern")


# error flag
error = False

# output citations file
output_loc = "_trainings/"

log()

log("Getting calendar events")

# master list of sources
rc_cal = "https://www.trumba.com/calendars/IT.ics"
ccb_cal = "https://computationalbiomed.hms.harvard.edu/?post_type=tribe_events&ical=1&eventDisplay=list"
countway_cal = "https://libcal.countway.harvard.edu/ical_subscribe.php?src=p&cid=9718&cat=41819,41820"
sources = [rc_cal, ccb_cal, countway_cal]

trainings = []
# loop through source calendars
for index, source in enumerate(sources):
    log(f"Processing calendar {index + 1} of {len(sources)}, {label(source)}")

    ccal = ic.Calendar.from_ical(requests.get(source).text)

    for component in ccal.walk():
        if component.name == "VEVENT":
            training = {}
            for item in component:
                if item == "VEVENT":
                    continue
                name = item
                val = ""
                if item == "UID":
                    training["_id"] = val.decode("utf-8").replace('\r\n', '\n').strip()
                if item.startswith("DT"):
                    dt = component[item].dt
                    val = dt.astimezone(EST).strftime('%c %Z')
                else:
                    try:
                        val = component.decoded(item)
                        if isinstance(val,bytes):
                        val = val.decode("utf-8").replace('\r\n', '\n').strip()
                    except AssertionError:
                        val = component[item].to_ical().decode("utf-8").replace('\r\n', '\n').strip()
                training[name] = val
            trainings.append(training)


log()

log("Saving updated dates")


# save new citations
try:
    save_data(output_file, trainings)
except Exception as e:
    log(e, level="ERROR")
    error = True


# exit at end, so user can see all errors in one run
if error:
    log("Error(s) occurred above", level="ERROR")
    exit(1)
else:
    log("All done!", level="SUCCESS")

log("\n")
