import mysql.connector
import adam6200
import datetime
import time
import utils

def capture_values(adam, db):
    
    cur = db.cursor()

    #Create a data table

    table_str = 'id INT AUTO_INCREMENT PRIMARY KEY, timestamp TIMESTAMP DEFAULT UTC_TIMESTAMP, channel INT, value INT'
    cur.execute(f"CREATE TABLE IF NOT EXISTS adam_value ({table_str})")

    
    values = adam.get_values()

    for channel, v in values.items():
        cur.execute(f'INSERT INTO adam_value (channel, value) VALUES ("{channel}", "{v}")')


    db.commit()
    cur.close()



def capture_ranges(adam, db):
    cur = db.cursor()

    #Create a range table

    table_str = 'id INT AUTO_INCREMENT PRIMARY KEY, timestamp TIMESTAMP DEFAULT UTC_TIMESTAMP, channel INT, range_id CHAR(16), name CHAR(16), range_min INT, range_max INT, unit CHAR(16)'
    cur.execute(f'CREATE TABLE IF NOT EXISTS adam_range ({table_str})')

    ranges = adam.ranges

    for channel, r in ranges.items():
        cur.execute(f'INSERT INTO adam_range (channel, range_id, name, range_min, range_max, unit) VALUES ("{channel}", "{r["id"]}", "{r["name"]}", "{r["min"]}", "{r["max"]}", "{r["unit"]}")')

    db.commit()
    cur.close()



if __name__ == '__main__':
    print(f'Pi DAQ Main Python Script')

    db = mysql.connector.connect(
            #host="pidaq.local",
            host="localhost",
            user="pi-daq-client",
            password="R7prr@bXw",
            database="hydromet_reactor"
            )

    adam1 = adam6200.ADAM6200('192.168.1.10')

    data_timer = utils.Timer(datetime.timedelta(seconds=1))
    range_timer = utils.Timer(datetime.timedelta(days=1))

    while True:
        if data_timer.fire():
            capture_values(adam1, db)

        if range_timer.fire():
            capture_ranges(adam1, db)

            time.sleep(.1)

