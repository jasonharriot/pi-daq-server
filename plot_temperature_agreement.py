import mysql.connector
import time
import configparser
import datetime
import zoneinfo
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation
import utils

if __name__ == '__main__':
    cfg = configparser.ConfigParser()
    cfg.read('config_client.ini')   #Read sensitive parameters from the configuration file.

    mysql_config = cfg['mysql']

    db = mysql.connector.connect(
        host=mysql_config['host'],
        user=mysql_config['user'],
        password=mysql_config['password'],
        database=mysql_config['database']
        )

    #Construct a basic line plot

    start_date = datetime.datetime.strptime('2025-05-23 15:40:00', '%Y-%m-%d %H:%M:%S').replace(tzinfo=datetime.timezone.utc) #UTC start date/time.

    df = utils.fetch_df_date(db, start_date, 1000)    #Grab the latest data. Decimate to 1000 points.

    fig, ax1 = plt.subplots(layout='constrained')    #Get the figure object and primary axes for later use

    #ax1.tick_params(axis='x', labelrotation=45) #Make the x-axis labels rotated so they fit better

    ax1.set_xlabel('T1 (°C)')
    ax1.set_ylabel('T2 (°C)')

    ax1.plot([0, 100], [0, 100], color='grey')  #A 1:1 reference line

    ax1.plot(df['T1_real'], df['T2_real'], color='black')

    min_T1 = df['T1_real'].min()
    max_T1 = df['T1_real'].max()

    min_T2 = df['T2_real'].min()
    max_T2 = df['T2_real'].max()

    ax1.set_ylim(min_T2-5, max_T2+5)
    ax1.set_xlim(min_T1-5, max_T1+5)

    plt.show()