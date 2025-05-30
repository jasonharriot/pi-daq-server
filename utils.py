import datetime
import mysql.connector
import time
import zoneinfo
import pandas as pd
import numpy as np

expected_server_data_rate = .1  #The expected frequency of datapoints collected by the server, in samples per second. Used to calculate decimation.

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

    print(f'Received total of {df.shape[0]} rows')

    cur.close()

    return df