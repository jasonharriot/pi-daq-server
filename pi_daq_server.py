import mysql.connector
import adam6200
import datetime
import time
import configparser
import timer

def map_raw_value(value, calib_item):
    real_slope_per_raw = (calib_item['max_real']-calib_item['min_real'])/(calib_item['max_raw'] - calib_item['min_raw'])
    real_intercept_at_zero_raw = (calib_item['max_real'] + calib_item['min_real'] - real_slope_per_raw*(calib_item['min_raw'] + calib_item['max_raw']))/2

    real_value = real_slope_per_raw*value + real_intercept_at_zero_raw

    return real_value


def capture_values(adam, db, calib):
    cur = db.cursor()

    #Create a data table

    data_column_names = []

    for channel, calib_item in calib.items():
        data_column_names.append(f"{calib_item['name']}_raw")

    for channel, calib_item in calib.items():
        data_column_names.append(f"{calib_item['name']}_real")

    #data_column_names_str = ', '.join(data_column_names)
    table_def_column_names_str = ', '.join(f"{x} FLOAT" for x in data_column_names)

    table_str = f'id INT AUTO_INCREMENT PRIMARY KEY, timestamp TIMESTAMP DEFAULT UTC_TIMESTAMP, {table_def_column_names_str}'
    cmd_str = f"CREATE TABLE IF NOT EXISTS adam_rows ({table_str})"
    #print(cmd_str)
    cur.execute(cmd_str)



    #Construct insert statement

    first_part_str = ', '.join(data_column_names)

    raw_values = adam.get_values()

    selected_raw_values = []
    real_values = []

    for channel, calib_item in calib.items():
        raw_value = raw_values[channel]
        real_value = map_raw_value(raw_value, calib_item)

        selected_raw_values.append(f'"{raw_value}"')
        real_values.append(f'"{real_value}"')


    second_part_str = ', '.join([', '.join(selected_raw_values), ', '.join(real_values)])

    cmd_str = f'INSERT INTO adam_rows ({first_part_str}) VALUES ({second_part_str})'

    #print(cmd_str)

    cur.execute(cmd_str)


    db.commit()
    cur.close()



def capture_ranges(adam, db, calib):
    cur = db.cursor()

    #Create a range table

    table_str = 'id INT AUTO_INCREMENT PRIMARY KEY, timestamp TIMESTAMP DEFAULT UTC_TIMESTAMP, channel INT, range_id CHAR(16), name CHAR(16), range_min FLOAT, range_max FLOAT, unit CHAR(16)'
    cmd_str = f'CREATE TABLE IF NOT EXISTS adam_range ({table_str})'
    print(cmd_str)
    cur.execute(cmd_str)

    ranges = adam.ranges

    for channel, r in ranges.items():
        cmd_str = f'INSERT INTO adam_range (channel, range_id, name, range_min, range_max, unit) VALUES ("{channel}", "{r["id"]}", "{r["name"]}", "{r["min"]}", "{r["max"]}", "{r["unit"]}")'
        print(cmd_str)
        cur.execute(cmd_str)

    db.commit()
    cur.close()



if __name__ == '__main__':
    print(f'Pi DAQ Main Python Script')

    cfg = configparser.ConfigParser()
    cfg.read('config_server.ini')   #Read sensitive parameters from the configuration file.

    adam1_config = cfg['adam1']

    databases = []

    for config_mysql_section in ['mysql', 'mysqlalt1']:
        config = cfg[config_mysql_section]
        print(f'Creating connection to database at {config["host"]}')
        db = mysql.connector.connect(
            host=config['host'],
            user=config['user'],
            password=config['password'],
            database=config['database']
            )

        databases.append(db)

    adam1 = adam6200.ADAM6200(adam1_config['ip'])


    calib = {   #Map raw ADC values (mA or V) from the ADAM to real-world process values. Units not saved anywhere in the DB.
        2:{
            'name':'T1',
            'min_raw':1,
            'max_raw':5,
            'min_real':0,
            'max_real':120,
        },
        3:{
            'name':'T2',
            'min_raw':1,
            'max_raw':5,
            'min_real':0,
            'max_real':100,
        },
        4:{
            'name':'V1',
            'min_raw':1,
            'max_raw':5,
            'min_real':337,
            'max_real':785,
        },
        5:{
            'name':'S1',
            'min_raw':0.04515,
            'max_raw':20,
            'min_real':0,
            'max_real':87
        }
    }


    data_timer = timer.Timer(datetime.timedelta(seconds=10))    #Capture new data at this interval

    for database in databases:
        capture_ranges(adam1, database, calib)

    while True:
        if data_timer.fire():
            for database in databases:
                try:
                    capture_values(adam1, database, calib)
                except:
                    print(f'Exception while writing data to database @ {database.server_host}.')
                    try:
                        database.reconnect()
                        print(f'Reconnected to {database.server_host}')
                    except:
                        print(f'Could not reconnect to {database.server_host}')

        time.sleep(.1)

##

