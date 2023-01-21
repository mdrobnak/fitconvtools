#!/bin/env python3
import convutils
import csv
import datetime
import json
import os
import pprint
import pytz
import sys
import time

# Process arguments
args           = convutils.get_arguments()
full_date      = args.date
offset_ts_data = args.offset_ts_data

year         = full_date.split("-",3)[0]
month        = full_date.split("-",3)[1]
day_of_month = full_date.split("-",3)[2]

# Load data from files
filename_date = convutils.find_file(args.src_dir, full_date, day_of_month)
with open("%s/Physical Activity/heart_rate-%s.json" % (args.src_dir, full_date)) as json_file:
  heart_rate = json.load(json_file)

with open('%s/Physical Activity/steps-%s.json' % (args.src_dir, filename_date)) as json_file:
  steps = json.load(json_file)

with open('%s/Physical Activity/distance-%s.json' % (args.src_dir, filename_date)) as json_file:
  distance = json.load(json_file)

with open('%s/Physical Activity/altitude-%s.json' % (args.src_dir, filename_date)) as json_file:
  floors = json.load(json_file)

# Initalize empty objects and values
distval = 0.0
hrsamples = 0
hrvals = []
out_dict = {}
seven_day_avg = 0
stepval = 0

# FIT Offset from UnixTime AND ADDITIONAL 365 DAYS OFFSET!
FIT_EPOCH_OFFSET = 631065600+31536000

date_time = datetime.datetime(int(year),int(month),int(day_of_month),4,0,0)
start_ts = int(time.mktime(date_time.timetuple()))
garmin_start_ts = start_ts-FIT_EPOCH_OFFSET
garmin_start_ts_not_utc = garmin_start_ts + int(pytz.timezone("US/Eastern").utcoffset(date_time).total_seconds())
local_to_utc_diff = garmin_start_ts - garmin_start_ts_not_utc
fb_json_date_format = "%m/%d/%y %H:%M:%S"

def process_hr():
  hrcount = 0
  hrsum = 0

  for emp in heart_rate:
    if emp['value']['confidence'] != 0:
      dt_object = datetime.datetime.strptime(emp['dateTime'], fb_json_date_format)
      ts = int(dt_object.timestamp())
      if ts >= start_ts and ts < start_ts+86400:
        # Gather data for Resting Heart Rate calculation
        hrcount += 1
        hrsum += emp['value']['bpm']
        if (start_ts - ts) % 1800 == 0 and hrcount >= 150:
          hrvals.append(hrsum / hrcount)
          hrcount = 0
          hrsum = 0
        data_ts = ts - local_to_utc_diff if offset_ts_data else ts
        if data_ts in out_dict:
          out_dict[data_ts].update( {"heartRate": emp['value']['bpm']})
        else:
          out_dict[data_ts] = {"heartRate": emp['value']['bpm']}

if args.rhr_only:
    rhr = []
    with open("%s/rhr-stats.json" % os.environ.get('HOME')) as rhr_file:
        rhr = json.load(rhr_file)
    process_hr()
    daily_rhr = int(min(hrvals))
    rhr.append({ "dateTime": "%s" % full_date, "rhr": daily_rhr })
    with open("%s/rhr-stats.json" % os.environ.get('HOME'), "w") as jsonFile:
        json.dump(rhr, jsonFile)
    sys.exit(0)
else:
    with open("%s/rhr-stats.json" % os.environ.get('HOME')) as rhr_file:
        rhr = json.load(rhr_file)
    today = datetime.datetime.strptime("%s" % full_date, "%Y-%m-%d")
    seven_days = today - datetime.timedelta(days=7)
    today_ts = today.timestamp()
    seven_day_ts = seven_days.timestamp()
    rhr_json_date_format = "%Y-%m-%d"
    for samples in rhr:
         dt_object = datetime.datetime.strptime(samples['dateTime'], rhr_json_date_format)
         ts = int(dt_object.timestamp())
         if ts > seven_day_ts and ts < today_ts:
           seven_day_avg += int(samples['rhr'])
           hrsamples += 1

# Main processing loop
# There should be a steps timestamp every minute. If there's no reading, then the watch was not on the wrist.
for emp in steps:
  dt_object = datetime.datetime.strptime(emp['dateTime'], fb_json_date_format)
  ts = int(dt_object.timestamp())
  if ts >= start_ts and ts < start_ts+86400:
    stepval += int(emp['value'])
    dist = next((x for x in distance if x['dateTime'] == emp['dateTime']), None)
    distval += (int(dist['value'])/100.0) # centimeters to meters conversion.
    data_ts = ts - local_to_utc_diff if offset_ts_data else ts
    out_dict[data_ts] = { "distance": distval, "steps": stepval }

# Floor data is in local time. Ugh.
for emp in floors:
  dt_object = datetime.datetime.strptime(emp['dateTime'], fb_json_date_format)
  ts = int(dt_object.timestamp())
  if ts >= start_ts and ts < start_ts+86400:
    ascentval = int(emp['value'])/10.0 * 3.04 # 10 ft is 3.048 meters. Still a little too high. Try 3.04.
    data_ts = ts if offset_ts_data else ts + local_to_utc_diff # already in local time
    if ts in out_dict:
      out_dict[data_ts].update({"floors": ascentval})
    else:
      out_dict[data_ts] = {"floors": ascentval}

# HR calc is broken out so that we can do RHR JSON stuff.
process_hr()

# RHR Calc:
# Resting Heart Rate: This value is for the current day. Daily RHR is calculated using the lowest 30 minute average in a 24 hour period.
# 7-Day Average Resting Heart Rate: Some watches will display a 7-day average resting value which is the daily average resting heart rate over the last seven days. It is a rolling value.
day_rhr = int(min(hrvals))
print("Today's RHR: ", day_rhr)
seven_day_avg += day_rhr
seven_day_avg = int(seven_day_avg/7)

# Wellness
convutils.write_wellness(out_dict, full_date, offset_ts_data, garmin_start_ts, garmin_start_ts_not_utc, hrsamples, day_rhr, seven_day_avg, args.file_number)

# Sleep
convutils.write_sleep(full_date, garmin_start_ts, garmin_start_ts_not_utc, local_to_utc_diff)
