import json
import os
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
import timer
from scipy.signal import savgol_filter
from scipy.ndimage import gaussian_filter1d

def write_latest_data(df, filepath):
    #Write the latest data to a JSON file.
    latest_row = df.iloc[-1]
    json_obj = {
            'timestamp': latest_row['timestamp'].timestamp() * 1000,
            'T1': latest_row['T1_real'],
            'T2': latest_row['T2_real'],
            'V1': latest_row['V1_real'].tolist(),   #A conversion here is needed because NumPy datatypes cannot be serialized by the JSON library.
            'V1c': latest_row['V1_compensated'].tolist(),
            'E1': latest_row['E1'],
            'P1': latest_row['P1'],
            'S1': latest_row['S1_real']
    }

    print(json_obj)

    json_str = json.dumps(json_obj)

    f = open(filepath, 'w+')

    f.write(json_str)

    f.close()


def do_df_calcs(df):
    #Calculate reactor energy
    liquid_density = 1 #kg/L
    liquid_specific_heat = 4184 #J-kg^-1-K^-1


    df['T1_real_smooth'] = gaussian_filter1d(df['T1_real'], 5)
    df['T2_real_smooth'] = gaussian_filter1d(df['T2_real'], 5)

    df['V1_real_smooth'] = gaussian_filter1d(df['V1_real'], 5)
    df['V1_compensated_smooth'] = gaussian_filter1d(df['V1_compensated'], 5)

    df['E1'] = df['V1_compensated']*(df['T1_real']+273.15)*liquid_specific_heat*liquid_density #Energy of the reactor, in joules
    #constant_volume = df['V1_compensated'].iloc[-1] #Assume this volume for the entire timespan plotted.
    #df['E1'] = constant_volume*(df['T1_real_smooth']+273.15)*liquid_specific_heat*liquid_density
    df['E1_smooth'] = gaussian_filter1d(df['E1'], 5)

    #Calculate reactor net power
    energy_diff = df['E1'].diff()

    time_diff = [x.seconds for x in df['timestamp_local'].diff()]  #Get the number of seconds

    df['P1'] = energy_diff/time_diff    #P20ower of the reactor, in Watts
    df['P1_smooth'] = gaussian_filter1d(df['P1'], 10)
    #df['P1_smooth'] = savgol_filter(df['P1'], 200, 3)





    




def do_plot_1(db, timespan_hours, filepath):    #Plot temperatures
    now = datetime.datetime.now()
    now_str = now.strftime('%Y-%m-%d %H:%M:%S')

    df = fetch_df.fetch_df_hours(db, timespan_hours, 1000) #Grab n datapoints across the past t hours.
    do_df_calcs(df)

    #Plot the data

    fig, ax1 = plt.subplots(layout='constrained')    #Get the figure object and primary axes for later use. Use the constrained layout option for better looks.

    plt.grid(visible=True, which='both')

    fig.suptitle(f'Reactor thermals\n{now_str} ({timespan_hours} hours)')
    
    ax1.tick_params(axis='x', labelrotation=45) #Make the x-axis labels rotated so they fit better
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Temperature (°C)')

    graph_T2 = ax1.plot(df['timestamp_local'], df['T2_real_smooth'], color='orange', label='T2')[0] #Plot T2
    graph_T1 = ax1.plot(df['timestamp_local'], df['T1_real_smooth'], color='red', label='T1')[0]    #Plot T1.
    
    graphs = [graph_T2, graph_T1] #Create a list of objects returned from the plots we have invoked.
    labels = [graph.get_label() for graph in graphs]    #Greate a list of labels where each label is generated from the list of graphs. While tedious, this is the only way to have one legend with multiple labels from multiple axes.

    ax1.legend(graphs, labels, loc=0)   #Create the legend from the list of graphs and list of labels. The legend technically belongs only to ax1, but it will contain entries for all plots on all axes, because we have specified them explicitly in those lists.

    plt.savefig(filepath)

    return df


