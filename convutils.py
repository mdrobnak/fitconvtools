#!/bin/env python3
import argparse
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
