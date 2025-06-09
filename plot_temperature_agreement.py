import mysql.connector
import time
import configparser
import datetime
import zoneinfo
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation
import fetch_df
import pi_daq_db

if __name__ == '__main__':
    db = pi_daq_db.PiDAQDB()

    #Construct a basic line plot

    start_date = datetime.datetime.strptime('2025-01-01 00:00:00', '%Y-%m-%d %H:%M:%S').replace(tzinfo=datetime.timezone.utc) #UTC start date/time.

    df = fetch_df.fetch_df_date(db, start_date, 50000)    #Grab the latest data. Decimate to 1000 points.

    fig, ax1 = plt.subplots(layout='constrained')    #Get the figure object and primary axes for later use

    #ax1.tick_params(axis='x', labelrotation=45) #Make the x-axis labels rotated so they fit better

    ax1.set_xlabel('T1 (°C)')
    ax1.set_ylabel('T2 (°C)')

    ax1.plot([0, 100], [0, 100], color='grey')  #A 1:1 reference line

    ax1.scatter(df['T1_real'], df['T2_real'], color='black', marker='+')

    min_T1 = df['T1_real'].min()
    max_T1 = df['T1_real'].max()

    min_T2 = df['T2_real'].min()
    max_T2 = df['T2_real'].max()

    ax1.set_ylim(min_T2-5, max_T2+5)
    ax1.set_xlim(min_T1-5, max_T1+5)

    plt.show()