#!/usr/bin/env python2.6
"""
This is an example script to show the capabilities of the fitbit client.

An alternative to directly specifying the arguments to the fitbit.Client
is to create a config file at ~/.fitbit.conf with the following:

[fitbit]
user_id: 123ABC
sid: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
uid: 123456
uis: XXX%3D
"""
import os, sys
from  fitbit import Client
import ConfigParser
import datetime, time

# Fitbit Configuration
CONFIG = ConfigParser.ConfigParser()
CONFIG.read(["fitbit.conf", os.path.expanduser("~/.fitbit.conf")])

client = Client(CONFIG.get('fitbit', 'user_id'),
                CONFIG.get('fitbit', 'sid'),
                CONFIG.get('fitbit', 'uid'),
                CONFIG.get('fitbit', 'uis'))

yesterday = datetime.date.today() - datetime.timedelta(days=1)

# Daily Historical data for the last month
#historical_data = client.historical(yesterday, period='3d')
#print historical_data

# Intraday time series 
steps = client.intraday_steps(yesterday)
#print(steps[:3])
print "Steps"
for ent in steps:
	print ent['time'].ctime(), time.mktime(ent['time'].timetuple()),  ent['value']

print "\n\nCalories"
calories = client.intraday_calories_burned(yesterday)
for ent in steps:
	print ent

print "\n\nActive Score"
active_score = client.intraday_active_score(yesterday)
for ent in active_score:
	print ent


sys.exit(0)
# Sleep records

# Summaries of all sleep records for a date
sleep = client.sleep_log(yesterday)
print(sleep[:3])

# By minute detailed data of all sleep records for a date
intraday_sleep = client.intraday_sleep(yesterday)
print(intraday_sleep[:3])

# Summaries of all sleep records for a date, with a sleepProcAlgorithm specified
sleep2 = client.sleep_log(yesterday, 'SENSITIVE')
print(sleep2[:3])

intraday_sleep2 = client.intraday_sleep(yesterday, 'COMPOSITE')
print(intraday_sleep2[:3])

# Activity Records

# Summaries of all activity records for a date
activity_records = client.activity_records(yesterday)
print(activity_records[:3])

# By minute detailed data of all activity records for a date
activity_records = client.activity_records(yesterday)
print(activity_records[:3])

print "\n\n All Logged Activities for a date"
logged_activities = client.logged_activities(yesterday)
for ent in logged_activities:
	print ent

