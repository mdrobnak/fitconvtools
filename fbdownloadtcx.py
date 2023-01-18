#!/bin/env python3
import fitbit
import json
import os
import pprint
import time

# gather_keys_oauth2.py file needs to be in the same directory.
import gather_keys_oauth2 as Oauth2

# YOU NEED TO PUT IN YOUR OWN CLIENT_ID AND CLIENT_SECRET
CLIENT_ID='XXXXXX'
CLIENT_SECRET='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
server=Oauth2.OAuth2Server(CLIENT_ID, CLIENT_SECRET, redirect_uri='https://XX.XXXXXXX.com/')
try:
    with open("%s/fb-token.json" % os.environ.get('HOME')) as rhr_file:
      token = json.load(rhr_file)
except FileNotFoundError:
    token = {}

if "access_token" not in token:
  server.browser_authorize()
  ACCESS_TOKEN=str(server.fitbit.client.session.token["access_token"])
  REFRESH_TOKEN=str(server.fitbit.client.session.token["refresh_token"])
  token["access_token"] = str(server.fitbit.client.session.token["access_token"])
  token["refresh_token"] = str(server.fitbit.client.session.token["refresh_token"])
  with open("%s/fb-token.json" % os.environ.get('HOME'), "w") as jsonFile:
    json.dump(token, jsonFile)
else:
  ACCESS_TOKEN=token["access_token"]
  REFRESH_TOKEN=token["refresh_token"]
auth2_client=fitbit.Fitbit(CLIENT_ID,CLIENT_SECRET,oauth2=True,access_token=ACCESS_TOKEN,refresh_token=REFRESH_TOKEN)

try:
  obj = auth2_client.make_request("https://api.fitbit.com/1/user/-/activities/list.json?afterDate=2014-01-01&sort=asc&offset=0&limit=100")
except fitbit.exceptions.HTTPTooManyRequests as tmr:
  sleeptime = int(tmr.retry_after_secs+90)
  print ("Too many requests: Sleeping %s seconds" % sleeptime)
  time.sleep(sleeptime)
  obj = auth2_client.make_request("https://api.fitbit.com/1/user/-/activities/list.json?afterDate=2014-01-01&sort=asc&offset=0&limit=100")

morePages = True
while morePages:
  with open("fbdownload/api-output-%s.json" % obj["pagination"]['offset'], "w") as jsonFile:
    json.dump(obj, jsonFile)
  for act in obj["activities"]:
    if "tcxLink" in act:
      try:
          source = act["source"]
          if "GPS" in act["source"]["trackerFeatures"]:
            output_fn = "{0}-{1}.tcx".format(act["startTime"], act["logId"])
            print(output_fn)
            try:
              tcxObj = auth2_client.do_download(act["tcxLink"])
              #print("Would download ", act["tcxLink"])
            except fitbit.exceptions.HTTPTooManyRequests as tmr:
              sleeptime = int(tmr.retry_after_secs+90)
              print ("Too many requests: Sleeping %s seconds" % sleeptime)
              time.sleep(sleeptime)
              #print("Would download ", act["tcxLink"])
              tcxObj = auth2_client.do_download(act["tcxLink"])

            with open("fbdownload/%s" % output_fn, "wb") as tcxFile:
              tcxFile.write(tcxObj)
            time.sleep(1.0)
      except KeyError:
        continue
  if obj["pagination"]['next'] != '':
    obj = auth2_client.make_request(obj["pagination"]['next'])
  else:
    morePages = False
