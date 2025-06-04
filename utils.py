import datetime
import mysql.connector
import time
import zoneinfo
import pandas as pd
import numpy as np

expected_server_data_rate = .1  #The expected frequency of datapoints collected by the server, in samples per second. Used to calculate decimation.
reactor_volume_empty_threshold = 338    #If equal to or below this volume, the reactor does not have enough liquid in it to make a volume measurement. The volume datapoint will be changed to NaN.
reactor_volume_full_threshold = 753     #If equal to or above this volume, the reactor does not have enough liquid in it to make a volume measurement. The volume datapoint will be changed to NaN.

def agitation_liquid_level_compensator(volume, speed):  #Return the real liquid level for any given reported liquid level and agitation speed

    #Volume not considered yet.
    delta_V = 327e-6*pow(speed, 3) + 11.15e-3*pow(speed, 2) + 11.02e-3*speed    #Change in volume due to agitation

    volume_compensated = volume - delta_V

    #print(f'[Compensator] V1: {volume} S1: {speed} V1c: {volume_compensated}')

    return volume_compensated

class Timer:    #Basic timer class. Maintains a set interval.
    def __init__(self, interval):
        self.last_datetime = None
        self.interval = interval

    def fire(self):
        now = datetime.datetime.now()

        if self.last_datetime is None or now - self.last_datetime > self.interval:
            if self.last_datetime is None:
                self.last_datetime = now

            while now - self.last_datetime > self.interval: #Bring the last time up to current in ammounts equal to the interval.
                self.last_datetime += self.interval

            return True

        return False

def fetch_columns(db):
    cur = db.cursor()

    cur.execute(f"SHOW COLUMNS IN adam_rows")

    column_names = []

    for row in cur:
        column_names.append(row[0])

    return column_names

def convert_utc_local(date):
    timestamp_utc = date.replace(tzinfo=datetime.timezone.utc) #Interpret the date as UTC. Don't change it, just assume that it represents UTC.
    timestamp_local = timestamp_utc.astimezone(zoneinfo.ZoneInfo('America/New_York'))   #Convert the date (yes, actually changing the time) to a local timezone.

    return timestamp_local

def fetch_df_date(db, start_date, target_point_count):  #Fetch dataframe by start date and number of points
    now = datetime.datetime.now(datetime.timezone.utc)    #Get UTC time
    expected_server_data_rate = .1    #Expected frequency of datapoints per second in the data retreived from the server
    if target_point_count == 0:
        decimation = 1
    else:
        timespan = now - start_date
        #print(f'Date range: {start_date.isoformat()} - {now.isoformat()}')
        #print(f'{(timespan.seconds, timespan.days)}')
        decimation = int(expected_server_data_rate / (target_point_count / (timespan.days*24*60*60 + timespan.seconds)))

    if decimation <= 0: #Just return every point that exists if we are asking for more than there really are
        decimation = 1

    df = fetch_df(db, start_date, now, decimation)

    return df

def fetch_df_date_date(db, start_date, end_date, target_point_count):   #Fetch dataframe by start and end dates, and number of points
    expected_server_data_rate = .1    #Expected frequency of datapoints per second in the data retreived from the server
    if target_point_count == 0:
        decimation = 1
    else:
        timespan = end_date - start_date
        #print(f'{(timespan.seconds, timespan.days)}')
        decimation = int(expected_server_data_rate / (target_point_count / (timespan.days*24*60*60 + timespan.seconds)))

    if decimation <= 0: #Just return every point that exists if we are asking for more than there really are
        decimation = 1

    df = fetch_df(db, start_date, end_date, decimation)

    return df

def fetch_df_hours(db, timespan_hours, target_point_count): #Fetch dataframe by number of hours into the past, and number of points
    now = datetime.datetime.now(datetime.timezone.utc)    #Get UTC time
    expected_server_data_rate = .1    #Expected frequency of datapoints per second in the data retreived from the server
    start_date = now - datetime.timedelta(hours=timespan_hours)
    
    df = fetch_df_date(db, start_date, target_point_count)

    return df

def fetch_df(db, start_date, end_date, decimation): #Fetch a dataframe from the SQL server. Dates must be UTC. Specify start and end dates, and decimation factor.
    column_names = fetch_columns(db)

    cur = db.cursor()

    start_date_str = start_date.strftime('%Y-%m-%d %H:%M:%S')   #Start date. Make a string representation of the date and time in a format like: 2025-05-23 13:48:34
    end_date_str = end_date.strftime('%Y-%m-%d %H:%M:%S')   #End date

    print(f'Grabbing data starting from UTC date: {start_date} until: {end_date} with decimation: {decimation}')

    query_str = f"SELECT * FROM adam_rows WHERE timestamp >= '{start_date_str}' AND timestamp <= '{end_date_str}' AND id % {decimation} = 0"

    df = pd.read_sql(query_str, db)

    print(f'SQL command exeuted.')

    df['timestamp_local'] = df['timestamp'].apply(convert_utc_local)    #Create a new column for a localized timestamp. The timestamp from the server is in UTC.


    #Modify the volume column to be zero if below or above a threshold.
    def f(x):
        if x > reactor_volume_empty_threshold and x < reactor_volume_full_threshold:
            return x

        return float('NaN')

    df['V1_real'] = df['V1_real'].apply(f)



    #Calculate the real liquid level, compensated for agitation. Make this calculation AFTER nullifying over-full and under-empty volume measurements in V1_real. This way, the compensated volume will also be NaN at appropriate times.
    df['V1_compensated'] = df.apply(lambda x: agitation_liquid_level_compensator(x.V1_real, x.S1_real), axis=1)

    


    print(f'Received total of {df.shape[0]} rows')

    cur.close()

    return df