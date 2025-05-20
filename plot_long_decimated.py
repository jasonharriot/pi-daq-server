import mysql.connector
import time
import configparser
import datetime
import zoneinfo
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation

def fetch_df(db, channel_names):
    cur = db.cursor()

    now = datetime.datetime.now(datetime.timezone.utc)    #Get UTC time

    timespan_hours = 24

    target_point_count = 1000

    server_data_rate = 1    #per second

    start_date = now - datetime.timedelta(hours=timespan_hours)
    start_date_str = start_date.strftime('%Y-%m-%d %H:%M:%S')

    decimation = int((server_data_rate) / (target_point_count / (timespan_hours*60*60)))

    print(f'Grabbing data starting from UTC date: {start_date}. Decimation: {decimation}')

    cur.execute(f"SELECT * FROM adam_rows WHERE timestamp > '{start_date_str}' HAVING id % {decimation} = 0")

    print(f'SQL command exeuted.')

    df = pd.DataFrame(columns = ['timestamp'] + channel_names)  #Dataframe shall have timestamp, T1, T2, etc. columns.

    #print(df.columns)


    print(f'Receiving data...')

    i=0

    for row in cur:
        row_id = row[0]
        timestamp_utc = row[1].replace(tzinfo=datetime.timezone.utc) #Capture the time as recorded in the DB, and make sure it is interpreted as a UTC date.
        timestamp_local = timestamp_utc.astimezone(zoneinfo.ZoneInfo('America/New_York'))

        #Real values:
        t1 = row[5]
        t2 = row[6]
        v1 = row[7]

        df_row = [timestamp_local, t1, t2, v1]  #We will have the local time in our data from here on.

        df.loc[i] = df_row

        i+=1

    print(f'Received total of {i} rows')

    print(df)

    cur.close()

    return df

def fetch_ranges(db, channel_names):
    pass

def update(frame, db, channel_names, df, graph_T1, graph_T2, graph_V1):
    df = fetch_df(db, channel_names)    #Grab the latest data

    graph_T1.set_xdata(df['timestamp'])
    graph_T1.set_ydata(df['T1'])

    graph_T2.set_xdata(df['timestamp'])
    graph_T2.set_ydata(df['T2'])

    graph_V1.set_xdata(df['timestamp'])
    graph_V1.set_ydata(df['V1'])

    plt.xlim(df['timestamp'].iloc[0], df['timestamp'].iloc[-1] + datetime.timedelta(minutes=5))



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

    channel_names = ['T1', 'T2', 'V1']  #Name prototypes for which we can find columns in the DB like T1_raw, etc.

    #Construct a basic line plot

    df = fetch_df(db, channel_names)    #Grab the latest data

    fig, ax1 = plt.subplots()    #Get the figure object and primary axes for later use

    ax2 = ax1.twinx()   #Secondary y-axis object

    ax1.tick_params(axis='x', labelrotation=45) #Make the x-axis labels rotated so they fit better

    ax1.set_xlabel('Date')
    ax1.set_ylabel('Temperature (°C)')
    ax2.set_ylabel('Volume (L)')

    ax2.yaxis.set_major_formatter('{x:.0f}')    #Display numbers on the secondary y-axis with no decimal point.
    ax2.set_ylim(300, 900)  #Set the limits of the secondary y-axis.

    graph_T1 = ax1.step(df['timestamp'], df['T1'], color='red', label='T1')[0]    #Plot T1. Grab element [0] of the return value. Don't need the other values.
    graph_T2 = ax1.step(df['timestamp'], df['T2'], color='orange', label='T2')[0] #Plot T2
    graph_V1 = ax2.step(df['timestamp'], df['V1'], color='blue', label='V1')[0]   #Plot V1 on the secondary y-axis

    #ax1.legend(loc='upper left')    #Place a legend for the primary axes
    #ax2.legend(loc='upper center')   #Place a legend for the secondary axes, but specify the location.

    graphs = [graph_T1, graph_T2, graph_V1]

    labels = [graph.get_label() for graph in graphs]

    ax1.legend(graphs, labels, loc=0)

    #Plot the data stored in the df variable. We will modify it later

   

    plt.tight_layout()  #This option is a better layout than the default. By default, some labels and text are compeltely cut-off at the edges of the plot.


    anim = matplotlib.animation.FuncAnimation(fig, update, interval=60000, frames = None, fargs = (db, channel_names, df, graph_T1, graph_T2, graph_V1), cache_frame_data = False)

    plt.show()