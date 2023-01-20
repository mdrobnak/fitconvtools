#!/bin/env python3
import argparse
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
