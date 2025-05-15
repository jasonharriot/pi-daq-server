import mysql.connector
import adam6200

db = mysql.connector.connect(
        #host="pidaq.local",
        host="localhost",
        user="pi-daq-client",
        password="R7prr@bXw",
        database="hydromet_reactor"
        )

print(db)

cur = db.cursor()

cur.execute('show databases')

for row in cur:
    print(row)



#Create a test data table

table_str = 'id INT AUTO_INCREMENT PRIMARY KEY, timestamp TIMESTAMP DEFAULT UTC_TIMESTAMP, channel INT, value INT'
print(f'Making a table with this configuration: {table_str}')
cur.execute(f"CREATE TABLE IF NOT EXISTS adam_value ({table_str})")



#Create a test range table

table_str = 'id INT AUTO_INCREMENT PRIMARY KEY, timestamp TIMESTAMP DEFAULT UTC_TIMESTAMP, channel INT, range_id CHAR(16), name CHAR(16), range_min INT, range_max INT, unit CHAR(16)'
print(f'Making a table with this configuration: {table_str}')
cur.execute(f'CREATE TABLE IF NOT EXISTS adam_range ({table_str})')

adam1 = adam6200.ADAM6200('192.168.1.10')

ranges = adam1.ranges

for channel, r in ranges.items():
    print(r["name"])
    cur.execute(f'INSERT INTO adam_range (channel, range_id, name, range_min, range_max, unit) VALUES ("{channel}", "{r["id"]}", "{r["name"]}", "{r["min"]}", "{r["max"]}", "{r["unit"]}")')

values = adam1.get_values()

for channel, v in values.items():
    cur.execute(f'INSERT INTO adam_value (channel, value) VALUES ("{channel}", "{v}")')


db.commit()

print('Done.')
