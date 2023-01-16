#!/bin/env python3
import argparse
import csv
import datetime
import json
import os
import pprint
import pytz
import sys
import time


parser = argparse.ArgumentParser(
                    prog = 'fit-import',
                    description = 'Converts Fitbit data for use with CSVTool')

parser.add_argument('-d', '--date')      # option that takes a value
parser.add_argument('-o', '--rhr-only', action='store_true', default=False)
parser.add_argument('-f', '--file-number', type=int, default=1)

args = parser.parse_args()
if args.date is not None:
  df_date=args.date
else:
  print("Must specify date.")
  sys.exit(1)

with open("./Physical Activity/heart_rate-2015-06-%s.json" % df_date) as json_file:
  heart_rate = json.load(json_file)

with open('./Physical Activity/steps-2015-06-09.json') as json_file:
  steps = json.load(json_file)

#with open('./Physical Activity/steps-2015-04-10.json') as json_file:
#  steps = json.load(json_file) + steps

with open('./Physical Activity/distance-2015-06-09.json') as json_file:
  distance = json.load(json_file)

with open('./Physical Activity/altitude-2015-06-09.json') as json_file:
  floors = json.load(json_file)


# Initalize empty objects.
out_dict = {}
hrvals = []

# Date format

fb_json_date_format = "%m/%d/%y %H:%M:%S"

# FIT Offset from UnixTime AND ADDITIONAL 365 DAYS OFFSET!
FIT_EPOCH_OFFSET = 631065600+31536000

date_time = datetime.datetime(2015,6,int(df_date),4,0,0)
start_ts = int(time.mktime(date_time.timetuple()))
garmin_start_ts = start_ts-FIT_EPOCH_OFFSET
garmin_start_ts_not_utc = garmin_start_ts + int(pytz.timezone("US/Eastern").utcoffset(date_time).total_seconds())

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
        if ts in out_dict:
          out_dict[ts].update( {"heartRate": emp['value']['bpm']})
        else:
          out_dict[ts] = {"heartRate": emp['value']['bpm']}


seven_day_avg = 0
hr_samples = 0
if args.rhr_only:
    rhr = []
    with open("./rhr-stats.json") as rhr_file:
        rhr = json.load(rhr_file)
    process_hr()
    daily_rhr = int(min(hrvals))
    rhr.append({ "dateTime": "2015-06-%s" % df_date, "rhr": daily_rhr })
    with open("./rhr-stats.json", "w") as jsonFile:
        json.dump(rhr, jsonFile)
    sys.exit(0)
else:
    with open("%s/rhr-stats.json" % os.environ.get('HOME')) as rhr_file:
        rhr = json.load(rhr_file)
    today = datetime.datetime.strptime("2015-06-%s" % df_date, "%Y-%m-%d")
    seven_days = today - datetime.timedelta(days=7)
    today_ts = today.timestamp()
    seven_day_ts = seven_days.timestamp()
    rhr_json_date_format = "%Y-%m-%d"
    for samples in rhr:
         dt_object = datetime.datetime.strptime(samples['dateTime'], rhr_json_date_format)
         ts = int(dt_object.timestamp())
         if ts > seven_day_ts and ts < today_ts:
           seven_day_avg += int(samples['rhr'])
           hr_samples += 1

file_id_number = args.file_number


# Counter variable used for writing
# headers to the CSV file
count = 0
# Writing headers of CSV file
header = [ "Type","Local Number","Message","Field 1","Value 1","Units 1","Field 2","Value 2","Units 2","Field 3","Value 3","Units 3", "Field 4","Value 4","Units 4","Field 5","Value 5","Units 5","Field 6","Value 6","Units 6" ]

# Write required data
file_id_def = [ "Definition","0","file_id","serial_number","1",None,"time_created",1,"","manufacturer","1","","product","1","","number","1","","type","1","" ]
dev_inf_def = [ "Definition","1","device_info","timestamp","1",None,"serial_number","1",None,"manufacturer","1",None,"product","1",None,"software_version","1", None ]
sw_ver_def  = [ "Definition","2","software","version","1",None ]
s_inf_def   = [ "Definition","3","soft_info","field0","1",None,"field1","1",None,"field2","1",None ]
m_inf_def   = [ "Definition","4","monitoring_info","timestamp","1",None,"cycles_to_distance","2",None,"cycles_to_calories","2",None,"step_goal","2",None,"resting_metabolic_rate","1",None,"activity_type","2",None,"unk_enum","1",None ]
#m_inf_def   = [ "Definition","4","monitoring_info","timestamp","1",None,"local_timestamp","1",None,"cycles_to_distance","2",None,"cycles_to_calories","2",None,"step_goal","2",None,"resting_metabolic_rate","1",None,"activity_type","2",None,"unk_enum","1",None ]
m_def       = [ "Definition","6","monitoring","timestamp","1",None,"distance","1",None,"cycles","1",None,"activity_type","1",None ]
hr_def      = [ "Definition","7","monitoring","timestamp","1",None,"heart_rate","1",None ]
floor_def   = [ "Definition","8","monitoring","timestamp","1",None,"ascent","1",None ]
rhr_def     = [ "Definition","9","resting_heart_rate","timestamp","1",None,"seven_day_rhr","1",None,"daily_rhr","1",None ]


