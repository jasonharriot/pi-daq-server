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

def get_df(db): 
    df = fetch_df.fetch_df_hours(db, 1, 1000)    #Grab the latest data

    return df

def update(frame, db, graph_T1, graph_T2, graph_V1):
    df = get_df(db)

    graph_T1.set_xdata(df['timestamp'])
    graph_T1.set_ydata(df['T1_real'])

    graph_T2.set_xdata(df['timestamp'])
    graph_T2.set_ydata(df['T2_real'])

    graph_V1.set_xdata(df['timestamp'])
    graph_V1.set_ydata(df['V1_real'])

    plt.xlim(df['timestamp'].iloc[0] - datetime.timedelta(minutes=10), df['timestamp'].iloc[-1] + datetime.timedelta(minutes=10)) #Set the bounds of the plot to something nice, with padding on each side between the datapoints and the edge.

    min_y1 = min([df['T1_real'].min(), df['T2_real'].min()])
    max_y1 = max([df['T1_real'].max(), df['T2_real'].max()])

    graph_T1.axes.set_ylim(min_y1-3, max_y1+3)

if __name__ == '__main__':
    db = pi_daq_db.PiDAQDB()

    df = get_df(db)

    #Construct a basic line plot
    fig, ax1 = plt.subplots()    #Get the figure object and primary axes for later use

    ax1.tick_params(axis='x', labelrotation=45) #Make the x-axis labels rotated so they fit better
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Temperature (°C)')

    ax2 = ax1.twinx()   #Secondary y-axis object
    ax2.set_ylabel('Volume (L)')

    ax2.yaxis.set_major_formatter('{x:.0f}')    #Display numbers on the secondary y-axis with no decimal point.
    ax2.set_ylim(300, 900)  #Set the limits of the secondary y-axis.

    #Plot dummy data. The real data will be updated when the callback is executed each time.
    graph_T1 = ax1.plot([0], [0], color='red', label='T1')[0]    #Plot T1. Grab element [0] of the return value. Don't need the other values.
    graph_T2 = ax1.plot([0], [0], color='orange', label='T2')[0] #Plot T2
    graph_V1 = ax2.step([0], [0], color='blue', label='V1')[0]   #Plot V1 on the secondary y-axis

    graphs = [graph_T1, graph_T2, graph_V1]
    labels = [graph.get_label() for graph in graphs]
    ax1.legend(graphs, labels, loc=0)

    plt.tight_layout()  #This option is a better layout than the default. By default, some labels and text are compeltely cut-off at the edges of the plot.

    update_args = (db, graph_T1, graph_T2, graph_V1)    #Extra arguments for the update callback function

    anim = matplotlib.animation.FuncAnimation(fig, update, interval=5000, frames = None, fargs = update_args, cache_frame_data = False)

    update(None, *update_args)  #Run the callback function once immediately so we don't have to wait for the timer.

    plt.show()