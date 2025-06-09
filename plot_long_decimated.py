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

    df = fetch_df.fetch_df_hours(db, 1, 100)    #Grab the latest data

    fig, ax1 = plt.subplots()    #Get the figure object and primary axes for later use

    ax2 = ax1.twinx()   #Secondary y-axis object

    ax1.tick_params(axis='x', labelrotation=45) #Make the x-axis labels rotated so they fit better

    ax1.set_xlabel('Date')
    ax1.set_ylabel('Temperature (°C)')
    ax2.set_ylabel('Volume (L)')

    ax2.yaxis.set_major_formatter('{x:.0f}')    #Display numbers on the secondary y-axis with no decimal point.
    ax2.set_ylim(300, 900)  #Set the limits of the secondary y-axis.

    graph_T1 = ax1.step(df['timestamp'], df['T1_real'], color='red', label='T1')[0]    #Plot T1. Grab element [0] of the return value. Don't need the other values.
    graph_T2 = ax1.step(df['timestamp'], df['T2_real'], color='orange', label='T2')[0] #Plot T2
    graph_V1 = ax2.step(df['timestamp'], df['V1_real'], color='blue', label='V1')[0]   #Plot V1 on the secondary y-axis

    #ax1.legend(loc='upper left')    #Place a legend for the primary axes
    #ax2.legend(loc='upper center')   #Place a legend for the secondary axes, but specify the location.

    graphs = [graph_T1, graph_T2, graph_V1]

    labels = [graph.get_label() for graph in graphs]

    ax1.legend(graphs, labels, loc=0)

    plt.tight_layout()  #This option is a better layout than the default. By default, some labels and text are compeltely cut-off at the edges of the plot.

    plt.show()