# Welness first
file_id_type = 32
file_id_data  = [ "Data","0","file_id","serial_number","3411930528",None,"time_created",garmin_start_ts_not_utc,None,"manufacturer","1",None,"garmin_product","3851",None,"number",file_id_number,None,"type",file_id_type,None ]
dev_info_data = [ "Data","1","device_info","timestamp",garmin_start_ts_not_utc,"s","serial_number","3411930528",None,"manufacturer","1",None,"garmin_product","3851",None,"software_version","11.16",None ]
sw_ver_data   = [ "Data","2","software","version","6.0",None ]
s_inf_data    = [ "Data","3","soft_info","field0","0",None,"field1","0",None,"field2","200",None ]
m_inf_data    = [ "Data","4","monitoring_info","timestamp",garmin_start_ts_not_utc,"s","cycles_to_distance","1.6198|2.4296","m/cycle","cycles_to_calories","0.047|0.1482","kcal/cycle","step_goal","10000|10000",None,"resting_metabolic_rate","1987","kcal / day","activity_type","6|0",None,None,None,None ]
#m_inf_data    = [ "Data","4","monitoring_info","timestamp",garmin_start_ts,"s","local_timestamp",garmin_start_ts_not_utc,"s","cycles_to_distance","1.6198|2.4296","m/cycle","cycles_to_calories","0.047|0.1482","kcal/cycle","step_goal","10000|10000",None,"resting_metabolic_rate","1987","kcal / day","activity_type","6|0",None,None,None,None ]



output_data = []
stepval = 0
distval = 0.0
local_to_utc_diff = garmin_start_ts - garmin_start_ts_not_utc

# There should be a steps timestamp every minute. If there's no reading, then the watch was not on the wrist.
for emp in steps:
  dt_object = datetime.datetime.strptime(emp['dateTime'], fb_json_date_format)
  ts = int(dt_object.timestamp())
  if ts >= start_ts and ts < start_ts+86400:
    stepval += int(emp['value'])
    dist = next((x for x in distance if x['dateTime'] == emp['dateTime']), None)
    distval += (int(dist['value'])/100.0) # centimeters to meters conversion.
    out_dict[ts] = { "distance": distval, "steps": stepval }

for emp in floors:
  dt_object = datetime.datetime.strptime(emp['dateTime'], fb_json_date_format)
  ts = int(dt_object.timestamp())
  if ts >= start_ts and ts < start_ts+86400:
    ascentval = int(emp['value'])/10.0 * 3.048 # 10 ft is 3.048 meters.
    if ts in out_dict:
      out_dict[ts].update({"floors": ascentval})
    else:
      out_dict[ts] = {"floors": ascentval}


process_hr()

# Final output stuff
for key in sorted(out_dict.keys()):
    if "steps" in out_dict[key].keys():
      output_data.append(["Data",6,"monitoring","timestamp",key-local_to_utc_diff-FIT_EPOCH_OFFSET, "s", "distance", "{0:.3f}".format(out_dict[key]['distance']), "m", "steps",int(out_dict[key]['steps']),"cycles","activity_type","6",None])
    if "heartRate" in out_dict[key].keys():
      output_data.append(["Data",7,"monitoring","timestamp",key-local_to_utc_diff-FIT_EPOCH_OFFSET, "s", "heart_rate",out_dict[key]['heartRate'],"bpm"])
    if "floors" in out_dict[key].keys():
      output_data.append(["Data",8,"monitoring","timestamp",key-FIT_EPOCH_OFFSET, "s", "ascent", "{0:.3f}".format(out_dict[key]['floors']),"m"])

