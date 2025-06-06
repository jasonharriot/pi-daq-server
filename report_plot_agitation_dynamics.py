import mysql.connector
import time
import configparser
import datetime
import zoneinfo
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation
from scipy.signal import savgol_filter
import liquid_level
import fetch_df
import pi_daq_db

if __name__ == '__main__':
    db = pi_daq_db.PiDAQDB()

    fig, all_axes = plt.subplots(layout='constrained', nrows=2, ncols=2, sharey='all')    #Get the figure object and primary axes for later use. Use the constrained layout option for better looks.

    print(f'Created the following subplot axes: {all_axes}')

    ((ax1, ax2), (ax3, ax4)) = all_axes

    all_axes_list = [ax1, ax2, ax3, ax4]


    #Set some properties of the first y-axis. Others will follow. X-axis properties set on a per-subplot basis since they are all different.


    #fig.suptitle(f'Reactor process values\n{start_date_str} to {end_date_str}')

    

    ax1.set_ylabel('Volume (L)')
    ax1.yaxis.set_major_formatter('{x:.0f}')
    ax1.set_ylim(300, 800)

    all_graphs = []

    date_ranges = [
        ('2025-06-03 15:22:58', '2025-06-03 15:34:58'),
        ('2025-06-05 15:34:58', '2025-06-05 15:47:58'),
        ('2025-06-05 16:58:58', '2025-06-05 17:11:58')
    ]

    plot_index = 0

    for date_range in date_ranges:
        def utc_timestamp_to_date(s):
            return datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S').replace(tzinfo=datetime.timezone.utc)

        (start_date, end_date) = (utc_timestamp_to_date(x) for x in date_range)

        df = fetch_df.fetch_df_date_date(db, start_date, end_date, 1000) #Grab the latest N datapoints. Actual number of rows returned is approximate.

        print(df)

        ax = all_axes_list[plot_index]

        ax.set_title(f'{df['timestamp_local'].iloc[0].strftime('%Y-%m-%d %H:%M:%S')}')
        #ax.set_xlabel('Date')
        ax.tick_params(axis='x', labelrotation=45) #Make the x-axis labels rotated so they fit better

        ax.grid()   #Enables both X and Y grids.

        #Plot each set of data. Grab element [0] of the return value, which we will use to generate labels. Don't need the other values.
        graph_real = ax.plot(df['timestamp_local'], df['V1_real'], color='blue', label='V1')[0]   #Plot V1 on the secondary y-axis
        graph_comp = ax.plot(df['timestamp_local'], df['V1_compensated'], color='#99f', label='V1c')[0]   #Plot agitation-compensated volume

        plot_index += 1
    
    labels = [graph.get_label() for graph in all_graphs]    #Greate a list of labels where each label is generated from the list of graphs. While tedious, this is the only way to have one legend with multiple labels from multiple axes.

    #ax1.legend(graphs, labels, loc='lower center')   #Create the legend from the list of graphs and list of labels. The legend technically belongs only to ax1, but it will contain entries for all plots on all axes, because we have specified them explicitly in those lists.

    plt.show()