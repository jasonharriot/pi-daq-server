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

    df = fetch_df.fetch_df_hours(db, 48, 1000)    #Grab the latest data. Past 48 hours, decimate to 1000 points.

    df['Tdiff'] = df['T2_real'] - df['T1_real']
    
    #Calculate time derivative. 
    dT1 = []
    dT2 = []

    last_row = None

    for index, row in df.iterrows():
        if index==0:
            dT1.append(0)
            dT2.append(0)

        else:
            dt_timedelta = row['timestamp'] - last_row['timestamp']
            dt = dt_timedelta.seconds / (60)  #Minutes

            dT1.append((row['T1_real'] - last_row['T1_real']) / dt)
            dT2.append((row['T2_real'] - last_row['T2_real']) / dt)

        last_row = row

    df['dT1'] = dT1
    df['dT2'] = dT2

    #Smooth the data. Replace original columns.
    df['dT1'] = df['dT1'].rolling(50).mean()
    df['dT2'] = df['dT2'].rolling(50).mean()

    fig, ax1 = plt.subplots()    #Get the figure object and primary axes for later use

    ax2 = ax1.twinx()   #Secondary y-axis object

    #ax1.set_yscale('symlog')

    ax1.tick_params(axis='x', labelrotation=45) #Make the x-axis labels rotated so they fit better

    ax1.set_xlabel('Date')
    ax1.set_ylabel(r'$dT/dt\/(°C-min^{-1})$')
    ax2.set_ylabel(r'$Tdiff\/(°C)$')

    #ax2.yaxis.set_major_formatter('{x:.0f}')    #Display numbers on the secondary y-axis with no decimal point.
    #ax2.set_ylim(300, 900)  #Set the limits of the secondary y-axis.

    graph_dT1 = ax1.plot(df['timestamp_local'], df['dT1'], color='red', label='dT1')[0]    #Plot T1. Grab element [0] of the return value. Don't need the other values.
    graph_dT2 = ax1.plot(df['timestamp_local'], df['dT2'], color='orange', label='dT2')[0] #Plot T2
    graph_Tdiff = ax2.step(df['timestamp_local'], df['Tdiff'], color='blue', label='Tdiff')[0]   #Plot V1 on the secondary y-axis

    graphs = [graph_dT1, graph_dT2, graph_Tdiff]

    labels = [graph.get_label() for graph in graphs]

    ax1.legend(graphs, labels, loc=0)

    plt.tight_layout()  #This option is a better layout than the default. By default, some labels and text are compeltely cut-off at the edges of the plot.

    plt.show()