# RHR Calc:
# Resting Heart Rate: This value is for the current day. Daily RHR is calculated using the lowest 30 minute average in a 24 hour period.
# 7-Day Average Resting Heart Rate: Some watches will display a 7-day average resting value which is the daily average resting heart rate over the last seven days. It is a rolling value.
day_rhr = int(min(hrvals))
print("Today's RHR: ", day_rhr)
seven_day_avg += day_rhr
seven_day_avg = int(seven_day_avg/7)


##### BEGIN OUTPUT SECTION
# create the csv writer object
wellness_filename = "new-wellness-2015-06-%s.csv" % df_date
wellness_data_file = open(wellness_filename, 'w')
wellness_writer = csv.writer(wellness_data_file)

sleep_filename = "sleep-2015-06-%s.csv" % df_date
sleep_data_file = open(sleep_filename, 'w')

# create the csv writer object
sleep_writer = csv.writer(sleep_data_file)


wellness_writer.writerow(header)
wellness_writer.writerow(file_id_def)
wellness_writer.writerow(file_id_data)
wellness_writer.writerow(dev_inf_def)
wellness_writer.writerow(dev_info_data)
wellness_writer.writerow(sw_ver_def)
wellness_writer.writerow(sw_ver_data)
wellness_writer.writerow(s_inf_def)
wellness_writer.writerow(s_inf_data)
wellness_writer.writerow(m_inf_def)
wellness_writer.writerow(m_inf_data)
wellness_writer.writerow(m_def)
wellness_writer.writerow(hr_def)
wellness_writer.writerow(floor_def)
wellness_writer.writerow(rhr_def)


# Sort and write out.
#output_data.sort(key= operator.itemgetter(4,1))
wellness_writer.writerows(output_data)
if hr_samples == 6:
  wellness_writer.writerow( [ "Data", "9","resting_heart_rate", "timestamp", garmin_start_ts+86000,None,"seven_day_rhr", seven_day_avg, None, "daily_rhr", day_rhr, None ] )
else:
  wellness_writer.writerow( [ "Data", "9","resting_heart_rate", "timestamp", garmin_start_ts+86000,None,"daily_rhr", day_rhr, None ] )
wellness_data_file.close()

# Sleep
sleep_writer.writerow(header)
file_id_def = [ "Definition","0","file_id","serial_number","1",None,"time_created",1,"","manufacturer","1","","product","1","","type","1","" ]
sleep_writer.writerow(file_id_def)
file_id_type = 49
file_id_data  = [ "Data","0","file_id","serial_number","3411930528",None,"time_created",garmin_start_ts,None,"manufacturer","1",None,"garmin_product","3851",None,"type",file_id_type,None ]
sleep_writer.writerow(file_id_data)


file_creator_def  = [ "Definition","1","file_creator","software_version",1,None ]
file_creator_data = [ "Data","1","file_creator","software_version","1116",None ]

sleep_event_def = [ "Definition","4","event","timestamp","1",None,"data","1",None,"event","1",None,"event_type","1",None ]

# Event data is in local time, timestamps are in UTC....
# TS = Jan 6 6:30 UTC, data Jan 5 23:30 UTC (Denver time in this case, so that lines up)
# sleep_event_sta = ["Data","4","event","timestamp","1041921000","s","data","1041895800",None,"event","74",None,"event_type","0",None]
# TS = Fri Jan  6 13:46:00 UTC 2023, data Fri Jan  6 06:46:00 UTC 2023
#sleep_event_stp = ["Data","4","event","timestamp","1041947160","s","data","1041921960",None,"event","74",None,"event_type","1",None]

sleep_start = garmin_start_ts+84600
sleep_start_local = sleep_start-local_to_utc_diff
sleep_stop = sleep_start + 25200
sleep_stop_local = sleep_start_local + 25200
sleep_event_sta = ["Data","4","event","timestamp",sleep_start,"s","data",sleep_start_local,None,"event","74",None,"event_type","0",None]
# TS = Fri Jan  6 13:46:00 UTC 2023, data Fri Jan  6 06:46:00 UTC 2023
sleep_event_stp = ["Data","4","event","timestamp",sleep_stop,"s","data",sleep_stop_local,None,"event","74",None,"event_type","1",None]


sleep_writer.writerow(file_creator_def)
sleep_writer.writerow(file_creator_data)
sleep_writer.writerow(dev_inf_def)
sleep_writer.writerow(dev_info_data)
sleep_writer.writerow(sleep_event_def)
sleep_writer.writerow(sleep_event_sta)
sleep_writer.writerow(sleep_event_stp)
#sleep_writer.writerows(output_data)
sleep_data_file.close()
