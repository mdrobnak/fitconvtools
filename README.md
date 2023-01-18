Copyright 2023, Matthew Drobnak

These are some tools to help migrate data into the Garmin ecosystem.

I'm not sure on licensing yet, but help is appreciated with issues related to Timezone issues. Currently the only way I have it working the way I would like is having the data time shifted from GMT to local time.

fitsdk:
Contains the messages.csv and types.csv I'm using in my build of the SDK. Most of them are unused, save for the resting heart rate items.

fbtocsv.py:

Used to process fitbit data export to CSV file suitable for use with FIT SDK CSVTool after providing custom types and message CSV files.


fbdownloadtcx.py:

Use this to download any TCX activity files for uploading. Note that only items with GPS data are valid files. Sort by size to weed out bad files.

You'll need python-fitbit: https://github.com/orcasgit/python-fitbit
Using instructions from here: https://towardsdatascience.com/using-the-fitbit-web-api-with-python-f29f119621ea

Go to dev.fitbit.com

Register An App

App name: Anything
Description: Download Personal TCX files
Application Website URL: Anything
Org: Anything
Org Website: Anything
Terms of Service URL: https://dev.fitbit.com/legal/platform-terms-of-service/
Privacy Policy: https://www.fitbit.com/legal/privacy-policy
OAuth 2.0 App Type: Personal

Set Callback URL to http://127.0.0.1:8080/

 -- This will fail. You'll need to set up HTTPS unfortunately. I have a home server setup so I was able to make use of that.

Agree and Register.

You need this file: gather_keys_oauth2.py from the python-fitbit package.


Apply the python-fitbit-api.diff using "git apply" to add the do_download function, which will not decode the downloaded items.
You need to set the client ID and secret in the file.
