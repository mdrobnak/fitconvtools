#!/bin/env python3
import argparse
import csv
import os
import sys

def get_arguments():
  parser = argparse.ArgumentParser(
                      prog = 'fbtocsv',
                      description = 'Converts Fitbit data for use with CSVTool')
  parser.add_argument('-d', '--date')
  parser.add_argument('-f', '--file-number', type=int, default=1)
  parser.add_argument('-r', '--rhr-only', action='store_true', default=False)
  parser.add_argument('-s', '--src-dir', default=".")
  parser.add_argument('-t', '--offset-ts-data', action='store_true', default=False)

  args = parser.parse_args()
  if args.date is None:
    print("Must specify date.")
    parser.print_usage()
    sys.exit(1)

  return args

def find_file(source_directory, full_date, day_of_month):
# Open needed files.
  filename_date = ""
  check_prev_month = False
  for f_name in os.listdir("%s/Physical Activity" % source_directory):
    # heart rate file is exact date - don't need to search for that.
    # Check to see if the beginning matches, and that the desired date is >= date in the file.
    # The rest of the data is aligned on this other date, so find one, find them all.
    if f_name.startswith('steps-%s' % full_date.rsplit("-",1)[0]):
      if int(day_of_month) >= int(f_name.rsplit("-",1)[1].split(".json")[0]):
        # Yes I could use regex, but I was lazy here for the moment.
        filename_date=f_name.split("steps-",1)[1].split(".json",1)[0]
        break
      else:
        check_prev_month = True

  if check_prev_month:
    old_month=int((full_date.split("-")[1]))
    new_month_int=int(old_month)-1
    if int(old_month) <= 10:
        new_month = "0%s" % str(new_month_int)
    else:
        new_month = "%s" % str(new_month_int)
    for f_name in os.listdir("%s/Physical Activity" % source_directory):
      tgtstring='steps-%s-%s' % (full_date.split("-",1)[0], new_month)
      if f_name.startswith('steps-%s-%s' % (full_date.split("-",1)[0], new_month)):
        filename_date=f_name.split("steps-",1)[1].split(".json",1)[0]
        break
  return filename_date

def write_sleep(full_date, garmin_start_ts, garmin_start_ts_not_utc, local_to_utc_diff):
  sleep_filename = "sleep-%s.csv" % full_date
  sleep_data_file = open(sleep_filename, 'w')

  # create the csv writer object
  sleep_writer = csv.writer(sleep_data_file)

  # Sleep
  header = [ "Type","Local Number","Message","Field 1","Value 1","Units 1","Field 2","Value 2","Units 2","Field 3","Value 3","Units 3", "Field 4","Value 4","Units 4","Field 5","Value 5","Units 5","Field 6","Value 6","Units 6" ]
  sleep_writer.writerow(header)
  file_id_def = [ "Definition","0","file_id","serial_number","1",None,"time_created",1,"","manufacturer","1","","product","1","","type","1","" ]
  sleep_writer.writerow(file_id_def)
  file_id_type = 49
  file_id_data  = [ "Data","0","file_id","serial_number","3411930528",None,"time_created",garmin_start_ts,None,"manufacturer","1",None,"garmin_product","3851",None,"type",file_id_type,None ]
  sleep_writer.writerow(file_id_data)


  file_creator_def  = [ "Definition","1","file_creator","software_version",1,None ]
  file_creator_data = [ "Data","1","file_creator","software_version","1116",None ]

  dev_inf_def = [ "Definition","1","device_info","timestamp","1",None,"serial_number","1",None,"manufacturer","1",None,"product","1",None,"software_version","1", None ]
  dev_info_data = [ "Data","1","device_info","timestamp",garmin_start_ts_not_utc,"s","serial_number","3411930528",None,"manufacturer","1",None,"garmin_product","3851",None,"software_version","11.16",None ]

  sensor_def  = [ "Definition","3","sleep_sensor","timestamp","1",None,"local_timestamp","1",None,"sensor_sw_ver","32",None,"vlue_1","1",None,"value_2","1",None,"sleep_sensor_enum","1",None ]
  sensor_data = [ "Data","3","sleep_sensor","timestamp",garmin_start_ts,None,"local_timestamp",garmin_start_ts_not_utc,None,"sensor_sw_ver","6.14.8.3-ETE-garmin-7c33af24",None,"vlue_1","60",None,"value_2","2",None,"sleep_sensor_enum","1",None ]
  sleep_writer.writerow(sensor_def)
  sleep_writer.writerow(sensor_data)

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
  sleep_data_file.close()
