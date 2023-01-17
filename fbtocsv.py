import datetime
import time
import json
import csv
import operator
import pprint
import pytz

df_date="23"

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


wellness_filename = "wellness-2015-06-%s.csv" % df_date
wellness_data_file = open(wellness_filename, 'w')

# create the csv writer object
#wellness_writer = csv.writer(wellness_data_file, quoting=csv.QUOTE_ALL)
wellness_writer = csv.writer(wellness_data_file)

sleep_filename = "sleep-2015-06-%s.csv" % df_date
sleep_data_file = open(sleep_filename, 'w')

# create the csv writer object
sleep_writer = csv.writer(sleep_data_file)


# FIT Offset from UnixTime AND ADDITIONAL 365 DAYS OFFSET!
FIT_EPOCH_OFFSET = 631065600+31536000

date_time = datetime.datetime(2015,6,int(df_date),4,0,0)
start_ts = int(time.mktime(date_time.timetuple()))
garmin_start_ts = start_ts-FIT_EPOCH_OFFSET
garmin_start_ts_not_utc = garmin_start_ts + int(pytz.timezone("US/Eastern").utcoffset(date_time).total_seconds())

file_id_number = 1

# Date format

format = "%m/%d/%y %H:%M:%S"

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

# Welness first
file_id_type = 32
file_id_data  = [ "Data","0","file_id","serial_number","3411930528",None,"time_created",garmin_start_ts_not_utc,None,"manufacturer","1",None,"garmin_product","3851",None,"number",file_id_number,None,"type",file_id_type,None ]
dev_info_data = [ "Data","1","device_info","timestamp",garmin_start_ts_not_utc,"s","serial_number","3411930528",None,"manufacturer","1",None,"garmin_product","3851",None,"software_version","11.16",None ]
sw_ver_data   = [ "Data","2","software","version","6.0",None ]
s_inf_data    = [ "Data","3","soft_info","field0","0",None,"field1","0",None,"field2","200",None ]
m_inf_data    = [ "Data","4","monitoring_info","timestamp",garmin_start_ts_not_utc,"s","cycles_to_distance","1.6198|2.4296","m/cycle","cycles_to_calories","0.047|0.1482","kcal/cycle","step_goal","10000|10000",None,"resting_metabolic_rate","1987","kcal / day","activity_type","6|0",None,None,None,None ]
#m_inf_data    = [ "Data","4","monitoring_info","timestamp",garmin_start_ts,"s","local_timestamp",garmin_start_ts_not_utc,"s","cycles_to_distance","1.6198|2.4296","m/cycle","cycles_to_calories","0.047|0.1482","kcal/cycle","step_goal","10000|10000",None,"resting_metabolic_rate","1987","kcal / day","activity_type","6|0",None,None,None,None ]

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



output_data = []
stepval = 0
distval = 0.0
local_to_utc_diff = garmin_start_ts - garmin_start_ts_not_utc

# Loop over data
for emp in heart_rate:
  print(emp)
  if emp['value']['confidence'] != 0:
    dt_object = datetime.datetime.strptime(emp['dateTime'], format)
    ts = int(dt_object.timestamp())
    if ts >= start_ts and ts < start_ts+86400:
      output_data.append(["Data",7,"monitoring","timestamp",ts-local_to_utc_diff-FIT_EPOCH_OFFSET, "s", "heart_rate",emp['value']['bpm'],"bpm"])

for emp in floors:
  dt_object = datetime.datetime.strptime(emp['dateTime'], format)
  ts = int(dt_object.timestamp())
  if ts >= start_ts and ts < start_ts+86400:
    ascentval = int(emp['value'])/10.0 * 3.03
    print(emp['dateTime'],int(emp['value'])/10.0, ascentval)
    output_data.append(["Data",8,"monitoring","timestamp",ts-FIT_EPOCH_OFFSET, "s", "ascent", "{0:.3f}".format(ascentval),"m"])

for emp in steps:
  dt_object = datetime.datetime.strptime(emp['dateTime'], format)
  ts = int(dt_object.timestamp())
  if ts >= start_ts and ts < start_ts+86400:
    stepval += int(emp['value'])
    dist = next((x for x in distance if x['dateTime'] == emp['dateTime']), None)
    distval += (int(dist['value'])/100.0) # centimeters to meters conversion.
    print(emp)
    output_data.append(["Data",6,"monitoring","timestamp",ts-local_to_utc_diff-FIT_EPOCH_OFFSET, "s", "distance", "{0:.3f}".format(distval), "m", "steps",int(stepval),"cycles","activity_type","6",None])

# Sort and write out.
output_data.sort(key= operator.itemgetter(4,1))
wellness_writer.writerows(output_data)
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