def do_plot_2(df, timespan_hours, filepath):    #Plot reactor energy, power, volume
    now = datetime.datetime.now()
    now_str = now.strftime('%Y-%m-%d %H:%M:%S')

    df = fetch_df.fetch_df_hours(db, timespan_hours, 1000) #Grab n datapoints across the past t hours.
    do_df_calcs(df)
    
    #Plot the data

    fig, ax1 = plt.subplots(layout='constrained')    #Get the figure object and primary axes for later use. Use the constrained layout option for better looks.
    fig.suptitle(f'Reactor energy\n{now_str} ({timespan_hours} hours)')

    plt.grid(visible=True, which='both')
        
    ax1.tick_params(axis='x', labelrotation=45) #Make the x-axis labels rotated so they fit better
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Power (kW)')
    ax1.set_ylim(-3, 3)

    ax2 = ax1.twinx()   #Secondary y-axis object
    ax2.set_ylabel('Volume (L)')
    ax2.set_ylim(300, 800)

    ax3 = ax1.twinx()
    ax3.set_ylabel('Energy (GJ)')
    ax3.spines.right.set_position(('outward', 50))
    ax3.yaxis.set_major_formatter('{x:.3f}')
    #ax3.set_ylim

    #Plot each set of data. Grab element [0] of the return value, which we will use to generate labels. Don't need the other values.
    graph_P1 = ax1.plot(df['timestamp_local'], df['P1_smooth']*1e-3, color='green', label='P1')[0]  #Plot power in kilowatts.
    graph_V1c = ax2.plot(df['timestamp_local'], df['V1_compensated_smooth'], color='#99f', label='V1c')[0]   #Plot agitation-compensated volume
    graph_E1 = ax3.plot(df['timestamp_local'], df['E1_smooth']*1e-9, color='purple', label='E1')[0]    #Power, in gigawatts
    
    graphs = [graph_P1, graph_E1, graph_V1c]  #Create a list of objects returned from the plots we have invoked.

    labels = [graph.get_label() for graph in graphs]    #Greate a list of labels where each label is generated from the list of graphs. While tedious, this is the only way to have one legend with multiple labels from multiple axes.

    ax1.legend(graphs, labels, loc=0)   #Create the legend from the list of graphs and list of labels. The legend technically belongs only to ax1, but it will contain entries for all plots on all axes, because we have specified them explicitly in those lists.

    plt.savefig(filepath)

    return df






def do_plot_3(df, timespan_hours, filepath):    #Plot liquid level(s), agitation speed
    now = datetime.datetime.now()
    now_str = now.strftime('%Y-%m-%d %H:%M:%S')

    df = fetch_df.fetch_df_hours(db, timespan_hours, 1000) #Grab n datapoints across the past t hours.
    do_df_calcs(df)

    fig, ax1 = plt.subplots(layout='constrained')    #Get the figure object and primary axes for later use. Use the constrained layout option for better looks.
    fig.suptitle(f'Reactor fluids\n{now_str} ({timespan_hours} hours)')

    plt.grid(visible=True, which='both')

    ax1.tick_params(axis='x', labelrotation=45) #Make the x-axis labels rotated so they fit better
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Volume (L)')
    ax1.set_ylim(300, 800)
    
    ax2 = ax1.twinx()   #Secondary y-axis object
    ax2.set_ylabel('Agitation speed (rpm)')
    ax2.set_ylim(0, 90)

    graph_V1 = ax1.plot(df['timestamp_local'], df['V1_real'], color='blue', label='V1')[0]   #Plot V1 on the secondary y-axis
    graph_V1c = ax1.plot(df['timestamp_local'], df['V1_compensated'], color='#99f', label='V1c')[0]   #Plot agitation-compensated volume
    graph_S1 = ax2.plot(df['timestamp_local'], df['S1_real'], color='red', label='S1')[0]   #Plot agitation speed
    
    graphs = [graph_V1, graph_V1c, graph_S1]    #Create a list of objects returned from the plots we have invoked.

    labels = [graph.get_label() for graph in graphs]    #Greate a list of labels where each label is generated from the list of graphs. While tedious, this is the only way to have one legend with multiple labels from multiple axes.

    ax1.legend(graphs, labels, loc=0)   #Create the legend from the list of graphs and list of labels. The legend technically belongs only to ax1, but it will contain entries for all plots on all axes, because we have specified them explicitly in those lists.

    plt.savefig(filepath)

    return df








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

    img_dir_path = 'web/img/'
    json_dir_path = 'web/json'

    try:
        os.makedirs(img_dir_path)
    except FileExistsError: #Ignore the error if the directory already exists.
        pass

    try:
        os.makedirs(json_dir_path)
    except FileExistsError: 
        pass



    #Grab a dataframe just for the purpose of extracting the last row
    df = fetch_df.fetch_df_hours(db, 1, 0)
    do_df_calcs(df)

    write_latest_data(df, os.path.join(json_dir_path, 'live.json'))



    #Multiple plots. Each with a different timespan. Write each to an image that will by retrieved by the webpage.

    do_plot_1(db, 7*24, os.path.join(img_dir_path, 'live_a.png'))  #Just grab the dataframe from one of these do_plot calls. Since we want to extract the last row for write_latest_data, it doesn't matter which.
    do_plot_1(db, 24, os.path.join(img_dir_path, 'live_b.png'))
    do_plot_1(db, 2, os.path.join(img_dir_path, 'live_c.png'))

    do_plot_2(db, 2, os.path.join(img_dir_path, 'live_d.png'))  #Power plot
    do_plot_3(db, 2, os.path.join(img_dir_path, 'live_e.png'))  #Volumes/agitation plot


